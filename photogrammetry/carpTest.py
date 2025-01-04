import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton

class TableWidgetDemo(QMainWindow):
   #self.table_widget=QTableWidget()
   def __init__(self):
      super().__init__()
      self.setWindowTitle("QTableWidget User Input Example")
      self.setGeometry(150, 150, 700, 400)

      self.table_widget = QTableWidget()
      self.table_widget.setRowCount(10)
      self.table_widget.setColumnCount(6)
      self.table_widget.setHorizontalHeaderLabels(["Year", "Region 1", "Region 2", "Region 3", "Region 4", "Region 5"])

      # Add a button to retrieve data
      self.button = QPushButton("Get Data")
      self.button.clicked.connect(self.convert_table_data_array)

      layout = QVBoxLayout()
      layout.addWidget(self.table_widget)
      layout.addWidget(self.button)

      container = QWidget()
      container.setLayout(layout)
      self.setCentralWidget(container)

   # def get_table_data(self):
   #    data = []
   #    for row in range(self.table_widget.rowCount()):
   #       for column in range(self.table_widget.columnCount()):
   #          item = self.table_widget.item(row, column)
   #          text = item.text() if item is not None else ""
   #          if item:
   #             #print(f"Row {row}, Column {column}: {item.text()}")
   #             data.append(text)
   #             print(data)
   #          else:
   #             print(f"Row {row}, Column {column}: Empty")
   # def get_column_values(self, column):
   #    column_val = []
   #    for row in range(self.table_widget.rowCount()):
   #       item = self.table_wdiget.item(row,column)
   #       if item is not None:
   #          column_val.append(item.text())
   #    return column_val

   def convert_table_data_array(self):
         def get_column_values(self, column):
            column_val = []
            for row in range(self.table_widget.rowCount()):
               item = self.table_widget.item(row,column)
               if item is not None:
                  column_val.append(item.text())
            return column_val
         column_data1 = get_column_values(self, 1)
         column_data2 = get_column_values(self, 2)
         column_data3 = get_column_values(self, 3)
         column_data4 = get_column_values(self, 4)
         column_data5 = get_column_values(self, 5)
         print("Region 1: ", column_data1,
               "Region 2: ", column_data2,
               "Region 3: ", column_data3,
               "Region 4: ", column_data4,
               "Region 5: ", column_data5)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TableWidgetDemo()
    window.show()
    sys.exit(app.exec_())