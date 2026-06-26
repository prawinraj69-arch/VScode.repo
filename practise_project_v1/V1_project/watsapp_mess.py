"""Send a WhatsApp group message when the script runs.

How it works:
1. Set GROUP_ID and MESSAGE below.
2. Run this file.
3. It schedules the message for the next minute using WhatsApp Web.

Requirements:
- pip install pywhatkit
- You must already be logged in to WhatsApp Web in your default browser.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import urlparse

import pywhatkit


# Replace this with your real WhatsApp group ID.
# Example group invite link: https://chat.whatsapp.com/AbCdEfGhIjKlMnOpQrStUv
# GROUP_ID is the last part only: "AbCdEfGhIjKlMnOpQrStUv"
GROUP_ID = "https://chat.whatsapp.com/KyfcOL55tcKB2JopHl6tVn"

# Message to send to the group.
MESSAGE = "this message is sent by a python script. Do not worry, it's just a test message to demonstrate automation, Have a great day everyone!"


def validate_group_id(group_id: str) -> None:
	if not group_id or group_id == "PASTE_YOUR_GROUP_ID_HERE":
		raise ValueError(
			"Set GROUP_ID in the script before running. "
			"Use the code from your WhatsApp group invite link."
		)


def normalize_group_id(group_id: str) -> str:
	"""Accept either a raw group code or full WhatsApp invite URL."""
	value = group_id.strip()

	if value.startswith("http://") or value.startswith("https://"):
		parsed = urlparse(value)
		path_parts = [part for part in parsed.path.split("/") if part]
		if not path_parts:
			raise ValueError("Invalid GROUP_ID URL. Could not extract group code.")
		value = path_parts[-1]

	if "/" in value or " " in value:
		raise ValueError(
			"GROUP_ID must be a group code (or a valid invite URL) without spaces."
		)

	return value


def send_group_message(group_id: str, message: str) -> None:
	now = datetime.now()
	send_time = now + timedelta(minutes=1)

	print("Preparing WhatsApp group message...")
	print(f"Message will be sent at {send_time.strftime('%H:%M')}")
	print("Do not close the browser until sending is completed.")

	pywhatkit.sendwhatmsg_to_group(
		group_id=group_id,
		message=message,
		time_hour=send_time.hour,
		time_min=send_time.minute,
		wait_time=20,
		tab_close=True,
		close_time=3,
	)

	print("Message sent successfully.")


def main() -> None:
	try:
		validate_group_id(GROUP_ID)
		group_id = normalize_group_id(GROUP_ID)
		send_group_message(group_id, MESSAGE)
	except Exception as exc:
		print(f"Error: {exc}")


if __name__ == "__main__":
	main()
