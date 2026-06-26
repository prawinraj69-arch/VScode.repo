"""Daily attendance email sender with click tracking.
python attendence.py --serve
python attendence.py --send-now
python attendence.py --status
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import smtplib
import threading
import time
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse


SENDER_EMAIL = os.getenv("ATTENDANCE_GMAIL_ADDRESS", "praveen.raj.mohan.learn@gmail.com")
SENDER_PASSWORD = os.getenv("ATTENDANCE_GMAIL_APP_PASSWORD", "fcva fbmk triq tyuv")

RECIPIENTS = [
	{"alias": "KD", "email": "prawinraj69@gmail.com"},
	{"alias": "A1-accused", "email": "prawin.raj.mohan.@gmail.com"},
	{"alias": "Praveen the Monk", "email": "praveen.raj.mohan.learn@gmail.com"},
]

# Set this to a publicly reachable URL if the recipients are outside your network.
PUBLIC_BASE_URL = os.getenv("ATTENDANCE_PUBLIC_BASE_URL", "http://127.0.0.1:8000")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

ATTENDANCE_TIME = os.getenv("ATTENDANCE_TIME", "08:00")
SERVER_HOST = os.getenv("ATTENDANCE_SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("ATTENDANCE_SERVER_PORT", "8000"))

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "attendance_log.csv"


def ensure_log_file() -> None:
	if LOG_FILE.exists():
		return
	with LOG_FILE.open("w", newline="", encoding="utf-8") as file_handle:
		writer = csv.writer(file_handle)
		writer.writerow(["email", "token", "created_at", "checked_in_at"])


@dataclass
class CheckinRecord:
	token: str
	email: str
	alias: str
	created_at: str
	checked_in_at: Optional[str] = None


class AttendanceManager:
	def __init__(self) -> None:
		self.records: Dict[str, CheckinRecord] = {}
		self.lock = threading.Lock()

	def _token_for(self, email: str, day: date) -> str:
		raw = f"{email.lower()}|{day.isoformat()}|attendance"
		return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]

	def create_daily_links(self) -> Dict[str, str]:
		today = date.today()
		links = {}

		with self.lock:
			for recipient in RECIPIENTS:
				email = recipient["email"]
				alias = recipient["alias"]
				token = self._token_for(email, today)
				self.records[token] = CheckinRecord(
					token=token,
					email=email,
					alias=alias,
					created_at=datetime.now().isoformat(timespec="seconds"),
				)
				links[email] = f"{PUBLIC_BASE_URL.rstrip('/')}/checkin/{token}"

		return links

	def _token_owner_email(self, token: str) -> Optional[str]:
		candidate_days = [date.today(), date.today() - timedelta(days=1)]
		for recipient in RECIPIENTS:
			candidate_email = recipient["email"]
			for day in candidate_days:
				if token == self._token_for(candidate_email, day):
					return candidate_email
		return None

	def _alias_for_email(self, email: str) -> str:
		for recipient in RECIPIENTS:
			if recipient["email"].lower() == email.lower():
				return recipient["alias"]
		return email

	def _find_logged_record(self, token: str) -> Optional[CheckinRecord]:
		ensure_log_file()
		with LOG_FILE.open("r", newline="", encoding="utf-8") as file_handle:
			reader = csv.DictReader(file_handle)
			for row in reader:
				if row.get("token") == token:
					email = row.get("email", "unknown")
					return CheckinRecord(
						token=token,
						email=email,
						alias=self._alias_for_email(email),
						created_at=row.get("created_at", ""),
						checked_in_at=row.get("checked_in_at", ""),
					)
		return None

	def mark_checkin(self, token: str) -> Optional[CheckinRecord]:
		with self.lock:
			record = self.records.get(token)

			# If this process restarted, recover from log or deterministic token match.
			if not record:
				record = self._find_logged_record(token)
				if record:
					self.records[token] = record
					return record

				owner_email = self._token_owner_email(token)
				if not owner_email:
					return None

				record = CheckinRecord(
					token=token,
					email=owner_email,
					alias=self._alias_for_email(owner_email),
					created_at=datetime.now().isoformat(timespec="seconds"),
				)
				self.records[token] = record

			if record.checked_in_at is None:
				record.checked_in_at = datetime.now().isoformat(timespec="seconds")
				self._append_log(record)
			return record

	def _append_log(self, record: CheckinRecord) -> None:
		ensure_log_file()
		with LOG_FILE.open("a", newline="", encoding="utf-8") as file_handle:
			writer = csv.writer(file_handle)
			writer.writerow([record.email, record.token, record.created_at, record.checked_in_at])

	def status_for_today(self) -> list[CheckinRecord]:
		today = date.today().isoformat()
		with self.lock:
			return [
				record
				for record in self.records.values()
				if record.created_at.startswith(today)
			]


ATTENDANCE = AttendanceManager()


def send_email(to_email: str, subject: str, html_body: str, text_body: str) -> None:
	if not SENDER_PASSWORD:
		raise RuntimeError("Set ATTENDANCE_GMAIL_APP_PASSWORD before sending emails.")

	message = EmailMessage()
	message["From"] = SENDER_EMAIL
	message["To"] = to_email
	message["Subject"] = subject
	message.set_content(text_body)
	message.add_alternative(html_body, subtype="html")

	with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
		smtp.starttls()
		smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
		smtp.send_message(message)


def build_attendance_email(candidate_email: str, checkin_link: str) -> tuple[str, str, str]:
	subject = f"Daily Attendance Check-in - {date.today().isoformat()}"
	text_body = (
		f"Hello,\n\n"
		f"Please mark your attendance for today by clicking the link below:\n"
		f"{checkin_link}\n\n"
		f"If you already clicked, no further action is needed.\n"
	)
	html_body = f"""
	<html>
	  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
		<h2>Daily Attendance</h2>
		<p>Hello {candidate_email},</p>
		<p>Please mark your attendance for today by clicking the link below:</p>
		<p>
		  <a href="{checkin_link}" style="background:#2563eb;color:#ffffff;padding:12px 18px;text-decoration:none;border-radius:6px;display:inline-block;">
			Mark Attendance
		  </a>
		</p>
		<p>If you already clicked, no further action is needed.</p>
	  </body>
	</html>
	"""
	return subject, text_body + "\n", html_body


def notify_owner(record: CheckinRecord) -> None:
	subject = f"Attendance received: {record.alias}"
	text_body = (
		f"Attendance received.\n\n"
		f"Name: {record.alias}\n"
		f"Email: {record.email}\n"
		f"Checked in at: {record.checked_in_at}\n"
	)
	html_body = f"""
	<html>
	  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
		<h2>Attendance Received</h2>
		<p><strong>Name:</strong> {record.alias}</p>
		<p><strong>Email:</strong> {record.email}</p>
		<p><strong>Checked in at:</strong> {record.checked_in_at}</p>
	  </body>
	</html>
	"""
	send_email(SENDER_EMAIL, subject, html_body, text_body)


def send_daily_attendance_emails() -> None:
	ensure_log_file()
	links = ATTENDANCE.create_daily_links()
	for recipient in RECIPIENTS:
		email = recipient["email"]
		alias = recipient["alias"]
		subject, text_body, html_body = build_attendance_email(email, links[email])
		send_email(email, subject, html_body, text_body)
		print(f"Sent attendance email to {alias}")


def parse_path(path: str) -> list[str]:
	parsed = urlparse(path)
	return [part for part in parsed.path.split("/") if part]


class AttendanceRequestHandler(BaseHTTPRequestHandler):
	def do_GET(self) -> None:
		parts = parse_path(self.path)

		if len(parts) == 2 and parts[0] == "checkin":
			token = parts[1]
			record = ATTENDANCE.mark_checkin(token)

			if record is None:
				self.send_response(404)
				self.send_header("Content-Type", "text/html; charset=utf-8")
				self.end_headers()
				self.wfile.write(b"<h1>Invalid or expired attendance link.</h1>")
				return

			try:
				notify_owner(record)
			except Exception as exc:
				print(f"Failed to notify owner: {exc}")

			self.send_response(200)
			self.send_header("Content-Type", "text/html; charset=utf-8")
			self.end_headers()
			self.wfile.write(
				f"""
				<html>
				  <head>
				    <title>Attendance Confirmed</title>
				    <script>
				      window.onload = function() {{
				        alert('Thanks a lot, Praveen');
				      }};
				    </script>
				    <style>
				      body {{
				        font-family: Arial, sans-serif;
				        display: flex;
				        align-items: center;
				        justify-content: center;
				        min-height: 100vh;
				        margin: 0;
				        background: #f7f7fb;
				      }}
				      .card {{
				        background: white;
				        padding: 32px 40px;
				        border-radius: 16px;
				        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
				        text-align: center;
				      }}
				      h1 {{ margin: 0 0 12px; color: #16a34a; }}
				      p {{ margin: 0; color: #333; font-size: 18px; }}
				    </style>
				  </head>
				  <body>
				    <div class="card">
				      <h1>Attendance Recorded</h1>
				      <p>Thanks a lot, Praveen. Your attendance has been saved.</p>
				    </div>
				  </body>
				</html>
				""".encode("utf-8")
			)
			print(f"Attendance recorded for {record.email} at {record.checked_in_at}")
			return

		if len(parts) == 1 and parts[0] == "health":
			self.send_response(200)
			self.send_header("Content-Type", "text/plain; charset=utf-8")
			self.end_headers()
			self.wfile.write(b"ok")
			return

		self.send_response(200)
		self.send_header("Content-Type", "text/html; charset=utf-8")
		self.end_headers()
		self.wfile.write(
			b"<html><body><h1>Attendance server running</h1><p>Use /checkin/&lt;token&gt; links from email.</p></body></html>"
		)

	def log_message(self, format: str, *args) -> None:
		return


def seconds_until(time_text: str) -> int:
	target_hour, target_minute = map(int, time_text.split(":"))
	now = datetime.now()
	target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
	if target <= now:
		target += timedelta(days=1)
	return int((target - now).total_seconds())


def run_scheduler() -> None:
	while True:
		wait_seconds = seconds_until(ATTENDANCE_TIME)
		print(f"Next attendance email will send in {wait_seconds} seconds at {ATTENDANCE_TIME}.")
		time.sleep(wait_seconds)
		try:
			send_daily_attendance_emails()
		except Exception as exc:
			print(f"Failed to send attendance emails: {exc}")


def start_server() -> ThreadingHTTPServer:
	server = ThreadingHTTPServer((SERVER_HOST, SERVER_PORT), AttendanceRequestHandler)
	thread = threading.Thread(target=server.serve_forever, daemon=True)
	thread.start()
	print(f"Attendance server running on http://{SERVER_HOST}:{SERVER_PORT}")
	print(f"Public base URL set to: {PUBLIC_BASE_URL}")
	return server


def print_configuration() -> None:
	print("Attendance automation configured with:")
	print(f"- Sender: {SENDER_EMAIL}")
	recipient_names = ", ".join(recipient["alias"] for recipient in RECIPIENTS)
	print(f"- Recipients: {recipient_names}")
	print(f"- Daily send time: {ATTENDANCE_TIME}")
	print(f"- Public base URL: {PUBLIC_BASE_URL}")
	print(f"- Log file: {LOG_FILE}")


def print_today_status() -> None:
	ensure_log_file()

	today = date.today().isoformat()
	matched_rows = []

	with LOG_FILE.open("r", newline="", encoding="utf-8") as file_handle:
		reader = csv.DictReader(file_handle)
		for row in reader:
			checked_in_at = row.get("checked_in_at", "")
			if checked_in_at.startswith(today):
				matched_rows.append(row)

	if not matched_rows:
		print(f"No attendance entries found for today ({today}).")
		return

	print(f"Attendance entries for today ({today}):")
	for row in matched_rows:
		email = row.get("email", "unknown")
		name = ATTENDANCE._alias_for_email(email)
		print(f"- {name} at {row.get('checked_in_at', 'unknown')}")


def main() -> None:
	parser = argparse.ArgumentParser(description="Daily attendance email sender")
	parser.add_argument("--send-now", action="store_true", help="Send today's attendance emails immediately")
	parser.add_argument("--serve", action="store_true", help="Start the click-tracking web server")
	parser.add_argument("--schedule", action="store_true", help="Run the daily scheduler")
	parser.add_argument("--run-all", action="store_true", help="Send emails now, start the server, and keep the scheduler running")
	parser.add_argument("--status", action="store_true", help="Show today's attendance log entries")
	args = parser.parse_args()

	print_configuration()

	if args.run_all:
		args.send_now = True
		args.serve = True
		args.schedule = True

	if args.status:
		print_today_status()

	if args.send_now:
		send_daily_attendance_emails()

	if args.serve:
		start_server()
		if not args.schedule:
			print("Press Ctrl+C to stop the attendance server.")
			try:
				threading.Event().wait()
			except KeyboardInterrupt:
				print("Server stopped.")

	if args.schedule:
		run_scheduler()

	if not any([args.send_now, args.serve, args.schedule, args.run_all, args.status]):
		print("No action selected. Try one of: --send-now, --serve, --schedule, --run-all, or --status")


if __name__ == "__main__":
	main()

