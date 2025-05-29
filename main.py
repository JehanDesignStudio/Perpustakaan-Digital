from flask import Flask, render_template, request, redirect, url_for, session, flash, current_app # berfungsi untuk membuat aplikasi web yang terdiri dari beberapa route yaitu
# Flask yang digunakan untuk menangani request dan response HTTP, 
# render_template untuk merender template HTML, 
# request untuk mengambil data dari request, 
# redirect untuk mengarahkan ke route lain, 
# url_for untuk membuat URL berdasarkan nama fungsi, 
# session untuk menyimpan data session,
# flash untuk menampilkan pesan sementara
from flask_mysqldb import MySQL # berfungsi untuk menghubungkan aplikasi web dengan database MySQL
from werkzeug.security import generate_password_hash, check_password_hash # berfungsi untuk meng-hash password
import MySQLdb.cursors # berfungsi untuk mengakses database MySQL
from datetime import date # berfungsi untuk mengakses tanggal
from functools import wraps # berfungsi untuk membuat decorator
from flask_mail import Mail, Message # berfungsi untuk mengirim email
from flask import make_response # berfungsi untuk membuat response HTTP
from xhtml2pdf import pisa # berfungsi untuk mengkonversi HTML ke PDF
from io import BytesIO # berfungsi untuk mengolah data dalam bentuk byte
from flask import render_template_string # berfungsi untuk merender template HTML sebagai string
import pandas as pd # berfungsi untuk mengolah data dalam bentuk tabel
import os # berfungsi untuk mengakses sistem file
from werkzeug.utils import secure_filename # berfungsi untuk mengamankan nama file yang diupload

app = Flask(__name__) # Inisialisasi Flask
app.secret_key = 'k3l0mp0k1' # Kunci rahasia untuk session

# Konfigurasi database
app.config['MYSQL_HOST'] = 'localhost' # Alamat host database
app.config['MYSQL_USER'] = 'root' # Username database
app.config['MYSQL_PASSWORD'] = '' # Password database (kosong jika tidak ada password)
app.config['MYSQL_DB'] = 'perpustakaan' # Nama database

mysql = MySQL(app) # Inisialisasi MySQL

# Konfigurasi Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com' # Server SMTP Gmail
app.config['MAIL_PORT'] = 587 # Port untuk SMTP Gmail
app.config['MAIL_USE_TLS'] = True # Gunakan TLS untuk keamanan
app.config['MAIL_USERNAME'] = 'emailpengirim@gmail.com'  # ganti dengan email pengirim
app.config['MAIL_PASSWORD'] = 'passwordemail'            # gunakan App Password jika 2FA aktif
mail = Mail(app) # Inisialisasi Flask-Mail

# Simulasi data user
dummy_user = {
    'nama_lengkap': 'Budi Santoso',
    'email': 'emailpenerima@gmail.com',
    'telepon': '08123456789'
} # Simulasi data user untuk pengiriman email

# Route home (redirect ke login)
@app.route('/') # Route untuk halaman utama
def home(): # berfungsi untuk mengarahkan ke halaman login
    return redirect(url_for('login')) # berfungsi untuk mengarahkan ke halaman login

# === LOGIN ===
@app.route('/login', methods=['GET', 'POST']) # berfungsi untuk menangani request GET dan POST pada route /login
def login(): # berfungsi untuk menangani login 
    if request.method == 'POST': # berfungsi untuk menangani request POST
        username = request.form['username'] # mengambil username dari form login
        password_input = request.form['password'] # mengambil password dari form login
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # membuat cursor untuk eksekusi query
        cursor.execute("SELECT * FROM users WHERE username = %s", [username]) # query untuk mengambil data user berdasarkan username
        user = cursor.fetchone() # mengambil satu data user yang sesuai dengan username
        if user and check_password_hash(user['password'], password_input): # berfungsi untuk memeriksa apakah user ditemukan dan password yang diinputkan sesuai dengan password yang ada di database
            session['loggedin'] = True # menyimpan session loggedin sebagai True
            session['id'] = user['id'] # menyimpan session id user
            session['username'] = user['username'] # menyimpan session username user
            session['role'] = user['role'] # menyimpan session role user
            return redirect(url_for(f"{user['role']}_dashboard")) # mengarahkan ke dashboard sesuai dengan role user
        flash('Username atau password salah') # menampilkan pesan error jika username atau password salah
    return render_template('login.html') # mengembalikan halaman login jika request method adalah GET atau jika login gagal

