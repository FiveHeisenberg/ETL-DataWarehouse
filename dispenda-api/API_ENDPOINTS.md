# 📡 Dispenda API - Endpoint Reference

REST API read-only untuk database `db_dispenda` (Pajak Daerah).

---

## 🔗 Base URL

```
http://localhost:8000
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
  "service": "REST API db_dispenda",
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
  "database": "db_dispenda",
  "status": "connected"
}
```

**Response (503 Service Unavailable):**
```json
{
  "success": false,
  "database": "db_dispenda",
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
      "endpoint": "/api/kategori-pajak",
      "table": "tb_kategori_pajak"
    },
    {
      "endpoint": "/api/metode-bayar",
      "table": "tb_metode_bayar"
    },
    {
      "endpoint": "/api/wajib-pajak",
      "table": "tb_wajib_pajak"
    },
    {
      "endpoint": "/api/objek-pajak",
      "table": "tb_objek_pajak"
    },
    {
      "endpoint": "/api/tagihan",
      "table": "tb_tagihan"
    },
    {
      "endpoint": "/api/pembayaran",
      "table": "tb_pembayaran"
    }
  ]
}
```

---

## 📊 Data Endpoints

### GET /api/kategori-pajak
Data kategori / jenis pajak.

**Request:**
```
GET /api/kategori-pajak?page=1&limit=100
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
      "id_kategori": 1,
      "nama_pajak": "Pajak Kendaraan Bermotor (Roda 2)",
      "tarif_persentase": 1.5
    },
    {
      "id_kategori": 2,
      "nama_pajak": "Pajak Kendaraan Bermotor (Roda 4)",
      "tarif_persentase": 2.0
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 5,
    "total_pages": 1,
    "has_next": false
  }
}
```

**Sample Data:**
- Total Records: 5
- Sample: PBB, BPHTB, Pajak Air, dll

---

### GET /api/metode-bayar
Data metode pembayaran.

**Request:**
```
GET /api/metode-bayar?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_metode_bayar": 1,
      "metode_bayar": "Transfer Bank"
    },
    {
      "id_metode_bayar": 2,
      "metode_bayar": "Bayar di Loket"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 12,
    "total_pages": 1,
    "has_next": false
  }
}
```

**Sample Data:**
- Total Records: 12
- Sample: Transfer, Bayar Loket, E-Wallet, dll

---

### GET /api/wajib-pajak
Data wajib pajak.

**Request:**
```
GET /api/wajib-pajak?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "nik_wp": "1101011234567890",
      "nama_lengkap": "Nama Wajib Pajak",
      "alamat": "Jl. Contoh No. 1",
      "telepon": "0812345678",
      "email": "wp@example.com",
      "status_aktif": "Aktif"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 1794,
    "total_pages": 18,
    "has_next": true
  }
}
```

**Sample Data:**
- Total Records: 1,794
- Paginasi: 18 halaman dengan 100 record/page

---

### GET /api/objek-pajak
Data objek pajak.

**Request:**
```
GET /api/objek-pajak?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_objek": "OBJ00001",
      "nik_wp": "1101011234567890",
      "jenis_objek": "Kendaraan Bermotor",
      "lokasi": "Banda Aceh",
      "nilai_objek": 250000000.00
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 1813,
    "total_pages": 19,
    "has_next": true
  }
}
```

**Sample Data:**
- Total Records: 1,813
- Terhubung ke wajib pajak

---

### GET /api/tagihan
Data tagihan pajak.

**Request:**
```
GET /api/tagihan?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_tagihan": "TAG00001",
      "id_objek": "OBJ00001",
      "tahun_pajak": 2025,
      "masa_pajak": "01",
      "jumlah_tagihan": 1500000.00,
      "status_tagihan": "Baru",
      "tanggal_tagihan": "2025-01-15"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 1813,
    "total_pages": 19,
    "has_next": true
  }
}
```

**Sample Data:**
- Total Records: 1,813
- Terhubung ke objek pajak

---

### GET /api/pembayaran
Data pembayaran pajak.

**Request:**
```
GET /api/pembayaran?page=1&limit=100
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id_pembayaran": "PMT00001",
      "id_tagihan": "TAG00001",
      "tanggal_pembayaran": "2025-02-10",
      "jumlah_pembayaran": 1500000.00,
      "metode_bayar": "Transfer Bank",
      "status_pembayaran": "Lunas",
      "denda": 0.00,
      "total_bayar": 1500000.00
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 831,
    "total_pages": 9,
    "has_next": true
  }
}
```

