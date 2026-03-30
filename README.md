# ☀️ Solar Energy Justice Index (SEJI)
### A Nationwide WebGIS Platform for Mapping Solar Potential and Energy Equity in Indonesia's 3T Regions

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit)
![Folium](https://img.shields.io/badge/Folium-0.16+-77B829?style=for-the-badge)
![Plotly](https://img.shields.io/badge/Plotly-5.19+-3F4F75?style=for-the-badge&logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Democratizing Energy Transition · Inclusive Access · Decentralized Ownership**

</div>

---

## 🎯 Overview

**Solar Energy Justice Index (SEJI)** adalah platform WebGIS interaktif berbasis Streamlit yang mengintegrasikan **potensi energi surya** dengan **indikator keadilan energi** untuk mengidentifikasi wilayah prioritas pengembangan Pembangkit Listrik Tenaga Surya (PLTS) di Indonesia, khususnya wilayah **3T (Tertinggal, Terdepan, Terluar)**.

### Latar Belakang

> *"Transisi energi tidak hanya berfokus pada pengurangan emisi karbon, tetapi juga harus memperhatikan aspek keadilan energi."* — Sovacool et al., 2017

Indonesia memiliki rata-rata radiasi matahari **4–5.5 kWh/m²/hari**, namun ketimpangan akses energi di wilayah 3T masih tinggi. SEJI hadir sebagai solusi analitik berbasis data untuk mendukung **perencanaan energi yang inklusif dan berbasis bukti**.

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 🏠 **Dashboard** | KPI nasional, top 10 provinsi prioritas, distribusi per kepulauan |
| 🗺️ **WebGIS Map** | Peta interaktif Folium dengan heatmap, marker cluster, multi-layer |
| 📊 **SEJI Analysis** | Analisis komponen AHP, distribusi spasial, korelasi antar variabel |
| ⚙️ **SEJI Calculator** | Kalkulator interaktif untuk menghitung SEJI Score wilayah custom |
| 📋 **Data Explorer** | Tabel lengkap dengan filter, scatter matrix, download CSV/JSON |
| ℹ️ **Metodologi** | Kerangka SEJI, sumber data, formula, matriks AHP |

---

## 🗂️ Struktur Proyek

```
seji_project/
├── app.py                    # Entry point Streamlit
├── requirements.txt          # Dependencies
├── .streamlit/
│   └── config.toml          # Tema & konfigurasi
├── pages/
│   ├── dashboard.py         # Halaman Dashboard
│   ├── webgis.py            # Halaman Peta Interaktif
│   ├── seji_analysis.py     # Analisis Komponen
│   ├── calculator.py        # Kalkulator SEJI
│   ├── data_explorer.py     # Eksplorasi Data
│   └── methodology.py       # Metodologi
└── utils/
    └── data.py              # Data generator & shared utilities
```

---

## 🧮 Metodologi SEJI

### Formula Indeks Komposit

```
SEJI = w₁·Solar_norm + w₂·(1−EnergyAccess_norm) + w₃·Poverty_norm
       + w₄·Population_norm + w₅·Remoteness_norm
```

Dimana setiap variabel dinormalisasi: `X_norm = (X − X_min) / (X_max − X_min)`

### Bobot AHP (Analytical Hierarchy Process)

| Parameter | Bobot (wᵢ) | Sumber Data | Resolusi |
|-----------|-----------|-------------|----------|
| ☀️ Solar Radiation | **0.30** | NASA POWER / Global Solar Atlas | ±1 km |
| ⚡ Energy Access (inv.) | **0.30** | VIIRS Day-Night Band | 500 m |
| 💸 Poverty Rate | **0.20** | BPS Indonesia | Administratif |
| 👥 Population Density | **0.10** | WorldPop | 100 m |
| 🌐 Remoteness | **0.10** | OSM + PLN | Vektor |

### Klasifikasi Prioritas

| Score | Kategori | Rekomendasi |
|-------|----------|-------------|
| > 75 | 🔴 **Critical** | Intervensi PLTS off-grid segera |
| 55–75 | 🟡 **High** | Perencanaan PLTS jangka pendek (1–2 tahun) |
| 33–55 | 🟢 **Moderate** | Program PLTS bersubsidi jangka menengah |
| < 33 | ⚪ **Low** | Optimasi PLTS rooftop existing |

---

## 🚀 Cara Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/USERNAME/seji-indonesia.git
cd seji-indonesia
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
# atau
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi

```bash
streamlit run app.py
```

Buka browser di `http://localhost:8501`

---

## 🌐 Deploy ke Streamlit Cloud

1. Push ke GitHub repository
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. Connect ke repo ini
4. Set **Main file path**: `app.py`
5. Klik **Deploy!**

---

## 📊 Data Sources

- **NASA POWER** — Global Horizontal Irradiance (GHI)
- **VIIRS Day-Night Band** — Nighttime Light sebagai proksi akses listrik
- **WorldPop** — Gridded Population Density
- **BPS Indonesia** — Poverty Rate & Socioeconomic Data
- **OpenStreetMap / PLN** — Jaringan Listrik
- **BIG / GADM** — Batas Administrasi
- **MODIS MOD06** — Cloud Fraction

> ⚠️ Data yang ditampilkan saat ini adalah **data simulasi representatif** untuk demonstrasi platform. Integrasi data nyata dapat dilakukan melalui Google Earth Engine API.

---

## 🔮 Roadmap

- [ ] Integrasi Google Earth Engine API (data real-time)
- [ ] Analisis level kabupaten/kota
- [ ] Simulasi kapasitas PLTS & estimasi CO₂ offset
- [ ] Export peta sebagai GeoJSON/Shapefile
- [ ] Dashboard multi-bahasa (ID/EN)
- [ ] Integrasi data BMKG untuk irradiance forecast

---

## 📚 Referensi

- IRENA. (2023). *Renewable Power Generation Costs in 2022*.
- ESDM. (2022). *Rencana Umum Energi Nasional (RUEN)*.
- Bappenas. (2021). *Percepatan Pembangunan Daerah Tertinggal*.
- Sovacool, B.K., et al. (2017). *Energy Justice: A Conceptual Review*. Energy Research & Social Science.
- Kumar, M., et al. (2020). *GIS-based multi-criteria approach for solar energy potential analysis*.

---

## 📄 Lisensi

MIT License — lihat [LICENSE](LICENSE) untuk detail.

---

<div align="center">
    Dibuat dengan ❤️ untuk mendukung <strong>Transisi Energi Berkeadilan Indonesia</strong><br>
    <em>"No one left behind in the energy transition"</em>
</div>
