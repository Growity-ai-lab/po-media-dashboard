"""
Petrol Ofisi Premium Market - Medya Planlama Dashboard
Flask + Meta Marketing API
Render.com deployment ready
"""

from flask import Flask, render_template_string, request, jsonify, session
import requests
import json
import os
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'po-premium-dashboard-2024')

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

TURKIYE_DATA = {
    "toplam_nufus": 85000000,
    "meta_kullanici": 58000000,
    "yas_dagilim": {"18-29": 0.28, "30-49": 0.42, "50+": 0.30}
}

# =============================================
# Meta API Functions
# =============================================
def get_meta_reach(access_token, ad_account_id, targeting_spec):
    """Meta Marketing API'den reach tahmini al"""
    url = f"https://graph.facebook.com/v18.0/{ad_account_id}/reachestimate"
    params = {
        "access_token": access_token,
        "targeting_spec": json.dumps(targeting_spec),
        "optimize_for": "REACH"
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        if "error" in data:
            return {"error": data["error"].get("message", "API hatası")}
        
        users_lower = data.get("data", {}).get("users_lower_bound") or data.get("users_lower_bound", 0)
        users_upper = data.get("data", {}).get("users_upper_bound") or data.get("users_upper_bound", 0)
        
        return {
            "reach_lower": users_lower,
            "reach_upper": users_upper,
            "reach_estimate": (users_lower + users_upper) // 2,
            "source": "api"
        }
    except Exception as e:
        return {"error": str(e)}

def test_api_connection(access_token, ad_account_id):
    """API bağlantısını test et"""
    url = f"https://graph.facebook.com/v18.0/{ad_account_id}"
    params = {"access_token": access_token, "fields": "name,account_status,currency"}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "error" in data:
            return {"success": False, "error": data["error"].get("message", "API hatası")}
        return {"success": True, "name": data.get("name", "Bağlandı"), "currency": data.get("currency", "TRY")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_interests(access_token, query):
    """Meta interest arama"""
    url = "https://graph.facebook.com/v18.0/search"
    params = {"access_token": access_token, "type": "adinterest", "q": query}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "error" in data:
            return {"error": data["error"].get("message", "API hatası")}
        return data.get("data", [])
    except Exception as e:
        return {"error": str(e)}

def calculate_simulated_reach(kume_name):
    """TDY verilerine dayalı simüle reach"""
    data = KUME_DATA[kume_name]
    kume_nufus = TURKIYE_DATA["toplam_nufus"] * (data["populasyon"] / 100)
    yas_faktoru = TURKIYE_DATA["yas_dagilim"].get(data["dominant_yas"], 0.35)
    reach = kume_nufus * data["meta_penetrasyon"] * yas_faktoru * data["interest_daralma"]
    reach *= (0.92 + random.random() * 0.16)
    cpm = 22 + random.random() * 13
    return {
        "reach_lower": int(reach * 0.85),
        "reach_upper": int(reach * 1.15),
        "reach_estimate": int(reach),
        "cpm": round(cpm, 2),
        "source": "simulated"
    }

# =============================================
# HTML Template
# =============================================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PO Premium Market - Medya Planlama</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
        .gradient-text { background: linear-gradient(90deg, #FF6B00, #FFB800); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
</head>
<body class="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 min-h-screen text-white">
    <div class="max-w-7xl mx-auto p-4">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6 flex-wrap gap-4">
            <div class="flex items-center gap-4">
                <div class="w-14 h-14 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-xl flex items-center justify-center font-bold text-2xl shadow-lg">PO</div>
                <div>
                    <h1 class="text-2xl font-bold gradient-text">Premium Market Medya Planlama</h1>
                    <p class="text-slate-400 text-sm">TDY Küme Analizi + Meta Marketing API</p>
                </div>
            </div>
            <div id="connection-status" class="px-4 py-2 rounded-lg bg-yellow-500/20 text-yellow-400 text-sm">
                🟡 API Bağlı Değil
            </div>
        </div>

        <!-- API Config -->
        <div class="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4 mb-6">
            <h3 class="font-semibold mb-4 flex items-center gap-2">
                <svg class="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                Meta API Ayarları
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Access Token</label>
                    <input type="password" id="access-token" class="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-orange-500" placeholder="EAAxxxxx...">
                </div>
                <div>
                    <label class="block text-sm text-slate-400 mb-1">Ad Account ID</label>
                    <input type="text" id="ad-account-id" value="act_4309518029371350" class="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-orange-500" placeholder="act_xxxxx">
                </div>
                <div class="flex items-end">
                    <button onclick="testConnection()" class="w-full px-4 py-2 bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 rounded-lg font-medium transition-all">
                        🔌 Bağlantıyı Test Et
                    </button>
                </div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="flex gap-1 mb-6 bg-slate-800/50 p-1 rounded-xl overflow-x-auto">
            <button onclick="showTab('overview')" id="tab-overview" class="tab-btn active flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all bg-gradient-to-r from-orange-500 to-yellow-500">📊 Genel Bakış</button>
            <button onclick="showTab('reach')" id="tab-reach" class="tab-btn flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all text-slate-400 hover:text-white hover:bg-slate-700/50">🎯 Reach & CPM</button>
            <button onclick="showTab('targeting')" id="tab-targeting" class="tab-btn flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all text-slate-400 hover:text-white hover:bg-slate-700/50">🎪 Targeting</button>
            <button onclick="showTab('budget')" id="tab-budget" class="tab-btn flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all text-slate-400 hover:text-white hover:bg-slate-700/50">💰 Bütçe</button>
        </div>

        <!-- Overview Tab -->
        <div id="content-overview" class="tab-content">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <!-- Küme Seçimi -->
                <div class="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                    <h3 class="font-semibold mb-4 flex items-center gap-2">
                        <svg class="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                        Hedef Kümeler
                    </h3>
                    <div class="space-y-2" id="kume-list">
                        {% for kume, data in kumeler.items() %}
                        <label class="flex items-center gap-3 p-3 rounded-xl bg-slate-800/30 border border-slate-700 hover:border-slate-600 cursor-pointer transition-all">
                            <input type="checkbox" name="kume" value="{{ kume }}" class="kume-checkbox w-4 h-4 accent-orange-500" {% if kume in ['Yeni Orta Sınıf', 'Kırılgan Orta Yaş', 'Metropolün Karamsar Gençleri'] %}checked{% endif %}>
                            <div class="w-3 h-3 rounded-full" style="background-color: {{ data.color }}"></div>
                            <div class="flex-1">
                                <div class="text-sm font-medium">{{ kume }}</div>
                                <div class="text-xs text-slate-400">%{{ data.populasyon }} • {{ data.dominant_yas }}</div>
                            </div>
                            <span class="text-xs px-2 py-1 bg-slate-700 rounded-full">{{ data.premium_skor }}</span>
                        </label>
                        {% endfor %}
                    </div>
                </div>

                <!-- Summary -->
                <div class="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                        <h3 class="font-semibold mb-3">💰 Toplam Bütçe</h3>
                        <div class="text-4xl font-bold gradient-text mb-3" id="total-budget-display">200M TL</div>
                        <input type="range" id="total-budget" min="50" max="500" step="10" value="200" class="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-orange-500" onchange="updateBudget()">
                        <div class="flex justify-between text-xs text-slate-500 mt-1"><span>50M</span><span>500M</span></div>
                    </div>

                    <div class="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                        <h3 class="font-semibold mb-3">🌍 Tahmini Reach</h3>
                        <div class="text-4xl font-bold text-blue-400 mb-1" id="total-reach-display">-</div>
                        <div class="text-sm text-slate-400" id="avg-cpm-display">Reach hesapla →</div>
                    </div>

                    <div class="md:col-span-2 bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                        <h3 class="font-semibold mb-3">📊 Medya Dağılımı</h3>
                        <div class="flex justify-between mb-2 text-sm">
                            <span>Geleneksel: <strong class="text-blue-400" id="geleneksel-pct">45%</strong></span>
                            <span>Dijital: <strong class="text-orange-400" id="dijital-pct">55%</strong></span>
                        </div>
                        <input type="range" id="media-split" min="20" max="80" value="45" class="w-full h-3 bg-gradient-to-r from-blue-500 to-orange-500 rounded-lg appearance-none cursor-pointer" onchange="updateMediaSplit()">
                    </div>

                    <div class="md:col-span-2 bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                        <h3 class="font-semibold mb-3">💬 Küme Mesajları</h3>
                        <div class="grid gap-2" id="mesaj-list">
                            {% for kume, data in kumeler.items() %}
                            <div class="kume-mesaj hidden flex items-center gap-3 bg-slate-700/30 rounded-lg p-3" data-kume="{{ kume }}">
                                <div class="w-2 h-2 rounded-full" style="background-color: {{ data.color }}"></div>
                                <div class="flex-1">
                                    <div class="text-sm font-medium">{{ kume }}</div>
                                    <div class="text-xs text-orange-400">"{{ data.mesaj }}"</div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Reach Tab -->
        <div id="content-reach" class="tab-content hidden">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div class="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="font-semibold">🎯 Küme Bazlı Reach</h3>
                        <button onclick="calculateAllReach()" class="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg text-sm transition-all">
                            🔄 Tümünü Hesapla
                        </button>
                    </div>
                    <div id="reach-results" class="space-y-3">
                        <p class="text-slate-400 text-sm text-center py-8">Küme seçin ve "Tümünü Hesapla" tıklayın</p>
                    </div>
                </div>

                <div class="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                    <h3 class="font-semibold mb-4">📈 Reach Grafiği</h3>
                    <canvas id="reach-chart" height="250"></canvas>
                </div>

                <div class="lg:col-span-2 bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                    <h3 class="font-semibold mb-4">🔍 Interest Arama</h3>
                    <div class="flex gap-2 mb-4">
                        <input type="text" id="interest-search" placeholder="Coffee, Travel, Family..." class="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-orange-500">
                        <button onclick="searchInterests()" class="px-4 py-2 bg-orange-500 hover:bg-orange-600 rounded-lg transition-all">Ara</button>
                    </div>
                    <div id="interest-results" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2"></div>
                </div>
            </div>
        </div>

        <!-- Targeting Tab -->
        <div id="content-targeting" class="tab-content hidden">
            <div class="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4 mb-4">
                <div class="flex items-center gap-4">
                    <span class="font-semibold">Export Format:</span>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="export-format" value="meta" checked class="accent-blue-500"> Meta Ads
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="export-format" value="tiktok" class="accent-pink-500"> TikTok
                    </label>
                </div>
            </div>
            <div id="targeting-specs" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
        </div>

        <!-- Budget Tab -->
        <div id="content-budget" class="tab-content hidden">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div class="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                    <h3 class="font-semibold mb-4 text-blue-400">📺 Geleneksel Medya</h3>
                    <div class="space-y-4">
                        <div>
                            <div class="flex justify-between text-sm mb-1"><span>TV</span><span class="text-blue-400" id="tv-budget">55% (49.5M)</span></div>
                            <input type="range" id="tv-slider" min="30" max="70" value="55" class="w-full h-2 bg-slate-700 rounded-lg accent-blue-500" onchange="updateChannelBudgets()">
                        </div>
                        <div>
                            <div class="flex justify-between text-sm mb-1"><span>Radyo</span><span class="text-blue-400" id="radyo-budget">15% (13.5M)</span></div>
                            <input type="range" id="radyo-slider" min="5" max="30" value="15" class="w-full h-2 bg-slate-700 rounded-lg accent-blue-500" onchange="updateChannelBudgets()">
                        </div>
                        <div>
                            <div class="flex justify-between text-sm mb-1"><span>Outdoor</span><span class="text-blue-400" id="outdoor-budget">30% (27M)</span></div>
                            <input type="range" id="outdoor-slider" min="10" max="50" value="30" class="w-full h-2 bg-slate-700 rounded-lg accent-blue-500" onchange="updateChannelBudgets()">
                        </div>
                    </div>
                </div>

                <div class="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                    <h3 class="font-semibold mb-4 text-orange-400">📱 Dijital Medya</h3>
                    <div class="space-y-4">
                        <div>
                            <div class="flex justify-between text-sm mb-1"><span>Meta</span><span class="text-orange-400" id="meta-budget">40% (44M)</span></div>
                            <input type="range" id="meta-slider" min="20" max="60" value="40" class="w-full h-2 bg-slate-700 rounded-lg accent-orange-500" onchange="updateChannelBudgets()">
                        </div>
                        <div>
                            <div class="flex justify-between text-sm mb-1"><span>YouTube</span><span class="text-orange-400" id="youtube-budget">25% (27.5M)</span></div>
                            <input type="range" id="youtube-slider" min="10" max="40" value="25" class="w-full h-2 bg-slate-700 rounded-lg accent-orange-500" onchange="updateChannelBudgets()">
                        </div>
                        <div>
                            <div class="flex justify-between text-sm mb-1"><span>Google</span><span class="text-orange-400" id="google-budget">20% (22M)</span></div>
                            <input type="range" id="google-slider" min="10" max="30" value="20" class="w-full h-2 bg-slate-700 rounded-lg accent-orange-500" onchange="updateChannelBudgets()">
                        </div>
                        <div>
                            <div class="flex justify-between text-sm mb-1"><span>TikTok</span><span class="text-orange-400" id="tiktok-budget">5% (5.5M)</span></div>
                            <input type="range" id="tiktok-slider" min="0" max="20" value="5" class="w-full h-2 bg-slate-700 rounded-lg accent-orange-500" onchange="updateChannelBudgets()">
                        </div>
                        <div>
                            <div class="flex justify-between text-sm mb-1"><span>Influencer</span><span class="text-orange-400" id="influencer-budget">10% (11M)</span></div>
                            <input type="range" id="influencer-slider" min="5" max="20" value="10" class="w-full h-2 bg-slate-700 rounded-lg accent-orange-500" onchange="updateChannelBudgets()">
                        </div>
                    </div>
                </div>

                <div class="lg:col-span-2 bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                    <h3 class="font-semibold mb-4">📊 Bütçe Özet Tablosu</h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-sm" id="budget-table">
                            <thead>
                                <tr class="border-b border-slate-700 text-slate-400">
                                    <th class="text-left py-2 px-3">Kanal</th>
                                    <th class="text-right py-2 px-3">Oran</th>
                                    <th class="text-right py-2 px-3">Bütçe (M TL)</th>
                                    <th class="text-left py-2 px-3">Tip</th>
                                </tr>
                            </thead>
                            <tbody id="budget-table-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="mt-8 text-center text-xs text-slate-500 pb-4">
            Petrol Ofisi Premium Market • Medya Planlama Dashboard v1.0 • Meta Marketing API
        </div>
    </div>

    <script>
        // State
        let apiConnected = false;
        let reachData = {};
        let reachChart = null;
        const kumeData = {{ kumeler | tojson }};

        // Tab switching
        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(el => {
                el.classList.remove('bg-gradient-to-r', 'from-orange-500', 'to-yellow-500');
                el.classList.add('text-slate-400');
            });
            document.getElementById('content-' + tabId).classList.remove('hidden');
            const btn = document.getElementById('tab-' + tabId);
            btn.classList.add('bg-gradient-to-r', 'from-orange-500', 'to-yellow-500');
            btn.classList.remove('text-slate-400');
            
            if (tabId === 'targeting') updateTargetingSpecs();
            if (tabId === 'budget') updateChannelBudgets();
        }

        // Update displays
        function updateBudget() {
            const budget = document.getElementById('total-budget').value;
            document.getElementById('total-budget-display').textContent = budget + 'M TL';
            updateMediaSplit();
        }

        function updateMediaSplit() {
            const split = document.getElementById('media-split').value;
            document.getElementById('geleneksel-pct').textContent = split + '%';
            document.getElementById('dijital-pct').textContent = (100 - split) + '%';
            updateChannelBudgets();
        }

        function updateChannelBudgets() {
            const totalBudget = parseInt(document.getElementById('total-budget').value);
            const split = parseInt(document.getElementById('media-split').value);
            const gelenekselBudget = totalBudget * split / 100;
            const dijitalBudget = totalBudget - gelenekselBudget;

            // Geleneksel
            const tv = parseInt(document.getElementById('tv-slider').value);
            const radyo = parseInt(document.getElementById('radyo-slider').value);
            const outdoor = 100 - tv - radyo;
            document.getElementById('tv-budget').textContent = `${tv}% (${(gelenekselBudget * tv / 100).toFixed(1)}M)`;
            document.getElementById('radyo-budget').textContent = `${radyo}% (${(gelenekselBudget * radyo / 100).toFixed(1)}M)`;
            document.getElementById('outdoor-budget').textContent = `${outdoor}% (${(gelenekselBudget * outdoor / 100).toFixed(1)}M)`;

            // Dijital
            const meta = parseInt(document.getElementById('meta-slider').value);
            const youtube = parseInt(document.getElementById('youtube-slider').value);
            const google = parseInt(document.getElementById('google-slider').value);
            const tiktok = parseInt(document.getElementById('tiktok-slider').value);
            const influencer = 100 - meta - youtube - google - tiktok;
            document.getElementById('meta-budget').textContent = `${meta}% (${(dijitalBudget * meta / 100).toFixed(1)}M)`;
            document.getElementById('youtube-budget').textContent = `${youtube}% (${(dijitalBudget * youtube / 100).toFixed(1)}M)`;
            document.getElementById('google-budget').textContent = `${google}% (${(dijitalBudget * google / 100).toFixed(1)}M)`;
            document.getElementById('tiktok-budget').textContent = `${tiktok}% (${(dijitalBudget * tiktok / 100).toFixed(1)}M)`;
            document.getElementById('influencer-budget').textContent = `${influencer}% (${(dijitalBudget * influencer / 100).toFixed(1)}M)`;

            // Table
            const tbody = document.getElementById('budget-table-body');
            tbody.innerHTML = `
                <tr class="border-b border-slate-700/50"><td class="py-2 px-3">TV</td><td class="text-right">${tv}%</td><td class="text-right text-blue-400 font-medium">${(gelenekselBudget * tv / 100).toFixed(2)}</td><td><span class="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded">Geleneksel</span></td></tr>
                <tr class="border-b border-slate-700/50"><td class="py-2 px-3">Radyo</td><td class="text-right">${radyo}%</td><td class="text-right text-blue-400 font-medium">${(gelenekselBudget * radyo / 100).toFixed(2)}</td><td><span class="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded">Geleneksel</span></td></tr>
                <tr class="border-b border-slate-700/50"><td class="py-2 px-3">Outdoor</td><td class="text-right">${outdoor}%</td><td class="text-right text-blue-400 font-medium">${(gelenekselBudget * outdoor / 100).toFixed(2)}</td><td><span class="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded">Geleneksel</span></td></tr>
                <tr class="border-b border-slate-700/50"><td class="py-2 px-3">Meta</td><td class="text-right">${meta}%</td><td class="text-right text-orange-400 font-medium">${(dijitalBudget * meta / 100).toFixed(2)}</td><td><span class="text-xs px-2 py-1 bg-orange-500/20 text-orange-400 rounded">Dijital</span></td></tr>
                <tr class="border-b border-slate-700/50"><td class="py-2 px-3">YouTube</td><td class="text-right">${youtube}%</td><td class="text-right text-orange-400 font-medium">${(dijitalBudget * youtube / 100).toFixed(2)}</td><td><span class="text-xs px-2 py-1 bg-orange-500/20 text-orange-400 rounded">Dijital</span></td></tr>
                <tr class="border-b border-slate-700/50"><td class="py-2 px-3">Google</td><td class="text-right">${google}%</td><td class="text-right text-orange-400 font-medium">${(dijitalBudget * google / 100).toFixed(2)}</td><td><span class="text-xs px-2 py-1 bg-orange-500/20 text-orange-400 rounded">Dijital</span></td></tr>
                <tr class="border-b border-slate-700/50"><td class="py-2 px-3">TikTok</td><td class="text-right">${tiktok}%</td><td class="text-right text-orange-400 font-medium">${(dijitalBudget * tiktok / 100).toFixed(2)}</td><td><span class="text-xs px-2 py-1 bg-orange-500/20 text-orange-400 rounded">Dijital</span></td></tr>
                <tr class="border-b border-slate-700/50"><td class="py-2 px-3">Influencer</td><td class="text-right">${influencer}%</td><td class="text-right text-orange-400 font-medium">${(dijitalBudget * influencer / 100).toFixed(2)}</td><td><span class="text-xs px-2 py-1 bg-orange-500/20 text-orange-400 rounded">Dijital</span></td></tr>
                <tr class="font-bold bg-slate-700/30"><td class="py-3 px-3">TOPLAM</td><td class="text-right">100%</td><td class="text-right text-lg">${totalBudget}</td><td></td></tr>
            `;
        }

        // Küme checkbox handler
        document.querySelectorAll('.kume-checkbox').forEach(cb => {
            cb.addEventListener('change', updateKumeMesajlar);
        });

        function updateKumeMesajlar() {
            const selected = getSelectedKumeler();
            document.querySelectorAll('.kume-mesaj').forEach(el => {
                if (selected.includes(el.dataset.kume)) {
                    el.classList.remove('hidden');
                } else {
                    el.classList.add('hidden');
                }
            });
        }

        function getSelectedKumeler() {
            return Array.from(document.querySelectorAll('.kume-checkbox:checked')).map(cb => cb.value);
        }

        // API Connection
        async function testConnection() {
            const token = document.getElementById('access-token').value;
            const accountId = document.getElementById('ad-account-id').value;
            
            if (!token || !accountId) {
                alert('Token ve Account ID gerekli');
                return;
            }

            const statusEl = document.getElementById('connection-status');
            statusEl.innerHTML = '⏳ Test ediliyor...';
            statusEl.className = 'px-4 py-2 rounded-lg bg-yellow-500/20 text-yellow-400 text-sm';

            try {
                const response = await fetch('/api/test-connection', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({access_token: token, ad_account_id: accountId})
                });
                const data = await response.json();
                
                if (data.success) {
                    apiConnected = true;
                    statusEl.innerHTML = '🟢 Bağlı: ' + data.name;
                    statusEl.className = 'px-4 py-2 rounded-lg bg-green-500/20 text-green-400 text-sm';
                } else {
                    statusEl.innerHTML = '🔴 Hata: ' + data.error;
                    statusEl.className = 'px-4 py-2 rounded-lg bg-red-500/20 text-red-400 text-sm';
                }
            } catch (e) {
                statusEl.innerHTML = '🔴 Bağlantı hatası';
                statusEl.className = 'px-4 py-2 rounded-lg bg-red-500/20 text-red-400 text-sm';
            }
        }

        // Reach Calculation
        async function calculateAllReach() {
            const selected = getSelectedKumeler();
            if (selected.length === 0) {
                alert('En az bir küme seçin');
                return;
            }

            const token = document.getElementById('access-token').value;
            const accountId = document.getElementById('ad-account-id').value;
            const resultsEl = document.getElementById('reach-results');
            resultsEl.innerHTML = '<p class="text-center py-4">⏳ Hesaplanıyor...</p>';

            try {
                const response = await fetch('/api/calculate-reach', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        kumeler: selected,
                        access_token: token,
                        ad_account_id: accountId
                    })
                });
                const data = await response.json();
                reachData = data;
                
                // Display results
                let html = '';
                let totalReach = 0;
                let totalCpm = 0;
                let count = 0;

                for (const [kume, result] of Object.entries(data)) {
                    const color = kumeData[kume]?.color || '#666';
                    const reach = result.reach_estimate || 0;
                    const cpm = result.cpm || 25;
                    totalReach += reach;
                    totalCpm += cpm;
                    count++;

                    html += `
                        <div class="bg-slate-700/50 rounded-lg p-3">
                            <div class="flex items-center justify-between mb-2">
                                <div class="flex items-center gap-2">
                                    <div class="w-2 h-2 rounded-full" style="background-color: ${color}"></div>
                                    <span class="text-sm font-medium">${kume}</span>
                                </div>
                                <span class="text-lg font-bold text-blue-400">${(reach / 1000000).toFixed(2)}M</span>
                            </div>
                            <div class="grid grid-cols-3 gap-2 text-xs text-slate-400">
                                <div><span class="block text-slate-500">Aralık</span>${(result.reach_lower / 1000000).toFixed(1)}M - ${(result.reach_upper / 1000000).toFixed(1)}M</div>
                                <div><span class="block text-slate-500">CPM</span>₺${cpm.toFixed(2)}</div>
                                <div><span class="block text-slate-500">Kaynak</span>${result.source === 'api' ? '🟢 API' : '🟡 Simüle'}</div>
                            </div>
                        </div>
                    `;
                }

                // Total
                html += `
                    <div class="bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-lg p-4 border border-blue-500/30">
                        <div class="flex justify-between items-center">
                            <span class="font-medium">Toplam Potansiyel</span>
                            <span class="text-2xl font-bold text-blue-400">${(totalReach / 1000000).toFixed(1)}M</span>
                        </div>
                    </div>
                `;

                resultsEl.innerHTML = html;

                // Update overview
                document.getElementById('total-reach-display').textContent = (totalReach / 1000000).toFixed(1) + 'M';
                document.getElementById('avg-cpm-display').textContent = 'Ort. CPM: ₺' + (totalCpm / count).toFixed(2);

                // Update chart
                updateReachChart(data);
            } catch (e) {
                resultsEl.innerHTML = '<p class="text-red-400 text-center py-4">Hata: ' + e.message + '</p>';
            }
        }

        function updateReachChart(data) {
            const ctx = document.getElementById('reach-chart').getContext('2d');
            const labels = Object.keys(data).map(k => k.split(' ')[0]);
            const values = Object.values(data).map(d => (d.reach_estimate || 0) / 1000000);
            const colors = Object.keys(data).map(k => kumeData[k]?.color || '#666');

            if (reachChart) reachChart.destroy();
            
            reachChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Reach (M)',
                        data: values,
                        backgroundColor: colors,
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        // Interest Search
        async function searchInterests() {
            const query = document.getElementById('interest-search').value;
            const token = document.getElementById('access-token').value;
            
            if (!query) return;

            const resultsEl = document.getElementById('interest-results');
            resultsEl.innerHTML = '<p class="col-span-3 text-center py-4">⏳ Aranıyor...</p>';

            try {
                const response = await fetch('/api/search-interests', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query, access_token: token})
                });
                const data = await response.json();
                
                if (data.error) {
                    resultsEl.innerHTML = `<p class="col-span-3 text-red-400">${data.error}</p>`;
                    return;
                }

                let html = '';
                for (const item of data.slice(0, 9)) {
                    html += `
                        <div class="bg-slate-700/50 rounded-lg p-3">
                            <div class="text-sm font-medium">${item.name}</div>
                            <div class="text-xs text-slate-400 font-mono">ID: ${item.id}</div>
                            <button onclick="navigator.clipboard.writeText('${item.id}')" class="mt-2 text-xs px-2 py-1 bg-slate-600 hover:bg-slate-500 rounded">📋 Kopyala</button>
                        </div>
                    `;
                }
                resultsEl.innerHTML = html || '<p class="col-span-3 text-slate-400">Sonuç bulunamadı</p>';
            } catch (e) {
                resultsEl.innerHTML = '<p class="col-span-3 text-red-400">Arama hatası</p>';
            }
        }

        // Targeting Specs
        function updateTargetingSpecs() {
            const selected = getSelectedKumeler();
            const format = document.querySelector('input[name="export-format"]:checked').value;
            const container = document.getElementById('targeting-specs');
            
            let html = '';
            for (const kume of selected) {
                const data = kumeData[kume];
                let spec;
                
                if (format === 'meta') {
                    spec = {
                        name: `PO Premium - ${kume}`,
                        targeting: data.meta_targeting,
                        optimization_goal: "REACH"
                    };
                } else {
                    spec = {
                        audience_name: `PO Premium - ${kume}`,
                        location: ["TR"],
                        age_min: data.meta_targeting.age_min,
                        age_max: data.meta_targeting.age_max
                    };
                }

                html += `
                    <div class="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-4">
                        <div class="flex items-center justify-between mb-3">
                            <div class="flex items-center gap-2">
                                <div class="w-3 h-3 rounded-full" style="background-color: ${data.color}"></div>
                                <h4 class="font-semibold text-sm">${kume}</h4>
                            </div>
                            <button onclick="copySpec('${kume}')" class="p-2 rounded-lg bg-slate-700 hover:bg-slate-600 transition-all">📋</button>
                        </div>
                        <div class="bg-slate-900 rounded-lg p-3 max-h-48 overflow-y-auto">
                            <pre class="text-xs text-slate-300 whitespace-pre-wrap font-mono" id="spec-${kume.replace(/\\s/g, '-')}">${JSON.stringify(spec, null, 2)}</pre>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html || '<p class="col-span-3 text-slate-400 text-center py-8">Küme seçin</p>';
        }

        function copySpec(kume) {
            const specEl = document.getElementById('spec-' + kume.replace(/\\s/g, '-'));
            navigator.clipboard.writeText(specEl.textContent);
            alert('Kopyalandı!');
        }

        // Radio change handler
        document.querySelectorAll('input[name="export-format"]').forEach(radio => {
            radio.addEventListener('change', updateTargetingSpecs);
        });

        // Initial updates
        updateKumeMesajlar();
        updateBudget();
    </script>
</body>
</html>
'''

# =============================================
# Routes
# =============================================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, kumeler=KUME_DATA)

@app.route('/api/test-connection', methods=['POST'])
def api_test_connection():
    data = request.json
    result = test_api_connection(data.get('access_token'), data.get('ad_account_id'))
    return jsonify(result)

@app.route('/api/calculate-reach', methods=['POST'])
def api_calculate_reach():
    data = request.json
    kumeler = data.get('kumeler', [])
    access_token = data.get('access_token')
    ad_account_id = data.get('ad_account_id')
    
    results = {}
    for kume in kumeler:
        if kume not in KUME_DATA:
            continue
        
        if access_token and ad_account_id:
            # Try real API
            targeting = KUME_DATA[kume]['meta_targeting']
            result = get_meta_reach(access_token, ad_account_id, targeting)
            if 'error' not in result:
                result['cpm'] = round(22 + random.random() * 13, 2)
                results[kume] = result
            else:
                # Fallback to simulated
                results[kume] = calculate_simulated_reach(kume)
        else:
            # Simulated
            results[kume] = calculate_simulated_reach(kume)
    
    return jsonify(results)

@app.route('/api/search-interests', methods=['POST'])
def api_search_interests():
    data = request.json
    access_token = data.get('access_token')
    query = data.get('query')
    
    if not access_token:
        # Return simulated results
        return jsonify([
            {"id": "6003139266461", "name": f"{query}"},
            {"id": "6003139266462", "name": f"{query} enthusiasts"},
            {"id": "6003139266463", "name": f"{query} lovers"}
        ])
    
    result = search_interests(access_token, query)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result)
    return jsonify(result)

# =============================================
# Run
# =============================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
