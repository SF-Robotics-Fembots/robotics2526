import tkinter as tk
import threading
import os
import camsgui
import screenshotprogram
import onecam
import sys

def allCam():
    print("display all cams")
    allCode = threading.Thread(target=camsgui.main, daemon=True)
    #os.system("camsgui.py")
    allCode.start()
    allCode.join()
    allCode.terminate()

'''def openPhotosphere():'
    print("display screenshotgui")
    screenshotCode = threading.Thread(target=screenshotprogram.main, daemon=True)
    #os.system("screenshot.py")
    screenshotCode.start()
    screenshotCode.join() '''

def oneCam():
    print("display one camera")
    oneCamCode = threading.Thread(target=onecam.main, daemon=True)
    oneCamCode.start()
    oneCamCode.join()

window = tk.Tk()
window.title("camera gui")

allButton = tk.Button(window, text = "All Cams", command=allCam)
allButton.pack()

oneButton = tk.Button(window, text="One Cam", command= oneCam)
oneButton.pack()

#ssButton = tk.Button(window, text = "Photosphere", command=openPhotosphere)
#ssButton.pack()

window.mainloop()