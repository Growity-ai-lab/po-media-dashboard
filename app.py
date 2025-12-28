"""
PO Premium - Audience Intersection Builder
Gercek zamanli Venn diagram + Sabit reach hesaplama
"""
from flask import Flask, render_template_string, request, jsonify
import json, os, hashlib

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'po-2024')

# Sabit reach değerleri olan interest data
INTERESTS = {
    "coffee": [
        {"id": "i001", "name": "Coffee", "reach": 12500000},
        {"id": "i002", "name": "Starbucks", "reach": 8200000},
        {"id": "i003", "name": "Cafe Culture", "reach": 4500000},
    ],
    "food": [
        {"id": "i004", "name": "Restaurants", "reach": 18000000},
        {"id": "i005", "name": "Brunch", "reach": 5200000},
        {"id": "i006", "name": "Organic Food", "reach": 6500000},
    ],
    "travel": [
        {"id": "i007", "name": "Travel", "reach": 22000000},
        {"id": "i008", "name": "Weekend Getaways", "reach": 4800000},
        {"id": "i009", "name": "Road Trips", "reach": 5200000},
    ],
    "family": [
        {"id": "i010", "name": "Family", "reach": 28000000},
        {"id": "i011", "name": "Parenting", "reach": 12000000},
        {"id": "i012", "name": "Child Safety", "reach": 4200000},
    ],
    "wellness": [
        {"id": "i013", "name": "Health & Wellness", "reach": 15000000},
        {"id": "i014", "name": "Fitness", "reach": 11000000},
        {"id": "i015", "name": "Self-care", "reach": 7200000},
    ],
    "tech": [
        {"id": "i016", "name": "Technology", "reach": 19000000},
        {"id": "i017", "name": "Online Shopping", "reach": 21000000},
        {"id": "i018", "name": "Mobile Apps", "reach": 18000000},
    ],
    "shopping": [
        {"id": "i019", "name": "Engaged Shoppers", "reach": 16000000},
        {"id": "i020", "name": "Quality Products", "reach": 7500000},
        {"id": "i021", "name": "Brand Conscious", "reach": 5200000},
    ],
    "entertainment": [
        {"id": "i022", "name": "Netflix", "reach": 14000000},
        {"id": "i023", "name": "Streaming", "reach": 11000000},
        {"id": "i024", "name": "Podcasts", "reach": 5500000},
    ],
    "auto": [
        {"id": "i025", "name": "Car Owners", "reach": 15000000},
        {"id": "i026", "name": "Road Safety", "reach": 6500000},
        {"id": "i027", "name": "Fuel Efficiency", "reach": 3800000},
    ],
    "premium": [
        {"id": "i028", "name": "Quality Conscious", "reach": 6200000},
        {"id": "i029", "name": "Premium Services", "reach": 4800000},
        {"id": "i030", "name": "Convenience Seekers", "reach": 8900000},
    ],
}

# Tüm interest'leri düz liste olarak
ALL_INTERESTS = {}
for cat, items in INTERESTS.items():
    for item in items:
        ALL_INTERESTS[item["id"]] = {**item, "category": cat}

CATEGORIES = [
    {"key": "coffee", "name": "Kahve", "icon": "☕"},
    {"key": "food", "name": "Yemek", "icon": "🍽️"},
    {"key": "travel", "name": "Seyahat", "icon": "✈️"},
    {"key": "family", "name": "Aile", "icon": "👨‍👩‍👧"},
    {"key": "wellness", "name": "Sağlık", "icon": "🧘"},
    {"key": "tech", "name": "Teknoloji", "icon": "📱"},
    {"key": "shopping", "name": "Alışveriş", "icon": "🛒"},
    {"key": "entertainment", "name": "Eğlence", "icon": "🎬"},
    {"key": "auto", "name": "Otomotiv", "icon": "🚗"},
    {"key": "premium", "name": "Premium", "icon": "⭐"},
]

def calc_segment_reach(interest_ids):
    """Segment reach hesapla - deterministik"""
    if not interest_ids:
        return 0
    
    # Interest reach değerlerini al
    reaches = []
    for iid in interest_ids:
        if iid in ALL_INTERESTS:
            reaches.append(ALL_INTERESTS[iid]["reach"])
    
    if not reaches:
        return 0
    
    # OR mantığı: En büyük + diğerlerinin kademeli katkısı
    reaches.sort(reverse=True)
    total = reaches[0]
    for i, r in enumerate(reaches[1:], 1):
        # Her eklenen interest %30/i oranında katkı sağlar
        total += int(r * 0.30 / i)
    
    # Max TR Meta kullanıcısı
    return min(total, 35000000)

