import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog, QMessageBox
from PyQt5.QtGui import QIcon, QPainter, QPixmap
import os
import platform
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from pdf2image import convert_from_path

from helpers.utils import resource_path, save2DB
from helpers.extract import pdfTable, groupBkuByBukti
from helpers.cetak import cetakKuitansi

from threads.pdf_extractor_thread import PDFExtractorThread
from parts.dialogs import FormIdentitas, FormKuitansi

if platform.system() == "Windows":
    gs_path = os.path.abspath("lib/ghostscript/bin")
    poppler_path = os.path.abspath("lib/poppler/Library/bin")
    os.environ["PATH"] += os.pathsep + gs_path
    os.environ["PATH"] += os.pathsep + poppler_path

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        ui_path = resource_path("appkuibos_responsive_fixed.ui")
        loadUi(ui_path, self)
        icon_path = resource_path("resources/ledger.png")
        self.setWindowIcon(QIcon(icon_path))
        self.btn_from_bku.clicked.connect(self.pickFile)
        self.btn_from_db.clicked.connect(self.fromDB)
        self.progress_bar.hide()
        self.label_loading.hide()
        #Cek idetitas sekolah
        # self.checkIdSekolah()
        # Dialog Identitas
        self.btn_setting.clicked.connect(self.show_dialog_id)
        #Cetak Baris terpilih
        self.btn_print_selected.clicked.connect(self.printSelectedBku)
        self.btn_simpan_db.clicked.connect(self.save2Db)

        # Tes
        self.startExtraction('./contoh/bku.pdf')

        # Transaksi
        self.transaksis = []

    def finishExtraction(self, header, bkus):
        self.progress_bar.hide()
        self.label_loading.setText("Selsai")

        self.table_bku.setRowCount(len(bkus))
        self.table_bku.setColumnCount(8)
        self.table_bku.setHorizontalHeaderLabels([
            "#", "Tanggal", "Kode Kegiatan", "Kode Rekening", "No. Bukti", "Uraian", "Nominal", "Opsi"
        ])
        self.transaksis = []
        for row, bku in enumerate(bkus):
            values = [
                str(row + 1),
                bku["tanggal"],
                bku["kode_kegiatan"],
                bku["kode_rekening"],
                bku["no_bukti"],
                bku["uraian"],
                bku["nilai"],
                "penerima"
            ]
            
            self.transaksis.append({
                "tanggal": bku["tanggal"],
                "kode_kegiatan": bku["kode_kegiatan"],
                "kode_rekening": bku["kode_rekening"],
                "no_bukti": bku["no_bukti"],
                "uraian": bku["uraian"],
                "nilai": bku["nilai"],
                "penerima": '' 
            })

            for col, val in enumerate(values):
                if col == 4:
                    item = QtWidgets.QTableWidgetItem(str(val))
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemFlag.ItemIsEditable)
                    self.table_bku.setItem(row, col, item)
                elif col == 7:
                    btn_edit = QtWidgets.QPushButton("Edit")
                    btn_edit.clicked.connect(lambda _, data=values: self.editKuitansi(data))

                    cell_widget = QtWidgets.QWidget()
                    layout = QtWidgets.QHBoxLayout(cell_widget)
                    layout.addWidget(btn_edit)
                    layout.setAlignment(btn_edit, QtCore.Qt.AlignCenter)
                    layout.setContentsMargins(5,2,5,2)

                    self.table_bku.setCellWidget(row, col, cell_widget)
                else:
                    label = QtWidgets.QLabel(str(val))
                    if col == 0:
                        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    else:
                        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    label.setWordWrap(True)
                    label.setStyleSheet("padding: 6px;")
                    self.table_bku.setCellWidget(row, col, label)
        
        self.table_bku.setSelectionBehavior(QtWidgets.QTableWidget.SelectionBehavior.SelectRows)
        self.table_bku.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)

        
        header = self.table_bku.horizontalHeader()
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)

        self.table_bku.setWordWrap(True)
        self.table_bku.resizeColumnsToContents()
        self.table_bku.resizeRowsToContents()
        self.table_bku.verticalHeader().setVisible(False)

        QtCore.QTimer.singleShot(2000, lambda: self.label_loading.hide())

    def editKuitansi(self, data):
        form_kuitansi = FormKuitansi(self, data)
        form_kuitansi.exec_()

    def gagalExtraction(self, pesan):
        self.progress_bar.hide()
        self.label_loading.setText("Gagal")
        QtWidgets.QMessageBox.warning(self, "Gagal", pesan)
        QtCore.QTimer.singleShot(2000, lambda: self.label_loading.hide())

    def printSelectedBku(self):
        
        bku_row = self.table_bku.currentRow()
        if bku_row >= 0:
            data = {
                "tanggal": self.table_bku.cellWidget(bku_row, 1).text(),
                "kode_kegiatan": self.table_bku.cellWidget(bku_row, 2).text(),
                "kode_rekening": self.table_bku.cellWidget(bku_row, 3).text(),
                "no_bukti": self.table_bku.item(bku_row, 4).text(),
                "uraian": self.table_bku.cellWidget(bku_row, 5).text(),
                "nilai": self.table_bku.cellWidget(bku_row, 6).text()
            }
            # options = QFileDialog.Options()
            # file_name, _ = QFileDialog.getSaveFileName(self, "Simpan Kuitansi", f"Kuitansi_{data['no_bukti']}.pdf", "PDF Files (*.pdf)", options=options)
            file_name=f"Kuitansi_{data['no_bukti']}.pdf"
            base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
            output_path = os.path.join(base_dir, "output", file_name)
            base_path =getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            poppler_path = os.path.join(base_path, "lib","poppler", "Library", "bin")
            if file_name:
                try:
                    cetakKuitansi(data, file_name=file_name)
                    QtWidgets.QMessageBox.information(self, "Berhasil", f"Kuitansi berhasil disimpan: {file_name}. Cetak!")
                    images = convert_from_path(output_path, dpi=300, poppler_path=poppler_path)
                    img_path= "tmp_cetak.png"
                    images[0].save(img_path, "PNG")

                    printer = QPrinter()
                    preview = QPrintPreviewDialog(printer, self)
                    preview.paintRequested.connect(lambda p: self.cetakBku(p, img_path))
                    preview.exec_()

                    
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat menyimpan kuitansi: {str(e)}")
            else:
                QtWidgets.QMessageBox.warning(self, "Batal", "Penyimpanan kuitansi gagal")
        else:
            QtWidgets.QMessageBox.warning(self, "Peringatan", "Silahkan pilih BKU dulu.")

    def cetakBku(self, printer, img_path):
        painter = QPainter(printer)
        pixmap = QPixmap(img_path)

        rect = painter.viewport()
        size = pixmap.size()
        size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)

        painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
        painter.setWindow(pixmap.rect())
        painter.drawPixmap(0,0, pixmap)

        painter.end()

    def pickFile(self):
        if self.checkIdSekolah():
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Pilih File BKU:", "", "PDF Files (*.pdf)")
            if file_path:
                self.startExtraction(file_path)

    def startExtraction(self, file_path):
        self.progress_bar.setRange(0,0)
        self.progress_bar.show()
        self.label_loading.setText("Loading...")
        self.label_loading.show()

        self.thread = PDFExtractorThread(file_path)
        self.thread.selesai.connect(self.finishExtraction)
        self.thread.gagal.connect(self.gagalExtraction)
        self.thread.start()

    def save2Db(self):
        success, message = save2DB(self.transaksis)
        if success:
            QMessageBox.information(self, "Info", message)
        else:
            QMessageBox.warning(self, "Error", message)
    def fromDB(self):
        dialog = QDialog(self, )
        dialog.setWindowTitle("Info")
        dialog.setGeometry(700, 400, 200, 100)

        layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Maaf.. Masih dikembangkan, mohon doanya..")
        layout.addWidget(message)
        dialog.setLayout(layout)
        dialog.exec()

    # Cek Data identitas
    def checkIdSekolah(self):
        dialog_identitas = FormIdentitas(self)
        data = dialog_identitas.get_data()
        if not data:
            QtWidgets.QMessageBox.warning(self, "Peringatan", "Isi dulu identitas sekolah!")
            self.show_dialog_id()
        else:
            return True

    def show_dialog_id(self):
        dialog_identitas = FormIdentitas(self)
        if dialog_identitas.exec_():
            
            QtWidgets.QMessageBox.information(self, "Berhasil", "Identitas Sekolah disimpan")


#Main
app = QApplication(sys.argv)
win = MainWindow()
print("Loading..")
win.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")
