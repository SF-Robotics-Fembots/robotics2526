# #program for invasive carp model
# #%matplotlib inline
# from matplotlib.pyplot import figure
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
# from matplotlib import pyplot as plt, animation
# img = plt.imread(r"C:/Users/rosar/Downloads/carpRegion.png")

# #yearList = [2016, 2017, 2018]

# figure(figsize=(7, 12), dpi=150)
# plt.text(-300, 150, 'year', fontsize=18, color='red')
# # def updateYear(i):
# #     yearLabel
# #     yearLabel.set_text(yearList[i + 1])

# imgplot = plt.imshow(img)
# #anim = animation.FuncAnimation(updateYear, interval=200, frames=len(yearList))
# plt.axis('off')
# plt.show()
import tkinter as tk
import time

# def Draw():
#     global text
#     frame = tk.Frame(root,width=100,height=100,relief='solid',bd=1)
#     frame.place(x=10,y=10)
#     text=tk.Label(frame,text='HELLO')
#     text.pack()

def update_year():
    global text
    label.configure(text=years[text])
    text = (text + 1) % len(years)
    root.after(2000, update_year)
    
root = tk.Tk()
years = [2016, 2017, 2018]
text = 0
label = tk.Label(root, text=years[0])
label.pack()
update_year()
root.mainloop()