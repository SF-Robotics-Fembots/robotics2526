import tkinter as tk
import threading
import camsgui
import onecam
import time

is_all_cams_running = False
is_one_cam_running = False

def allCam():
    global is_all_cams_running
    if not is_all_cams_running:
        is_all_cams_running = True
        print("Starting all cams")
        threading.Thread(target=runAllCams, daemon=True).start()

def runAllCams():
    try:
        print("Running camsgui.main() in a thread")
        camsgui.main()
    except Exception as e:
        print(f"Error in allCam thread: {e}")
    finally:
        global is_all_cams_running
        is_all_cams_running = False

def oneCam():
    global is_one_cam_running
    if not is_one_cam_running:
        is_one_cam_running = True
        print("Starting one cam")
        threading.Thread(target=runOneCam, daemon=True).start()

def runOneCam():
    try:
        print("Running onecam.main() in a thread")
        onecam.main()
    except Exception as e:
        print(f"Error in oneCam thread: {e}")
    finally:
        global is_one_cam_running
        is_one_cam_running = False

def stop_all_cams():
    global is_all_cams_running
    if is_all_cams_running:
        print("Stopping all cams")
        is_all_cams_running = False
  
def stop_one_cam():
    global is_one_cam_running
    if is_one_cam_running:
        print("Stopping one cam")
        is_one_cam_running = False

window = tk.Tk()
window.title("Camera GUI")

# buttons
allButton = tk.Button(window, text="All Cams", command=allCam)
allButton.pack()

oneButton = tk.Button(window, text="One Cam", command=oneCam)
oneButton.pack()

stopButton = tk.Button(window, text="Stop All Cams", command=stop_all_cams)
stopButton.pack()

stopOneButton = tk.Button(window, text="Stop One Cam", command=stop_one_cam)
stopOneButton.pack()

#runs window in a loop
window.mainloop()
