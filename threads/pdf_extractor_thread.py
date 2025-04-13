from PyQt5.QtCore import QThread, pyqtSignal
from helpers.extract import pdfTable, groupBkuByBukti

class PDFExtractorThread(QThread):
    selesai = pyqtSignal(list, list)
    gagal = pyqtSignal(str)

    def __init__(self, file_pdf):
        super().__init__()
        self.file_pdf = file_pdf

    def run(self):
        try:
            hasil = pdfTable(self.file_pdf)
            if not hasil:
                self.gagal.emit("Tidak ada Tabel di berkas")
            else:
                header_row, data_rows = hasil
                data_rows.columns = header_row.values.flatten().tolist()
                bkus = data_rows.to_dict(orient='records')
                bkus = groupBkuByBukti(bkus)
                self.selesai.emit(header_row.values.flatten().tolist(), bkus)
        except Exception as e:
            self.gagal.emit(str(e))