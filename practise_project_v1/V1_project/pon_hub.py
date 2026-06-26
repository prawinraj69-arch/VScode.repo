"""
Default duration is 30 minutes.
NordVPN:
python porn_hub.py --provider nordvpn

NordVPN with country:
python porn_hub.py --provider nordvpn --country India

ProtonVPN:
python porn_hub.py --provider protonvpn

Change duration:
python porn_hub.py --provider nordvpn --minutes 45
"""

import argparse
import os
import subprocess
import sys
import time


def provider_commands(args: argparse.Namespace) -> tuple[str | None, str | None]:
	"""Build connect/disconnect commands from a known VPN provider."""
	provider = (args.provider or "").lower()

	if not provider:
		return args.connect_cmd, args.disconnect_cmd

	if provider == "nordvpn":
		connect_cmd = "nordvpn connect"
		if args.country:
			connect_cmd += f" {args.country}"
		return connect_cmd, "nordvpn disconnect"

	if provider == "protonvpn":
		# ProtonVPN CLI v3 style command.
		connect_cmd = "protonvpn-cli connect --fastest"
		if args.country:
			connect_cmd = f"protonvpn-cli connect --cc {args.country}"
		return connect_cmd, "protonvpn-cli disconnect"

	if provider == "rasdial":
		if not args.vpn_name:
			raise ValueError("--vpn-name is required when --provider rasdial is used")

		if args.vpn_user and args.vpn_password:
			connect_cmd = f'rasdial "{args.vpn_name}" "{args.vpn_user}" "{args.vpn_password}"'
		else:
			connect_cmd = f'rasdial "{args.vpn_name}"'

		disconnect_cmd = f'rasdial "{args.vpn_name}" /disconnect'
		return connect_cmd, disconnect_cmd

	raise ValueError("Unsupported provider. Use: nordvpn, protonvpn, or rasdial")


def run_command(command: str, action_name: str) -> None:
	"""Run a shell command and fail fast if it does not succeed."""
	print(f"[{action_name}] Running: {command}")
	completed = subprocess.run(command, shell=True, text=True)
	if completed.returncode != 0:
		raise RuntimeError(f"{action_name} command failed with exit code {completed.returncode}")


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Activate VPN for a fixed duration, then auto-disconnect."
	)
	parser.add_argument(
		"--minutes",
		type=int,
		default=30,
		help="How long to keep VPN active (default: 30 minutes)",
	)
	parser.add_argument(
		"--connect-cmd",
		default=os.getenv("VPN_CONNECT_CMD"),
		help="Command to connect VPN. Can also be set via VPN_CONNECT_CMD env var.",
	)
	parser.add_argument(
		"--disconnect-cmd",
		default=os.getenv("VPN_DISCONNECT_CMD"),
		help="Command to disconnect VPN. Can also be set via VPN_DISCONNECT_CMD env var.",
	)
	parser.add_argument(
		"--provider",
		choices=["nordvpn", "protonvpn", "rasdial"],
		help="Optional VPN provider shortcut.",
	)
	parser.add_argument(
		"--country",
		help="Optional country code/name for provider connect command (for nordvpn/protonvpn).",
	)
	parser.add_argument(
		"--vpn-name",
		help="VPN connection name used by rasdial.",
	)
	parser.add_argument(
		"--vpn-user",
		help="VPN username for rasdial (optional if profile stores credentials).",
	)
	parser.add_argument(
		"--vpn-password",
		help="VPN password for rasdial (optional if profile stores credentials).",
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()

	if args.minutes <= 0:
		print("Error: --minutes must be greater than 0")
		return 1

	try:
		args.connect_cmd, args.disconnect_cmd = provider_commands(args)
	except ValueError as exc:
		print(f"Error: {exc}")
		return 1

	if not args.connect_cmd or not args.disconnect_cmd:
		print("Error: VPN commands are missing.")
		print("Provide either:")
		print("  1) --provider with provider-specific args, or")
		print("  2) --connect-cmd and --disconnect-cmd, or")
		print("  3) env vars VPN_CONNECT_CMD and VPN_DISCONNECT_CMD")
		print()
		print("Examples:")
		print("  python porn_hub.py --provider nordvpn")
		print('  python porn_hub.py --provider rasdial --vpn-name "MyVPN" --vpn-user "myUser" --vpn-password "myPass"')
		print('  python porn_hub.py --connect-cmd "rasdial MyVPN myUser myPass" --disconnect-cmd "rasdial MyVPN /disconnect"')
		print()
		print("Env vars:")
		print("  VPN_CONNECT_CMD")
		print("  VPN_DISCONNECT_CMD")
		return 1

	duration_seconds = args.minutes * 60

	disconnect_failed = False

	try:
		run_command(args.connect_cmd, "CONNECT")
		print(f"VPN connected. Keeping it ON for {args.minutes} minute(s)...")
		time.sleep(duration_seconds)
	except KeyboardInterrupt:
		print("\nInterrupted by user. Attempting VPN disconnect...")
	except Exception as exc:
		print(f"Error: {exc}")
		return 1
	finally:
		try:
			run_command(args.disconnect_cmd, "DISCONNECT")
			print("VPN disconnected.")
		except Exception as exc:
			print(f"Warning: Could not disconnect VPN automatically: {exc}")
			disconnect_failed = True

	if disconnect_failed:
		return 1

	return 0


if __name__ == "__main__":
	sys.exit(main())