def calc_intersection(segments):
    """Kesişim hesapla - AND mantığı"""
    if len(segments) < 2:
        return 0
    
    # Her segmentin reach'ini hesapla
    segment_reaches = []
    for seg in segments:
        if seg.get("interests"):
            reach = calc_segment_reach([i["id"] for i in seg["interests"]])
            if reach > 0:
                segment_reaches.append(reach)
    
    if len(segment_reaches) < 2:
        return 0
    
    # Kesişim: En küçük segmentin belirli bir oranı
    min_reach = min(segment_reaches)
    
    # Segment sayısına göre kesişim oranı
    # 2 segment: %25, 3 segment: %15, 4+: %10
    if len(segment_reaches) == 2:
        ratio = 0.25
    elif len(segment_reaches) == 3:
        ratio = 0.15
    else:
        ratio = 0.10
    
    return int(min_reach * ratio)

def calc_union(segments):
    """Birleşim hesapla - OR mantığı"""
    if not segments:
        return 0
    
    # Tüm unique interest'leri topla
    all_interest_ids = set()
    for seg in segments:
        for i in seg.get("interests", []):
            all_interest_ids.add(i["id"])
    
    if not all_interest_ids:
        return 0
    
    return calc_segment_reach(list(all_interest_ids))

HTML = '''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PO Premium - Audience Builder</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body { font-family: system-ui, -apple-system, sans-serif; }
.venn-circle { transition: all 0.3s ease; }
.segment-pill { transition: all 0.2s; }
.segment-pill:hover { transform: scale(1.02); }
</style>
</head>
<body class="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 min-h-screen text-white">
<div class="max-w-7xl mx-auto p-4">

<!-- Header -->
<div class="flex items-center gap-4 mb-6">
    <div class="w-14 h-14 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-xl flex items-center justify-center font-bold text-2xl shadow-lg">PO</div>
    <div>
        <h1 class="text-2xl font-bold bg-gradient-to-r from-orange-400 to-yellow-400 bg-clip-text text-transparent">Premium Audience Builder</h1>
        <p class="text-slate-400 text-sm">Erişilebilir Premium - Gerçek Zamanlı Kesişim Analizi</p>
    </div>
</div>

<!-- Info -->
<div class="bg-orange-500/10 border border-orange-500/30 rounded-xl p-4 mb-6">
    <p class="text-sm"><strong class="text-orange-400">💡 Nasıl Çalışır:</strong> Kategorilerden interest seçin, segmentlere ekleyin. Venn diagramı ve reach değerleri anlık güncellenir.</p>
</div>

<div class="grid lg:grid-cols-12 gap-6">

<!-- Sol Panel: Kategoriler & Interest'ler -->
<div class="lg:col-span-3 space-y-4">
    <div class="bg-slate-800/80 rounded-xl p-4 border border-slate-700">
        <h3 class="text-sm font-semibold text-slate-400 mb-3">KATEGORİLER</h3>
        <div class="grid grid-cols-2 gap-2" id="categories"></div>
    </div>
    
    <div class="bg-slate-800/80 rounded-xl p-4 border border-slate-700">
        <h3 class="text-sm font-semibold text-slate-400 mb-3" id="interest-title">Interest Seçin</h3>
        <div id="interests" class="space-y-2 max-h-[400px] overflow-y-auto pr-1"></div>
    </div>
</div>

<!-- Orta Panel: Segmentler -->
<div class="lg:col-span-4">
    <div class="bg-slate-800/80 rounded-xl p-4 border border-slate-700 h-full">
        <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold">📊 Segmentler</h3>
            <button onclick="addSegment()" class="px-3 py-1.5 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg text-sm font-medium">+ Yeni Segment</button>
        </div>
        <div id="segments" class="space-y-3"></div>
        <div class="mt-4 p-3 bg-slate-700/30 rounded-lg">
            <p class="text-xs text-slate-400">💡 Her segment bir hedef kitle grubu. Kesişim = tüm segmentlerde ortak olan kişiler.</p>
        </div>
    </div>
</div>

<!-- Sağ Panel: Venn & Sonuçlar -->
<div class="lg:col-span-5 space-y-4">
    
    <!-- Venn Diagram -->
    <div class="bg-slate-800/80 rounded-xl p-4 border border-slate-700">
        <h3 class="font-semibold mb-3">🎯 Kesişim Diagramı</h3>
        <div class="bg-slate-900/50 rounded-lg p-4">
            <svg id="venn" viewBox="0 0 400 280" class="w-full"></svg>
        </div>
    </div>
    
    <!-- Reach Sonuçları -->
    <div class="grid grid-cols-2 gap-4">
        <div class="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-xl p-4 border border-blue-500/30">
            <p class="text-xs text-slate-400 mb-1">Birleşim (OR)</p>
            <p class="text-2xl font-bold text-blue-400" id="union-reach">0</p>
            <p class="text-xs text-slate-500">En az birinde olan</p>
        </div>
        <div class="bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl p-4 border border-purple-500/30">
            <p class="text-xs text-slate-400 mb-1">Kesişim (AND)</p>
            <p class="text-2xl font-bold text-purple-400" id="intersection-reach">0</p>
            <p class="text-xs text-slate-500">Tümünde ortak</p>
        </div>
    </div>
    
    <!-- Segment Reach Listesi -->
    <div class="bg-slate-800/80 rounded-xl p-4 border border-slate-700">
        <h3 class="font-semibold mb-3">📈 Segment Reach</h3>
        <div id="reach-list" class="space-y-2"></div>
    </div>
    
    <!-- Export -->
    <div class="grid grid-cols-2 gap-3">
        <button onclick="exportJSON()" class="py-2.5 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-xl text-sm font-medium">📋 JSON Export</button>
        <button onclick="copyIntersection()" class="py-2.5 bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 rounded-xl text-sm font-medium">🎯 Kesişim Kopyala</button>
    </div>
</div>

</div>
</div>

<script>
// Data
const INTERESTS = ''' + json.dumps(INTERESTS) + ''';
const ALL_INTERESTS = ''' + json.dumps(ALL_INTERESTS) + ''';
const CATEGORIES = ''' + json.dumps(CATEGORIES) + ''';

// State
let segments = [];
let segmentIdCounter = 0;
const COLORS = ['#FF6B00', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    renderCategories();
    addSegment(); // İlk segment
    updateAll();
});

function renderCategories() {
    const container = document.getElementById('categories');
    container.innerHTML = CATEGORIES.map(cat => `
        <button onclick="showCategory('${cat.key}')" 
            class="category-btn flex flex-col items-center gap-1 p-3 rounded-lg bg-slate-700/50 hover:bg-slate-700 border border-slate-600 hover:border-slate-500 transition-all">
            <span class="text-xl">${cat.icon}</span>
            <span class="text-xs">${cat.name}</span>
        </button>
    `).join('');
}

function showCategory(key) {
    const interests = INTERESTS[key] || [];
    const cat = CATEGORIES.find(c => c.key === key);
    
    document.getElementById('interest-title').textContent = cat ? cat.icon + ' ' + cat.name : 'Interest';
    
    const container = document.getElementById('interests');
    container.innerHTML = interests.map(int => {
        const reachM = (int.reach / 1000000).toFixed(1);
        return `
            <div class="bg-slate-700/50 rounded-lg p-3 hover:bg-slate-700/80 transition-all">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <div class="font-medium text-sm">${int.name}</div>
                        <div class="text-xs text-slate-400">${reachM}M reach</div>
                    </div>
                </div>
                <div class="flex flex-wrap gap-1">
                    ${segments.map((seg, idx) => {
                        const isIn = seg.interests.some(i => i.id === int.id);
                        return `
                            <button onclick="toggleInterest('${int.id}', ${seg.id})"
                                class="px-2 py-1 rounded text-xs font-medium transition-all ${isIn 
                                    ? 'text-white' 
                                    : 'bg-slate-600 hover:bg-slate-500 text-slate-300'}"
                                style="${isIn ? 'background:' + seg.color : ''}">
                                ${isIn ? '✓' : '+'} ${seg.name}
                            </button>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }).join('');
}

function addSegment() {
    segmentIdCounter++;
    const color = COLORS[(segmentIdCounter - 1) % COLORS.length];
    segments.push({
        id: segmentIdCounter,
        name: 'Segment ' + segmentIdCounter,
        color: color,
        interests: []
    });
    renderSegments();
    updateAll();
}

function removeSegment(id) {
    segments = segments.filter(s => s.id !== id);
    renderSegments();
    updateAll();
    // Refresh interest buttons
    const title = document.getElementById('interest-title').textContent;
    if (title !== 'Interest Seçin') {
        const key = CATEGORIES.find(c => title.includes(c.name))?.key;
        if (key) showCategory(key);
    }
}

function renameSegment(id, name) {
    const seg = segments.find(s => s.id === id);
    if (seg) seg.name = name;
    updateAll();
}

function toggleInterest(intId, segId) {
    const seg = segments.find(s => s.id === segId);
    if (!seg) return;
    
    const int = ALL_INTERESTS[intId];
    if (!int) return;
    
    const idx = seg.interests.findIndex(i => i.id === intId);
    if (idx >= 0) {
        seg.interests.splice(idx, 1);
    } else {
        seg.interests.push({ id: int.id, name: int.name, reach: int.reach });
    }
    
    renderSegments();
    updateAll();
    
    // Refresh interest list to update buttons
    const title = document.getElementById('interest-title').textContent;
    if (title !== 'Interest Seçin') {
        const key = CATEGORIES.find(c => title.includes(c.name))?.key;
        if (key) showCategory(key);
    }
}

function removeInterestFromSegment(intId, segId) {
    const seg = segments.find(s => s.id === segId);
    if (seg) {
        seg.interests = seg.interests.filter(i => i.id !== intId);
        renderSegments();
        updateAll();
    }
}

function renderSegments() {
    const container = document.getElementById('segments');
    
    if (segments.length === 0) {
        container.innerHTML = '<p class="text-slate-500 text-sm text-center py-8">Segment ekleyin</p>';
        return;
    }
    
    container.innerHTML = segments.map((seg, idx) => {
        const reach = calcSegmentReach(seg.interests);
        const reachText = reach > 0 ? (reach / 1000000).toFixed(2) + 'M' : '-';
        
        return `
            <div class="segment-pill bg-slate-700/40 rounded-xl p-3 border-l-4" style="border-color: ${seg.color}">
                <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center gap-2">
                        <div class="w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold text-white" style="background: ${seg.color}">${idx + 1}</div>
                        <input type="text" value="${seg.name}" 
                            onchange="renameSegment(${seg.id}, this.value)"
                            class="bg-transparent text-sm font-semibold w-28 focus:outline-none focus:bg-slate-600 rounded px-1">
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-sm font-bold" style="color: ${seg.color}">${reachText}</span>
                        <button onclick="removeSegment(${seg.id})" class="text-slate-400 hover:text-red-400 text-lg">×</button>
                    </div>
                </div>
                <div class="flex flex-wrap gap-1 min-h-[28px]">
                    ${seg.interests.length === 0 
                        ? '<span class="text-slate-500 text-xs">← Kategoriden interest ekleyin</span>'
                        : seg.interests.map(int => `
                            <span class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs" 
                                style="background: ${seg.color}22; color: ${seg.color}; border: 1px solid ${seg.color}44">
                                ${int.name}
                                <button onclick="removeInterestFromSegment('${int.id}', ${seg.id})" class="hover:opacity-70">×</button>
                            </span>
                        `).join('')
                    }
                </div>
            </div>
        `;
    }).join('');
}

function calcSegmentReach(interests) {
    if (!interests || interests.length === 0) return 0;
    
    const reaches = interests.map(i => i.reach).sort((a, b) => b - a);
    let total = reaches[0];
    
    for (let i = 1; i < reaches.length; i++) {
        total += Math.floor(reaches[i] * 0.30 / i);
    }
    
    return Math.min(total, 35000000);
}

function calcUnion() {
    const allInterests = new Map();
    segments.forEach(seg => {
        seg.interests.forEach(int => {
            if (!allInterests.has(int.id)) {
                allInterests.set(int.id, int);
            }
        });
    });
    
    return calcSegmentReach(Array.from(allInterests.values()));
}

function calcIntersection() {
    const validSegs = segments.filter(s => s.interests.length > 0);
    if (validSegs.length < 2) return 0;
    
    const reaches = validSegs.map(s => calcSegmentReach(s.interests));
    const minReach = Math.min(...reaches);
    
    // Segment sayısına göre kesişim oranı
    let ratio;
    if (validSegs.length === 2) ratio = 0.25;
    else if (validSegs.length === 3) ratio = 0.15;
    else ratio = 0.10;
    
    return Math.floor(minReach * ratio);
}

function updateAll() {
    updateReachList();
    updateTotals();
    drawVenn();
}

function updateReachList() {
    const container = document.getElementById('reach-list');
    const validSegs = segments.filter(s => s.interests.length > 0);
    
    if (validSegs.length === 0) {
        container.innerHTML = '<p class="text-slate-500 text-sm text-center py-4">Segmentlere interest ekleyin</p>';
        return;
    }
    
    const segsWithReach = validSegs.map(s => ({
        ...s,
        reach: calcSegmentReach(s.interests)
    })).sort((a, b) => b.reach - a.reach);
    
    const maxReach = segsWithReach[0]?.reach || 1;
    
    container.innerHTML = segsWithReach.map(seg => {
        const pct = (seg.reach / maxReach * 100).toFixed(0);
        return `
            <div class="relative overflow-hidden rounded-lg">
                <div class="absolute inset-0 opacity-20 rounded-lg" style="background: ${seg.color}; width: ${pct}%"></div>
                <div class="relative flex items-center justify-between p-2">
                    <div class="flex items-center gap-2">
                        <div class="w-3 h-3 rounded-full" style="background: ${seg.color}"></div>
                        <span class="text-sm">${seg.name}</span>
                    </div>
                    <span class="font-semibold" style="color: ${seg.color}">${(seg.reach / 1000000).toFixed(2)}M</span>
                </div>
            </div>
        `;
    }).join('');
}

function updateTotals() {
    const union = calcUnion();
    const intersection = calcIntersection();
    
    document.getElementById('union-reach').textContent = union > 0 ? (union / 1000000).toFixed(2) + 'M' : '0';
    document.getElementById('intersection-reach').textContent = intersection > 0 ? (intersection / 1000000).toFixed(2) + 'M' : '0';
}

function drawVenn() {
    const svg = document.getElementById('venn');
    const validSegs = segments.filter(s => s.interests.length > 0);
    
    if (validSegs.length === 0) {
        svg.innerHTML = `
            <text x="200" y="140" text-anchor="middle" fill="#64748b" font-size="14">
                Segmentlere interest ekleyin
            </text>
        `;
        return;
    }
    
    let html = '';
    
    // Reach değerlerini hesapla
    const segsData = validSegs.map(s => ({
        ...s,
        reach: calcSegmentReach(s.interests)
    }));
    
    const union = calcUnion();
    const intersection = calcIntersection();
    
    if (validSegs.length === 1) {
        const seg = segsData[0];
        const r = Math.min(80, Math.max(40, seg.reach / 500000));
        
        html += `
            <circle cx="200" cy="120" r="${r}" fill="${seg.color}" fill-opacity="0.3" stroke="${seg.color}" stroke-width="3" class="venn-circle"/>
            <text x="200" y="115" text-anchor="middle" fill="white" font-size="12" font-weight="bold">${seg.name}</text>
            <text x="200" y="135" text-anchor="middle" fill="${seg.color}" font-size="14" font-weight="bold">${(seg.reach/1000000).toFixed(1)}M</text>
        `;
    } else if (validSegs.length === 2) {
        const s1 = segsData[0], s2 = segsData[1];
        
        html += `
            <circle cx="150" cy="120" r="70" fill="${s1.color}" fill-opacity="0.3" stroke="${s1.color}" stroke-width="3" class="venn-circle"/>
            <circle cx="250" cy="120" r="70" fill="${s2.color}" fill-opacity="0.3" stroke="${s2.color}" stroke-width="3" class="venn-circle"/>
            
            <text x="110" y="100" text-anchor="middle" fill="white" font-size="11">${s1.name}</text>
            <text x="110" y="120" text-anchor="middle" fill="${s1.color}" font-size="13" font-weight="bold">${(s1.reach/1000000).toFixed(1)}M</text>
            
            <text x="290" y="100" text-anchor="middle" fill="white" font-size="11">${s2.name}</text>
            <text x="290" y="120" text-anchor="middle" fill="${s2.color}" font-size="13" font-weight="bold">${(s2.reach/1000000).toFixed(1)}M</text>
            
            <text x="200" y="115" text-anchor="middle" fill="#a855f7" font-size="11">Kesişim</text>
            <text x="200" y="135" text-anchor="middle" fill="#a855f7" font-size="15" font-weight="bold">${(intersection/1000000).toFixed(2)}M</text>
        `;
    } else if (validSegs.length >= 3) {
        const s1 = segsData[0], s2 = segsData[1], s3 = segsData[2];
        
        html += `
            <circle cx="160" cy="100" r="60" fill="${s1.color}" fill-opacity="0.25" stroke="${s1.color}" stroke-width="3" class="venn-circle"/>
            <circle cx="240" cy="100" r="60" fill="${s2.color}" fill-opacity="0.25" stroke="${s2.color}" stroke-width="3" class="venn-circle"/>
            <circle cx="200" cy="170" r="60" fill="${s3.color}" fill-opacity="0.25" stroke="${s3.color}" stroke-width="3" class="venn-circle"/>
            
            <text x="120" y="80" text-anchor="middle" fill="white" font-size="10">${s1.name.substring(0,10)}</text>
            <text x="120" y="95" text-anchor="middle" fill="${s1.color}" font-size="11" font-weight="bold">${(s1.reach/1000000).toFixed(1)}M</text>
            
            <text x="280" y="80" text-anchor="middle" fill="white" font-size="10">${s2.name.substring(0,10)}</text>
            <text x="280" y="95" text-anchor="middle" fill="${s2.color}" font-size="11" font-weight="bold">${(s2.reach/1000000).toFixed(1)}M</text>
            
            <text x="200" y="220" text-anchor="middle" fill="white" font-size="10">${s3.name.substring(0,10)}</text>
            <text x="200" y="235" text-anchor="middle" fill="${s3.color}" font-size="11" font-weight="bold">${(s3.reach/1000000).toFixed(1)}M</text>
            
            <text x="200" y="125" text-anchor="middle" fill="#a855f7" font-size="10">Kesişim</text>
            <text x="200" y="142" text-anchor="middle" fill="#a855f7" font-size="14" font-weight="bold">${(intersection/1000000).toFixed(2)}M</text>
        `;
    }
    
    // Birleşim bilgisi
    html += `
        <text x="200" y="270" text-anchor="middle" fill="#64748b" font-size="11">
            Toplam Birleşim: ${(union/1000000).toFixed(2)}M
        </text>
    `;
    
    svg.innerHTML = html;
}

function exportJSON() {
    const data = {
        campaign: "PO Premium Market",
        segments: segments.map(s => ({
            name: s.name,
            interests: s.interests,
            reach: calcSegmentReach(s.interests),
            meta_targeting: {
                geo_locations: { countries: ["TR"] },
                age_min: 25,
                age_max: 54,
                flexible_spec: [{ interests: s.interests.map(i => ({ id: i.id, name: i.name })) }]
            }
        })),
        union_reach: calcUnion(),
        intersection_reach: calcIntersection()
    };
    
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    alert('JSON kopyalandı!');
}

function copyIntersection() {
    const validSegs = segments.filter(s => s.interests.length > 0);
    
    const spec = {
        name: "PO Premium - Kesişim Kitlesi",
        description: "Tüm segmentlerde ortak hedef kitle (AND mantığı)",
        reach: calcIntersection(),
        meta_targeting: {
            geo_locations: { countries: ["TR"] },
            age_min: 25,
            age_max: 54,
            flexible_spec: validSegs.map(s => ({
                interests: s.interests.map(i => ({ id: i.id, name: i.name }))
            }))
        }
    };
    
    navigator.clipboard.writeText(JSON.stringify(spec, null, 2));
    alert('Kesişim targeting kopyalandı!\\n\\nMeta Ads Manager\'da:\\nHer flexible_spec grubu AND koşulu oluşturur.');
}
</script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/calc', methods=['POST'])
def api_calc():
    d = request.json
    segs = d.get('segments', [])
    
    results = {
        "segments": [],
        "union": calc_union(segs),
        "intersection": calc_intersection(segs)
    }
    
    for seg in segs:
        if seg.get('interests'):
            reach = calc_segment_reach([i['id'] for i in seg['interests']])
            results['segments'].append({
                'id': seg.get('id'),
                'name': seg.get('name'),
                'reach': reach
            })
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
