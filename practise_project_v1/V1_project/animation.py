"""Hand-gesture anti-gravity drawing demo.

Features:
- Webcam hand tracking using MediaPipe Tasks HandLandmarker.
- Pinch gesture (thumb + index) to draw in air.
- Anti-gravity particles that float upward while drawing.
- Heart-shape stroke detection; if detected, the shape is color-filled and gets a particle burst.

Controls:
- q : quit
- c : clear canvas and particles
- r : random drawing color
- a : toggle anti-gravity particle effect
"""

from __future__ import annotations

import math
import random
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision


WINDOW_NAME = "HandGesture Anti-Gravity Painter"
MODEL_URL = (
	"https://storage.googleapis.com/mediapipe-models/"
	"hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
)


@dataclass
class Particle:
	x: float
	y: float
	vx: float
	vy: float
	life: float
	size: int
	color: tuple[int, int, int]


def ensure_model_downloaded() -> str:
	model_dir = Path.home() / ".mediapipe_models"
	model_dir.mkdir(exist_ok=True)
	model_path = model_dir / "hand_landmarker.task"

	if not model_path.exists():
		urllib.request.urlretrieve(MODEL_URL, model_path)

	return str(model_path)


def create_hand_landmarker():
	base_options = BaseOptions(model_asset_path=ensure_model_downloaded())
	options = vision.HandLandmarkerOptions(
		base_options=base_options,
		num_hands=1,
		min_hand_detection_confidence=0.7,
		min_hand_presence_confidence=0.6,
		min_tracking_confidence=0.6,
	)
	return vision.HandLandmarker.create_from_options(options)