**Sample Data:**
- Total Records: 831
- Terhubung ke tagihan

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
?page=100    # Halaman ke-100
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
    "total": 5000,
    "total_pages": 50,
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
        f"http://localhost:8000/api/wajib-pajak?page={page}&limit=100"
    )
    data = response.json()
    
    # Process records
    for record in data['data']:
        print(record)
    
    # Check if there's next page
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
    "kategori-pajak",
    "metode-bayar",
    "wajib-pajak",
    "objek-pajak",
    "tagihan",
    "pembayaran"
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
curl http://localhost:8000/health

# Get kategori-pajak
curl "http://localhost:8000/api/kategori-pajak?page=1&limit=5"

# Get with large limit
curl "http://localhost:8000/api/wajib-pajak?page=1&limit=500"

# Get specific page
curl "http://localhost:8000/api/pembayaran?page=2&limit=100"
```

### Using PowerShell

```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Get kategori-pajak
Invoke-WebRequest -Uri "http://localhost:8000/api/kategori-pajak?page=1&limit=5" -UseBasicParsing | ConvertFrom-Json
```

### Using Python

```python
import requests

# Simple fetch
response = requests.get("http://localhost:8000/api/kategori-pajak?page=1&limit=5")
data = response.json()
print(data['data'])

# With error handling
try:
    response = requests.get("http://localhost:8000/api/wajib-pajak")
    if response.status_code == 200:
        data = response.json()
        print(f"Total records: {data['pagination']['total']}")
except Exception as e:
    print(f"Error: {e}")
```

---

## 📈 Data Dictionary

### tb_kategori_pajak

| Column | Type | Description |
|--------|------|-------------|
| id_kategori | INT | Primary Key |
| nama_pajak | VARCHAR(100) | Nama jenis pajak |
| tarif_persentase | DECIMAL | Tarif pajak dalam % |

---

### tb_metode_bayar

| Column | Type | Description |
|--------|------|-------------|
| id_metode_bayar | INT | Primary Key |
| metode_bayar | VARCHAR(50) | Nama metode pembayaran |

---

### tb_wajib_pajak

| Column | Type | Description |
|--------|------|-------------|
| nik_wp | VARCHAR(20) | Primary Key (NIK) |
| nama_lengkap | VARCHAR(200) | Nama wajib pajak |
| alamat | VARCHAR | Alamat |
| telepon | VARCHAR | Nomor telepon |
| email | VARCHAR | Email |
| status_aktif | VARCHAR | Status aktif/tidak |

---

### tb_objek_pajak

| Column | Type | Description |
|--------|------|-------------|
| id_objek | VARCHAR(20) | Primary Key |
| nik_wp | VARCHAR(20) | FK to wajib_pajak |
| jenis_objek | VARCHAR | Jenis objek pajak |
| lokasi | VARCHAR | Lokasi objek |
| nilai_objek | DECIMAL | Nilai objek |

---

### tb_tagihan

| Column | Type | Description |
|--------|------|-------------|
| id_tagihan | VARCHAR(20) | Primary Key |
| id_objek | VARCHAR(20) | FK to objek_pajak |
| tahun_pajak | INT | Tahun |
| masa_pajak | VARCHAR | Periode |
| jumlah_tagihan | DECIMAL | Jumlah tagihan |
| status_tagihan | VARCHAR | Status |
| tanggal_tagihan | DATE | Tanggal tagihan |

---

### tb_pembayaran

| Column | Type | Description |
|--------|------|-------------|
| id_pembayaran | VARCHAR(20) | Primary Key |
| id_tagihan | VARCHAR(20) | FK to tagihan |
| tanggal_pembayaran | DATE | Tanggal pembayaran |
| jumlah_pembayaran | DECIMAL | Jumlah bayar |
| metode_bayar | VARCHAR | Metode pembayaran |
| status_pembayaran | VARCHAR | Status |
| denda | DECIMAL | Denda jika ada |
| total_bayar | DECIMAL | Total termasuk denda |

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
- Check `TAHAP_1_VERIFIKASI.md` untuk test results
- Lihat contoh `../CONTOH_FETCH_API.py` untuk implementation

---

**Last Updated**: 14 November 2026  
**API Version**: 1.0.0  
**Database**: db_dispenda  
**Status**: ✅ Production Ready
