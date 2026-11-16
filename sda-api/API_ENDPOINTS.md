# 📡 SDA Lingkungan API - Endpoint Reference

REST API read-only untuk database `db_sda_lingkungan` (Sumber Daya Alam & Lingkungan).

---

## 🔗 Base URL

```
http://localhost:8002
```

Ganti `localhost` dengan IP komputer jika diakses dari mesin lain.

---

## 🏥 Health & Metadata

### GET / (Root)
Cek status service.

**Request:**
```
GET /
```

**Response (200 OK):**
```json
{
  "success": true,
  "service": "REST API db_sda_lingkungan",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### GET /health
Cek koneksi database.

**Request:**
```
GET /health
```

**Response (200 OK):**
```json
{
  "success": true,
  "database": "db_sda_lingkungan",
  "status": "connected"
}
```

**Response (503 Service Unavailable):**
```json
{
  "success": false,
  "database": "db_sda_lingkungan",
  "status": "disconnected",
  "error": "Connection refused"
}
```

---

### GET /api/tables
List semua endpoint dan tabel terkait.

**Request:**
```
GET /api/tables
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "endpoint": "/api/wilayah",
      "table": "master_wilayah"
    },
    {
      "endpoint": "/api/fasilitas-sampah",
      "table": "master_fasilitas_sampah"
    },
    {
      "endpoint": "/api/perusahaan",
      "table": "master_perusahaan"
    },
    {
      "endpoint": "/api/stasiun-pantau",
      "table": "master_stasiun_pantau"
    },
    {
      "endpoint": "/api/izin-lingkungan",
      "table": "izin_lingkungan"
    },
    {
      "endpoint": "/api/kualitas-air-sungai",
      "table": "kualitas_air_sungai"
    },
    {
      "endpoint": "/api/kualitas-udara",
      "table": "kualitas_udara"
    },
    {
      "endpoint": "/api/timbulan-sampah",
      "table": "timbulan_sampah"
    },
    {
      "endpoint": "/api/tutupan-lahan-rth",
      "table": "tutupan_lahan_rth"
    }
  ]
}
```

---

## 📊 Data Endpoints - Master Tables

### GET /api/wilayah
Data master wilayah (desa, kecamatan, kabupaten, provinsi).

**Request:**
```
GET /api/wilayah?page=1&limit=100
```

**Parameters:**
- `page` (optional, default: 1) - Nomor halaman
- `limit` (optional, default: 100) - Records per page (max: 1000)

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_desa": "01011",
      "nama_desa": "Desa Peuniti",
      "id_kecamatan": "0101",
      "nama_kecamatan": "Kecamatan Baiturrahman",
      "id_kabupaten_kota": "01",
      "nama_kabupaten_kota": "Kota Banda Aceh",
      "nama_provinsi": "Aceh"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 133,
    "total_pages": 2,
    "has_next": true
  }
}
```

**Sample Data:**
- Total Records: 133 desa
- Coverage: Banda Aceh, Sabang, Langsa, Lhokseumawe, Aceh Barat, dll

---

### GET /api/fasilitas-sampah
Data master fasilitas pengelolaan sampah (TPA, TPS 3R, Bank Sampah).

**Request:**
```
GET /api/fasilitas-sampah?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_fasilitas": "FAS-002",
      "nama_fasilitas": "Fasilitas Bank Sampah Desa Meulaboh Jaya",
      "jenis_fasilitas": "bank sampah",
      "id_desa": "07014",
      "nama_desa": "Desa Meulaboh Jaya",
      "kapasitas_maksimal_ton": 1417.58,
      "status_operasional": "Aktif"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 22,
    "total_pages": 1,
    "has_next": false
  }
}
```

**Sample Data:**
- Total Records: 22 fasilitas
- Jenis: TPA, TPS 3R, Bank Sampah
- Status: Aktif / Non-Aktif

---

### GET /api/perusahaan
Data master perusahaan yang perlu izin lingkungan.

**Request:**
```
GET /api/perusahaan?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_perusahaan": "PT-002",
      "nama_perusahaan": "PT. Aceh Mandiri 2",
      "bidang_usaha": "Agribisnis",
      "alamat_lengkap": "Jalan Utama Desa Banda Raya No. 2",
      "id_desa": "07122",
      "nama_desa": "Desa Banda Raya",
      "kontak_perusahaan": "08123456702"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 15,
    "total_pages": 1,
    "has_next": false
  }
}
```

**Sample Data:**
- Total Records: 15 perusahaan
- Bidang Usaha: Agribisnis, PLTU/Energi, Pertambangan, Pengolahan Kayu, Pabrik Kopi

