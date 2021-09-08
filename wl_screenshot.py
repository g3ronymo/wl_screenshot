#!/usr/bin/env python3
"""
Wrapper for 'grim' and 'slurp' to provide a simple utility to take screenshots
under wayland.

Dependencies:
    - grim
    - slurp
"""
import time
import subprocess
import argparse
from pathlib import Path
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def capture_full_screen(image_path):
    """Capture the full screen"""
    subprocess.run(["grim", str(image_path)])


def capture_screen_area(image_path):
    """Select and capture only an area of the screen"""
    area = subprocess.run(["slurp"], capture_output=True, text=True)
    area = str(area.stdout).strip()
    subprocess.run(["grim", "-g", area, str(image_path)])


# Gui to selecte mode and name
class MainWindow(Gtk.Window):
    """Choose what should be captured and select a name for the screenshot."""

    def __init__(self, screenshot_directory: Path):
        super().__init__(title="wl_screenshot")
        self.screenshot_directory = screenshot_directory

        self.connect("destroy", Gtk.main_quit)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.vbox)
        hbox = Gtk.Box(spacing=6)
        self.vbox.pack_start(hbox, False, False, 0)

        # select what should be captured
        self.radio_btn_area = Gtk.RadioButton.new_with_label_from_widget(
                None,
                "Area",
        )
        hbox.pack_start(self.radio_btn_area, False, False, 0)
        self.radio_btn_full_screen = Gtk.RadioButton.new_from_widget(
                self.radio_btn_area,
        )
        self.radio_btn_full_screen.set_label("Full Screen")
        hbox.pack_start(self.radio_btn_full_screen, False, False, 0)

        # select a name for the screenshot
        label = Gtk.Label(label="Screenshot Name:")
        self.vbox.pack_start(label, False, False, 0)
        self.screenshot_name = Gtk.Entry()
        default_name = str(int(time.time()))
        self.screenshot_name.set_text(default_name)
        self.vbox.pack_start(self.screenshot_name, False, False, 0)

        # cancel button
        self.btn_cancel = Gtk.Button(label="Cancel")
        self.btn_cancel.connect("clicked", self.on_cancel)
        self.vbox.pack_start(self.btn_cancel, False, False, 0)

        # ok button
        self.btn_ok = Gtk.Button(label="Ok")
        self.btn_ok.connect("clicked", self.on_ok)
        self.vbox.pack_start(self.btn_ok, False, False, 0)

    def on_cancel(self, widget):
        """Called when the Cancel button is clicked"""
        self.destroy()

    def on_ok(self, widget):
        """Called when the Ok button is clicked"""
        screenshot_name = self.screenshot_name.get_text().strip()
        if len(screenshot_name) <= 0:
            screenshot_name = str(int(time.time()))
        image_path = self.screenshot_directory.joinpath(
                screenshot_name + ".png"
        )
        if self.radio_btn_area.get_active():
            capture_screen_area(image_path)
        elif self.radio_btn_full_screen.get_active():
            capture_full_screen(image_path)
        self.destroy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Take screenshots under wayland."
    )
    parser.add_argument(
            "SCREENSHOT_DIRECTORY",
            help="directory where the screenshot should be saved",
    )
    args = parser.parse_args()
    screenshot_directory = Path(args.SCREENSHOT_DIRECTORY).resolve()
    if screenshot_directory.is_dir():
        win = MainWindow(screenshot_directory)
        win.show_all()
        Gtk.main()
    else:
        print("Not a valid directory:", args.SCREENSHOT_DIRECTORY)