# === REGISTER ===
@app.route('/register', methods=['GET', 'POST']) # berfungsi untuk menangani request GET dan POST pada route /register
def register(): # berfungsi untuk menangani registrasi user baru
    if request.method == 'POST': # berfungsi untuk menangani request POST
        username = request.form['username'].strip() # mengambil username dari form registrasi
        email = request.form['email'].strip() # mengambil email dari form registrasi
        telepon = request.form['telepon'].strip() # mengambil telepon dari form registrasi
        password = generate_password_hash(request.form['password']) # meng-hash password yang diinputkan
        role = request.form['role'] # mengambil role dari form registrasi
        nama_lengkap = request.form['nama_lengkap'].strip() # mengambil nama lengkap dari form registrasi

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # membuat cursor untuk eksekusi query

        # Cek username sudah ada atau belum
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,)) # query untuk mengambil data user berdasarkan username
        existing_user = cursor.fetchone() # mengambil satu data user yang sesuai dengan username
        if existing_user: # berfungsi untuk memeriksa apakah username sudah ada di database
            flash('Username sudah digunakan, silakan pilih username lain.') # menampilkan pesan error jika username sudah ada
            return redirect(url_for('register')) # mengarahkan kembali ke halaman registrasi

        # Cek email sudah ada atau belum (opsional)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))  # query untuk mengambil data user berdasarkan email
        existing_email = cursor.fetchone() # mengambil satu data user yang sesuai dengan email
        if existing_email:  # berfungsi untuk memeriksa apakah email sudah ada di database
            flash('Email sudah terdaftar, silakan gunakan email lain.') # menampilkan pesan error jika email sudah ada
            return redirect(url_for('register'))    # mengarahkan kembali ke halaman registrasi

        # Insert data user baru
        cursor.execute("INSERT INTO users (username, password, role, nama_lengkap, email, telepon) VALUES (%s, %s, %s, %s, %s, %s)",
                       (username, password, role, nama_lengkap, email, telepon))    # query untuk memasukkan data user baru ke database
        mysql.connection.commit()   # menyimpan perubahan ke database
        flash('Registrasi berhasil, silakan login.')    # menampilkan pesan sukses setelah registrasi berhasil
        return redirect(url_for('login'))   # mengarahkan ke halaman login setelah registrasi berhasil

    return render_template('register.html') # mengembalikan halaman registrasi jika request method adalah GET


# === LOGOUT ===
@app.route('/logout') # berfungsi untuk menangani logout user
def logout():   # berfungsi untuk menangani logout user
    session.clear() # menghapus semua data session
    return redirect(url_for('login'))   # mengarahkan ke halaman login setelah logout

# === DASHBOARD ADMIN ===
@app.route('/admin/kata_sambutan')  # berfungsi untuk menampilkan halaman kata sambutan admin
def admin_kata_sambutan():  # berfungsi untuk menampilkan halaman kata sambutan admin
    if 'loggedin' in session and session['role'] == 'admin':    # berfungsi untuk memeriksa apakah user sudah login dan memiliki role admin
        return render_template('admin/kata_sambutan.html')  # mengembalikan halaman kata sambutan admin
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role admin

@app.route('/admin/dashboard')  # berfungsi untuk menampilkan halaman dashboard admin
def admin_dashboard():  # berfungsi untuk menampilkan halaman dashboard admin
    if 'loggedin' in session and session['role'] == 'admin':    # berfungsi untuk memeriksa apakah user sudah login dan memiliki role admin
        cur = mysql.connection.cursor() # membuat cursor untuk eksekusi query

        cur.execute("SELECT COUNT(*) FROM buku")    # query untuk menghitung total buku
        total_buku = cur.fetchone()[0]  # mengambil hasil query (total buku)

        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'pengunjung'") # query untuk menghitung total pengunjung
        total_pengunjung = cur.fetchone()[0]    # mengambil hasil query (total pengunjung)

        cur.execute("SELECT COUNT(*) FROM pinjaman WHERE status = 'Dipinjam'")  # query untuk menghitung total pinjaman yang sedang dipinjam
        total_pinjaman = cur.fetchone()[0]  # mengambil hasil query (total pinjaman)

        today = date.today()    # mendapatkan tanggal hari ini
        cur.execute("SELECT COUNT(*) FROM pinjaman WHERE status = 'Dipinjam' AND tanggal_kembali < %s", (today,))   # query untuk menghitung total pinjaman yang terlambat
        total_terlambat = cur.fetchone()[0] # menghitung total pinjaman yang terlambat

        cur.close() # menutup cursor setelah selesai digunakan

        return render_template("admin/dashboard.html",  # mengembalikan halaman dashboard admin dengan data yang sudah diambil
                               total_buku=total_buku,   # total buku yang ada di database
                               total_pengunjung=total_pengunjung,   # total pengunjung yang ada di database
                               total_pinjaman=total_pinjaman,   # total pinjaman yang sedang dipinjam
                               total_terlambat=total_terlambat) # total pinjaman yang terlambat
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role admin

# === DAFTAR BUKU ADMIN ===
@app.route('/admin/buku')   # berfungsi untuk menampilkan daftar buku di halaman admin
def admin_buku():   # berfungsi untuk menampilkan daftar buku di halaman admin
    if 'username' not in session:   # berfungsi untuk memeriksa apakah user sudah login
        return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login

    keyword = request.args.get('q') # mengambil keyword pencarian dari query string
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    # membuat cursor untuk eksekusi query

    if keyword: # berfungsi untuk memeriksa apakah ada keyword pencarian
        query = "SELECT * FROM buku WHERE judul LIKE %s OR penulis LIKE %s"
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%")) # query untuk mencari buku berdasarkan judul atau penulis
    else:   # jika tidak ada keyword pencarian
        cursor.execute("SELECT * FROM buku")    # query untuk mengambil semua data buku

    buku = cursor.fetchall()    # mengambil semua data buku yang sudah diquery
    return render_template('admin/daftar_buku.html', buku=buku) # mengembalikan halaman daftar buku


# === TAMBAH BUKU ===
@app.route('/admin/buku/tambah', methods=['GET', 'POST'])   # berfungsi untuk menampilkan form tambah buku di halaman admin
def admin_tambah_buku():    # berfungsi untuk menampilkan form tambah buku di halaman admin
    if request.method == 'POST':    # berfungsi untuk menangani request POST saat menambahkan buku
        data = (    # mengambil data dari form tambah buku
            request.form['judul'],  # judul buku
            request.form['penulis'],    # penulis buku
            request.form['penerbit'],   # penerbit buku
            request.form['tahun_terbit'],   # tahun terbit buku
            request.form['stok']    # stok buku yang tersedia
        )
        cursor = mysql.connection.cursor()  # membuat cursor untuk eksekusi query
        cursor.execute("INSERT INTO buku (judul, penulis, penerbit, tahun_terbit, stok) VALUES (%s, %s, %s, %s, %s)", data) # query untuk memasukkan data buku baru ke database
        mysql.connection.commit()   # menyimpan perubahan ke database
        return redirect(url_for('admin_buku'))  # mengarahkan ke halaman daftar buku
    return render_template('admin/form_buku.html', action="Tambah", buku=None)  # mengembalikan halaman form tambah

