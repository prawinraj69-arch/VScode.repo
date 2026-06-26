"""Real-time emotion detection or augmented reality demo.

Usage examples:
  python emotions.py --mode emotion
  python emotions.py --mode ar
  python emotions.py --mode ar --camera 1

Dependencies:
  pip install opencv-python opencv-contrib-python fer
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import importlib
from pathlib import Path
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import cv2
import numpy as np


def put_label(frame: np.ndarray, text: str, origin: Tuple[int, int], color: Tuple[int, int, int]) -> None:
	"""Draw readable text with a small dark background."""
	x, y = origin
	(w, h), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
	cv2.rectangle(frame, (x, y - h - baseline - 8), (x + w + 8, y + 4), (20, 20, 20), -1)
	cv2.putText(frame, text, (x + 4, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)


def open_camera(camera_index: int) -> cv2.VideoCapture:
	cap = cv2.VideoCapture(camera_index)
	if not cap.isOpened():
		raise RuntimeError(
			f"Could not open camera index {camera_index}. "
			"Try --camera 0, --camera 1, or close other apps using the webcam."
		)
	return cap


@dataclass
class EmotionPrediction:
	box: Tuple[int, int, int, int]
	emotion: str
	score: float


class EmotionCsvLogger:
	def __init__(self, csv_path: Path) -> None:
		self.csv_path = csv_path
		self.csv_path.parent.mkdir(parents=True, exist_ok=True)
		self._file = self.csv_path.open("a", newline="", encoding="utf-8")
		self._writer = csv.writer(self._file)

		if self.csv_path.stat().st_size == 0:
			self._writer.writerow(["timestamp", "emotion", "score", "x", "y", "w", "h"])
			self._file.flush()

	def write_prediction(self, prediction: EmotionPrediction) -> None:
		timestamp = datetime.now().isoformat(timespec="seconds")
		x, y, w, h = prediction.box
		self._writer.writerow([timestamp, prediction.emotion, f"{prediction.score:.4f}", x, y, w, h])
		self._file.flush()

	def close(self) -> None:
		self._file.close()


def save_snapshot(frame: np.ndarray, save_dir: Path) -> Path:
	save_dir.mkdir(parents=True, exist_ok=True)
	filename = f"emotion_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
	output_path = save_dir / filename
	cv2.imwrite(str(output_path), frame)
	return output_path


def infer_emotions_fallback(frame: np.ndarray) -> List[EmotionPrediction]:
	"""Fallback emotion approximation using Haar cascades.

	This is not a deep-learning emotion model. It uses face/smile/eye cues to
	provide basic labels when external emotion libraries are unavailable.
	"""
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
	smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")
	eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

	faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(70, 70))
	predictions: List[EmotionPrediction] = []

	for (x, y, w, h) in faces:
		roi_gray = gray[y:y + h, x:x + w]
		smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.7, minNeighbors=24, minSize=(25, 25))
		eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=8, minSize=(18, 18))

		if len(smiles) >= 1:
			label, score = "happy", 0.72
		elif len(eyes) == 0:
			label, score = "sleepy", 0.58
		else:
			label, score = "neutral", 0.60

		predictions.append(EmotionPrediction((int(x), int(y), int(w), int(h)), label, score))

	return predictions


def run_emotion_mode(camera_index: int, save_dir: Path, log_csv_path: Path, log_interval_seconds: float) -> None:
	fer_detector = None
	try:
		fer_module = importlib.import_module("fer")
		fer_detector = fer_module.FER(mtcnn=False)
		print("Using FER model for emotion detection.")
	except Exception:
		print("FER package not available. Using OpenCV heuristic fallback detector.")

	cap = open_camera(camera_index)
	logger = EmotionCsvLogger(log_csv_path)
	last_logged = 0.0

	print("Emotion mode started. Press 'c' to save snapshot, 'q' to quit.")
	print(f"CSV log file: {log_csv_path}")
	print(f"Snapshot folder: {save_dir}")

	try:
		while True:
			ok, frame = cap.read()
			if not ok:
				print("Warning: Could not read frame from camera.")
				break

			predictions: List[EmotionPrediction] = []

			if fer_detector is not None:
				rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
				results: List[Dict] = fer_detector.detect_emotions(rgb)

				for item in results:
					x, y, w, h = item["box"]
					emotions: Dict[str, float] = item.get("emotions", {})
					if not emotions:
						continue
					top_emotion = max(emotions, key=emotions.get)
					top_score = float(emotions[top_emotion])
					predictions.append(EmotionPrediction((x, y, w, h), top_emotion, top_score))
			else:
				predictions = infer_emotions_fallback(frame)

			for prediction in predictions:

				color = (60, 190, 120)
				cv2.rectangle(frame, (prediction.box[0], prediction.box[1]),
							  (prediction.box[0] + prediction.box[2], prediction.box[1] + prediction.box[3]),
							  color, 2)

				label = f"{prediction.emotion} ({prediction.score:.2f})"
				put_label(frame, label, (prediction.box[0], max(20, prediction.box[1])), color)

			now = time.time()
			if predictions and (now - last_logged) >= log_interval_seconds:
				for prediction in predictions:
					logger.write_prediction(prediction)
				last_logged = now

			put_label(frame, "Emotion Detection | Press c to capture | q to exit", (10, frame.shape[0] - 12), (230, 230, 230))
			cv2.imshow("Emotion Detector", frame)

			key = cv2.waitKey(1) & 0xFF
			if key == ord("c"):
				snapshot_path = save_snapshot(frame, save_dir)
				print(f"Saved snapshot: {snapshot_path}")
			if key == ord("q"):
				break
	finally:
		logger.close()
		cap.release()
		cv2.destroyAllWindows()


def _get_aruco_dictionary():
	if not hasattr(cv2, "aruco"):
		raise RuntimeError(
			"AR mode needs OpenCV aruco module. Install: pip install opencv-contrib-python"
		)
	return cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)


def draw_marker_id(frame: np.ndarray, marker_corners: np.ndarray, marker_id: int) -> None:
	corners = marker_corners.reshape((4, 2)).astype(int)
	top_left, top_right, bottom_right, bottom_left = corners

	cv2.polylines(frame, [corners], True, (255, 190, 0), 2)
	center_x = int((top_left[0] + bottom_right[0]) / 2)
	center_y = int((top_left[1] + bottom_right[1]) / 2)
	cv2.circle(frame, (center_x, center_y), 4, (255, 255, 255), -1)
	put_label(frame, f"Marker {marker_id}", (top_left[0], max(18, top_left[1])), (255, 200, 80))


def run_ar_mode(camera_index: int) -> None:
	aruco_dict = _get_aruco_dictionary()
	params = cv2.aruco.DetectorParameters()
	detector = cv2.aruco.ArucoDetector(aruco_dict, params)
	cap = open_camera(camera_index)

	print("AR mode started. Show an ArUco marker (DICT_4X4_50). Press 'q' to quit.")

	try:
		while True:
			ok, frame = cap.read()
			if not ok:
				print("Warning: Could not read frame from camera.")
				break

			corners, ids, _ = detector.detectMarkers(frame)

			if ids is not None and len(ids) > 0:
				for marker_corners, marker_id in zip(corners, ids.flatten()):
					draw_marker_id(frame, marker_corners, int(marker_id))

				cv2.putText(
					frame,
					"AR Overlay Active",
					(12, 34),
					cv2.FONT_HERSHEY_DUPLEX,
					0.8,
					(90, 240, 255),
					2,
					cv2.LINE_AA,
				)
			else:
				put_label(frame, "Point camera to an ArUco marker", (12, 34), (240, 240, 240))

			put_label(frame, "Augmented Reality | Press q to exit", (10, frame.shape[0] - 12), (230, 230, 230))
			cv2.imshow("AR Marker Demo", frame)

			key = cv2.waitKey(1) & 0xFF
			if key == ord("q"):
				break
	finally:
		cap.release()
		cv2.destroyAllWindows()


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Emotion detection or augmented reality webcam demo")
	parser.add_argument(
		"--mode",
		choices=["emotion", "ar"],
		default="emotion",
		help="Choose emotion detection or augmented reality marker mode",
	)
	parser.add_argument("--camera", type=int, default=0, help="Webcam index (default: 0)")
	parser.add_argument(
		"--save-dir",
		type=Path,
		default=Path("captures"),
		help="Directory for saving snapshots in emotion mode",
	)
	parser.add_argument(
		"--log-csv",
		type=Path,
		default=Path("emotion_log.csv"),
		help="CSV file path for emotion logs",
	)
	parser.add_argument(
		"--log-interval",
		type=float,
		default=1.0,
		help="Seconds between CSV log writes (default: 1.0)",
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()

	try:
		if args.mode == "emotion":
			run_emotion_mode(args.camera, args.save_dir, args.log_csv, max(0.1, args.log_interval))
		else:
			run_ar_mode(args.camera)
		return 0
	except RuntimeError as exc:
		print(f"Error: {exc}")
		return 1
	except KeyboardInterrupt:
		print("\nStopped by user.")
		return 0


if __name__ == "__main__":
	sys.exit(main())
