from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QLabel
import json
import os

class FormIdentitas(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Identitas Sekolah")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.npsn = QLineEdit()
        self.nama_sekolah = QLineEdit()
        self.alamat = QLineEdit()
        self.email = QLineEdit()
        self.website = QLineEdit()
        self.ks  = QLineEdit()
        self.nip_ks = QLineEdit()
        self.bendahara = QLineEdit()
        self.nip_bendahara = QLineEdit()

        data_awal = self.get_data()
        if data_awal:
            self.npsn.setText(data_awal.get("npsn", ""))
            self.nama_sekolah.setText(data_awal.get("nama_sekolah", ""))
            self.alamat.setText(data_awal.get("alamat", ""))
            self.email.setText(data_awal.get("email", ""))
            self.website.setText(data_awal.get("website", ""))
            self.ks.setText(data_awal.get("ks", ""))
            self.nip_ks.setText(data_awal.get("nip_ks", ""))
            self.bendahara.setText(data_awal.get("bendahara", ""))
            self.nip_bendahara.setText(data_awal.get("nip_bendahara", ""))

        form_layout.addRow("NPSN:", self.npsn)
        form_layout.addRow("Nama Sekolah:", self.nama_sekolah)
        form_layout.addRow("Alamat:", self.alamat)
        form_layout.addRow("Email:", self.email)
        form_layout.addRow("Website:", self.website)
        form_layout.addRow("Kepala Sekolah:", self.ks)
        form_layout.addRow("NIP Sekolah:", self.nip_ks)
        form_layout.addRow("Bendahara:", self.bendahara)
        form_layout.addRow("NIP Bendahara:", self.nip_bendahara)

        layout.addLayout(form_layout)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

    def accept(self):
        npsn = self.npsn.text().strip()
        nama_sekolah = self.nama_sekolah.text().strip()
        alamat = self.alamat.text().strip()
        email = self.email.text().strip()
        website = self.website.text().strip()
        ks = self.ks.text().strip()
        nip_ks = self.nip_ks.text().strip()
        bendahara = self.bendahara.text().strip()
        nip_bendahara = self.nip_bendahara.text().strip()

        data = {
            "npsn": npsn,
            "nama_sekolah": nama_sekolah,
            "alamat": alamat,
            "email": email,
            "website": website,
            "ks": ks,
            "nip_ks": nip_ks,
            "bendahara": bendahara,
            "nip_bendahara": nip_bendahara
        }
        
        os.makedirs("./data", exist_ok=True)
        with open("./data/identitas.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return super().accept()

    def get_data(path="./data/identitas.json"):
        try:
            with open("./data/identitas.json") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

class AlertIdentitas(QDialog):
    def __init__(self, parent = None, message=None):
        super().__init__(parent)
        self.setWindowTitle("Peringatan")
        self.setMinimumWidth(200)
        self.label = QLabel()
        self.label.setText(message)
        layout = QVBoxLayout()
        layout.addWidget(self.label)