# === EDIT BUKU ===
@app.route('/admin/buku/edit/<int:id>', methods=['GET', 'POST'])    # berfungsi untuk menampilkan form edit buku di halaman admin
def admin_edit_buku(id):    # berfungsi untuk menampilkan form edit buku di halaman admin
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    # membuat cursor untuk eksekusi query
    if request.method == 'POST':    # berfungsi untuk menangani request POST saat mengedit buku
        data = (    # mengambil data dari form edit buku
            request.form['judul'],  # judul buku
            request.form['penulis'],    # penulis buku
            request.form['penerbit'],   # penerbit buku
            request.form['tahun_terbit'],   # tahun terbit buku
            request.form['stok'],   # stok buku yang tersedia
            id  # id buku yang akan diedit
        )   # query untuk mengupdate data buku yang sudah ada di database
        cursor.execute("UPDATE buku SET judul=%s, penulis=%s, penerbit=%s, tahun_terbit=%s, stok=%s WHERE id=%s", data) # berfungsi untuk mengupdate data buku yang sudah ada di database
        mysql.connection.commit()   # menyimpan perubahan ke database
        return redirect(url_for('admin_buku'))  # mengarahkan ke halaman daftar buku
    cursor.execute("SELECT * FROM buku WHERE id = %s", [id])    # query untuk mengambil data buku berdasarkan id
    buku = cursor.fetchone()    # mengambil satu data buku yang sesuai dengan id
    return render_template('admin/form_buku.html', action="Edit", buku=buku)    # mengembalikan halaman form edit buku dengan data buku yang sudah diambil

# === HAPUS BUKU ===
@app.route('/admin/buku/hapus/<int:id>')    # berfungsi untuk menghapus buku berdasarkan id
def admin_hapus_buku(id):   # berfungsi untuk menghapus buku berdasarkan id
    cursor = mysql.connection.cursor()  # membuat cursor untuk eksekusi query
    cursor.execute("DELETE FROM buku WHERE id = %s", [id])  # query untuk menghapus data buku berdasarkan id
    mysql.connection.commit()   # menyimpan perubahan ke database
    return redirect(url_for('admin_buku'))  # mengarahkan ke halaman daftar buku

# === DAFTAR PINJAMAN PENGUNJUNG DI DATA ADMIN ===
@app.route('/admin/pinjaman')   # berfungsi untuk menampilkan daftar pinjaman buku di halaman admin
def admin_pinjaman():   # berfungsi untuk menampilkan daftar pinjaman buku di halaman admin
    if 'loggedin' in session and session['role'] == 'admin':    # berfungsi untuk memeriksa apakah user sudah login dan memiliki role admin
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    # membuat cursor untuk eksekusi query
        cursor.execute("""
            SELECT p.*, b.judul, u.username 
            FROM pinjaman p 
            JOIN buku b ON p.buku_id = b.id 
            JOIN users u ON p.user_id = u.id
            ORDER BY p.tanggal_pinjam DESC
        """)    # query untuk mengambil data pinjaman buku yang sudah ada di database
        pinjaman = cursor.fetchall()    # mengambil semua data pinjaman buku yang sudah diquery
        return render_template('admin/daftar_pinjaman.html', pinjaman=pinjaman) # mengembalikan halaman daftar pinjaman buku
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role admin

# === DAFTAR PENGUNJUNG DI DATA ADMIN===
from functools import wraps # berfungsi untuk membuat decorator
from flask import session, redirect, url_for, flash # berfungsi untuk mengakses session, mengarahkan ke route lain, dan menampilkan pesan flash

def admin_required(f):  # berfungsi untuk membuat decorator yang memeriksa apakah user sudah login dan memiliki role admin
    @wraps(f)   # berfungsi untuk menjaga nama fungsi asli
    def decorated_function(*args, **kwargs):    # berfungsi untuk menangani request yang masuk
        if 'loggedin' not in session or session.get('role') != 'admin':     # berfungsi untuk memeriksa apakah user sudah login dan memiliki role admin
            flash("Anda harus login sebagai admin untuk mengakses halaman ini.", "warning") # menampilkan pesan flash jika user belum login atau tidak memiliki role admin
            return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role admin
        return f(*args, **kwargs)   # mengembalikan fungsi yang sudah didekorasi jika user sudah login dan memiliki role admin
    return decorated_function       # berfungsi untuk mengembalikan fungsi yang sudah didekorasi

@app.route('/admin/pengunjung') # berfungsi untuk menampilkan daftar pengunjung di halaman admin
@admin_required # menggunakan decorator admin_required untuk memeriksa apakah user sudah login dan memiliki role admin
def admin_pengunjung():     # berfungsi untuk menampilkan daftar pengunjung di halaman admin
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    # membuat cursor untuk eksekusi query
    try:            # berfungsi untuk menangani error saat mengambil data pengunjung
        cursor.execute("SELECT * FROM users WHERE role = 'pengunjung'") # query untuk mengambil data pengunjung yang sudah ada di database
        pengunjung = cursor.fetchall()  # mengambil semua data pengunjung yang sudah diquery
    except Exception as e:  # berfungsi untuk menangani error saat mengambil data pengunjung
        flash("Gagal mengambil data pengunjung: " + str(e), "danger")   # menampilkan pesan flash jika gagal mengambil data pengunjung
        pengunjung = [] # menginisialisasi pengunjung sebagai list kosong jika gagal mengambil data pengunjung
    finally:    # berfungsi untuk menutup cursor setelah selesai digunakan
        cursor.close()  # menutup cursor setelah selesai digunakan
    return render_template('admin/daftar_pengunjung.html', pengunjung=pengunjung)   # mengembalikan halaman daftar peng