def get_index_and_thumb_px(landmarks, frame_shape: tuple[int, int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
	h, w, _ = frame_shape
	idx = landmarks[8]
	thb = landmarks[4]
	index_px = (int(idx.x * w), int(idx.y * h))
	thumb_px = (int(thb.x * w), int(thb.y * h))
	return index_px, thumb_px


def pinch_active(index_px: tuple[int, int], thumb_px: tuple[int, int], threshold_px: int = 45) -> bool:
	dist = math.dist(index_px, thumb_px)
	return dist < threshold_px


def random_vibrant_color() -> tuple[int, int, int]:
	palette = [
		(255, 80, 80),
		(255, 180, 60),
		(80, 255, 160),
		(90, 190, 255),
		(230, 120, 255),
		(255, 120, 200),
	]
	return random.choice(palette)


def spawn_particles(particles: list[Particle], x: int, y: int, color: tuple[int, int, int], burst: bool = False) -> None:
	count = 35 if burst else 4
	for _ in range(count):
		vx = random.uniform(-0.8, 0.8) if not burst else random.uniform(-2.0, 2.0)
		vy = random.uniform(-2.8, -1.2) if not burst else random.uniform(-4.8, -1.5)
		life = random.uniform(0.5, 1.0) if not burst else random.uniform(0.8, 1.4)
		size = random.randint(1, 3) if not burst else random.randint(2, 5)
		particles.append(Particle(float(x), float(y), vx, vy, life, size, color))


def update_and_draw_particles(frame: np.ndarray, particles: list[Particle]) -> None:
	h, w, _ = frame.shape
	alive: list[Particle] = []

	for p in particles:
		p.x += p.vx
		p.y += p.vy
		p.vx *= 0.99
		p.vy -= 0.02
		p.life -= 0.02

		if p.life <= 0 or p.x < 0 or p.x >= w or p.y < 0 or p.y >= h:
			continue

		alpha = max(0.0, min(1.0, p.life))
		draw_color = tuple(int(c * alpha) for c in p.color)
		cv2.circle(frame, (int(p.x), int(p.y)), p.size, draw_color, -1)
		alive.append(p)

	particles[:] = alive


def normalize_points(points: list[tuple[int, int]], size: int = 256) -> np.ndarray:
	pts = np.array(points, dtype=np.float32)
	min_xy = pts.min(axis=0)
	max_xy = pts.max(axis=0)
	span = np.maximum(max_xy - min_xy, 1.0)
	norm = (pts - min_xy) / span
	norm *= size - 1
	return norm.astype(np.int32)


def heart_template_hu() -> np.ndarray:
	t = np.linspace(0, 2 * math.pi, 500)
	x = 16 * np.sin(t) ** 3
	y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
	pts = np.column_stack((x, -y)).astype(np.float32)

	min_xy = pts.min(axis=0)
	max_xy = pts.max(axis=0)
	pts = (pts - min_xy) / (max_xy - min_xy)
	pts *= 255
	pts = pts.astype(np.int32)

	mask = np.zeros((256, 256), dtype=np.uint8)
	cv2.fillPoly(mask, [pts], 255)
	moments = cv2.moments(mask)
	hu = cv2.HuMoments(moments).flatten()
	hu = np.sign(hu) * np.log10(np.abs(hu) + 1e-12)
	return hu


HEART_HU = heart_template_hu()


def looks_like_heart(stroke_points: list[tuple[int, int]]) -> bool:
	if len(stroke_points) < 40:
		return False

	if math.dist(stroke_points[0], stroke_points[-1]) > 40:
		return False

	norm_pts = normalize_points(stroke_points)
	mask = np.zeros((256, 256), dtype=np.uint8)
	cv2.polylines(mask, [norm_pts], isClosed=True, color=255, thickness=4)

	contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	if not contours:
		return False

	cnt = max(contours, key=cv2.contourArea)
	area = cv2.contourArea(cnt)
	if area < 900:
		return False

	filled = np.zeros_like(mask)
	cv2.drawContours(filled, [cnt], -1, 255, thickness=-1)
	moments = cv2.moments(filled)
	hu = cv2.HuMoments(moments).flatten()
	hu = np.sign(hu) * np.log10(np.abs(hu) + 1e-12)
	diff = float(np.mean(np.abs(hu - HEART_HU)))

	return diff < 1.6


def fill_stroke_shape(canvas: np.ndarray, stroke_points: list[tuple[int, int]], color: tuple[int, int, int]) -> None:
	pts = np.array(stroke_points, dtype=np.int32)
	if len(pts) < 3:
		return
	cv2.fillPoly(canvas, [pts], color)


def draw_ui(frame: np.ndarray, draw_color: tuple[int, int, int], mode_text: str, antigravity_on: bool) -> None:
	cv2.rectangle(frame, (12, 12), (560, 120), (18, 28, 40), -1)
	cv2.rectangle(frame, (12, 12), (560, 120), (0, 220, 255), 1)

	cv2.putText(frame, "ANTI-GRAVITY HAND PAINTER", (24, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (0, 220, 255), 2)
	cv2.putText(frame, f"Status: {mode_text}", (24, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (230, 230, 230), 2)
	cv2.putText(frame, "Pinch to draw | q quit | c clear | r color | a particles", (24, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (180, 200, 220), 1)

	cv2.rectangle(frame, (575, 20), (625, 70), draw_color, -1)
	cv2.rectangle(frame, (575, 20), (625, 70), (255, 255, 255), 1)
	ag_color = (60, 220, 120) if antigravity_on else (90, 90, 90)
	cv2.putText(frame, "AG", (638, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.8, ag_color, 2)


def run() -> None:
	cap = cv2.VideoCapture(0)
	if not cap.isOpened():
		raise RuntimeError("Could not open webcam. Check camera permissions/device.")

	hand_landmarker = create_hand_landmarker()
	canvas: Optional[np.ndarray] = None
	particles: list[Particle] = []

	drawing = False
	stroke_points: list[tuple[int, int]] = []
	draw_color = random_vibrant_color()
	mode_text = "Searching for hand"
	antigravity_on = True

	print("[BOOT] HandGesture Anti-Gravity Painter")
	print("[INFO] Pinch thumb + index to draw. Draw a closed heart to auto-fill with color.")
	print("[INFO] Keys: q quit | c clear | r random color | a toggle anti-gravity")

	try:
		while True:
			ok, frame = cap.read()
			if not ok:
				continue

			frame = cv2.flip(frame, 1)
			if canvas is None:
				canvas = np.zeros_like(frame)

			rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

			try:
				results = hand_landmarker.detect(mp_image)
			except Exception:
				results = None

			just_finished_stroke = False

			if results and results.hand_landmarks:
				lm = results.hand_landmarks[0]
				index_px, thumb_px = get_index_and_thumb_px(lm, frame.shape)

				cv2.circle(frame, index_px, 8, (0, 220, 255), -1)
				cv2.circle(frame, thumb_px, 8, (255, 180, 80), -1)
				cv2.line(frame, index_px, thumb_px, (120, 180, 255), 2)

				active = pinch_active(index_px, thumb_px)
				if active:
					mode_text = "Drawing"
					if not drawing:
						drawing = True
						stroke_points = [index_px]
					else:
						last = stroke_points[-1]
						if math.dist(last, index_px) > 2:
							stroke_points.append(index_px)
							cv2.line(canvas, last, index_px, draw_color, 4)

					if antigravity_on:
						spawn_particles(particles, index_px[0], index_px[1], draw_color)
				else:
					if drawing:
						just_finished_stroke = True
					drawing = False
					mode_text = "Hand detected"
			else:
				if drawing:
					just_finished_stroke = True
				drawing = False
				mode_text = "Searching for hand"

			if just_finished_stroke and len(stroke_points) > 20:
				if looks_like_heart(stroke_points):
					fill_color = random_vibrant_color()
					fill_stroke_shape(canvas, stroke_points, fill_color)
					mode_text = "Heart recognized - color fill applied"

					cx = int(sum(p[0] for p in stroke_points) / len(stroke_points))
					cy = int(sum(p[1] for p in stroke_points) / len(stroke_points))
					if antigravity_on:
						spawn_particles(particles, cx, cy, fill_color, burst=True)
				stroke_points = []

			composed = cv2.addWeighted(frame, 0.8, canvas, 1.0, 0)
			if antigravity_on:
				update_and_draw_particles(composed, particles)

			if drawing and len(stroke_points) > 1:
				pts = np.array(stroke_points, dtype=np.int32)
				cv2.polylines(composed, [pts], False, (255, 255, 255), 1)

			draw_ui(composed, draw_color, mode_text, antigravity_on)
			cv2.imshow(WINDOW_NAME, composed)

			key = cv2.waitKey(1) & 0xFF
			if key == ord("q"):
				break
			if key == ord("c"):
				canvas = np.zeros_like(frame)
				particles.clear()
				stroke_points = []
				mode_text = "Canvas cleared"
			if key == ord("r"):
				draw_color = random_vibrant_color()
				mode_text = "Drawing color changed"
			if key == ord("a"):
				antigravity_on = not antigravity_on
				mode_text = "Anti-gravity on" if antigravity_on else "Anti-gravity off"

	finally:
		cap.release()
		hand_landmarker.close()
		cv2.destroyAllWindows()


if __name__ == "__main__":
	run()
