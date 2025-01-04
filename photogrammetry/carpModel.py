#program for invasive carp model
#%matplotlib inline
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import pyplot as plt, animation
img = plt.imread(r"C:/Users/rosar/Downloads/carpRegion.png")

#yearList = [2016, 2017, 2018]

figure(figsize=(7, 12), dpi=150)
plt.text(-300, 150, 'year', fontsize=18, color='red')
# def updateYear(i):
#     yearLabel
#     yearLabel.set_text(yearList[i + 1])

imgplot = plt.imshow(img)
#anim = animation.FuncAnimation(updateYear, interval=200, frames=len(yearList))
plt.axis('off')
plt.show()