# === LAPORAN PEMINJAMAN UNTUK ROLE ADMIN ===
from datetime import datetime   # berfungsi untuk mengakses tanggal dan waktu

@app.route('/admin/laporan', methods=['GET', 'POST'])   # berfungsi untuk menampilkan laporan peminjaman di halaman admin
def admin_laporan():    # berfungsi untuk menampilkan laporan peminjaman di halaman admin
    if 'loggedin' in session and session['role'] == 'admin':    # berfungsi untuk memeriksa apakah user sudah login dan memiliki role admin
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    # membuat cursor untuk eksekusi query
        query = """
            SELECT p.*, b.judul, u.username 
            FROM pinjaman p 
            JOIN buku b ON p.buku_id = b.id 
            JOIN users u ON p.user_id = u.id
            WHERE 1
        """ # query dasar untuk mengambil data peminjaman buku
        filters = []    # inisialisasi list untuk menyimpan filter query

        start = request.args.get('start')   # mengambil tanggal mulai dari query string
        end = request.args.get('end')   # mengambil tanggal akhir dari query string

        if start:   # berfungsi untuk memeriksa apakah ada tanggal mulai yang diinputkan
            query += " AND p.tanggal_pinjam >= %s"  # menambahkan filter tanggal mulai ke query
            filters.append(start)   # menambahkan tanggal mulai ke list filter
        if end:  # berfungsi untuk memeriksa apakah ada tanggal akhir yang diinputkan
            query += " AND p.tanggal_pinjam <= %s"  # menambahkan filter tanggal akhir ke query
            filters.append(end) # menambahkan tanggal akhir ke list filter

        query += " ORDER BY p.tanggal_pinjam DESC"  # menambahkan pengurutan berdasarkan tanggal peminjaman secara menurun

        cursor.execute(query, filters)  # mengeksekusi query dengan filter yang sudah ditambahkan
        laporan = cursor.fetchall() # mengambil semua data laporan peminjaman buku yang sudah diquery
        return render_template('admin/laporan.html', laporan=laporan, start=start, end=end) # mengembalikan halaman laporan pem
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role admin

# === BAGIAN UNTUK MENGUNDUH LAPORAN PEMINJAMAN DI ROLE ADMIN ===
@app.route('/admin/export/pdf') # berfungsi untuk mengunduh laporan peminjaman dalam format PDF
def export_pdf():   # berfungsi untuk mengunduh laporan peminjaman dalam format PDF
    if 'loggedin' in session and session['role'] == 'admin':    # berfungsi untuk memeriksa apakah user sudah login dan memiliki role admin
        start = request.args.get('start')   # mengambil tanggal mulai dari query string
        end = request.args.get('end')   # mengambil tanggal akhir dari query string

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    # membuat cursor untuk eksekusi query
        query = """
            SELECT p.*, b.judul, u.username 
            FROM pinjaman p 
            JOIN buku b ON p.buku_id = b.id 
            JOIN users u ON p.user_id = u.id
            WHERE 1
        """ # query dasar untuk mengambil data peminjaman buku
        filters = []    # inisialisasi list untuk menyimpan filter query
        if start:   # berfungsi untuk memeriksa apakah ada tanggal mulai yang diinputkan
            query += " AND p.tanggal_pinjam >= %s"  # menambahkan filter tanggal mulai ke query
            filters.append(start)   # menambahkan tanggal mulai ke list filter
        if end: # berfungsi untuk memeriksa apakah ada tanggal akhir yang diinputkan
            query += " AND p.tanggal_pinjam <= %s"  # menambahkan filter tanggal akhir ke query
            filters.append(end) # menambahkan tanggal akhir ke list filter
        cursor.execute(query, filters)  # mengeksekusi query dengan filter yang sudah ditambahkan
        laporan = cursor.fetchall() # mengambil semua data laporan peminjaman buku yang sudah diquery

        html = render_template('admin/laporan_pdf.html', laporan=laporan)   # merender template HTML untuk laporan PDF dengan data yang sudah diambil
        result = BytesIO()  # membuat objek BytesIO untuk menyimpan hasil PDF
        pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=result)  # mengkonversi HTML ke PDF dan menyimpan hasilnya ke objek BytesIO
        response = make_response(result.getvalue()) # membuat response HTTP dengan isi dari objek BytesIO
        response.headers['Content-Type'] = 'application/pdf'    # mengatur header Content-Type untuk PDF
        response.headers['Content-Disposition'] = 'attachment; filename=laporan_pinjaman.pdf'   # mengatur header Content-Disposition untuk mengunduh file dengan nama laporan_pinjaman.pdf
        return response # mengembalikan response HTTP yang sudah dibuat
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role admin

