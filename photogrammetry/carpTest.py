import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from PIL import Image, ImageTk
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton

import cv2

class TableWidgetDemo(QMainWindow):
   #self.table_widget=QTableWidget()
   def __init__(self):
      super().__init__()
      self.setWindowTitle("Fish Modeling")
      self.setGeometry(150, 150, 700, 400)

      self.table_widget = QTableWidget()
      self.table_widget.setRowCount(10)
      self.table_widget.setColumnCount(6)
      self.table_widget.setHorizontalHeaderLabels(["Year", "Region 1", "Region 2", "Region 3", "Region 4", "Region 5"])

      # Add a button to retrieve data
      self.button = QPushButton("Get Data")
      self.button2 = QPushButton("Animate")
      self.button.clicked.connect(self.convert_table_data_array)
      self.button2.clicked.connect(self.animate)

      layout = QVBoxLayout()
      layout.addWidget(self.table_widget)
      layout.addWidget(self.button)
      layout.addWidget(self.button2)

      container = QWidget()
      container.setLayout(layout)
      self.setCentralWidget(container)

   def convert_table_data_array(self):
         global np_array
         def get_column_values(self, column):
            column_val = []
            for row in range(self.table_widget.rowCount()):
               item = self.table_widget.item(row,column)
               if item is not None:
                  column_val.append(item.text())
            return column_val
         self.column_data1 = get_column_values(self, 1)
         self.column_data2 = get_column_values(self, 2)
         self.column_data3 = get_column_values(self, 3)
         self.column_data4 = get_column_values(self, 4)
         self.column_data5 = get_column_values(self, 5)
         np_array = np.array([self.column_data1, self.column_data2, self.column_data3, self.column_data4, self.column_data5])
         #print(np_array)
         return np_array
         #return self.column_data1
      

   # def changeRegionColor(self):
   #    region1 = np_array[0]
   #    region2 = np_array[1]

   #    if 'y' in region1:
   #       print(np.where(region1 == 'y'))
      
   def update_year(self):
      global text
      #region1 = np_array[0]
      self.label.configure(text=self.years[self.text])
      self.text = (self.text + 1) % len(self.years)
      self.parent.after(1000, self.update_year)

      self.convert_table_data_array()
      self.print_data()

      # if 'y' in region1:
      #    print(np.argwhere(region1 == 'y'))
         
      #Update region carp presence



   def print_data(self):

      #33this works
      if self.text == 1:
         print("Its 2016")
      
      #Use Later
      #2016
      # if self.text == 1:
      #    if 'y' in np_array[0]:
      #       print(np.where(np_array[0] == 'y'))
      #    if 'y' in np_array[1]:
      #       print(np.where(np_array[1] == 'y'))
      #    if 'y' in np_array[2]:
      #       print(np.where(np_array[2] == 'y'))
      #    if 'y' in np_array[3]:
      #       print(np.where(np_array[3] == 'y'))
      #    if 'y' in np_array[4]:
      #       print(np.where(np_array[4] == 'y'))

      if self.text == 1:
         if np_array[0][0] == 'y':
            print("in 2016, there is carp in region 1")

         else:
            print("none")
            

   def animate(self):
      self.parent = tk.Tk()
      self.parent.title("Pls work")

      #open image
      #self.image = PhotoImage(file="C:/Users/rosar/Pictures/Screenshots/waterRegioncarp.png")
      map = Image.open("C:/Users/alyss/Downloads/waterRegioncarp.png")
      self.image_label = tk.Label(self.parent, image=self.image)

      #changing year
      self.years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
      self.text = 0
      self.label = tk.Label(self.parent, text=self.years[0])
      self.label.pack()
      self.update_year()
      #self.changeRegionColor()
      

      #image
      self.image_label.pack()
      self.parent.mainloop()
      

if __name__ == "__main__":
    main() 