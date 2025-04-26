from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import os
import locale
import sys
import platform
import subprocess
import traceback
from datetime import datetime
from helpers.utils import resource_path, get_identitas
from jinja2 import Environment, FileSystemLoader

# WeasyPrint import with better error handling for Windows
WEASYPRINT_AVAILABLE = True
try:
    from weasyprint import HTML
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("WeasyPrint not available. PDF preview will be disabled.")

# pywebview import for cross-platform HTML preview
WEBVIEW_AVAILABLE = True
try:
    import webview
except ImportError:
    WEBVIEW_AVAILABLE = False
    print("Webview not available. Using fallback preview methods.")

import datetime

def cetakKuitansi(bku, file_name="kuitansi.pdf"):
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
    os.makedirs("./output", exist_ok=True)
    output_path = f"output/{file_name}"
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=1.8*cm, leftMargin=2*cm, topMargin=0.3*cm, bottomMargin=1.5*cm)

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
        
    # try:
    #     logo_sekolah_path = resource_path("./logo_sekolah.png")
    #     logo_sekolah = Image(logo_sekolah_path, width=2*cm, height=2*cm)

    # except Exception as e:
    #     print(f"Error loading logo_sekolah: {e}")
    #     # Use empty image as fallback
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
        [[logo_kab, kop_text]],
        colWidths=[2*cm, 13*cm]
    )

    kop_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 0, colors.white)
    ]))

    story.append(kop_table)

    # Garis HR
    story.append(HRFlowable(width="100%", thickness=1, color='black', spaceBefore=1, spaceAfter=1, hAlign='CENTER'))
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

def check_weasyprint_dependencies():
    """
    Check if WeasyPrint dependencies are properly installed.
    
    Returns:
        tuple: (bool, str) - (is_available, error_message)
    """
    # If WeasyPrint is not installed, return False
    if not WEASYPRINT_AVAILABLE:
        return False, "WeasyPrint is not installed. Please install it with: pip install weasyprint"
    
    # On Windows, check for GTK3
    if platform.system() == 'Windows':
        # Check if GTK3 is available by checking for a common DLL
        gtk_paths = [
            r'C:\Program Files\GTK3-Runtime\bin',
            r'C:\msys64\mingw64\bin',  # MSYS2 path
            r'C:\GTK\bin'
        ]
        
        gtk_found = False
        for path in gtk_paths:
            if os.path.exists(os.path.join(path, 'libgtk-3-0.dll')):
                gtk_found = True
                # Add to PATH if not already there
                if path not in os.environ['PATH']:
                    os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
                break
        
        if not gtk_found:
            return False, (
                "GTK3 is required for WeasyPrint on Windows but was not found. "
                "Using webview for preview instead. "
                "To enable PDF export, install GTK3 from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer"
            )
    
    return True, ""

