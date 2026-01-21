import sqlite3

def setup():
    conn = sqlite3.connect('rs_antrean.db')
    cur = conn.cursor()

    # Hapus tabel lama agar tidak terjadi konflik ID
    cur.execute('DROP TABLE IF EXISTS antrean')
    cur.execute('DROP TABLE IF EXISTS poli')

    # Buat tabel Poli
    cur.execute('''CREATE TABLE poli (
        id_poli INTEGER PRIMARY KEY,
        nama_poli TEXT NOT NULL
    )''')

    # Buat tabel Antrean
    cur.execute('''CREATE TABLE antrean (
        id_antrean INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_pasien TEXT NOT NULL,
        gejala TEXT,
        id_poli INTEGER,
        nomor_urut INTEGER,
        waktu_daftar TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_poli) REFERENCES poli (id_poli)
    )''')

    # Masukkan data master Poli secara lengkap
    daftar_poli = [
        (1, 'Poli Umum'),
        (2, 'Poli Penyakit Dalam'),
        (3, 'Poli Jantung'),
        (4, 'Poli Gigi'),
        (5, 'Poli Mata'),
        (6, 'Poli Syaraf')
    ]
    cur.executemany('INSERT INTO poli (id_poli, nama_poli) VALUES (?, ?)', daftar_poli)

    conn.commit()
    conn.close()
    print("Suksess: Database rs_antrean.db telah dibuat dengan data master terbaru.")

if __name__ == "__main__":
    setup()