---

### GET /api/stasiun-pantau
Data master stasiun pemantauan lingkungan (air sungai, udara).

**Request:**
```
GET /api/stasiun-pantau?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_stasiun": "ST-001",
      "nama_stasiun": "Stasiun Desa Tanjong Layeu",
      "jenis_stasiun": "Air Sungai",
      "id_desa": "09041",
      "nama_desa": "Desa Tanjong Layeu",
      "koordinat_gps": "2.8395,97.5629",
      "status_aktif": "1"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 27,
    "total_pages": 1,
    "has_next": false
  }
}
```

**Sample Data:**
- Total Records: 27 stasiun
- Jenis: Air Sungai, Udara
- Status: Aktif (1/yes/Aktif) / Non-Aktif (0/no/Non-Aktif)

---

## 📈 Data Endpoints - Transactional Tables

### GET /api/izin-lingkungan
Data izin lingkungan perusahaan.

**Request:**
```
GET /api/izin-lingkungan?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_izin": "IZN-001",
      "id_perusahaan": "PT-010",
      "nama_perusahaan": "PT. Aceh Mandiri 10",
      "jenis_izin": "AMDAL",
      "tanggal_terbit": "2022-03-15",
      "tanggal_berlaku_hingga": "2027-03-15",
      "status_izin": "Aktif",
      "instansi_penerbit": "Dinas Lingkungan Hidup Aceh"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 45,
    "total_pages": 1,
    "has_next": false
  }
}
```

**Sample Data:**
- Total Records: 45 izin
- Jenis Izin: AMDAL, UKL-UPL, SPPL
- Status: Aktif, Berlaku, Kadaluarsa

---

### GET /api/kualitas-air-sungai
Data monitoring kualitas air sungai.

**Request:**
```
GET /api/kualitas-air-sungai?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_pengukuran": "AIR-001",
      "id_stasiun": "ST-001",
      "nama_stasiun": "Stasiun Desa Tanjong Layeu",
      "tanggal_pengukuran": "2025-01-15",
      "parameter_ph": 7.2,
      "parameter_do_mg_per_l": 6.5,
      "parameter_bod_mg_per_l": 3.2,
      "parameter_cod_mg_per_l": 15.8,
      "parameter_tss_mg_per_l": 45.3,
      "status_kualitas": "Baik"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 81,
    "total_pages": 1,
    "has_next": false
  }
}
```

**Sample Data:**
- Total Records: 81 pengukuran
- Parameter: pH, DO, BOD, COD, TSS
- Status: Baik, Sedang, Buruk

---

### GET /api/kualitas-udara
Data monitoring kualitas udara.

**Request:**
```
GET /api/kualitas-udara?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_pengukuran": "UDR-001",
      "id_stasiun": "ST-003",
      "nama_stasiun": "Stasiun Desa Sabang Kota",
      "tanggal_pengukuran": "2025-01-10",
      "parameter_pm25_ug_per_m3": 35.2,
      "parameter_pm10_ug_per_m3": 68.5,
      "parameter_so2_ug_per_m3": 12.3,
      "parameter_no2_ug_per_m3": 28.4,
      "parameter_co_ug_per_m3": 850.6,
      "parameter_o3_ug_per_m3": 45.7,
      "indeks_standar_pencemar_udara": 58,
      "kategori_ispu": "Sedang"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 81,
    "total_pages": 1,
    "has_next": false
  }
}
```

**Sample Data:**
- Total Records: 81 pengukuran
- Parameter: PM2.5, PM10, SO2, NO2, CO, O3
- Kategori ISPU: Baik, Sedang, Tidak Sehat

---

### GET /api/timbulan-sampah
Data timbulan sampah per desa.

**Request:**
```
GET /api/timbulan-sampah?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_timbulan": "SMH-001",
      "id_desa": "01011",
      "nama_desa": "Desa Peuniti",
      "id_fasilitas": "FAS-034",
      "nama_fasilitas": "Fasilitas TPA Desa Peuniti",
      "tanggal_pencatatan": "2025-01-15",
      "volume_sampah_ton": 3.5,
      "jenis_sampah_dominan": "Organik",
      "metode_pengolahan": "TPA"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 66,
    "total_pages": 1,
    "has_next": false
  }
}
```

**Sample Data:**
- Total Records: 66 catatan
- Jenis Sampah: Organik, Anorganik, B3
- Metode: TPA, TPS 3R, Bank Sampah, Composting

---

### GET /api/tutupan-lahan-rth
Data tutupan lahan ruang terbuka hijau (RTH).

