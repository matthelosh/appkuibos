import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
import os
import platform

from helpers.extract import pdfTable, groupBkuByBukti
from helpers.cetak import cetakKuitansi

if platform.system() == "Windows":
    gs_path = os.path.abspath("lib/ghostscript/bin")
    os.environ["PATH"] += os.pathsep + gs_path

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("appkuibos.ui", self)
        self.loadData()

    def loadData(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Pilih File BKU:", "", "PDF Files (*.pdf)")
        kolom, data = pdfTable(file_path)
        data.columns = kolom.values.flatten().tolist()
        bkus = data.to_dict(orient='records')
        bkus = groupBkuByBukti(bkus)
        # row=0
        self.tableWidget.setRowCount(len(bkus))
        self.tableWidget.setColumnCount(7)

        for row, bku in enumerate(bkus):
            values = [
                bku["tanggal"],
                bku["kode_kegiatan"],
                bku["kode_rekening"],
                bku["no_bukti"],
                bku["uraian"],
                bku["nilai"]
            ]

            for col, val in enumerate(values):
                label = QtWidgets.QLabel(str(val))
                label.setWordWrap(True)
                label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
                label.setStyleSheet("padding: 6px;")
                self.tableWidget.setCellWidget(row, col, label)

                btnCetak = QtWidgets.QPushButton("Cetak")
                btnCetak.clicked.connect(lambda checked, bku_row=bku: self.cetakPerbaris(bku_row))
                self.tableWidget.setCellWidget(row, 6 , btnCetak)
        
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def cetakPerbaris(self, bku_row):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Simpan Kuitansi", f"Kuitansi_{bku_row['no_bukti']}.pdf", "PDF Files (*.pdf)", options=options)

        if file_name:
            cetakKuitansi(bku_row, output_path=file_name)
            QtWidgets.QMessageBox.information(self, "Berhasil", f"Kuitansi berhasil disimpan: {file_name}")
        else:
            QtWidgets.QMessageBox.warning(self, "Batal", "Penyimpanan kuitansi gagal")


#Main
app = QApplication(sys.argv)
win = MainWindow()
print("Loading..")
win.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