# === BAGIAN UNTUK MENGUNDUH LAPORAN PEMINJAMAN DI ROLE ADMIN DALAM FORMAT EXCEL ===
@app.route('/admin/export/excel')   # berfungsi untuk mengunduh laporan peminjaman dalam format Excel
def export_excel():   # berfungsi untuk mengunduh laporan peminjaman dalam format Excel
    if 'loggedin' in session and session['role'] == 'admin':        # berfungsi untuk memeriksa apakah user sudah login dan memiliki role admin
        start = request.args.get('start')   # mengambil tanggal mulai dari query string
        end = request.args.get('end')   # mengambil tanggal akhir dari query string

        cursor = mysql.connection.cursor()  # membuat cursor untuk eksekusi query
        query = """
            SELECT u.username, b.judul, p.tanggal_pinjam, p.tanggal_kembali, p.status 
            FROM pinjaman p 
            JOIN buku b ON p.buku_id = b.id 
            JOIN users u ON p.user_id = u.id
            WHERE 1
        """ # query dasar untuk mengambil data peminjaman buku
        filters = []    # inisialisasi list untuk menyimpan filter query
        if start:   # berfungsi untuk memeriksa apakah ada tanggal mulai yang diinputkan
            query += " AND p.tanggal_pinjam >= %s"  # menambahkan filter tanggal mulai ke query
            filters.append(start)   # menambahkan tanggal mulai ke list filter
        if end: # berfungsi untuk memeriksa apakah ada tanggal akhir yang diinputkan
            query += " AND p.tanggal_pinjam <= %s"      # menambahkan filter tanggal akhir ke query
            filters.append(end) # menambahkan tanggal akhir ke list filter
        cursor.execute(query, filters)  # mengeksekusi query dengan filter yang sudah ditambahkan
        data = cursor.fetchall()    # mengambil semua data laporan peminjaman buku yang sudah diquery
        df = pd.DataFrame(data, columns=['Pengunjung', 'Judul Buku', 'Tanggal Pinjam', 'Tanggal Kembali', 'Status'])    # membuat DataFrame dari data yang sudah diambil

        output = BytesIO()  # membuat objek BytesIO untuk menyimpan hasil Excel
        with pd.ExcelWriter(output, engine='openpyxl') as writer:       # membuat writer untuk menulis DataFrame ke file Excel
            df.to_excel(writer, index=False, sheet_name='Laporan')  # menulis DataFrame ke file Excel tanpa index dan dengan nama sheet 'Laporan'

        output.seek(0)  # mengatur posisi pointer ke awal objek BytesIO
        response = make_response(output.read()) # membuat response HTTP dengan isi dari objek BytesIO
        response.headers['Content-Disposition'] = 'attachment; filename=laporan_pinjaman.xlsx'  # mengatur header Content-Disposition untuk mengunduh file dengan nama laporan_pinjaman.xlsx
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # mengatur header Content-Type untuk file Excel
        return response # mengembalikan response HTTP yang sudah dibuat
    return redirect(url_for('login'))       # mengarahkan ke halaman login jika user belum login atau tidak memiliki role admin

# ===================================== AKHIR HALAMAN ADMIN ===================================


# ===================================== AWAL HALAMAN PENGUNJUNG ===================================
# PROFIL PENGUNJUNG
@app.route('/pengunjung/profil')    # berfungsi untuk menampilkan profil pengunjung
def pengunjung_profil():    # berfungsi untuk menampilkan profil pengunjung
    if 'username' not in session:   # berfungsi untuk memeriksa apakah user sudah login
        flash('Silakan login terlebih dahulu.') # menampilkan pesan flash jika user belum login
        return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login
    cur = mysql.connection.cursor() # membuat cursor untuk eksekusi query
    username = session['username']  # mengambil username dari session
    conn = mysql.connection  # mendapatkan koneksi database
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)    # membuat cursor untuk eksekusi query dengan dictionary cursor

    # Ambil data user
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))  # query untuk mengambil data user berdasarkan username
    user = cursor.fetchone()    # mengambil satu data user yang sesuai dengan username

    # Hitung total peminjaman
    cur.execute("SELECT COUNT(*) FROM pinjaman WHERE status = 'Dipinjam'")  # query untuk menghitung total peminjaman yang sedang dipinjam
    total_pinjaman = cur.fetchone()[0]  # mengambil hasil query (total peminjaman)
    cursor.close()  # menutup cursor setelah selesai digunakan
    return render_template('pengunjung/profil.html', user=user, total_pinjaman=total_pinjaman)  # mengembalikan halaman profil peng

# EDIT PROFIL PENGUNJUNG
# Boleh sesuaikan ekstensi file yang diizinkan
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # berfungsi untuk mendefinisikan ekstensi file yang diizinkan untuk diupload

def allowed_file(filename): # berfungsi untuk memeriksa apakah file yang diupload memiliki ekstensi yang diizinkan
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS # berfungsi untuk memeriksa apakah file yang diupload memiliki ekstensi yang diizinkan


