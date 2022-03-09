
from PyQt5.QtWidgets import  *


#
# def display(self,msg):
#     row_count  = self.tableWidget.rowCount()
#     if row_count >= 100:
#         self.table.removeRow(0)
#     self.tableWidget.insertRow(row_count)
#
#     can_data = []
#     i = 0
#     while i < msg.DataLen:
#         can_data.append(hex(msg.Data[i]))
#         i = i+1
#     self.tableWidget.setItem(row_count, 2, QTableWidgetItem(str(hex(msg.ID))))
#     self.tableWidget.setItem(row_count, 3, QTableWidgetItem(str(can_data)))
