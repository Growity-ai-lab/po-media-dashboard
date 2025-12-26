"""
Petrol Ofisi Premium Market - Medya Planlama Dashboard
Streamlit + Meta Marketing API
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =============================================
# Sayfa Ayarları
# =============================================
st.set_page_config(
    page_title="PO Premium Market - Medya Planlama",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF6B00, #FFB800);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #64748b;
        font-size: 1rem;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b, #334155);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #475569;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #FF6B00, #FFB800);
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# TDY Küme Verileri
# =============================================
KUME_DATA = {
    "Yeni Orta Sınıf": {
        "premium_skor": 61.4,
        "populasyon": 13.81,
        "ortalama_gelir": 92007,
        "modern_yasam": 57.0,
        "universite": 50.5,
        "netflix": 42.2,
        "instagram_yogun": 42.7,
        "dominant_yas": "30-49",
        "kadin_oran": 53.9,
        "color": "#FF6B00",
        "meta_penetrasyon": 0.72,
        "interest_daralma": 0.35,
        "meta_targeting": {
            "age_min": 30,
            "age_max": 49,
            "genders": [1, 2],
            "geo_locations": {"countries": ["TR"], "location_types": ["home", "recent"]},
            "flexible_spec": [{
                "interests": [
                    {"id": "6003349442455", "name": "Online shopping"},
                    {"id": "6003139266461", "name": "Restaurants"},
                    {"id": "6003384248805", "name": "Netflix"},
                    {"id": "6003277229371", "name": "Family"}
                ],
                "behaviors": [{"id": "6002714895372", "name": "Engaged Shoppers"}]
            }],
            "publisher_platforms": ["facebook", "instagram"]
        },
        "mesaj": "Kalite artık herkesin hakkı"
    },
    "Kırılgan Orta Yaş": {
        "premium_skor": 64.1,
        "populasyon": 11.95,
        "ortalama_gelir": 85699,
        "modern_yasam": 59.3,
        "universite": 47.3,
        "netflix": 44.6,
        "instagram_yogun": 35.6,
        "dominant_yas": "30-49",
        "kadin_oran": 50.3,
        "color": "#FFB800",
        "meta_penetrasyon": 0.68,
        "interest_daralma": 0.38,
        "meta_targeting": {
            "age_min": 30,
            "age_max": 49,
            "genders": [1, 2],
            "geo_locations": {"countries": ["TR"], "location_types": ["home", "recent"]},
            "flexible_spec": [{
                "interests": [
                    {"id": "6003397425735", "name": "Family and relationships"},
                    {"id": "6003020834693", "name": "Parenting"},
                    {"id": "6003384248805", "name": "Netflix"},
                    {"id": "6003348604980", "name": "Health and wellness"}
                ],
                "behaviors": [
                    {"id": "6002714895372", "name": "Engaged Shoppers"},
                    {"id": "6015559470583", "name": "Parents"}
                ]
            }],
            "publisher_platforms": ["facebook", "instagram"]
        },
        "mesaj": "Ailen için en iyisi"
    },
    "Metropolün Karamsar Gençleri": {
        "premium_skor": 63.7,
        "populasyon": 15.03,
        "ortalama_gelir": 87337,
        "modern_yasam": 75.2,
        "universite": 38.6,
        "netflix": 46.7,
        "instagram_yogun": 36.2,
        "dominant_yas": "18-29",
        "kadin_oran": 56.0,
        "color": "#1E3A5F",
        "meta_penetrasyon": 0.85,
        "interest_daralma": 0.32,
        "meta_targeting": {
            "age_min": 18,
            "age_max": 29,
            "genders": [1, 2],
            "geo_locations": {"countries": ["TR"], "location_types": ["home", "recent"]},
            "flexible_spec": [{
                "interests": [
                    {"id": "6003107902433", "name": "Coffee"},
                    {"id": "6003139266461", "name": "Lifestyle"},
                    {"id": "6003348604980", "name": "Self-care"},
                    {"id": "6003384248805", "name": "Netflix"}
                ],
                "behaviors": [
                    {"id": "6002714895372", "name": "Engaged Shoppers"},
                    {"id": "6017253486583", "name": "Mobile shoppers"},
                    {"id": "6002764392172", "name": "Early technology adopters"}
                ]
            }],
            "publisher_platforms": ["facebook", "instagram"]
        },
        "mesaj": "Kaliteli = Pahalı değil"
    },
    "Kentli Dijitaller": {
        "premium_skor": 62.4,
        "populasyon": 17.92,
        "ortalama_gelir": 248844,
        "modern_yasam": 63.3,
        "universite": 36.7,
        "netflix": 48.7,
        "instagram_yogun": 31.5,
        "dominant_yas": "30-49",
        "kadin_oran": 52.9,
        "color": "#4A90A4",
        "meta_penetrasyon": 0.78,
        "interest_daralma": 0.28,
        "meta_targeting": {
            "age_min": 30,
            "age_max": 49,
            "genders": [1, 2],
            "geo_locations": {"countries": ["TR"], "location_types": ["home", "recent"]},
            "flexible_spec": [{
                "interests": [
                    {"id": "6003139266461", "name": "Travel"},
                    {"id": "6003384248805", "name": "Investment"},
                    {"id": "6003020834693", "name": "Technology"}
                ],
                "behaviors": [{"id": "6002714895372", "name": "Frequent travelers"}]
            }],
            "publisher_platforms": ["facebook", "instagram"]
        },
        "mesaj": "Zamanın değerli, kaliteniz hazır"
    },
    "Kentli Gelenekselciler": {
        "premium_skor": 58.7,
        "populasyon": 18.14,
        "ortalama_gelir": 94908,
        "modern_yasam": 64.5,
        "universite": 33.5,
        "netflix": 33.7,
        "instagram_yogun": 28.4,
        "dominant_yas": "30-49",
        "kadin_oran": 48.7,
        "color": "#6B7280",
        "meta_penetrasyon": 0.58,
        "interest_daralma": 0.42,
        "meta_targeting": {
            "age_min": 35,
            "age_max": 55,
            "genders": [1, 2],
            "geo_locations": {"countries": ["TR"], "location_types": ["home", "recent"]},
            "flexible_spec": [{
                "interests": [
                    {"id": "6003397425735", "name": "Family"},
                    {"id": "6003020834693", "name": "Home"}
                ],
                "behaviors": [{"id": "6002714895372", "name": "Engaged Shoppers"}]
            }],
            "publisher_platforms": ["facebook", "instagram"]
        },
        "mesaj": "Güvendiğin kalite"
    }
}

# Türkiye verileri
TURKIYE_DATA = {
    "toplam_nufus": 85000000,
    "meta_kullanici": 58000000,
    "yas_dagilim": {"18-29": 0.28, "30-49": 0.42, "50+": 0.30},
    "cpm": {"awareness": 25, "traffic": 35, "conversion": 55}
}

# =============================================
# Meta API Fonksiyonları
# =============================================
def get_meta_reach_estimate(access_token, ad_account_id, targeting_spec):
    """Meta Marketing API'den reach tahmini al"""
    url = f"https://graph.facebook.com/v18.0/{ad_account_id}/reachestimate"
    
    params = {
        "access_token": access_token,
        "targeting_spec": json.dumps(targeting_spec),
        "optimize_for": "REACH"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "error" in data:
            return {"error": data["error"].get("message", "API hatası")}
        
        users_lower = data.get("data", {}).get("users_lower_bound", 0)
        users_upper = data.get("data", {}).get("users_upper_bound", 0)
        
        if users_lower == 0:
            users_lower = data.get("users_lower_bound", 0)
            users_upper = data.get("users_upper_bound", 0)
        
        return {
            "reach_lower": users_lower,
            "reach_upper": users_upper,
            "reach_estimate": (users_lower + users_upper) // 2,
            "source": "api"
        }
    except Exception as e:
        return {"error": str(e)}


def search_interests(access_token, query):
    """Meta interest arama"""
    url = "https://graph.facebook.com/v18.0/search"
    
    params = {
        "access_token": access_token,
        "type": "adinterest",
        "q": query
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "error" in data:
            return {"error": data["error"].get("message", "API hatası")}
        
        return data.get("data", [])
    except Exception as e:
        return {"error": str(e)}


def test_api_connection(access_token, ad_account_id):
    """API bağlantısını test et"""
    url = f"https://graph.facebook.com/v18.0/{ad_account_id}"
    
    params = {
        "access_token": access_token,
        "fields": "name,account_status,currency"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "error" in data:
            return {"success": False, "error": data["error"].get("message", "API hatası")}
        
        return {
            "success": True,
            "name": data.get("name", "Bağlandı"),
            "currency": data.get("currency", "TRY"),
            "status": data.get("account_status", 1)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def calculate_simulated_reach(kume_name):
    """TDY verilerine dayalı simüle reach hesapla"""
    import random
    
    data = KUME_DATA[kume_name]
    kume_nufus = TURKIYE_DATA["toplam_nufus"] * (data["populasyon"] / 100)
    yas_faktoru = TURKIYE_DATA["yas_dagilim"].get(data["dominant_yas"], 0.35)
    
    reach = kume_nufus * data["meta_penetrasyon"] * yas_faktoru * data["interest_daralma"]
    reach *= (0.92 + random.random() * 0.16)
    
    return {
        "reach_lower": int(reach * 0.85),
        "reach_upper": int(reach * 1.15),
        "reach_estimate": int(reach),
        "source": "simulated"
    }


# =============================================
# Session State Başlat
# =============================================
if "api_connected" not in st.session_state:
    st.session_state.api_connected = False
if "account_name" not in st.session_state:
    st.session_state.account_name = ""
if "reach_data" not in st.session_state:
    st.session_state.reach_data = {}


# =============================================
# Sidebar - API Ayarları
# =============================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Petrol_Ofisi_logo.svg/200px-Petrol_Ofisi_logo.svg.png", width=150)
    st.markdown("### ⚙️ API Ayarları")
    
    access_token = st.text_input(
        "Access Token",
        type="password",
        value=st.session_state.get("access_token", ""),
        help="Meta Business Manager'dan alınan access token"
    )
    
    ad_account_id = st.text_input(
        "Ad Account ID",
        value=st.session_state.get("ad_account_id", "act_4309518029371350"),
        help="Format: act_XXXXXXXXX"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Bağlan", use_container_width=True):
            if access_token and ad_account_id:
                with st.spinner("Test ediliyor..."):
                    result = test_api_connection(access_token, ad_account_id)
                    if result["success"]:
                        st.session_state.api_connected = True
                        st.session_state.account_name = result["name"]
                        st.session_state.access_token = access_token
                        st.session_state.ad_account_id = ad_account_id
                        st.success(f"✅ {result['name']}")
                    else:
                        st.error(f"❌ {result['error']}")
            else:
                st.warning("Token ve Account ID gerekli")
    
    with col2:
        if st.button("🔄 Sıfırla", use_container_width=True):
            st.session_state.api_connected = False
            st.session_state.reach_data = {}
    
    # Bağlantı durumu
    if st.session_state.api_connected:
        st.success(f"🟢 Bağlı: {st.session_state.account_name}")
    else:
        st.info("🟡 Simüle mod (API bağlı değil)")
    
    st.divider()
    
    # Bütçe ayarları
    st.markdown("### 💰 Bütçe Ayarları")
    toplam_butce = st.slider("Toplam Bütçe (M TL)", 50, 500, 200, 10)
    geleneksel_oran = st.slider("Geleneksel Medya %", 20, 80, 45)
    
    geleneksel_butce = toplam_butce * geleneksel_oran / 100
    dijital_butce = toplam_butce - geleneksel_butce
    
    st.metric("Geleneksel", f"{geleneksel_butce:.1f}M TL")
    st.metric("Dijital", f"{dijital_butce:.1f}M TL")


# =============================================
# Ana İçerik
# =============================================
st.markdown('<p class="main-header">⛽ Premium Market Medya Planlama</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">TDY Küme Analizi + Meta Marketing API</p>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Genel Bakış", "🎯 Reach & CPM", "🎪 Targeting", "📈 Bütçe Detay"])

# =============================================
# Tab 1: Genel Bakış
# =============================================
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 👥 Hedef Kümeler")
        selected_kumeler = st.multiselect(
            "Küme Seçin",
            options=list(KUME_DATA.keys()),
            default=["Yeni Orta Sınıf", "Kırılgan Orta Yaş", "Metropolün Karamsar Gençleri"],
            help="Birden fazla küme seçebilirsiniz"
        )
        
        # Küme bilgileri
        for kume in selected_kumeler:
            data = KUME_DATA[kume]
            with st.expander(f"🔹 {kume}", expanded=False):
                st.write(f"**Premium Skor:** {data['premium_skor']}")
                st.write(f"**Popülasyon:** %{data['populasyon']}")
                st.write(f"**Ort. Gelir:** ₺{data['ortalama_gelir']:,}")
                st.write(f"**Yaş Grubu:** {data['dominant_yas']}")
                st.write(f"**Mesaj:** _{data['mesaj']}_")
    
    with col2:
        st.markdown("### 📊 Küme Karşılaştırma")
        
        if selected_kumeler:
            # Premium skor chart
            df_skor = pd.DataFrame([
                {"Küme": k, "Premium Skor": KUME_DATA[k]["premium_skor"], "Renk": KUME_DATA[k]["color"]}
                for k in selected_kumeler
            ])
            
            fig = px.bar(
                df_skor, x="Küme", y="Premium Skor",
                color="Küme",
                color_discrete_map={k: KUME_DATA[k]["color"] for k in selected_kumeler},
                title="Premium Skor Karşılaştırma"
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#94a3b8',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Özet metrikler
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                total_pop = sum(KUME_DATA[k]["populasyon"] for k in selected_kumeler)
                st.metric("Toplam Popülasyon", f"%{total_pop:.1f}")
            with col_b:
                avg_income = sum(KUME_DATA[k]["ortalama_gelir"] for k in selected_kumeler) / len(selected_kumeler)
                st.metric("Ort. Gelir", f"₺{avg_income:,.0f}")
            with col_c:
                avg_skor = sum(KUME_DATA[k]["premium_skor"] for k in selected_kumeler) / len(selected_kumeler)
                st.metric("Ort. Premium Skor", f"{avg_skor:.1f}")


# =============================================
# Tab 2: Reach & CPM
# =============================================
with tab2:
    st.markdown("### 🎯 Reach Estimation")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        if st.button("🔄 Tüm Reach'leri Hesapla", use_container_width=True, type="primary"):
            progress = st.progress(0)
            
            for i, kume in enumerate(selected_kumeler):
                with st.spinner(f"{kume} hesaplanıyor..."):
                    if st.session_state.api_connected:
                        # Gerçek API çağrısı
                        targeting = KUME_DATA[kume]["meta_targeting"]
                        result = get_meta_reach_estimate(
                            st.session_state.access_token,
                            st.session_state.ad_account_id,
                            targeting
                        )
                        if "error" not in result:
                            st.session_state.reach_data[kume] = result
                        else:
                            # API hatası - simüle et
                            st.session_state.reach_data[kume] = calculate_simulated_reach(kume)
                            st.warning(f"{kume}: API hatası, simüle veri kullanıldı")
                    else:
                        # Simüle reach
                        st.session_state.reach_data[kume] = calculate_simulated_reach(kume)
                
                progress.progress((i + 1) / len(selected_kumeler))
            
            st.success("✅ Tüm reach'ler hesaplandı!")
    
    with col1:
        # Reach sonuçları
        if st.session_state.reach_data:
            reach_df = []
            for kume in selected_kumeler:
                if kume in st.session_state.reach_data:
                    r = st.session_state.reach_data[kume]
                    reach_df.append({
                        "Küme": kume,
                        "Reach (Min)": f"{r['reach_lower']/1000000:.2f}M",
                        "Reach (Max)": f"{r['reach_upper']/1000000:.2f}M",
                        "Reach (Ort)": f"{r['reach_estimate']/1000000:.2f}M",
                        "Kaynak": "🟢 API" if r.get("source") == "api" else "🟡 Simüle"
                    })
            
            if reach_df:
                st.dataframe(pd.DataFrame(reach_df), use_container_width=True, hide_index=True)
                
                # Toplam reach
                total_reach = sum(st.session_state.reach_data[k]["reach_estimate"] for k in selected_kumeler if k in st.session_state.reach_data)
                st.metric("📊 Toplam Potansiyel Reach", f"{total_reach/1000000:.1f}M")
    
    # Reach chart
    if st.session_state.reach_data:
        st.markdown("### 📈 Reach Grafiği")
        
        chart_data = [
            {
                "Küme": k.split()[0],  # Kısa isim
                "Reach": st.session_state.reach_data[k]["reach_estimate"] / 1000000,
                "Full Name": k
            }
            for k in selected_kumeler if k in st.session_state.reach_data
        ]
        
        fig = px.bar(
            pd.DataFrame(chart_data),
            x="Küme", y="Reach",
            color="Full Name",
            color_discrete_map={k: KUME_DATA[k]["color"] for k in selected_kumeler},
            title="Küme Bazlı Reach (Milyon)"
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#94a3b8'
        )
        st.plotly_chart(fig, use_container_width=True)


# =============================================
# Tab 3: Targeting
# =============================================
with tab3:
    st.markdown("### 🎪 Targeting Spec Export")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        export_format = st.radio("Format", ["Meta Ads", "TikTok"], horizontal=True)
    
    with col2:
        if st.session_state.api_connected:
            st.markdown("#### 🔍 Interest Arama")
            search_query = st.text_input("Arama", placeholder="Coffee, Travel, Family...")
            if st.button("Ara") and search_query:
                results = search_interests(st.session_state.access_token, search_query)
                if isinstance(results, list):
                    for r in results[:5]:
                        st.code(f"ID: {r['id']} - {r['name']}")
                else:
                    st.error(results.get("error", "Hata"))
    
    st.divider()
    
    # Targeting specs
    for kume in selected_kumeler:
        with st.expander(f"📋 {kume}", expanded=True):
            data = KUME_DATA[kume]
            
            if export_format == "Meta Ads":
                spec = {
                    "name": f"PO Premium - {kume}",
                    "targeting": data["meta_targeting"],
                    "optimization_goal": "REACH",
                    "billing_event": "IMPRESSIONS"
                }
            else:
                spec = {
                    "audience_name": f"PO Premium - {kume}",
                    "location": ["TR"],
                    "age_min": data["meta_targeting"]["age_min"],
                    "age_max": data["meta_targeting"]["age_max"],
                    "interests": [i["name"] for i in data["meta_targeting"]["flexible_spec"][0]["interests"]]
                }
            
            st.code(json.dumps(spec, indent=2, ensure_ascii=False), language="json")
            
            st.download_button(
                f"⬇️ {kume} JSON İndir",
                json.dumps(spec, indent=2, ensure_ascii=False),
                f"po_targeting_{kume.replace(' ', '_').lower()}.json",
                "application/json"
            )


# =============================================
# Tab 4: Bütçe Detay
# =============================================
with tab4:
    st.markdown("### 📈 Bütçe Dağılımı")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📺 Geleneksel Medya")
        tv_oran = st.slider("TV %", 30, 70, 55)
        radyo_oran = st.slider("Radyo %", 5, 30, 15)
        outdoor_oran = 100 - tv_oran - radyo_oran
        
        st.write(f"Outdoor: %{outdoor_oran}")
        
        geleneksel_detay = {
            "TV": geleneksel_butce * tv_oran / 100,
            "Radyo": geleneksel_butce * radyo_oran / 100,
            "Outdoor": geleneksel_butce * outdoor_oran / 100
        }
        
        fig = px.pie(
            values=list(geleneksel_detay.values()),
            names=list(geleneksel_detay.keys()),
            title=f"Geleneksel ({geleneksel_butce:.1f}M TL)",
            color_discrete_sequence=["#3b82f6", "#60a5fa", "#93c5fd"]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📱 Dijital Medya")
        meta_oran = st.slider("Meta %", 20, 60, 40)
        youtube_oran = st.slider("YouTube %", 10, 40, 25)
        google_oran = st.slider("Google %", 10, 30, 20)
        tiktok_oran = st.slider("TikTok %", 0, 20, 5)
        influencer_oran = 100 - meta_oran - youtube_oran - google_oran - tiktok_oran
        
        st.write(f"Influencer: %{influencer_oran}")
        
        dijital_detay = {
            "Meta": dijital_butce * meta_oran / 100,
            "YouTube": dijital_butce * youtube_oran / 100,
            "Google": dijital_butce * google_oran / 100,
            "TikTok": dijital_butce * tiktok_oran / 100,
            "Influencer": dijital_butce * influencer_oran / 100
        }
        
        fig = px.pie(
            values=list(dijital_detay.values()),
            names=list(dijital_detay.keys()),
            title=f"Dijital ({dijital_butce:.1f}M TL)",
            color_discrete_sequence=["#f97316", "#fb923c", "#fdba74", "#fed7aa", "#ffedd5"]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Özet tablo
    st.markdown("### 📊 Bütçe Özet Tablosu")
    
    butce_data = []
    for k, v in geleneksel_detay.items():
        butce_data.append({"Kanal": k, "Bütçe (M TL)": f"{v:.2f}", "Tip": "Geleneksel"})
    for k, v in dijital_detay.items():
        butce_data.append({"Kanal": k, "Bütçe (M TL)": f"{v:.2f}", "Tip": "Dijital"})
    
    st.dataframe(pd.DataFrame(butce_data), use_container_width=True, hide_index=True)
    
    # Excel export
    df_export = pd.DataFrame(butce_data)
    st.download_button(
        "📥 Excel İndir",
        df_export.to_csv(index=False).encode('utf-8'),
        "po_butce_plani.csv",
        "text/csv"
    )


# =============================================
# Footer
# =============================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.8rem;">
    Petrol Ofisi Premium Market • Medya Planlama Dashboard v1.0<br>
    TDY Küme Analizi + Meta Marketing API
</div>
""", unsafe_allow_html=True)