**Request:**
```
GET /api/tutupan-lahan-rth?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_tutupan": "RTH-001",
      "id_desa": "01011",
      "nama_desa": "Desa Peuniti",
      "tahun": 2024,
      "luas_total_desa_ha": 250.5,
      "luas_rth_ha": 75.2,
      "persentase_rth": 30.02,
      "jenis_tutupan": "Hutan Kota"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 40,
    "total_pages": 1,
    "has_next": false
  }
}
```

**Sample Data:**
- Total Records: 40 catatan
- Jenis Tutupan: Hutan Kota, Taman, Jalur Hijau, Kebun

---

## 📋 Query Parameters

### page
Nomor halaman hasil query.

**Type**: `integer`  
**Default**: `1`  
**Min**: `1`  
**Max**: Unlimited (tergantung total records)

**Examples:**
```
?page=1      # Halaman pertama
?page=5      # Halaman ke-5
```

---

### limit
Jumlah records per halaman.

**Type**: `integer`  
**Default**: `100`  
**Min**: `1`  
**Max**: `1000`

**Examples:**
```
?limit=10         # 10 records per page
?limit=100        # 100 records per page (default)
?limit=500        # 500 records per page
?limit=1000       # 1000 records per page (max)
```

---

## 🔄 Pagination

Semua endpoint mendukung pagination otomatis.

### Response Structure

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 300,
    "total_pages": 3,
    "has_next": true
  }
}
```

### Fields

- `current_page` - Halaman saat ini
- `per_page` - Records per halaman
- `total` - Total records di database
- `total_pages` - Total halaman (ceil(total / per_page))
- `has_next` - Apakah ada halaman berikutnya

### Auto-Pagination Example (Python)

```python
page = 1
while True:
    response = requests.get(
        f"http://localhost:8002/api/wilayah?page={page}&limit=100"
    )
    data = response.json()
    
    for record in data['data']:
        print(record)
    
    if not data['pagination']['has_next']:
        break
    
    page += 1
```

---

## ❌ Error Responses

### 404 - Invalid Endpoint

**Request:**
```
GET /api/invalid-endpoint
```

**Response:**
```json
{
  "success": false,
  "error": "Endpoint 'invalid-endpoint' tidak tersedia.",
  "available_endpoints": [
    "wilayah",
    "fasilitas-sampah",
    "perusahaan",
    "stasiun-pantau",
    "izin-lingkungan",
    "kualitas-air-sungai",
    "kualitas-udara",
    "timbulan-sampah",
    "tutupan-lahan-rth"
  ]
}
```

---

### 500 - Database Error

**Response:**
```json
{
  "success": false,
  "error": "Database error",
  "message": "Connection failed"
}
```

---

## 🧪 Testing Examples

### Using curl

```bash
# Health check
curl http://localhost:8002/health

# Get wilayah
curl "http://localhost:8002/api/wilayah?page=1&limit=5"

# Get kualitas udara
curl "http://localhost:8002/api/kualitas-udara?page=1&limit=100"
```

### Using PowerShell

```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:8002/health" -UseBasicParsing

# Get fasilitas-sampah
Invoke-WebRequest -Uri "http://localhost:8002/api/fasilitas-sampah?page=1&limit=5" -UseBasicParsing | ConvertFrom-Json
```

### Using Python

```python
import requests

# Simple fetch
response = requests.get("http://localhost:8002/api/wilayah?page=1&limit=5")
data = response.json()
print(data['data'])

# With error handling
try:
    response = requests.get("http://localhost:8002/api/timbulan-sampah")
    if response.status_code == 200:
        data = response.json()
        print(f"Total records: {data['pagination']['total']}")
except Exception as e:
    print(f"Error: {e}")
```

---

## 🔐 Security Notes

- ✅ **Read-only** - GET endpoints hanya
- ✅ **CORS enabled** - Dapat diakses dari cross-origin (dev)
- ✅ **No auth required** - Cocok untuk local/internal use
- ✅ **SQL injection safe** - Parameterized queries
- ✅ **Rate limiting** - Built-in page limit (max 1000)

---

## 💡 Best Practices

1. **Always check `has_next`** untuk pagination
2. **Handle errors** dengan check `success` field
3. **Use reasonable limit** (100-500) untuk performance
4. **Cache responses** untuk production
5. **Add retry logic** untuk network resilience

---

## 📞 Support

Untuk issue atau pertanyaan:
- Check `README.md` untuk setup
- Lihat contoh di dokumentasi Swagger: `http://localhost:8002/docs`

---

**Last Updated**: 16 November 2026  
**API Version**: 1.0.0  
**Database**: db_sda_lingkungan  
**Status**: ✅ Production Ready
