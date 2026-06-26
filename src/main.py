#!/usr/bin/env python3

import os
import sys
from pathlib import Path

from cli import parse_args
from downloader import pull_image
from container import Container

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / "images"

def main():
    if os.geteuid() != 0:
        print("[gkr] run with sudo, please")
        sys.exit(1)

    args = parse_args()
    IMAGES_DIR.mkdir(exist_ok=True)

    if args.command == "pull":
        pull_image(args.image, args.tag, IMAGES_DIR)
        
    elif args.command == "run":
        rootfs_path = IMAGES_DIR / f"{args.image}_latest"
        
        if not rootfs_path.exists():
            rootfs_path = pull_image(args.image, "latest", IMAGES_DIR)
        container = Container(str(rootfs_path), args.container_command)
        container.start()

if __name__ == "__main__":
    main()