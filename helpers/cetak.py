from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import os
from datetime import datetime

def cetakKuitansi(bku, output_path="kuitansi.pdf"):
    # Format tanggal
    tanggal_obj = datetime.strptime(bku["tanggal"], "%Y-%m-%d")
    tanggal_str = tanggal_obj.strftime("%d %B %Y")

    # Output file
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BoldCenter', parent=styles['Heading2'], alignment=1, fontSize=14))

    story = []

    # Header Sekolah
    story.append(Paragraph("<b>PEMERINTAH KABUPATEN MALANG</b>", styles['Normal']))
    story.append(Paragraph("DINAS PENDIDIKAN", styles['Normal']))
    story.append(Paragraph("KOORDINATOR WILAYAH KECAMATAN WAGIR<br/><b>SD NEGERI 1 BEDALISODO</b>", styles['Normal']))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>KUITANSI</b>", styles['BoldCenter']))
    story.append(Spacer(1, 0.2*cm))

    # Kode Rekening dan Kegiatan
    story.append(Paragraph("Kode Rekening: 5.1.02.02.01.00.30 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Kode Kegiatan: 07.12.02.", styles['Normal']))
    story.append(Spacer(1, 0.3*cm))

    # Tabel Isi
    data = [
        ["Sudah diterima dari", ":", "Bendahara BOS Reguler SD Negeri 1 Bedalisodo"],
        ["Uang Sebesar", ":", Paragraph(f"<i>{terbilang(bku['nilai'])}</i>")],
        ["Untuk Keperluan", ":", bku["uraian"]],
    ]
    table = Table(data, colWidths=[4.5*cm, 0.5*cm, 10*cm])
    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONT', (0,0), (-1,1), 'Helvetica'),
    ]))
    story.append(table)

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("<b>Bukti / Berkas Terlampir</b>", styles['Normal']))
    story.append(Spacer(1, 0.2*cm))

    # Terbilang dan nilai nominal
    story.append(Paragraph("Terbilang", styles['Normal']))
    story.append(Spacer(1, 0.2*cm))
    # nilai_formatted = f"{int(bku['nilai']):,}".replace(",",".")
    story.append(Paragraph(f"<b><font size=14>Rp. {bku['nilai']},-</font></b>".replace(",", "."), styles['BoldCenter']))
    story.append(Spacer(1, 1*cm))

    # TTD Table
    ttd_table = Table([
        [Paragraph("Menyetujui,<br/>Kepala Sekolah"), "", Paragraph(f"Malang, {tanggal_str}<br/>Yang Menerima",)],
        [Paragraph("<br/><br/><br/><b>NURUL HUDA</b><br/>NIP. 196802261993011004"), "", Paragraph(f"<br/><br/><br/><b>......................</b>")],
        ["", "Bendahara", ""],
        ["", Paragraph("<b>RIRIN TIA VRIONICA</b><br/>NIP. 198502202022122002"), ""],
    ], colWidths=[6*cm, 6*cm, 5*cm])

    ttd_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('SPAN', (1,2), (1,2)),
        ('SPAN', (1,3), (1,3)),
    ]))
    story.append(ttd_table)

    # Build dokumen
    doc.build(story)
    output_path



    # c = canvas.Canvas(output_path, pagesize=A4)
    # width, height = A4

    # c.setFont("Helvetica-Bold", 14)
    # c.drawCentredString(width / 2, height - 2 * cm, "KUITANSI")

    # c.setFont("Helvetica", 11)

    # # Isi Data
    # c.drawString(2 * cm, height - 3.5 * cm, f"No. Bukti         : {data['no_bukti']}")
    # c.drawString(2 * cm, height - 4.5 * cm, f"Tanggal           : {data['tanggal']}")
    # c.drawString(2 * cm, height - 5.5 * cm, f"Kode Kegiatan     : {data['kode_kegiatan']}")
    # c.drawString(2 * cm, height - 6.5 * cm, f"Kode Rekening     : {data['kode_rekening']}")
    # c.drawString(2 * cm, height - 7.5 * cm, f"Untuk Keperluan   : ")

    # #Uraian
    # uraian = data['uraian']
    # text = c.beginText(3 * cm, height - 8.5 * cm)
    # text.setFont("Helvetica-Oblique", 11)
    # for line in uraian.split("\n"):
    #     text.textLine(line)
    
    # c.drawText(text)

    # #Jumlah Uang
    # c.setFont("Helvetica-Bold", 12)
    # c.drawString(2 * cm, height - 12 * cm, f"Jumlah             : Rp. {data['nilai']}")
    
    # #Terbilang
    # c.setFont("Helvetica-Bold", 10)
    # c.drawString(2 * cm, height - 13 * cm, f"Terbilang             :  { terbilang(data['nilai']) }")

    # #Tanda tangan
    # c.setFont("Helvetica", 11)
    # c.drawRightString(width - 2 * cm, 4 * cm, "Bendahara")

    # c.save()

def terbilang(nilai):
    angka = ["", "Satu", "Dua", "Tiga", "Empat", "Lima", "Enam", "Tujuh", "Delapan", "Sembilan", "Sepuluh", "Sebelas"]
    nilai = nilai.replace(".","").replace(",","")
    nilai = int(nilai)
    def convert(x):
        if x < 12:
            return angka[x]
        elif x < 20:
            return convert(x - 10) + " Belas"
        elif x < 100:
            return convert(x // 10) + " Puluh" + (" " + convert(x % 10) if x % 10 != 0 else "")
        elif x < 200:
            return "Seratus" + (" " + convert(x - 100) if x > 100 else "")
        elif x < 1000:
            return convert(x // 100) + " Ratus" + (" " + convert(x % 100) if x % 100 != 0 else "")
        elif x < 2000:
            return "Seribu" + (" " + convert(x - 1000) if x > 1000 else "")
        elif x < 1_000_000:
            return convert(x // 1000) + " Ribu" + (" " + convert(x % 1000) if x % 1000 != 0 else "")
        elif x < 1_000_000_000:
            return convert(x // 1_000_000) + " Juta" + (" " + convert(x % 1_000_000) if x % 1_000_000 != 0 else "")
        else:
            return "Angka terlalu Besar"
        
    return convert(int(nilai)).strip() + " Rupiah"