@app.route('/pengunjung/profil/edit', methods=['GET', 'POST'])  # berfungsi untuk menampilkan form edit profil pengunjung
def pengunjung_edit_profil():   # berfungsi untuk menampilkan form edit profil pengunjung
    if 'username' not in session:   # berfungsi untuk memeriksa apakah user sudah login
        flash('Silakan login terlebih dahulu.', 'warning')  # menampilkan pesan flash jika user belum login
        return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login

    conn = mysql.connection # mendapatkan koneksi database
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)    # membuat cursor untuk eksekusi query dengan dictionary cursor
    username = session['username']  # mengambil username dari session

    if request.method == 'POST':    # berfungsi untuk menangani request POST saat mengedit profil
        nama_lengkap = request.form['nama_lengkap'].strip() # mengambil nama lengkap dari form edit profil
        email = request.form['email'].strip()   # mengambil email dari form edit profil
        telepon = request.form['telepon'].strip()   # mengambil telepon dari form edit profil

        if not nama_lengkap or not email:   # berfungsi untuk memeriksa apakah nama lengkap dan email sudah diisi
            flash('Nama lengkap dan email wajib diisi.', 'danger')  # menampilkan pesan flash jika nama lengkap atau email belum diisi
            return redirect(url_for('pengunjung_edit_profil'))  # mengarahkan kembali ke halaman edit profil jika nama lengkap atau email belum diisi

        foto_file = request.files.get('foto_profil')    # mengambil file foto profil dari form edit profil
        foto_filename = None    # inisialisasi variabel untuk menyimpan nama file foto profil

        if foto_file and foto_file.filename != '':  # berfungsi untuk memeriksa apakah ada file foto profil yang diupload
            if allowed_file(foto_file.filename):    # berfungsi untuk memeriksa apakah file foto profil memiliki ekstensi yang diizinkan
                filename_secure = secure_filename(foto_file.filename)   # mengamankan nama file foto profil agar tidak mengandung karakter yang tidak diizinkan
                # Buat nama file unik misalnya username + ekstensi  
                ext = filename_secure.rsplit('.', 1)[1].lower() # mengambil ekstensi file foto profil
                foto_filename = f"{username}_profile.{ext}" # membuat nama file unik berdasarkan username dan ekstensi file foto profil

                upload_path = os.path.join(current_app.root_path, 'static/uploads') # menentukan path untuk menyimpan file foto profil
                if not os.path.exists(upload_path):  # berfungsi untuk memeriksa apakah folder upload_path sudah ada
                    os.makedirs(upload_path)    # membuat folder upload_path jika belum ada

                foto_file.save(os.path.join(upload_path, foto_filename))    # menyimpan file foto profil ke folder upload_path dengan nama file unik
            else:   # jika file foto profil tidak memiliki ekstensi yang diizinkan
                flash('Format file foto tidak diizinkan. Gunakan JPG, PNG, JPEG, atau GIF.', 'danger')  # menampilkan pesan flash jika format file foto tidak diizinkan
                return redirect(url_for('pengunjung_edit_profil'))  # mengarahkan kembali ke halaman edit profil jika format file foto tidak diizinkan

        try:    # berfungsi untuk menangani error saat mengupdate profil pengunjung
            if foto_filename:   # berfungsi untuk memeriksa apakah ada file foto profil yang diupload
                cursor.execute(""" 
                    UPDATE users SET nama_lengkap=%s, email=%s, telepon=%s, foto_profil=%s
                    WHERE username=%s
                """, (nama_lengkap, email, telepon, foto_filename, username))   # query untuk mengupdate data profil pengunjung yang sudah ada di database
            else:   # jika tidak ada file foto profil yang diupload
                cursor.execute("""
                    UPDATE users SET nama_lengkap=%s, email=%s, telepon=%s
                    WHERE username=%s
                """, (nama_lengkap, email, telepon, username))  # query untuk mengupdate data profil pengunjung yang sudah ada di database tanpa mengupdate foto profil

            conn.commit()   # menyimpan perubahan ke database
            flash('Profil berhasil diperbarui.', 'success') # menampilkan pesan flash jika profil berhasil diperbarui
            return redirect(url_for('pengunjung_profil'))   # mengarahkan ke halaman profil pengunjung setelah berhasil diperbarui
        except Exception as e:  # berfungsi untuk menangani error saat mengupdate profil pengunjung
            conn.rollback() # membatalkan perubahan jika terjadi error saat mengupdate profil pengunjung
            flash(f'Gagal memperbarui profil: {e}', 'danger')   # menampilkan pesan flash jika gagal memperbarui profil pengunjung
            return redirect(url_for('pengunjung_edit_profil'))  # mengarahkan kembali ke halaman edit profil jika gagal memperbarui profil pengunjung

    # GET
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))  # query untuk mengambil data user berdasarkan username
    user = cursor.fetchone()    # mengambil satu data user yang sesuai dengan username
    cursor.close()  # menutup cursor setelah selesai digunakan

    return render_template('pengunjung/edit_profil.html', user=user)    # mengembalikan halaman edit profil

# === DASHBOARD PENGUNJUNG ===
@app.route('/pengunjung/dashboard') # berfungsi untuk menampilkan halaman dashboard pengunjung
def pengunjung_dashboard():   # berfungsi untuk menampilkan halaman dashboard pengunjung
    if 'loggedin' in session and session['role'] == 'pengunjung':   # berfungsi untuk memeriksa apakah user sudah login dan memiliki role pengunjung
        return render_template('pengunjung/dashboard.html', username=session['username'])   # mengembalikan halaman dashboard pengunjung dengan username yang sudah diambil dari session
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role pengunjung

# === DAFTAR BUKU UNTUK PENGUNJUNG ===
@app.route('/pengunjung/buku')  # berfungsi untuk menampilkan daftar buku di halaman pengunjung
def pengunjung_buku():  # berfungsi untuk menampilkan daftar buku di halaman pengunjung
    if 'loggedin' in session and session['role'] == 'pengunjung':   # berfungsi untuk memeriksa apakah user sudah login dan memiliki role pengunjung
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    # membuat cursor untuk eksekusi query
        cursor.execute("SELECT * FROM buku")    # query untuk mengambil semua data buku yang sudah ada di database
        buku = cursor.fetchall()    # mengambil semua data buku yang sudah diquery
        return render_template('pengunjung/daftar_buku.html', buku=buku)    # mengembalikan halaman daftar buku
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role pengunjung

