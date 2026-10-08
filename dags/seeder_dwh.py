import mysql.connector
from faker import Faker
import random
import string
from datetime import datetime

# Inisialisasi Faker dengan lokalisasi Indonesia
fake = Faker('id_ID')

# Konfigurasi Koneksi Database Aiven (Sesuaikan dengan milikmu)
DB_CONFIG = {
    'host': 'mysql-3a4534a4-muhammadnauval6777-f3ec.h.aivencloud.com', 
    'port': 16029,
    'user': 'avnadmin',
    'password': 'AVNS_FKxjLZwwtO5VzOsSIUX',
    'database': 'dwh'
}

# Kamus Kode 2 Digit yang sinkron dengan id_kabupaten_kota di dim_wilayah
wilayah_aceh = {
    "01": "Kota Banda Aceh", "02": "Kota Sabang", "03": "Kota Langsa",
    "04": "Kota Lhokseumawe", "05": "Kabupaten Aceh Barat", 
    "06": "Kabupaten Aceh Barat Daya", "07": "Kabupaten Aceh Besar", 
    "08": "Kabupaten Aceh Jaya", "09": "Kabupaten Aceh Selatan", 
    "10": "Kabupaten Aceh Singkil", "11": "Kabupaten Aceh Tamiang", 
    "12": "Kabupaten Aceh Tengah", "13": "Kabupaten Aceh Tenggara", 
    "14": "Kabupaten Aceh Utara", "15": "Kabupaten Gayo Lues", 
    "16": "Kabupaten Pidie", "17": "Kabupaten Pidie Jaya", 
    "18": "Kabupaten Simeulue"
}

def main():
    try:
        print("Menghubungkan ke Data Warehouse Aiven...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Kosongkan tabel (Truncate) agar data bersih dan Auto Increment kembali ke 1
        print("Mengosongkan tabel (Truncate)...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE fact_tagihan;")
        cursor.execute("TRUNCATE TABLE dim_objek_pajak;")
        cursor.execute("TRUNCATE TABLE dim_wajib_pajak;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()

        total_data = 797
        waktu_load = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sumber_db = 'db_dispenda'

        print(f"Mulai menyuntikkan {total_data} data sintetik...")

        for i in range(total_data):
            # --- DIMENSI WAJIB PAJAK ---
            jenis_kelamin = random.choice(['Pria', 'Wanita'])
            nama_lengkap = fake.name_male() if jenis_kelamin == 'Pria' else fake.name_female()
            nik_wp = str(fake.random_number(digits=16, fix_len=True))
            alamat = fake.street_address()
            
            # Mengambil kode 2 digit acak (misal: "01", "05", dll.)
            id_kabupaten = random.choice(list(wilayah_aceh.keys()))
            
            npwpd = f"P.0{random.randint(1,9)}.{random.randint(1000,9999)}"
            tanggal_daftar = fake.date_between(start_date='-3y', end_date='today').strftime('%Y-%m-%d')

            sql_wp = """
                INSERT INTO dim_wajib_pajak 
                (nik_wp, nama_lengkap, jenis_kelamin, alamat, id_kabupaten_kota, npwpd, tanggal_daftar, sumber_database, waktu_load) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_wp, (nik_wp, nama_lengkap, jenis_kelamin, alamat, id_kabupaten, npwpd, tanggal_daftar, sumber_db, waktu_load))
            wajib_pajak_key = cursor.lastrowid

            # --- DIMENSI OBJEK PAJAK ---
            id_objek = f"OBJ-{fake.random_number(digits=6, fix_len=True)}"
            id_kategori = str(random.randint(1, 4))

            if id_kategori == '1':
                # Pajak Kendaraan Bermotor: plat nomor & rincian kendaraan
                nomor_identitas_aset = f"BL {random.randint(1000, 9999)} {fake.lexify(text='??', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
                rincian_objek = random.choice([
                    'Honda Vario (Roda 2)', 'Toyota Avanza (Roda 4)', 'Yamaha NMAX (Roda 2)',
                    'Mitsubishi Pajero (Roda 4)', 'Suzuki Ertiga (Roda 4)'
                ])
            elif id_kategori == '2':
                # Pajak Alat Berat: nomor identitas alat berat & rincian alat berat
                nomor_identitas_aset = f"AB-{random.randint(100000, 999999)}/{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}"
                rincian_objek = random.choice([
                    'Excavator Caterpillar', 'Bulldozer Komatsu', 'Dump Truck Mercedes-Benz',
                    'Crane Tadano', 'Wheel Loader Hitachi'
                ])
            elif id_kategori == '3':
                # Pajak Air Permukaan: nomor Izin/SIP & rincian sumber air
                nomor_identitas_aset = f"SIP/{random.randint(10000, 99999)}/{random.randint(2020, 2026)}"
                rincian_objek = random.choice([
                    'Sumur Industri (500 m3)', 'Intake Sungai (1000 m3)', 'Sumur Domestik (200 m3)',
                    'Intake Danau (2000 m3)', 'Sumur Pertanian (1000 m3)'
                ])
            else:
                # Kategori 4: Pajak Rokok - nomor Cukai & rincian jenis rokok
                nomor_identitas_aset = f"04.{random.randint(100, 999)}.{random.randint(100000, 999999)}"
                rincian_objek = random.choice([
                    'Sigaret Kretek Mesin (SKM)', 'Sigaret Putih Mesin (SPM)',
                    'Sigaret Kretek Tangan (SKT)', 'Sigaret Putih Tangan (SPT)', 'Cerutu (CRU)'
                ])

            nilai_aset = random.randint(15, 450) * 1000000 

            sql_obj = """
                INSERT INTO dim_objek_pajak 
                (id_objek, nik_wp, id_kategori, nomor_identitas_aset, rincian_objek, nilai_aset, sumber_database, waktu_load) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_obj, (id_objek, nik_wp, id_kategori, nomor_identitas_aset, rincian_objek, nilai_aset, sumber_db, waktu_load))
            objek_pajak_key = cursor.lastrowid

            # --- FAKTA TAGIHAN ---
            waktu_key = 2026
            id_tagihan = f"INV-{fake.random_number(digits=8, fix_len=True)}"
            tahun_pajak = '2026'
            nominal_tagihan = int(nilai_aset * 0.015) 
            tanggal_jatuh_tempo = fake.date_between(start_date='-1M', end_date='+6M').strftime('%Y-%m-%d')
            status_tagihan = random.choices(['Lunas', 'Belum Lunas'], weights=[76, 24])[0]

            sql_fact = """
                INSERT INTO fact_tagihan 
                (wajib_pajak_key, objek_pajak_key, kategori_pajak_key, waktu_key, id_tagihan, tahun_pajak, nominal_tagihan, tanggal_jatuh_tempo, status_tagihan, sumber_database, waktu_load) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_fact, (wajib_pajak_key, objek_pajak_key, id_kategori, waktu_key, id_tagihan, tahun_pajak, nominal_tagihan, tanggal_jatuh_tempo, status_tagihan, sumber_db, waktu_load))

            if (i + 1) % 100 == 0:
                print(f"Progres: {i + 1} / {total_data} data disisipkan...")

        conn.commit()
        print("\nSelesai! Data berhasil disuntikkan dengan Kode Wilayah 2 digit yang sinkron.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Koneksi database ditutup.")

if __name__ == "__main__":
    main()