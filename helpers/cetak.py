from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import os
import locale
import sys
from datetime import datetime
from helpers.utils import resource_path, get_identitas

def cetakKuitansi(bku, output_path="kuitansi.pdf"):
    # Format tanggal
    try:
        locale.setlocale(locale.LC_TIME, 'id_ID.utf8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'ind')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'id_ID')
            except locale.Error:
                print("Locale Indonesia tidak tersedia di sistem")
                # Continue with default locale
            
    th, bln, tgl = map(int, bku['tanggal'].split("-"))
    tanggal = datetime(th, bln, tgl)
    tanggal_str = tanggal.strftime("%d %B %Y")

    # Output file
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BoldCenter', parent=styles['Heading2'], alignment=1, fontSize=14))
    styles.add(ParagraphStyle(name="KopTitle", parent=styles['Normal'], alignment=1, fontSize=14 ))
    styles.add(ParagraphStyle(name="KopAlamat", parent=styles['Normal'], alignment=1, fontSize=10 ))
    styles.add(ParagraphStyle(name="KopStyle", parent=styles['Normal'], fontSize=14, alignment=1, spaceAfter=0, leading=14))
    story = []

    # Header Sekolah
    sekolah = get_identitas()
    if not sekolah:
        return {
            "nama_sekolah" : "Atur Identitas dulu",
            "alamat" : "Atur Identitas dulu",
            "email" : "Atur Identitas dulu",
            "website" : "Atur Identitas dulu",
            "ks" : "Atur Identitas dulu",
            "nip_ks" : "Atur Identitas dulu",
            "bendahara" : "Atur Identitas dulu",
            "nip_bendahara" : "Atur Identitas dulu",
        }

    #Logo
    try:
        logo_kab_path = resource_path("resources/logo_kab.png")
        logo_kab = Image(logo_kab_path, width=2*cm, height=2.5*cm)
    except Exception as e:
        print(f"Error loading logo_kab: {e}")
        # Use empty image as fallback
        logo_kab = Spacer(2*cm, 2.5*cm)
        
    try:
        logo_sekolah_path = resource_path("resources/logo_sekolah.png")
        logo_sekolah = Image(logo_sekolah_path, width=2*cm, height=2*cm)
    except Exception as e:
        print(f"Error loading logo_sekolah: {e}")
        # Use empty image as fallback
        logo_sekolah = Spacer(2*cm, 2*cm)

    #Teks Kop
    kop_text = Paragraph(
        f"<b><font size=13>PEMERINTAH KABUPATEN MALANG</font></b><br/>"
        f"<b><font size=12>DINAS PENDIDIKAN</font></b><br/>"
        f"<b><font size=11>KORWIL KECAMATAN WAGIR</font></b><br/>"
        f"<b><font size=13>{sekolah.get('nama_sekolah')}</font></b><br/>"
        f"<font size=10>{sekolah.get('alamat')}</font><br/>"
        f"<font size=10>Email: {sekolah.get('email')}, Website: {sekolah.get('website')}</font><br/>",
        styles['KopStyle']
    )

    kop_table = Table(
        [[logo_kab, kop_text, logo_sekolah]],
        colWidths=[2*cm, 11*cm, 3*cm]
    )

    kop_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 0, colors.white)
    ]))

    story.append(kop_table)

    # Garis HR
    story.append(HRFlowable(width="100%", thickness=2, color='black', spaceBefore=1, spaceAfter=1, hAlign='CENTER'))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<b>KUITANSI</b>", styles['BoldCenter']))
    story.append(Spacer(1, 0.2*cm))

    # Kode Rekening dan Kegiatan
    story.append(Paragraph("Kode Rekening: 5.1.02.02.01.00.30 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Kode Kegiatan: 07.12.02.", styles['KopAlamat']))
    story.append(Spacer(1, 0.3*cm))

    # Tabel Isi
    data = [
        ["Sudah diterima dari", ":", "Bendahara BOS Reguler SD Negeri 1 Bedalisodo"],
        ["Uang Sebesar", ":", Paragraph(f"<i>{terbilang(bku['nilai'])}</i>")],
        ["Untuk Keperluan", ":", Paragraph(f"{bku['uraian']}")],
        ["Terbilang", ":", ""],
    ]
    table = Table(data, colWidths=[4.5*cm, 0.5*cm, 10*cm])
    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONT', (0,0), (-1,1), 'Helvetica'),
    ]))
    story.append(table)

    nilai = [[Paragraph(f"<b><font size=14>Rp. {bku['nilai']},-</font></b>".replace(",", "."), styles['Title'])]]
    box_nilai = Table(nilai, colWidths=[200])
    box_nilai.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1,colors.black),
        ('ALIGN', (0,0), (-1,-1) ,'CENTER'),
        ('VALIGN', (0,0), (-1,-1) ,'MIDDLE'),
        ('PADDING', (0,0), (-1,-1) , 6),
    ]))
    story.append(box_nilai)
    story.append(Spacer(1, 1*cm))

    
    # TTD Table
    ttd_table = Table([
        [
            Paragraph("Menyetujui,<br/>Kepala Sekolah"), 
            Paragraph("<br/>Bendahara<br/><br/><br/>"),
            Paragraph(f"Malang, {tanggal_str}<br/>Yang Menerima",)
        ],
        [
            Paragraph(f"<br/><br/><br/><b>{sekolah.get('ks')}</b><br/>NIP. {sekolah.get('nip_ks')}"), 
            Paragraph(f"<b>{sekolah.get('bendahara')}</b><br/>NIP. {sekolah.get('nip_bendahara')}"), 
            Paragraph(f"<br/><br/><b>....................................</b>")],
    ], colWidths=[6*cm, 6*cm, 5*cm])

    ttd_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('SPAN', (1,2), (1,2)),
        ('SPAN', (1,3), (1,3)),
    ]))
    story.append(ttd_table)
    story.append(Spacer(1, 1*cm))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="30%", thickness=1, color='black', spaceBefore=1, spaceAfter=1, hAlign='LEFT'))
    story.append(Paragraph("<b><i>Bukti / Berkas Terlampir *)</i></b>", styles['Normal']))


    # Build dokumen
    doc.build(story)
    output_path

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