# === PINJAM BUKU ===
@app.route('/pengunjung/buku/pinjam/<int:buku_id>') # berfungsi untuk menangani peminjaman buku oleh pengunjung
def pinjam_buku(buku_id):   # berfungsi untuk menangani peminjaman buku oleh pengunjung
    if 'loggedin' in session and session['role'] == 'pengunjung':   # berfungsi untuk memeriksa apakah user sudah login dan memiliki role pengunjung
        cursor = mysql.connection.cursor()  # membuat cursor untuk eksekusi query
        cursor.execute("INSERT INTO pinjaman (user_id, buku_id, tanggal_pinjam, status) VALUES (%s, %s, CURDATE(), 'dipinjam')",
                       (session['id'], buku_id))    # query untuk memasukkan data peminjaman buku baru ke database
        cursor.execute("UPDATE buku SET stok = stok - 1 WHERE id = %s AND stok > 0", [buku_id]) # mengurangi stok buku yang dipinjam
        mysql.connection.commit()   # menyimpan perubahan ke database
        flash('Buku berhasil dipinjam') # menampilkan pesan flash jika buku berhasil dipinjam
        return redirect(url_for('pengunjung_buku')) # mengarahkan ke halaman daftar buku
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role pengunjung

# === RIWAYAT PEMINJAMAN ===
@app.route('/pengunjung/riwayat')   # berfungsi untuk menampilkan riwayat peminjaman buku oleh pengunjung
def pengunjung_riwayat():   # berfungsi untuk menampilkan riwayat peminjaman buku oleh pengunjung
    if 'loggedin' in session and session['role'] == 'pengunjung':   # berfungsi untuk memeriksa apakah user sudah login dan memiliki role pengunjung
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    # membuat cursor untuk eksekusi query
        cursor.execute("""
            SELECT p.*, b.judul 
            FROM pinjaman p 
            JOIN buku b ON p.buku_id = b.id 
            WHERE p.user_id = %s
            ORDER BY p.tanggal_pinjam DESC
        """, [session['id']])   # query untuk mengambil data riwayat peminjaman buku berdasarkan user_id
        riwayat = cursor.fetchall()   # mengambil semua data riwayat peminjaman buku yang sudah diquery
        return render_template('pengunjung/riwayat.html', riwayat=riwayat)  # mengembalikan halaman riwayat pem
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role pengunjung

# === PENGEMBALIAN ===
@app.route('/pengunjung/kembali/<int:pinjaman_id>') # berfungsi untuk menangani pengembalian buku oleh pengunjung
def kembali_buku(pinjaman_id):  # berfungsi untuk menangani pengembalian buku oleh pengunjung
    if 'loggedin' in session and session['role'] == 'pengunjung':   # berfungsi untuk memeriksa apakah user sudah login dan memiliki role pengunjung
        cursor = mysql.connection.cursor()  # membuat cursor untuk eksekusi query
        cursor.execute("SELECT buku_id FROM pinjaman WHERE id = %s", [pinjaman_id]) # query untuk mengambil buku_id dari pinjaman berdasarkan
        buku = cursor.fetchone()    # mengambil satu data buku_id yang sesuai dengan pinjaman_id
        if buku: # berfungsi untuk memeriksa apakah ada buku yang ditemukan berdasarkan pinjaman_id
            cursor.execute("UPDATE pinjaman SET tanggal_kembali = CURDATE(), status = 'dikembalikan' WHERE id = %s", [pinjaman_id]) # query untuk mengupdate data pinjaman buku yang sudah dikembalikan
            cursor.execute("UPDATE buku SET stok = stok + 1 WHERE id = %s", [buku[0]])  # mengembalikan stok buku yang sudah dikembalikan
            mysql.connection.commit()   # menyimpan perubahan ke database
        return redirect(url_for('pengunjung_riwayat'))  # mengarahkan ke halaman riwayat pem
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role pengunjung

# === CARI BUKU UNTUK PENGUNJUNG ===
@app.route('/pengunjung/cari', methods=['GET', 'POST']) # berfungsi untuk menangani pencarian buku oleh pengunjung
def pengunjung_cari_buku(): # berfungsi untuk menangani pencarian buku oleh pengunjung
    if 'username' not in session or session.get('role') != 'pengunjung':    # berfungsi untuk memeriksa apakah user sudah login dan memiliki role pengunjung
        return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role pengunjung

    cursor = mysql.connection.cursor()  # membuat cursor untuk eksekusi query
    
    # Ambil keyword pencarian dari form 
    keyword = request.form.get('keyword')   # mengambil keyword pencarian dari form jika ada

    if keyword: # berfungsi untuk memeriksa apakah ada keyword pencarian
        query = "SELECT * FROM buku WHERE judul LIKE %s OR penulis LIKE %s OR penerbit LIKE %s" # query untuk mencari buku berdasarkan judul, penulis, atau penerbit
        like_keyword = f"%{keyword}%"   # menambahkan wildcard % di awal dan akhir keyword untuk pencarian yang lebih fleksibel
        cursor.execute(query, (like_keyword, like_keyword, like_keyword))   # mengeksekusi query dengan parameter keyword yang sudah ditambahkan wildcard
    else:   # jika tidak ada keyword pencarian
        cursor.execute("SELECT * FROM buku")    # query untuk mengambil semua data buku
    # Ambil semua buku yang sesuai dengan keyword pencarian
    buku = cursor.fetchall()    # mengambil semua data buku yang sudah diquery
    cursor.close()  # menutup cursor setelah selesai digunakan
    # Kembalikan halaman pencarian buku dengan hasil pencarian
    return render_template('pengunjung/cari_buku.html', buku=buku, keyword=keyword) # mengembalikan halaman pencarian buku dengan hasil pencarian

