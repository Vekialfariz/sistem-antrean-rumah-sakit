from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('rs_antrean.db')
    conn.row_factory = sqlite3.Row
    return conn

def diagnosa_poli(gejala):
    gejala = gejala.lower().strip()
    # Pemetaan kata kunci ke ID Poli
    keywords = {
        4: ["gigi", "gusi", "geraham", "bolong", "behel", "cabut"], # Poli Gigi
        3: ["jantung", "dada", "sesak", "debar", "aritmia"],         # Poli Jantung
        5: ["mata", "kabur", "minus", "katarak", "perih"],           # Poli Mata
        2: ["demam", "batuk", "flu", "lambung", "mual", "pusing"],   # Poli Umum/Dalam
        6: ["stroke", "saraf", "kejang", "migrain"]                  # Poli Saraf
    }
    for id_poli, kunci in keywords.items():
        if any(kata in gejala for kata in kunci):
            return id_poli
    return 1 # Default ke Poli Umum

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/daftar', methods=['POST'])
def daftar_antrean():
    data = request.json
    nama = data.get('nama')
    gejala = data.get('gejala', '')

    if not nama or not gejala:
        return jsonify({"status": "error", "pesan": "Nama dan Gejala wajib diisi"}), 400

    id_poli = diagnosa_poli(gejala)
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute('SELECT COUNT(*) FROM antrean WHERE id_poli = ?', (id_poli,))
        nomor_baru = cur.fetchone()[0] + 1

        cur.execute('''INSERT INTO antrean (nama_pasien, gejala, id_poli, nomor_urut) 
                       VALUES (?, ?, ?, ?)''', (nama, gejala, id_poli, nomor_baru))
        conn.commit()

        cur.execute('SELECT nama_poli FROM poli WHERE id_poli = ?', (id_poli,))
        row = cur.fetchone()
        nama_poli = row['nama_poli'] if row else "Poli Umum"

        return jsonify({"status": "sukses", "nama": nama, "poli": nama_poli, "nomor": nomor_baru})
    except Exception as e:
        return jsonify({"status": "error", "pesan": str(e)}), 500
    finally:
        conn.close()

@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    # Mengambil ID Antrean agar bisa dihapus nantinya
    cur.execute('''
        SELECT antrean.id_antrean, antrean.nama_pasien, antrean.nomor_urut, antrean.gejala, poli.nama_poli 
        FROM antrean 
        JOIN poli ON antrean.id_poli = poli.id_poli
        ORDER BY antrean.id_antrean DESC
    ''')
    semua_antrean = cur.fetchall()
    conn.close()
    return render_template('admin.html', antrean=semua_antrean)

@app.route('/hapus_antrean/<int:id_antrean>', methods=['POST'])
def hapus_antrean(id_antrean):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM antrean WHERE id_antrean = ?', (id_antrean,))
        conn.commit()
        return jsonify({"status": "sukses"})
    except Exception as e:
        return jsonify({"status": "error", "pesan": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)