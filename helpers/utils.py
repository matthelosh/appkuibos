import sys
import os
import json
import sqlite3


db = sqlite3.connect("./data/db.sqlite")
cursor = db.cursor()

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_identitas(file_path="./data/identitas.json"):
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def updateBku(data):
    try:
        sql = """
            UPDATE bkus SET
                tanggal=?,
                kode_kegiatan=?, 
                kode_rekening=?, 
                uraian=?, 
                nilai=?, 
                penerima=?
            WHERE no_bukti=?
        """
        values = (
            data['tanggal'],
            data['kode_kegiatan'],
            data['kode_rekening'],
            data['uraian'],
            data['nilai'],
            data['penerima'],
            data['no_bukti']
        )
        cursor.execute(sql, values )
        db.commit()
        db.close()

        return True, f"BKU dengan No Bukti: {data['no_bukti']} diperbarui."
    except Exception as e:
        return False, f"Error: {e}"

def save2DB(data):
    try: 
        # db = sqlite3.connect("./data/db.sqlite")
        # cursor = db.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bkus( 
        id Int auto_increment PRIMARY KEY, 
        tanggal Date, 
        kode_kegiatan VARCHAR(30), 
        kode_rekening VARCHAR(30), 
        no_bukti VARCHAR(10), 
        uraian TEXT, 
        nilai VARCHAR(20), 
        penerima VARCHAR(100) 
        )
        """
                       )
        for t in data:
            cursor.execute("""
            INSERT INTO bkus(tanggal, kode_kegiatan, kode_rekening, no_bukti, uraian, nilai, penerima) VALUES(?,?,?,?,?,?,?)
            """,
            (
                t['tanggal'], 
                t['kode_kegiatan'], 
                t['kode_rekening'], 
                t['no_bukti'], 
                t['uraian'], 
                t['nilai'], 
                t['penerima']
            ))

        db.commit()
        cursor.close()
        db.close()

        return True, "Data Transaksi disimpan"
    except Exception as e:
        return False, f"Error: {e}"
