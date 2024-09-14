#!/usr/bin/python

from pydbus import SessionBus
import sys

wallpaper_dir = ""
if len(sys.argv) > 1:
    wallpaper_dir = sys.argv[1]

# Connect to dbus
bus = SessionBus()
service = bus.get("net.nobody1902.pydbus.swimg")

if wallpaper_dir:
    service.set_wallpapers_dir(wallpaper_dir)

service.next_img()
