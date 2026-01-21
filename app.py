from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('rs_antrean.db')
    conn.row_factory = sqlite3.Row
    return conn

def diagnosa_poli(gejala):
    gejala = gejala.lower()
    
    # Pemetaan kata kunci yang lebih luas
    keywords = {
        4: ["gigi", "gusi", "geraham", "bolong", "behel", "cabut gigi"],
        3: ["jantung", "nyeri dada", "sesak napas", "debar", "aritmia"],
        5: ["mata", "kabur", "minus", "katarak", "perih", "merah"],
        2: ["demam", "batuk", "flu", "lambung", "tipes", "diabetes", "mual"],
        6: ["stroke", "saraf", "kejang", "migrain", "lumpuh"]
    }

    for id_poli, kunci in keywords.items():
        if any(kata in gejala for kata in kunci):
            return id_poli
    return 1  # Kembali ke Poli Umum jika tidak ada yang cocok

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
        # Hitung nomor antrean
        cur.execute('SELECT COUNT(*) FROM antrean WHERE id_poli = ?', (id_poli,))
        nomor_baru = cur.fetchone()[0] + 1

        # Simpan ke DB
        cur.execute('''INSERT INTO antrean (nama_pasien, gejala, id_poli, nomor_urut) 
                       VALUES (?, ?, ?, ?)''', (nama, gejala, id_poli, nomor_baru))
        conn.commit()

        # Ambil nama poli dari DB
        cur.execute('SELECT nama_poli FROM poli WHERE id_poli = ?', (id_poli,))
        nama_poli = cur.fetchone()['nama_poli']

        return jsonify({
            "status": "sukses",
            "nama": nama,
            "poli": nama_poli,
            "nomor": nomor_baru
        })
    except Exception as e:
        return jsonify({"status": "error", "pesan": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)