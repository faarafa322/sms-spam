# Tutorial Deployment SMS Spam Classifier

Panduan lengkap untuk menjalankan aplikasi SMS Spam Classifier di localhost dan production menggunakan Docker.

---

## 📋 Prasyarat

- Python 3.11+
- Git
- Docker (untuk production)
- Akun GitHub (untuk deployment)

---

## 🏠 Deployment di Localhost

### 1. Clone Repository

```bash
git clone https://github.com/faarafa322/sms-spam.git
cd sms-spam
```

### 2. Setup Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download Dataset (Opsional - Jika Ingin Training Ulang)

```bash
python train/download_dataset.py
```

File akan tersimpan di: `train/sms_spam.csv`

### 5. Training Model (Opsional - Jika Ingin Training Ulang)

```bash
python train/train.py
```

Output:
- `train/metrics_heatmap.png` - Visualisasi performa model
- `app/vectorizer.pkl` - TF-IDF vectorizer
- `app/model.pkl` - Model terbaik (berdasarkan F1-score)

**Catatan:** Jika tidak melakukan training ulang, aplikasi akan menggunakan model yang sudah ada di folder `app/`.

### 6. Jalankan API Server

```bash
cd app
uvicorn main:app --reload
```

Server akan berjalan di: http://127.0.0.1:8000

### 7. Akses Dokumentasi API

Buka browser dan akses:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

### 8. Test API

**Via Browser (Swagger UI):**
1. Buka http://127.0.0.1:8000/docs
2. Klik endpoint `/predict`
3. Klik "Try it out"
4. Masukkan text: `"Free entry in a weekly competition. Text WIN to 80086"`
5. Klik "Execute"

**Via cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/predict" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Free entry in a weekly competition. Text WIN to 80086\"}"
```

**Via Python:**
```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/predict",
    json={"text": "Free entry in a weekly competition. Text WIN to 80086"}
)
print(response.json())
```

**Expected Response:**
```json
{
  "label": "spam",
  "score": 0.9876
}
```

---

## 🐳 Deployment di Production (Docker)

### Metode 1: Docker Manual

#### 1. Build Docker Image

```bash
docker build -t sms-spam-api .
```

#### 2. Run Container

```bash
docker run -d -p 8000:8000 --name sms-spam-api sms-spam-api
```

#### 3. Test API

```bash
curl http://localhost:8000/
```

Expected response: `{"status":"ok"}`

#### 4. Stop & Remove Container

```bash
docker stop sms-spam-api
docker rm sms-spam-api
```

---

### Metode 2: Deploy ke Coolify (Recommended)

Coolify adalah platform self-hosted untuk deployment aplikasi dengan Docker.

#### 1. Push ke GitHub

Pastikan semua file sudah di-push ke repository:

```bash
git add .
git commit -m "Ready for production deployment"
git push origin main
```

**Penting:** Pastikan file `app/model.pkl` dan `app/vectorizer.pkl` sudah ter-push!

#### 2. Setup di Coolify Dashboard

1. Login ke Coolify dashboard
2. Klik **"New Resource"** → **"Application"**
3. Pilih **"Public Repository"**
4. Masukkan repository URL: `https://github.com/faarafa322/sms-spam`
5. Branch: `main`

#### 3. Konfigurasi Build

- **Build Pack:** `Dockerfile` (auto-detect)
- **Base Directory:** `/`
- **Dockerfile Location:** `/Dockerfile`
- **Docker Build Stage Target:** (kosongkan)

#### 4. Konfigurasi Network

- **Ports Exposes:** `8000`
- **Ports Mappings:** (kosongkan - auto)

#### 5. Konfigurasi Domain

- **Domains:** Masukkan domain/subdomain (contoh: `rafa.ohlc.dev`)
- **Direction:** `Allow www & non-www`

#### 6. Deploy

Klik **"Save"** lalu **"Deploy"**

Coolify akan:
1. Clone repository dari GitHub
2. Build Docker image
3. Run container
4. Generate SSL certificate (Let's Encrypt)
5. Setup reverse proxy

#### 7. Monitoring

- **Logs:** Tab "Logs" untuk melihat output container
- **Status:** Harus menunjukkan "Running" (hijau)
- **Health Check:** Otomatis check setiap 30 detik

#### 8. Test Production API

```bash
curl https://rafa.ohlc.dev/
```

Expected response: `{"status":"ok"}`

**Test Predict Endpoint:**
```bash
curl -X POST "https://rafa.ohlc.dev/predict" \
  -H "Content-Type: application/json" \
  -d '{"text":"Free entry in a weekly competition. Text WIN to 80086"}'
```

---

## 🔧 Troubleshooting

### Error: "Model artifacts not found"

**Penyebab:** File `model.pkl` atau `vectorizer.pkl` tidak ada.

**Solusi:**
```bash
# Training ulang
python train/download_dataset.py
python train/train.py

# Atau pastikan file sudah di-push ke GitHub
git add app/model.pkl app/vectorizer.pkl
git commit -m "Add model artifacts"
git push origin main
```

### Error: "Invalid SSL certificate" (Cloudflare)

**Penyebab:** SSL mode di Cloudflare tidak sesuai dengan konfigurasi server.

**Solusi:**
1. Buka Cloudflare Dashboard
2. **SSL/TLS** → **Overview**
3. Ubah **Encryption mode** ke `Full` (bukan Full Strict)
4. Tunggu 1-2 menit

### Error: Port sudah digunakan

**Solusi:**
```bash
# Cari process yang menggunakan port 8000
# Windows:
netstat -ano | findstr :8000

# Kill process (ganti PID dengan nomor yang muncul)
taskkill /PID <PID> /F

# Linux/macOS:
lsof -ti:8000 | xargs kill -9
```

### Container tidak bisa start

**Cek logs:**
```bash
docker logs sms-spam-api
```

**Rebuild image:**
```bash
docker build --no-cache -t sms-spam-api .
docker run -d -p 8000:8000 --name sms-spam-api sms-spam-api
```

---

## 📊 Struktur Project

```
sms-spam/
├── app/
│   ├── main.py              # FastAPI application
│   ├── model.pkl            # Trained model
│   ├── vectorizer.pkl       # TF-IDF vectorizer
│   └── requirements.txt     # App dependencies
├── train/
│   ├── download_dataset.py  # Download UCI dataset
│   ├── train.py             # Training script
│   ├── sms_spam.csv         # Dataset (after download)
│   └── metrics_heatmap.png  # Model comparison
├── Dockerfile               # Docker configuration
├── .dockerignore           # Docker ignore rules
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
```

---

## 🚀 Update Production

Jika ada perubahan code:

```bash
# 1. Commit & push changes
git add .
git commit -m "Update: description"
git push origin main

# 2. Di Coolify dashboard
# Klik "Redeploy" atau tunggu auto-deploy (jika enabled)
```

---

## 📝 Catatan Penting

1. **Model Files:** File `model.pkl` dan `vectorizer.pkl` harus ada di folder `app/` sebelum deployment
2. **Port:** Aplikasi menggunakan port `8000` secara default
3. **Environment:** Production menggunakan model yang sudah di-training, tidak perlu training ulang
4. **SSL:** Jika menggunakan Cloudflare, gunakan mode `Full` untuk SSL/TLS
5. **Health Check:** API memiliki endpoint `/` untuk health check

---

## 🔗 Resources

- **Repository:** https://github.com/faarafa322/sms-spam
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Coolify Docs:** https://coolify.io/docs
- **Docker Docs:** https://docs.docker.com/

---

## 📧 Support

Jika ada pertanyaan atau masalah, silakan buat issue di GitHub repository.