# === DAFTAR BUKU PENGUNJUNG DENGAN PAGINATION ===
@app.route('/pengunjung/buku/page') # berfungsi untuk menampilkan daftar buku dengan pagination di halaman pengunjung
def pengunjung_buku_paginated():    # berfungsi untuk menampilkan daftar buku dengan pagination di halaman pengunjung
    # isi fungsi pagination
    # hanya jika pengunjung sudah login
    if 'loggedin' in session and session['role'] == 'pengunjung':   # berfungsi untuk memeriksa apakah user sudah login dan memiliki role pengunjung
        page = request.args.get('page', 1, type=int)    # mengambil nomor halaman dari query string, default ke 1 jika tidak ada
        per_page = 5    # jumlah buku per halaman
        offset = (page - 1) * per_page  # menghitung offset untuk pagination

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)    # membuat cursor untuk eksekusi query
        cursor.execute("SELECT COUNT(*) as total FROM buku")    # query untuk menghitung total buku
        total = cursor.fetchone()['total']  # mengambil total buku dari hasil query
        total_pages = (total + per_page - 1) // per_page    # menghitung total halaman berdasarkan
        # total buku dan jumlah buku per halaman
        cursor.execute("SELECT * FROM buku LIMIT %s OFFSET %s", [per_page, offset]) # query untuk mengambil data buku dengan limit dan offset untuk pagination
        buku = cursor.fetchall()    # mengambil semua data buku yang sudah diquery
        return render_template('pengunjung/buku.html', buku=buku, page=page, total_pages=total_pages)   # mengembalikan halaman daftar buku
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role pengunjung

# ====BAGIAN HALAMAN PENGUNJUNG ====
def login_required(role):   # berfungsi untuk membuat decorator yang memeriksa apakah user sudah login dan memiliki role tertentu
    def decorator(f):   # berfungsi untuk mendekorasi fungsi yang akan diperiksa
        @wraps(f)   # berfungsi untuk menjaga nama fungsi asli
        def wrapped(*args, **kwargs):   # berfungsi untuk menangani request yang masuk
            if 'loggedin' in session and session.get('role') == role:   # berfungsi untuk memeriksa apakah user sudah login dan memiliki role yang sesuai
                return f(*args, **kwargs)   # mengembalikan fungsi yang sudah didekorasi jika user sudah login dan memiliki role yang sesuai
            return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role yang sesuai
        return wrapped  # berfungsi untuk mengembalikan fungsi yang sudah didekorasi
    return decorator    # berfungsi untuk mengembalikan decorator yang sudah dibuat

# === HALAMAN BANTUAN PENGUNJUNG ===
@app.route('/pengunjung/bantuan')   # berfungsi untuk menampilkan halaman bantuan pengunjung
@login_required('pengunjung')   # menggunakan decorator login_required untuk memeriksa apakah user sudah login dan memiliki role pengunjung
def pengunjung_bantuan():   # berfungsi untuk menampilkan halaman bantuan pengunjung
    return render_template('pengunjung/bantuan.html')   # mengembalikan halaman bantuan pengunjung

# === HALAMAN TENTANG PENGUNJUNG ===
@app.route('/pengunjung/tentang')   # berfungsi untuk menampilkan halaman tentang pengunjung
def pengunjung_tentang():   # berfungsi untuk menampilkan halaman tentang pengunjung
    if 'loggedin' in session and session['role'] == 'pengunjung':   # berfungsi untuk memeriksa apakah user sudah login dan memiliki role pengunjung
        return render_template('pengunjung/tentang.html')   # mengembalikan halaman tentang pengunjung  
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role pengunjung

# === HALAMAN KONTEN PENGUNJUNG ===
@app.route('/pengunjung/kontak')    # berfungsi untuk menampilkan halaman kontak pengunjung
def pengunjung_kontak():    # berfungsi untuk menampilkan halaman kontak pengunjung
    if 'loggedin' in session and session['role'] == 'pengunjung':   # berfungsi untuk memeriksa apakah user sudah login dan memiliki role pengunjung
        return render_template('pengunjung/kontak.html')    # mengembalikan halaman kontak peng
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role pengunjung

# === HALAMAN SYARAT DAN KETENTUAN PENGUNJUNG ===
@app.route('/pengunjung/syarat-ketentuan')  # berfungsi untuk menampilkan halaman syarat dan ketentuan pengunjung
def pengunjung_syarat_ketentuan():  # berfungsi untuk menampilkan halaman syarat dan ketentuan pengunjung
    if 'loggedin' in session and session['role'] == 'pengunjung':   # berfungsi untuk memeriksa apakah user sudah login dan memiliki role pengunjung
        return render_template('pengunjung/syarat_ketentuan.html')  # mengembalikan halaman syarat dan ketentuan pengunjung
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role pengunjung

# === HALAMAN KEBIJAKAN PRIVASI PENGUNJUNG ===
@app.route('/pengunjung/kebijakan-privasi') # berfungsi untuk menampilkan halaman kebijakan privasi pengunjung
def pengunjung_kebijakan_privasi(): # berfungsi untuk menampilkan halaman kebijakan privasi pengunjung
    if 'loggedin' in session and session['role'] == 'pengunjung':   # berfungsi untuk memeriksa apakah user sudah login dan memiliki role pengunjung    
        return render_template('pengunjung/kebijakan_privasi.html') # mengembalikan halaman kebijakan privasi pengunjung
    return redirect(url_for('login'))   # mengarahkan ke halaman login jika user belum login atau tidak memiliki role pengunjung


# === JALANKAN APLIKASI ===
if __name__ == '__main__':  # berfungsi untuk menjalankan aplikasi Flask
    app.run(debug=True) # mengatur debug=True untuk menampilkan error di browser saat terjadi kesalahan