def preview_with_webview(html_content, title="Kuitansi Preview"):
    """
    Preview HTML content using webview (cross-platform)
    
    Args:
        html_content (str): HTML content to display
        title (str): Window title
    
    Returns:
        bool: True if preview was successful, False otherwise
    """
    if not WEBVIEW_AVAILABLE:
        print("Webview is not available. Install with: pip install pywebview")
        return False
    
    try:
        # Create a temporary HTML file
        os.makedirs("./output", exist_ok=True)
        html_path = os.path.abspath("output/temp_preview.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create a webview window - this runs a local web server
        # The window will block until closed by user
        webview.create_window(title, html_path, width=800, height=800)
        webview.start()
        return True
    except Exception as e:
        print(f"Error previewing with webview: {e}")
        traceback.print_exc()
        return False

def previewKuitansi(bku):
    """
    Generate HTML and PDF previews for a kuitansi (receipt).
    
    Args:
        bku (dict): Dictionary containing receipt data with keys:
                   'tanggal', 'uraian', 'nilai', and optionally 'no_bukti'
    
    Returns:
        dict: Dictionary with paths to HTML and PDF previews or error message
    
    Windows Requirements:
        - WeasyPrint requires GTK3 to be installed on Windows
        - Download and install GTK3 from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
        - When bundling as exe, include appropriate GTK3 DLLs or ensure it's installed on target system
    """
    try:
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
        
        # Validate required fields
        required_fields = ['tanggal', 'uraian', 'nilai']
        for field in required_fields:
            if field not in bku:
                return {
                    "error": f"Data tidak lengkap: '{field}' tidak ditemukan"
                }
                    
        th, bln, tgl = map(int, bku['tanggal'].split("-"))
        tanggal = datetime.datetime(th, bln, tgl)
        tanggal_str = tanggal.strftime("%d %B %Y")
        tahun = str(th)
        
        # Get school identity
        sekolah = get_identitas()
        if not sekolah:
            return {
                "error": "Identitas sekolah belum diatur"
            }
        
        # Get absolute path to logo - handle bundled resources
        try:
            # Use resource_path to get correct path in both normal and bundled mode
            logo_path = resource_path("resources/logo_kab.png")
            
            # Check if file exists
            if not os.path.exists(logo_path):
                # Try alternative paths for bundled executable
                alt_paths = [
                    os.path.join(os.path.dirname(sys.executable), "resources", "logo_kab.png"),
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "logo_kab.png")
                ]
                
                for path in alt_paths:
                    if os.path.exists(path):
                        logo_path = path
                        break
            
            # Convert to data URI for embedding in HTML
            import base64
            with open(logo_path, "rb") as image_file:
                encoded_logo = base64.b64encode(image_file.read()).decode('utf-8')
            logo_data_uri = f"data:image/png;base64,{encoded_logo}"
        except Exception as e:
            print(f"Error loading logo: {e}")
            traceback.print_exc()
            logo_data_uri = ""
        
        # Prepare data for template
        data = {
            'title': 'Kuitansi',
            'data': {
                'kabupaten': 'MALANG',
                'kecamatan': 'WAGIR',
                'nama': sekolah.get('nama_sekolah'),
                'alamat': sekolah.get('alamat'),
                'desa': '',  # Fill if available in identitas
                'kode_pos': '',  # Fill if available in identitas
                'email': sekolah.get('email'),
                'website': sekolah.get('website'),
                'tanggal': tanggal_str,
                'tahun': tahun,
                'tahun': tahun,
                'no_bukti': bku.get('no_bukti', ''),
                'kode_kegiatan': '07.12.02.',
                'kode_rekening': '5.1.02.02.01.00.30',
                'uraian': bku['uraian'],
                'nilai': bku['nilai'],
                'terbilang': terbilang(bku['nilai']),
                'ks': sekolah.get('ks'),
                'nip_ks': sekolah.get('nip_ks'),
                'nip_bendahara': sekolah.get('nip_bendahara'),
                'penerima': '',  # To be filled by the receiver
                'logo_data_uri': logo_data_uri,  # Embedded logo data
            }
        }
        
        # Environment setup with custom filters
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('templates/kuitansi.html')
        
        # Modify template to include Bootstrap CSS inline
        bootstrap_css = """
        /* Bootstrap 5 minimal CSS for printing */
        .container {width: 100%; padding-right: 15px; padding-left: 15px; margin-right: auto; margin-left: auto;}
        .table {width: 100%; margin-bottom: 1rem; color: #212529; border-collapse: collapse;}
        .table-bordered {border: 1px solid #dee2e6;}
        .border-black {border-color: #000 !important;}
        .table-bordered td {border: 1px solid #dee2e6; padding: 0.75rem;}
        .mx-auto {margin-left: auto !important; margin-right: auto !important;}
        .p-4 {padding: 1.5rem !important;}
        .border {border: 1px solid #dee2e6 !important;}
        .border-dashed {border-style: dashed !important;}
        .bg-light {background-color: #f8f9fa !important;}
        .bg-gradient {background-image: linear-gradient(180deg, rgba(255,255,255,0.15), rgba(255,255,255,0));}
        .text-center {text-align: center !important;}
        .text-uppercase {text-transform: uppercase !important;}
        .text-decoration-underline {text-decoration: underline !important;}
        .w-80 {width: 80% !important;}
        .w-90 {width: 90% !important;}
        """
        
        # Create output directory if it doesn't exist
        os.makedirs("./output", exist_ok=True)
        
        # Render HTML with inlined CSS
        html_content = template.render(**data)
        
        # Replace external CSS with inlined CSS
        html_content = html_content.replace(
            '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.5/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-SgOJa3DmI69IUzQ2PVdRZhwQ+dy64/BUtbMJw1MZ8t5HZApcHrRKUc4W0kG879m7" crossorigin="anonymous">',
            f'<style>{bootstrap_css}</style>'
        )
        
        # Replace logo path with data URI
        html_content = html_content.replace(
            '<img src="../resources/logo_kab.png" alt="Logo Kab" style="width: 100px">',
            f'<img src="{logo_data_uri}" alt="Logo Kab" style="width: 100px">'
        )
        
        # Remove external JavaScript
        html_content = html_content.replace(
            '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.5/dist/js/bootstrap.bundle.min.js" integrity="sha384-k6d4wzSIapyDyv1kpU366/PK5hCdSbCRGRCMv+eplOQJWyd1fbcAu9OCUj5zNLiq" crossorigin="anonymous"></script>',
            ''
        )
        
        # Save to temporary HTML file for preview
        html_preview_path = f"output/kuitansi_preview.html"
        with open(html_preview_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Initialize result dictionary
        result = {
            "html_path": html_preview_path,
            "html_content": html_content
        }
        
        # Generate PDF preview using WeasyPrint if available
        pdf_preview_path = f"output/kuitansi_preview.pdf"
        
        # Check WeasyPrint dependencies
        weasyprint_available, error_message = check_weasyprint_dependencies()
        
        if weasyprint_available:
            try:
                HTML(string=html_content).write_pdf(pdf_preview_path)
                result["pdf_path"] = pdf_preview_path
            except Exception as e:
                print(f"Error generating PDF: {e}")
                traceback.print_exc()
                result["pdf_error"] = f"Gagal membuat PDF: {str(e)}"
        else:
            print(f"WeasyPrint dependencies missing: {error_message}")
            result["pdf_error"] = error_message
            
        # Add pywebview preview capability
        result["webview_available"] = WEBVIEW_AVAILABLE
        # Return result with available paths
        return result
    except Exception as e:
        import traceback
        print(f"Error in previewKuitansi: {e}")
        traceback.print_exc()
        return {
            "error": f"Terjadi kesalahan: {str(e)}"
        }
def preview_kuitansi_in_webview(bku):
    """
    Generate and display a kuitansi preview directly in a webview window
    
    Args:
        bku (dict): Dictionary containing receipt data
    
    Returns:
        bool: True if preview was successful, False otherwise
    """
    try:
        result = previewKuitansi(bku)
        
        if 'error' in result:
            print(f"Error in preview: {result['error']}")
            return False
            
        # Show preview in webview
        if WEBVIEW_AVAILABLE:
            return preview_with_webview(result['html_content'], f"Kuitansi - {bku.get('no_bukti', '')}")
        else:
            # Fallback to opening in browser
            return open_file(result['html_path'])
    
    except Exception as e:
        print(f"Error in preview_kuitansi_in_webview: {e}")
        traceback.print_exc()
        return False

def test_preview(use_webview=True):
    """Test function to generate a preview with sample data"""
    sample_data = {
        'tanggal': '2025-04-23',
        'uraian': 'Pembayaran ATK untuk Kantor',
        'nilai': '1250000',
        'no_bukti': 'BKK-001/IV/2025'
    }
    
    if use_webview and WEBVIEW_AVAILABLE:
        print("Opening preview in webview window...")
        return preview_kuitansi_in_webview(sample_data)
    
    # Traditional file-based preview
    result = previewKuitansi(sample_data)
    
    if 'error' in result:
        print(f"Error in preview: {result['error']}")
        return False
    
    print(f"Preview files generated successfully:")
    print(f"HTML: {result['html_path']}")
    if 'pdf_path' in result:
        print(f"PDF: {result['pdf_path']}")
    elif 'pdf_error' in result:
        print(f"PDF generation error: {result['pdf_error']}")
    # Try to open the files automatically
    try:
        # Open HTML preview
        html_opened = open_file(result['html_path'])
        
        # Open PDF preview if available
        pdf_opened = False
        if 'pdf_path' in result:
            pdf_opened = open_file(result['pdf_path'])
        elif 'pdf_error' in result:
            print(f"PDF preview not available: {result['pdf_error']}")
        
        return html_opened or pdf_opened
    except Exception as e:
        print(f"Error opening preview files: {e}")
        traceback.print_exc()
        return False
    
    return True
def open_file(file_path):
    """
    Open a file with the default system application
    
    Args:
        file_path (str): Path to the file to open
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
            
    system = platform.system()
    try:
        if system == 'Darwin':  # macOS
            subprocess.call(['open', file_path])
        elif system == 'Windows':
            # Use os.startfile which is more reliable for Windows
            try:
                os.startfile(file_path)
            except AttributeError:
                # Fallback if os.startfile is not available
                subprocess.call(['start', file_path], shell=True)
        elif system == 'Linux':
            subprocess.call(['xdg-open', file_path])
        else:
            print(f"Unsupported platform: {system}")
            return False
        return True
    except Exception as e:
        print(f"Error opening file {file_path}: {e}")
        return False

def get_exe_info():
    """
    Get information about the executable environment - useful for troubleshooting
    bundled applications on Windows.
    
    Returns:
        dict: Information about the execution environment
    """
    info = {
        "platform": platform.system(),
        "executable": sys.executable,
        "cwd": os.getcwd(),
        "script_dir": os.path.dirname(os.path.abspath(__file__)),
    }
    
    # Add frozen state (PyInstaller, cx_Freeze)
    if getattr(sys, 'frozen', False):
        info["frozen"] = True
        if hasattr(sys, '_MEIPASS'):  # PyInstaller
            info["bundle_dir"] = sys._MEIPASS
    else:
        info["frozen"] = False
    
    return info

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