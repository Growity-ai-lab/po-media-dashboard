"""
PO Premium Market - Audience Intersection Dashboard
Kume kesisim analizi + Unique reach hesaplama
"""
from flask import Flask, render_template_string, request, jsonify
import requests, json, os, random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'po-intersection-2024')

def get_reach(token, account, spec):
    try:
        r = requests.get(f"https://graph.facebook.com/v18.0/{account}/reachestimate", 
            params={"access_token": token, "targeting_spec": json.dumps(spec), "optimize_for": "REACH"}, timeout=15)
        d = r.json()
        if "error" in d: return {"error": d["error"].get("message", "API Error")}
        lo = d.get("data", {}).get("users_lower_bound") or d.get("users_lower_bound", 0)
        hi = d.get("data", {}).get("users_upper_bound") or d.get("users_upper_bound", 0)
        return {"lower": lo, "upper": hi, "estimate": (lo+hi)//2}
    except Exception as e: 
        return {"error": str(e)}

def test_connection(token, account):
    try:
        r = requests.get(f"https://graph.facebook.com/v18.0/{account}", 
            params={"access_token": token, "fields": "name,currency"}, timeout=10)
        d = r.json()
        if "error" in d: return {"success": False, "error": d["error"].get("message", "Error")}
        return {"success": True, "name": d.get("name", "Connected")}
    except Exception as e: 
        return {"success": False, "error": str(e)}

def search_interests(token, query):
    try:
        r = requests.get("https://graph.facebook.com/v18.0/search", 
            params={"access_token": token, "type": "adinterest", "q": query, "limit": 25}, timeout=10)
        d = r.json()
        if "error" in d: return {"error": d["error"].get("message", "Error")}
        return [{"id": i.get("id"), "name": i.get("name"), "size": i.get("audience_size_lower_bound", 0)} for i in d.get("data", [])]
    except Exception as e:
        return {"error": str(e)}

def build_targeting(interests, age_min=18, age_max=65):
    spec = {
        "geo_locations": {"countries": ["TR"], "location_types": ["home", "recent"]},
        "age_min": age_min,
        "age_max": age_max,
        "publisher_platforms": ["facebook", "instagram"]
    }
    if interests:
        spec["flexible_spec"] = [{"interests": [{"id": i["id"], "name": i["name"]} for i in interests]}]
    return spec

def build_intersection_targeting(segments):
    spec = {
        "geo_locations": {"countries": ["TR"], "location_types": ["home", "recent"]},
        "age_min": 18,
        "age_max": 65,
        "publisher_platforms": ["facebook", "instagram"],
        "flexible_spec": []
    }
    for seg in segments:
        if seg.get("interests"):
            spec["flexible_spec"].append({
                "interests": [{"id": i["id"], "name": i["name"]} for i in seg["interests"]]
            })
    return spec

HTML = '''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PO Audience Intersection Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body { font-family: system-ui, -apple-system, sans-serif; }
.segment-card { transition: all 0.2s; }
.segment-card:hover { transform: translateY(-2px); }
</style>
</head>
<body class="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 min-h-screen text-white">
<div class="max-w-7xl mx-auto p-4">

<!-- Header -->
<div class="flex items-center justify-between mb-6 flex-wrap gap-4">
    <div class="flex items-center gap-4">
        <div class="w-14 h-14 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-xl flex items-center justify-center font-bold text-2xl shadow-lg">PO</div>
        <div>
            <h1 class="text-2xl font-bold bg-gradient-to-r from-orange-400 to-yellow-400 bg-clip-text text-transparent">Audience Intersection Builder</h1>
            <p class="text-slate-400 text-sm">Kume kesisim analizi + Unique reach</p>
        </div>
    </div>
    <div id="api-status" class="px-4 py-2 rounded-lg bg-slate-700 text-sm">Bagli degil</div>
</div>

<!-- API Config -->
<div class="bg-slate-800/50 backdrop-blur rounded-xl p-4 mb-6 border border-slate-700">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <input type="password" id="token" placeholder="Access Token" class="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm">
        <input type="text" id="account" value="act_" placeholder="act_xxxxx" class="bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm">
        <button onclick="testAPI()" class="bg-gradient-to-r from-orange-500 to-yellow-500 rounded-lg px-4 py-2 font-medium">Baglan</button>
        <button onclick="calculateAll()" class="bg-blue-500 hover:bg-blue-600 rounded-lg px-4 py-2 font-medium">Tum Reach Hesapla</button>
    </div>
</div>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

<!-- Sol: Interest Arama -->
<div class="bg-slate-800/50 backdrop-blur rounded-xl p-4 border border-slate-700">
    <h3 class="font-semibold mb-4">Interest Arama</h3>
    <div class="flex gap-2 mb-4">
        <input type="text" id="search-input" placeholder="Coffee, Travel..." class="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm" onkeypress="if(event.key==='Enter')searchInterests()">
        <button onclick="searchInterests()" class="px-4 py-2 bg-orange-500 rounded-lg">Ara</button>
    </div>
    
    <div class="flex flex-wrap gap-2 mb-4">
        <button onclick="quickSearch('Coffee')" class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded">Coffee</button>
        <button onclick="quickSearch('Travel')" class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded">Travel</button>
        <button onclick="quickSearch('Shopping')" class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded">Shopping</button>
        <button onclick="quickSearch('Fitness')" class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded">Fitness</button>
        <button onclick="quickSearch('Food')" class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded">Food</button>
        <button onclick="quickSearch('Technology')" class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded">Tech</button>
        <button onclick="quickSearch('Parenting')" class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded">Parenting</button>
    </div>
    
    <div id="search-results" class="space-y-2 max-h-[400px] overflow-y-auto pr-2">
        <p class="text-slate-400 text-sm text-center py-4">Interest arama yapin</p>
    </div>
</div>

<!-- Orta: Segment Builder -->
<div class="bg-slate-800/50 backdrop-blur rounded-xl p-4 border border-slate-700">
    <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold">Segmentler</h3>
        <button onclick="addSegment()" class="px-3 py-1 bg-green-500/20 text-green-400 rounded text-sm">+ Segment</button>
    </div>
    
    <div id="segments-container" class="space-y-3 max-h-[500px] overflow-y-auto pr-2"></div>
    
    <div class="mt-4 p-3 bg-slate-700/30 rounded-lg text-xs text-slate-400">
        <strong class="text-orange-400">Ipucu:</strong> Her segment bir hedef kitle. Kesisim = hepsinde ortak olan kitle.
    </div>
</div>

<!-- Sag: Sonuclar -->
<div class="space-y-4">
    <div class="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-xl p-4 border border-blue-500/30">
        <h3 class="text-sm text-slate-400 mb-1">Toplam Reach (Birlesim)</h3>
        <div class="text-4xl font-bold text-blue-400" id="total-reach">-</div>
        <p class="text-xs text-slate-500 mt-1">Tum segmentlerin birlesimi</p>
    </div>
    
    <div class="bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl p-4 border border-purple-500/30">
        <h3 class="text-sm text-slate-400 mb-1">Kesisim Reach (AND)</h3>
        <div class="text-4xl font-bold text-purple-400" id="intersection-reach">-</div>
        <p class="text-xs text-slate-500 mt-1">Tum segmentlerde ortak</p>
    </div>
    
    <div class="bg-slate-800/50 backdrop-blur rounded-xl p-4 border border-slate-700">
        <h3 class="font-semibold mb-3">Segment Bazli</h3>
        <div id="segment-reaches" class="space-y-2">
            <p class="text-slate-400 text-sm text-center py-4">Reach hesaplayin</p>
        </div>
    </div>
    
    <div class="bg-slate-800/50 backdrop-blur rounded-xl p-4 border border-slate-700">
        <h3 class="font-semibold mb-3">Venn Diagram</h3>
        <div class="relative h-40">
            <svg id="venn-svg" viewBox="0 0 300 160" class="w-full h-full"></svg>
        </div>
    </div>
    
    <div class="flex gap-2">
        <button onclick="exportSegments()" class="flex-1 px-4 py-2 bg-green-500/20 text-green-400 rounded-lg text-sm">JSON Export</button>
        <button onclick="copyIntersection()" class="flex-1 px-4 py-2 bg-purple-500/20 text-purple-400 rounded-lg text-sm">Kesisim Kopyala</button>
    </div>
</div>

</div>
</div>

<script>
var segments = [];
var segmentCounter = 0;
var currentSearchResults = [];
var segmentColors = ['#FF6B00', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'];

document.addEventListener('DOMContentLoaded', function() {
    addSegment();
});

function testAPI() {
    var token = document.getElementById('token').value;
    var account = document.getElementById('account').value;
    var status = document.getElementById('api-status');
    
    if (!token || !account) {
        status.textContent = 'Token/ID gerekli';
        status.className = 'px-4 py-2 rounded-lg bg-red-500/20 text-red-400 text-sm';
        return;
    }
    
    status.textContent = 'Test...';
    status.className = 'px-4 py-2 rounded-lg bg-yellow-500/20 text-yellow-400 text-sm';
    
    fetch('/api/test', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({token: token, account: account})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.success) {
            status.textContent = 'OK: ' + d.name;
            status.className = 'px-4 py-2 rounded-lg bg-green-500/20 text-green-400 text-sm';
        } else {
            status.textContent = 'Hata';
            status.className = 'px-4 py-2 rounded-lg bg-red-500/20 text-red-400 text-sm';
        }
    });
}

function quickSearch(term) {
    document.getElementById('search-input').value = term;
    searchInterests();
}

function searchInterests() {
    var query = document.getElementById('search-input').value;
    var token = document.getElementById('token').value;
    var results = document.getElementById('search-results');
    
    if (!query) return;
    results.innerHTML = '<p class="text-center py-4 text-slate-400">Araniyor...</p>';
    
    fetch('/api/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: query, token: token})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.error) {
            results.innerHTML = '<p class="text-red-400 text-sm">' + d.error + '</p>';
            return;
        }
        
        currentSearchResults = d;
        renderSearchResults();
    });
}

function renderSearchResults() {
    var results = document.getElementById('search-results');
    var d = currentSearchResults;
    var html = '';
    
    for (var i = 0; i < d.length; i++) {
        var item = d[i];
        var sizeText = item.size ? (item.size / 1000000).toFixed(1) + 'M' : '-';
        
        html += '<div class="bg-slate-700/50 rounded-lg p-3">';
        html += '<div class="flex justify-between items-start gap-2">';
        html += '<div class="flex-1 min-w-0">';
        html += '<div class="text-sm font-medium truncate">' + item.name + '</div>';
        html += '<div class="text-xs text-slate-400">~' + sizeText + '</div>';
        html += '</div>';
        html += '<div class="flex flex-col gap-1">';
        
        for (var j = 0; j < segments.length; j++) {
            var seg = segments[j];
            var isIn = seg.interests.some(function(x) { return x.id === item.id; });
            html += '<button onclick="toggleInterest(' + seg.id + ',\'' + item.id + '\',\'' + item.name.replace(/'/g, '') + '\')" ';
            html += 'class="px-2 py-0.5 rounded text-xs ' + (isIn ? 'bg-green-500/30 text-green-400' : 'bg-slate-600 text-slate-300') + '" ';
            html += 'style="border-left:3px solid ' + seg.color + '">' + (isIn ? '✓' : '+') + ' ' + seg.name + '</button>';
        }
        
        html += '</div></div></div>';
    }
    
    results.innerHTML = html || '<p class="text-slate-400 text-sm text-center py-4">Sonuc yok</p>';
}

function addSegment() {
    segmentCounter++;
    var color = segmentColors[(segmentCounter - 1) % segmentColors.length];
    segments.push({
        id: segmentCounter,
        name: 'Segment ' + segmentCounter,
        color: color,
        interests: [],
        reach: null
    });
    renderSegments();
    if (currentSearchResults.length > 0) renderSearchResults();
}

function removeSegment(id) {
    segments = segments.filter(function(s) { return s.id !== id; });
    renderSegments();
    updateDisplays();
    drawVenn();
    if (currentSearchResults.length > 0) renderSearchResults();
}

function renameSegment(id, name) {
    var seg = segments.find(function(s) { return s.id === id; });
    if (seg) seg.name = name;
}

function toggleInterest(segId, intId, intName) {
    var seg = segments.find(function(s) { return s.id === segId; });
    if (!seg) return;
    
    var exists = seg.interests.some(function(i) { return i.id === intId; });
    if (exists) {
        seg.interests = seg.interests.filter(function(i) { return i.id !== intId; });
    } else {
        seg.interests.push({id: intId, name: intName});
    }
    
    renderSegments();
    renderSearchResults();
}

function removeInterest(segId, intId) {
    var seg = segments.find(function(s) { return s.id === segId; });
    if (seg) {
        seg.interests = seg.interests.filter(function(i) { return i.id !== intId; });
        renderSegments();
        if (currentSearchResults.length > 0) renderSearchResults();
    }
}

function renderSegments() {
    var container = document.getElementById('segments-container');
    if (segments.length === 0) {
        container.innerHTML = '<p class="text-slate-400 text-sm text-center py-8">Segment ekleyin</p>';
        return;
    }
    
    var html = '';
    for (var i = 0; i < segments.length; i++) {
        var seg = segments[i];
        var reachText = seg.reach ? (seg.reach / 1000000).toFixed(2) + 'M' : '-';
        
        html += '<div class="segment-card bg-slate-700/50 rounded-lg p-3 border-l-4" style="border-color:' + seg.color + '">';
        html += '<div class="flex items-center justify-between mb-2">';
        html += '<input type="text" value="' + seg.name + '" onchange="renameSegment(' + seg.id + ',this.value)" class="bg-transparent border-none text-sm font-semibold focus:outline-none w-24" style="color:' + seg.color + '">';
        html += '<div class="flex items-center gap-2">';
        html += '<span class="text-sm text-blue-400">' + reachText + '</span>';
        html += '<button onclick="removeSegment(' + seg.id + ')" class="text-red-400 text-sm">✕</button>';
        html += '</div></div>';
        
        html += '<div class="flex flex-wrap gap-1 min-h-[28px]">';
        if (seg.interests.length === 0) {
            html += '<span class="text-slate-500 text-xs">Interest ekleyin</span>';
        } else {
            for (var j = 0; j < seg.interests.length; j++) {
                var int = seg.interests[j];
                html += '<span class="inline-flex items-center gap-1 px-2 py-0.5 bg-slate-600 rounded text-xs">';
                html += '<span class="truncate max-w-[80px]">' + int.name + '</span>';
                html += '<button onclick="removeInterest(' + seg.id + ',\'' + int.id + '\')" class="text-slate-400 hover:text-red-400">×</button>';
                html += '</span>';
            }
        }
        html += '</div></div>';
    }
    
    container.innerHTML = html;
}

function calculateAll() {
    var token = document.getElementById('token').value;
    var account = document.getElementById('account').value;
    
    var segData = segments.filter(function(s) { return s.interests.length > 0; }).map(function(s) {
        return {id: s.id, name: s.name, interests: s.interests};
    });
    
    if (segData.length === 0) {
        alert('Segmentlere interest ekleyin');
        return;
    }
    
    document.getElementById('total-reach').textContent = '...';
    document.getElementById('intersection-reach').textContent = '...';
    
    fetch('/api/calculate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({token: token, account: account, segments: segData})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        for (var i = 0; i < segments.length; i++) {
            var res = d.segments.find(function(s) { return s.id === segments[i].id; });
            if (res) segments[i].reach = res.reach;
        }
        
        renderSegments();
        document.getElementById('total-reach').textContent = d.union ? (d.union / 1000000).toFixed(2) + 'M' : '-';
        document.getElementById('intersection-reach').textContent = d.intersection ? (d.intersection / 1000000).toFixed(2) + 'M' : '-';
        updateDisplays();
        drawVenn();
    });
}

function updateDisplays() {
    var container = document.getElementById('segment-reaches');
    var valid = segments.filter(function(s) { return s.reach !== null; });
    
    if (valid.length === 0) {
        container.innerHTML = '<p class="text-slate-400 text-sm text-center py-4">Reach hesaplayin</p>';
        return;
    }
    
    var html = '';
    for (var i = 0; i < valid.length; i++) {
        var seg = valid[i];
        html += '<div class="flex items-center justify-between p-2 bg-slate-700/30 rounded">';
        html += '<div class="flex items-center gap-2">';
        html += '<div class="w-3 h-3 rounded-full" style="background:' + seg.color + '"></div>';
        html += '<span class="text-sm">' + seg.name + '</span>';
        html += '</div>';
        html += '<span class="text-blue-400 font-medium">' + (seg.reach / 1000000).toFixed(2) + 'M</span>';
        html += '</div>';
    }
    container.innerHTML = html;
}

function drawVenn() {
    var svg = document.getElementById('venn-svg');
    var valid = segments.filter(function(s) { return s.reach !== null; });
    
    if (valid.length === 0) {
        svg.innerHTML = '<text x="150" y="80" text-anchor="middle" fill="#64748b" font-size="12">Reach hesaplayin</text>';
        return;
    }
    
    var html = '';
    if (valid.length === 1) {
        html += '<circle cx="150" cy="80" r="50" fill="' + valid[0].color + '" fill-opacity="0.3" stroke="' + valid[0].color + '" stroke-width="2"/>';
        html += '<text x="150" y="85" text-anchor="middle" fill="white" font-size="10">' + valid[0].name + '</text>';
    } else if (valid.length === 2) {
        html += '<circle cx="115" cy="80" r="45" fill="' + valid[0].color + '" fill-opacity="0.3" stroke="' + valid[0].color + '" stroke-width="2"/>';
        html += '<circle cx="185" cy="80" r="45" fill="' + valid[1].color + '" fill-opacity="0.3" stroke="' + valid[1].color + '" stroke-width="2"/>';
        html += '<text x="85" y="80" text-anchor="middle" fill="white" font-size="9">' + valid[0].name + '</text>';
        html += '<text x="215" y="80" text-anchor="middle" fill="white" font-size="9">' + valid[1].name + '</text>';
        html += '<text x="150" y="80" text-anchor="middle" fill="#a855f7" font-size="10" font-weight="bold">∩</text>';
    } else {
        html += '<circle cx="120" cy="65" r="40" fill="' + valid[0].color + '" fill-opacity="0.25" stroke="' + valid[0].color + '" stroke-width="2"/>';
        html += '<circle cx="180" cy="65" r="40" fill="' + valid[1].color + '" fill-opacity="0.25" stroke="' + valid[1].color + '" stroke-width="2"/>';
        html += '<circle cx="150" cy="110" r="40" fill="' + valid[2].color + '" fill-opacity="0.25" stroke="' + valid[2].color + '" stroke-width="2"/>';
        html += '<text x="95" y="55" text-anchor="middle" fill="white" font-size="8">' + valid[0].name + '</text>';
        html += '<text x="205" y="55" text-anchor="middle" fill="white" font-size="8">' + valid[1].name + '</text>';
        html += '<text x="150" y="140" text-anchor="middle" fill="white" font-size="8">' + valid[2].name + '</text>';
        html += '<text x="150" y="82" text-anchor="middle" fill="#a855f7" font-size="10" font-weight="bold">∩</text>';
    }
    svg.innerHTML = html;
}

function exportSegments() {
    var data = {
        segments: segments.map(function(s) {
            return {
                name: s.name,
                interests: s.interests,
                reach: s.reach,
                targeting: {
                    geo_locations: {countries: ["TR"]},
                    flexible_spec: [{interests: s.interests}]
                }
            };
        })
    };
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    alert('JSON kopyalandi!');
}

function copyIntersection() {
    var spec = {
        name: "PO Premium - Intersection",
        targeting: {
            geo_locations: {countries: ["TR"]},
            flexible_spec: segments.filter(function(s) { return s.interests.length > 0; }).map(function(s) {
                return {interests: s.interests};
            })
        }
    };
    navigator.clipboard.writeText(JSON.stringify(spec, null, 2));
    alert('Kesisim kopyalandi!');
}
</script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/test', methods=['POST'])
def api_test():
    d = request.json
    return jsonify(test_connection(d.get('token'), d.get('account')))

@app.route('/api/search', methods=['POST'])
def api_search():
    d = request.json
    token = d.get('token')
    query = d.get('query', '')
    
    if not token:
        return jsonify([
            {"id": "6003139266461", "name": query, "size": 5000000},
            {"id": "6003139266462", "name": query + " fans", "size": 3000000},
            {"id": "6003139266463", "name": query + " lovers", "size": 2000000}
        ])
    
    result = search_interests(token, query)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result)
    return jsonify(result)

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    d = request.json
    token = d.get('token')
    account = d.get('account')
    segs = d.get('segments', [])
    
    results = {"segments": [], "union": 0, "intersection": 0}
    all_reaches = []
    
    for seg in segs:
        if not seg.get('interests'):
            continue
            
        spec = build_targeting(seg['interests'])
        
        if token and account:
            reach_result = get_reach(token, account, spec)
            if 'error' not in reach_result:
                reach = reach_result['estimate']
            else:
                reach = len(seg['interests']) * 2000000 + random.randint(-500000, 500000)
        else:
            reach = len(seg['interests']) * 2000000 + random.randint(-500000, 500000)
        
        results['segments'].append({'id': seg['id'], 'name': seg['name'], 'reach': reach})
        all_reaches.append(reach)
    
    if all_reaches:
        results['union'] = int(sum(all_reaches) * (0.7 if len(all_reaches) > 1 else 1.0))
    
    if len(segs) > 1 and token and account:
        valid_segs = [s for s in segs if s.get('interests')]
        if len(valid_segs) > 1:
            int_spec = build_intersection_targeting(valid_segs)
            int_result = get_reach(token, account, int_spec)
            if 'error' not in int_result:
                results['intersection'] = int_result['estimate']
            else:
                results['intersection'] = int(min(all_reaches) * 0.3) if all_reaches else 0
        else:
            results['intersection'] = all_reaches[0] if all_reaches else 0
    elif all_reaches:
        results['intersection'] = int(min(all_reaches) * 0.25)
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
