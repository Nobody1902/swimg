#!/usr/bin/python

import os
import random
import threading
import time
import glob

from pydbus import SessionBus
from gi.repository import GLib

loop = GLib.MainLoop()

class WallpaperService(object):
    """
        <node>
            <interface name='net.nobody1902.pydbus.swimg'>
                <method name='set_wallpapers_dir'>
                    <arg type='s' name='wallpapers_dir' direction='in'/>
                </method>
                <method name='next_img'/>
                <method name='prev_img'/>
                <method name='quit'/>
            </interface>
        </node>
    """

    wallpapers_dir: str = "$HOME/.config/wallpapers/"
    wallpapers: list[str] = []
    current_image = -1
    image_formats: list[str] = [".png", ".jpg", ".jpeg", ".svg", ".gif"]
    time_thread: threading.Thread
    time: float = 0

    time_wait = 10 * 60 * 10 # milliseconds

    def __init__(self):
        self.wallpapers_dir = os.path.expandvars(self.wallpapers_dir)

        if not os.path.exists(self.wallpapers_dir):
            print(f"Wallpapers directory: '{self.wallpapers_dir}' doesn't exist.");
            exit()

        print(f"Wallpapers directory: '{self.wallpapers_dir}'")

        # Load all wallpapers
        paths_list = glob.glob(self.wallpapers_dir + "/**/*", recursive=True)
        self.wallpapers = [path for path in paths_list if os.path.isfile(path) and os.path.splitext(path)[1] in self.image_formats]
        print(self.wallpapers)

        if len(self.wallpapers) < 1:
            print(f"No wallpapers found in '{self.wallpapers_dir}'")
            exit()

        random.shuffle(self.wallpapers)

        self.next_img()

        # Start thread that changes the background
        self.time_thread = threading.Thread(target=self.loop_change_wallpapers)
        self.time_thread.start()


    def loop_change_wallpapers(self):
        self.time = self.time_wait
        while True:
            time.sleep(0.1)
            self.time -= 1
            if self.time <= 0:
                self.next_img()

    def set_wallpapers_dir(self, wallpapers_dir):

        wallpapers_dir = os.path.expandvars(wallpapers_dir)

        if not wallpapers_dir or not os.path.exists(wallpapers_dir) or not os.path.isdir(wallpapers_dir):
            print(f"Couldn't set wallpapers directory to: '{wallpapers_dir}' because it either doesn't exist or it is a file not a directory.")
            return

        self.wallpapers_dir = wallpapers_dir
        print(f"Set wallpapers directory to: '{self.wallpapers_dir}'")

    def next_img(self):
        if self.current_image >= len(self.wallpapers)-1:
            self.current_image = -1

        self.current_image += 1
        self.update_img()

    def prev_img(self):
        if self.current_image < 1:
            self.current_image = len(self.wallpapers)

        self.current_image -= 1
        self.update_img()

    def update_img(self):
        print(f"{self.current_image}")
        print(f"Set wallpaper to '{os.path.join(self.wallpapers_dir, self.wallpapers[self.current_image])}'")
        os.system(f"swww img {os.path.join(self.wallpapers_dir, self.wallpapers[self.current_image])}")
        self.time = self.time_wait

    def quit(self):
        loop.quit()


bus = SessionBus()
bus.publish("net.nobody1902.pydbus.swimg", WallpaperService())
loop.run()
