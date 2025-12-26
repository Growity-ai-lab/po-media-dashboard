[README.md](https://github.com/user-attachments/files/24347142/README.md)
# Petrol Ofisi Premium Market - Medya Planlama Dashboard

Meta Marketing API entegrasyonlu, TDY küme analizi tabanlı medya planlama aracı.

## 🚀 Hızlı Kurulum (Streamlit Cloud - Ücretsiz)

### Adım 1: GitHub Repo Oluştur
1. GitHub'da yeni repo oluştur: `po-media-dashboard`
2. Bu dosyaları yükle:
   - `streamlit_app.py`
   - `requirements.txt`

### Adım 2: Streamlit Cloud'a Deploy
1. [share.streamlit.io](https://share.streamlit.io) adresine git
2. GitHub hesabınla giriş yap
3. "New app" tıkla
4. Repo'yu seç: `po-media-dashboard`
5. Main file: `streamlit_app.py`
6. "Deploy" tıkla

### Adım 3: Kullan
- Dashboard URL'in hazır: `https://KULLANICI-po-media-dashboard.streamlit.app`
- Sol panelden Meta API credentials'ını gir
- Bağlan ve gerçek reach verilerini al!

---

## 💻 Lokal Kurulum

```bash
# Repo'yu klonla
git clone https://github.com/KULLANICI/po-media-dashboard.git
cd po-media-dashboard

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Çalıştır
streamlit run streamlit_app.py
```

Browser'da açılır: `http://localhost:8501`

---

## 🔐 Meta API Kurulumu

### Access Token Alma
1. [developers.facebook.com](https://developers.facebook.com) → My Apps
2. Create App → Business type
3. Add Products → Marketing API
4. Tools → Graph API Explorer
5. Permissions ekle:
   - `ads_read`
   - `ads_management`
   - `business_management`
6. Generate Access Token → Kopyala

### Ad Account ID
- Business Manager → Business Settings → Ad Accounts
- Format: `act_XXXXXXXXXX`

---

## 📊 Özellikler

- ✅ TDY Küme Analizi (5 küme)
- ✅ Meta Marketing API Reach Estimation
- ✅ Interest Search
- ✅ Targeting Spec Export (Meta + TikTok)
- ✅ Bütçe Planlama (Geleneksel + Dijital)
- ✅ Grafikler ve Tablolar
- ✅ Excel/JSON Export

---

## 📁 Dosya Yapısı

```
po-media-dashboard/
├── streamlit_app.py    # Ana uygulama
├── requirements.txt    # Python bağımlılıkları
└── README.md          # Bu dosya
```

---

## 🎯 Kullanım

1. **Sol Panel:** API credentials ve bütçe ayarları
2. **Genel Bakış:** Küme seçimi ve karşılaştırma
3. **Reach & CPM:** API'den reach tahmini al
4. **Targeting:** JSON spec export
5. **Bütçe Detay:** Kanal bazlı dağılım

---

## 📞 Destek

Sorular için: [GitHub Issues](https://github.com/KULLANICI/po-media-dashboard/issues)
