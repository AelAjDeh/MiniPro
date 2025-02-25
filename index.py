from flask import Flask, render_template, request, redirect, url_for, flash, session ,jsonify , send_from_directory
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Gantilah dengan secret key yang lebih aman

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Pastikan folder ada
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS lost (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            description TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            contact TEXT NOT NULL,
            image_url TEXT,
            reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS report (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            description TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            contact TEXT NOT NULL,
            image_url TEXT,
            reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html', title='Home')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('home_page'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('Lores.html', title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form.get('role', 'user')

        if role not in ['admin', 'user']:
            flash('Invalid role selection.', 'danger')
            return redirect(url_for('register'))

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if existing_user:
            flash('Username already exists', 'danger')
            conn.close()
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                     (username, hashed_password, role))
        conn.commit()
        conn.close()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('Lores.html', title='Register')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home_page'))


@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        last_seen = request.form['last_seen']
        contact = request.form['contact']

        image_url = None
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = filename

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO report (item_name, description, last_seen, contact, image_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_name, description, last_seen, contact, image_url))
        conn.commit()
        conn.close()

        flash('Laporan barang hilang telah dikirim!', 'success')
        return redirect(url_for('home_page'))
    return render_template('lapor.html', title='Report')

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Home')


@app.route('/lost', methods=['GET', 'POST'])
def lost():
    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        last_seen = request.form['last_seen']
        contact = request.form['contact']

        image_url = None
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = filename  # Simpan hanya nama file, bukan path lengkap

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO lost (item_name, description, last_seen, contact, image_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_name, description, last_seen, contact, image_url))
        conn.commit()
        conn.close()

        flash('Laporan barang hilang telah dikirim!', 'success')
        return redirect(url_for('home_page'))

    return render_template('ilang.html', title='Lost')

@app.route('/listHil')
def listHil():
    conn = get_db_connection()
    # Menggunakan ROW_NUMBER() untuk memberikan nomor urut dinamis berdasarkan waktu laporan
    query = '''
        SELECT 
            ROW_NUMBER() OVER (ORDER BY reported_at DESC) AS row_num,
            id, item_name, description, last_seen, contact, image_url, reported_at
        FROM lost
        ORDER BY reported_at DESC
        '''
    items = conn.execute('SELECT * FROM lost ORDER BY reported_at DESC').fetchall()
    conn.close()
    return render_template('listHil.html', title='Daftar Barang Hilang', items=items)

#Route List
@app.route('/listTem')
def listTem():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM report ORDER BY reported_at DESC').fetchall()
    conn.close()
    return render_template('listTem.html', title='Daftar Barang Hilang Yang Ditemukan', items=items)


@app.route('/hapus_barang/<int:item_id>', methods=['POST'])
def hapus_barang(item_id):
    """Menghapus laporan barang hilang berdasarkan ID dan memperbarui nomor urut"""
    if 'username' not in session or session.get('role') != 'user':
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    # Menghapus data barang hilang berdasarkan ID
    conn = get_db_connection()
    deleted = conn.execute('DELETE FROM lost WHERE id = ?', (item_id,)).rowcount
    conn.commit()

    if deleted:
        # Mengambil kembali data yang sudah diperbarui dengan nomor urut baru
        query = '''
            SELECT 
                ROW_NUMBER() OVER (ORDER BY reported_at DESC) AS row_num,
                id, item_name, description, last_seen, contact, image_url, reported_at
            FROM lost
            ORDER BY reported_at DESC
        '''
        items = conn.execute(query).fetchall()
        conn.close()

        # Mengirimkan data yang sudah terupdate ke template
        return jsonify({"success": True, "items": [dict(item) for item in items]})
    else:
        conn.close()
        return jsonify({"success": False, "error": "Not Found"}), 404

@app.route('/ambil_barang/<int:item_id>', methods=['POST'])
def ambil_barang(item_id):
    """Menghapus laporan barang hilang berdasarkan ID dan memperbarui nomor urut"""
    if 'username' not in session or session.get('role') != 'user':
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    # Menghapus data barang hilang berdasarkan ID
    conn = get_db_connection()
    deleted = conn.execute('DELETE FROM report WHERE id = ?', (item_id,)).rowcount
    conn.commit()

    if deleted:
        # Mengambil kembali data yang sudah diperbarui dengan nomor urut baru
        query = '''
            SELECT 
                ROW_NUMBER() OVER (ORDER BY reported_at DESC) AS row_num,
                id, item_name, description, last_seen, contact, image_url, reported_at
            FROM lost
            ORDER BY reported_at DESC
        '''
        items = conn.execute(query).fetchall()
        conn.close()

        # Mengirimkan data yang sudah terupdate ke template
        return jsonify({"success": True, "items": [dict(item) for item in items]})
    else:
        conn.close()
        return jsonify({"success": False, "error": "Not Found"}), 404

if __name__ == '__main__':
    create_table()
    app.run(debug=True, host='0.0.0.0')
