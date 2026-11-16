#!/usr/bin/env python3
"""Create SmartTube-compatible update metadata for a signed NewTube release."""
import argparse
import json
import re
import subprocess
from pathlib import Path

REPO = "https://github.com/arinaggarwal1/SmartTube/releases/download"
PACKAGES = {"stable": "com.arinaggarwal.newtube", "beta": "com.arinaggarwal.newtube.beta"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk", required=True, type=Path)
    parser.add_argument("--channel", choices=PACKAGES, default="stable")
    parser.add_argument("--tag", required=True, help="GitHub release tag")
    parser.add_argument("--aapt", default="aapt")
    parser.add_argument("--apksigner", default="apksigner")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.tag):
        parser.error("tag must use letters, digits, periods, dashes or underscores")
    signature = subprocess.check_output([args.apksigner, "verify", "--print-certs", str(args.apk)], text=True)
    matches = re.findall(r"^Signer #\d+ certificate SHA-256 digest: ([0-9a-fA-F]+)$", signature, re.MULTILINE)
    pin = (Path(__file__).resolve().parent.parent / "config/signing-cert.sha256").read_text().strip().lower()
    if len(matches) != 1 or matches[0].lower() != pin:
        raise SystemExit("APK signer does not match the pinned NewTube signing identity")
    info = subprocess.check_output([args.aapt, "dump", "badging", str(args.apk)], text=True)
    line = info.splitlines()[0]
    match = re.search(r"package: name='([^']+)' versionCode='([0-9]+)' versionName='([^']+)'", line)
    if not match or match.group(1) != PACKAGES[args.channel]:
        raise SystemExit("APK package or version does not match the selected NewTube channel")
    if not re.fullmatch(r"[A-Za-z0-9._-]+\.apk", args.apk.name):
        raise SystemExit("APK filename is not safe for a release URL")
    manifest = {
        "package": {"downloadUrl": f"{REPO}/{args.tag}/{args.apk.name}"},
        match.group(3): {"versionCode": int(match.group(2)), "changelog": ["NewTube update"]},
    }
    output = args.output or Path(f"newtube_{args.channel}.json")
    output.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
