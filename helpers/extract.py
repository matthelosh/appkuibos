import camelot
import pandas as pd
import datetime
from collections import defaultdict

def pdfTable(pdf_path):
    tables = camelot.read_pdf(pdf_path, pages="all")

    if tables.n == 0:
        print("Tidak ada label")
        return False
    
    all_data = [tables[i].df for i in range(tables.n)]
    final_df = pd.concat(all_data, ignore_index=True)

    def format_tanggal(tanggal):
        try:
            return datetime.datetime.strptime(tanggal, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            return tanggal
        
    final_df.iloc[:,0] = final_df.iloc[:,0].apply(format_tanggal)

    header_row = final_df.iloc[[0]]
    data_rows = final_df.iloc[1:]

    data_rows = data_rows[data_rows[1].notna() & (data_rows[1].astype(str).str.len() >= 3)]
    data_rows = data_rows[~data_rows[4].astype(str).str.contains("PPh|PPn", na=False, case=False)]
    data_rows = data_rows[data_rows[5].astype(str).str.strip().isin(["0","0.00","0,00",""])]
    
    data_rows[6] = (data_rows[6].astype(str).str.replace(".","",regex=False))
    data_rows[2] = (data_rows[2].astype(str).str.replace("\n","",regex=False))
    # Hapus kolom 5 dan 7
    data_rows = data_rows.drop(columns=[5,7], errors='ignore')
    header_row = header_row.drop(columns=[5,7], errors='ignore')
    header_row = header_row.map(
        lambda x: str(x).strip().lower().replace(" ","_").replace(".","").replace("pengeluaran","nilai").replace("\n","_")
    )

    final_df = pd.concat([header_row, data_rows], ignore_index=True)
    datas = final_df.to_dict(orient='records')
    return header_row, data_rows

def groupBkuByBukti(bkus):
    grouped = defaultdict( lambda: {
        "tanggal": "",
        "kode_kegiatan": "",
        "kode_rekening": "",
        "no_bukti": "",
        "uraian": [],
        "nilai": 0
    })

    for bku in bkus:
        key = bku["no_bukti"]
        group = grouped[key]

        group["tanggal"] = bku["tanggal"]
        group["kode_kegiatan"] = bku["kode_kegiatan"]
        group["kode_rekening"] = bku["kode_rekening"]
        group["no_bukti"] = bku["no_bukti"]

        group["uraian"].append(bku["uraian"])
        try:
            group["nilai"] += int(str(bku["nilai"]).replace(".","").replace(",",""))
        except ValueError:
            group["nilai"] += 0

    hasil = []
    for item in grouped.values():
        item["uraian"] = "; ".join(item["uraian"])
        nilai_asli = item['nilai']
        nilai_format = "{:,.0f}".format(nilai_asli)
        item["nilai"] = nilai_format.replace(",",".")
        hasil.append(item)

    return hasil
