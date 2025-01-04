import pygetwindow as gw
import psutil
import os
import threading
import time
from tkinter import Tk, Label


main_process_name = 'Dolphin.exe'
dolphin_process = None

timeout = time.time() + 10   # Try for 10 seconds to find the dolphin process before exiting
while time.time() < timeout:
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == main_process_name:
            dolphin_process = proc
            break
    if dolphin_process is not None:
        break
    time.sleep(1)
if dolphin_process is None:
    print(main_process_name, " process not found. Exiting.")
    exit()


# Global variables for the popup
popup_root = None
popup_label = None

# Function to create and show the popup
def show_popup():
    global popup_root, popup_label
    if popup_root is None:
        popup_root = Tk()
        popup_root.attributes("-topmost", True, "-alpha", 0.8)
        popup_root.overrideredirect(True)

        screen_width = popup_root.winfo_screenwidth()
        screen_height = popup_root.winfo_screenheight()

        # Set size and position for the popup
        popup_width, popup_height = 500, 60
        x = (screen_width // 2) - (popup_width // 2)
        y = screen_height - popup_height - 50  # Bottom-center with some margin

        popup_root.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        popup_label = Label(
            popup_root, text="Push  D  on your keyboard to insert a new game", font=("Arial", 16), bg="black", fg="white"
        )
        popup_label.pack(fill="both", expand=True)
        popup_root.update()
    else:
        popup_root.attributes("-topmost", 0)
        popup_root.attributes("-topmost", 1)
        popup_root.update()

# Function to dismiss the popup
def dismiss_popup():
    global popup_root
    if popup_root:
        popup_root.destroy()
        popup_root = None

already_focused_window = False
# Function to check for window title
def monitor_window_title():
    global already_focused_window
    while True:
        for window in gw.getAllWindows():
            title = window.title
            if title and "wii menu" in title.lower():
                show_popup()
                if not already_focused_window:
                    already_focused_window = True
                    try:
                        window.activate()  # Focus the window
                    except Exception as e:
                        print(f"Failed to activate window: {e}")
                break
        else:
            dismiss_popup()
        time.sleep(0.5)

# Function to check if Dolphin is still running
def continue_as_long_as_dolphin_is_running():
    global dolphin_process
    while True:
        if dolphin_process and (dolphin_process.status() == psutil.STATUS_RUNNING):
            time.sleep(1)
            continue
        break
    print(main_process_name, " process not found. Exiting.")


# Run the window monitor and Wii Remote listener in separate threads
if __name__ == "__main__":
    threading.Thread(target=monitor_window_title, daemon=True).start()
    continue_as_long_as_dolphin_is_running()
