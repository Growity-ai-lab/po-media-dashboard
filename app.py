"""
PO Premium - Audience Intersection Builder
"""
from flask import Flask, render_template_string, request, jsonify
import json, os

app = Flask(__name__)

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
        {"id": "i013", "name": "Health Wellness", "reach": 15000000},
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

HTML = '''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PO Premium Audience Builder</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
// GLOBAL DATA & STATE
var INTERESTS_DATA = %s;
var segments = [];
var segmentId = 0;
var COLORS = ["#FF6B00", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899"];
var currentCategory = null;

// FUNCTIONS - defined before DOM loads
function loadCategory(cat) {
    currentCategory = cat;
    var items = INTERESTS_DATA[cat] || [];
    var titles = {
        coffee: "KAHVE", food: "YEMEK", travel: "SEYAHAT",
        family: "AILE", wellness: "SAGLIK", tech: "TEKNOLOJI",
        shopping: "ALISVERIS", entertainment: "EGLENCE",
        auto: "OTOMOTIV", premium: "PREMIUM"
    };
    document.getElementById("cat-title").textContent = titles[cat] || "INTERESTS";
    renderInterests(items);
}

function renderInterests(items) {
    var container = document.getElementById("interest-list");
    if (!items || items.length === 0) {
        container.innerHTML = "<p class='text-slate-500 text-sm'>Kategori secin</p>";
        return;
    }
    
    var html = "";
    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        var reachM = (item.reach / 1000000).toFixed(1);
        html += "<div class='bg-slate-700/50 rounded p-3 mb-2'>";
        html += "<div class='mb-2'><div class='text-sm font-medium'>" + item.name + "</div>";
        html += "<div class='text-xs text-slate-400'>" + reachM + "M reach</div></div>";
        html += "<div class='flex flex-wrap gap-1'>";
        
        for (var j = 0; j < segments.length; j++) {
            var seg = segments[j];
            var isIn = isInterestInSegment(item.id, seg.id);
            if (isIn) {
                html += "<button onclick=\"toggleInt('" + item.id + "','" + item.name + "'," + item.reach + "," + seg.id + ")\" ";
                html += "class='px-2 py-1 rounded text-xs text-white' style='background:" + seg.color + "'>";
                html += "\\u2713 " + seg.name + "</button>";
            } else {
                html += "<button onclick=\"toggleInt('" + item.id + "','" + item.name + "'," + item.reach + "," + seg.id + ")\" ";
                html += "class='px-2 py-1 rounded text-xs bg-slate-600 text-slate-300 hover:bg-slate-500'>";
                html += "+ " + seg.name + "</button>";
            }
        }
        html += "</div></div>";
    }
    container.innerHTML = html;
}

function isInterestInSegment(intId, segId) {
    for (var i = 0; i < segments.length; i++) {
        if (segments[i].id === segId) {
            for (var j = 0; j < segments[i].interests.length; j++) {
                if (segments[i].interests[j].id === intId) return true;
            }
        }
    }
    return false;
}

function addSegment() {
    segmentId++;
    var color = COLORS[(segmentId - 1) %% COLORS.length];
    segments.push({
        id: segmentId,
        name: "Segment " + segmentId,
        color: color,
        interests: []
    });
    renderSegments();
    updateAll();
    if (currentCategory) renderInterests(INTERESTS_DATA[currentCategory]);
}

function removeSegment(id) {
    var newSegs = [];
    for (var i = 0; i < segments.length; i++) {
        if (segments[i].id !== id) newSegs.push(segments[i]);
    }
    segments = newSegs;
    renderSegments();
    updateAll();
    if (currentCategory) renderInterests(INTERESTS_DATA[currentCategory]);
}

function toggleInt(intId, intName, intReach, segId) {
    var seg = null;
    for (var i = 0; i < segments.length; i++) {
        if (segments[i].id === segId) { seg = segments[i]; break; }
    }
    if (!seg) return;
    
    var found = -1;
    for (var i = 0; i < seg.interests.length; i++) {
        if (seg.interests[i].id === intId) { found = i; break; }
    }
    
    if (found >= 0) {
        seg.interests.splice(found, 1);
    } else {
        seg.interests.push({ id: intId, name: intName, reach: intReach });
    }
    
    renderSegments();
    updateAll();
    if (currentCategory) renderInterests(INTERESTS_DATA[currentCategory]);
}

function removeInt(intId, segId) {
    for (var i = 0; i < segments.length; i++) {
        if (segments[i].id === segId) {
            var newInts = [];
            for (var j = 0; j < segments[i].interests.length; j++) {
                if (segments[i].interests[j].id !== intId) {
                    newInts.push(segments[i].interests[j]);
                }
            }
            segments[i].interests = newInts;
            break;
        }
    }
    renderSegments();
    updateAll();
    if (currentCategory) renderInterests(INTERESTS_DATA[currentCategory]);
}

function renderSegments() {
    var container = document.getElementById("segment-list");
    if (segments.length === 0) {
        container.innerHTML = "<p class='text-slate-500 text-sm text-center py-4'>Segment ekleyin</p>";
        return;
    }
    
    var html = "";
    for (var i = 0; i < segments.length; i++) {
        var seg = segments[i];
        var reach = calcSegmentReach(seg.interests);
        var reachText = reach > 0 ? (reach / 1000000).toFixed(2) + "M" : "-";
        
        html += "<div class='bg-slate-700/30 rounded-lg p-3 mb-2' style='border-left:4px solid " + seg.color + "'>";
        html += "<div class='flex justify-between items-center mb-2'>";
        html += "<div class='flex items-center gap-2'>";
        html += "<div class='w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white' style='background:" + seg.color + "'>" + (i+1) + "</div>";
        html += "<span class='text-sm font-semibold'>" + seg.name + "</span></div>";
        html += "<div class='flex items-center gap-2'>";
        html += "<span class='text-sm font-bold' style='color:" + seg.color + "'>" + reachText + "</span>";
        html += "<button onclick='removeSegment(" + seg.id + ")' class='text-red-400 text-lg leading-none'>\\u00D7</button>";
        html += "</div></div>";
        
        html += "<div class='flex flex-wrap gap-1 min-h-[28px]'>";
        if (seg.interests.length === 0) {
            html += "<span class='text-slate-500 text-xs'>Kategoriden interest ekleyin</span>";
        } else {
            for (var j = 0; j < seg.interests.length; j++) {
                var int = seg.interests[j];
                html += "<span class='inline-flex items-center gap-1 px-2 py-1 rounded text-xs' ";
                html += "style='background:" + seg.color + "33; color:" + seg.color + "'>";
                html += int.name;
                html += "<button onclick=\"removeInt('" + int.id + "'," + seg.id + ")\" class='ml-1 opacity-70 hover:opacity-100'>\\u00D7</button>";
                html += "</span>";
            }
        }
        html += "</div></div>";
    }
    container.innerHTML = html;
}

function calcSegmentReach(interests) {
    if (!interests || interests.length === 0) return 0;
    var reaches = [];
    for (var i = 0; i < interests.length; i++) {
        reaches.push(interests[i].reach);
    }
    reaches.sort(function(a, b) { return b - a; });
    var total = reaches[0];
    for (var i = 1; i < reaches.length; i++) {
        total += Math.floor(reaches[i] * 0.30 / i);
    }
    return Math.min(total, 35000000);
}

function calcUnion() {
    var allInts = {};
    for (var i = 0; i < segments.length; i++) {
        for (var j = 0; j < segments[i].interests.length; j++) {
            var int = segments[i].interests[j];
            allInts[int.id] = int;
        }
    }
    var arr = [];
    for (var key in allInts) {
        arr.push(allInts[key]);
    }
    return calcSegmentReach(arr);
}

function calcIntersection() {
    var valid = [];
    for (var i = 0; i < segments.length; i++) {
        if (segments[i].interests.length > 0) valid.push(segments[i]);
    }
    if (valid.length < 2) return 0;
    
    var reaches = [];
    for (var i = 0; i < valid.length; i++) {
        reaches.push(calcSegmentReach(valid[i].interests));
    }
    var minReach = Math.min.apply(null, reaches);
    
    var ratio = 0.10;
    if (valid.length === 2) ratio = 0.25;
    else if (valid.length === 3) ratio = 0.15;
    
    return Math.floor(minReach * ratio);
}

function updateAll() {
    var union = calcUnion();
    var inter = calcIntersection();
    
    document.getElementById("union-val").textContent = union > 0 ? (union / 1000000).toFixed(2) + "M" : "0";
    document.getElementById("inter-val").textContent = inter > 0 ? (inter / 1000000).toFixed(2) + "M" : "0";
    
    renderReachList();
    drawVenn();
}

function renderReachList() {
    var container = document.getElementById("reach-list");
    var valid = [];
    for (var i = 0; i < segments.length; i++) {
        if (segments[i].interests.length > 0) {
            valid.push({
                name: segments[i].name,
                color: segments[i].color,
                reach: calcSegmentReach(segments[i].interests)
            });
        }
    }
    
    if (valid.length === 0) {
        container.innerHTML = "<p class='text-slate-500 text-sm text-center py-2'>Interest ekleyin</p>";
        return;
    }
    
    valid.sort(function(a, b) { return b.reach - a.reach; });
    var maxR = valid[0].reach;
    
    var html = "";
    for (var i = 0; i < valid.length; i++) {
        var s = valid[i];
        var pct = Math.round(s.reach / maxR * 100);
        html += "<div class='relative overflow-hidden rounded mb-1'>";
        html += "<div class='absolute inset-0 opacity-20' style='background:" + s.color + "; width:" + pct + "%%'></div>";
        html += "<div class='relative flex justify-between p-2'>";
        html += "<div class='flex items-center gap-2'><div class='w-3 h-3 rounded-full' style='background:" + s.color + "'></div>";
        html += "<span class='text-sm'>" + s.name + "</span></div>";
        html += "<span class='font-semibold' style='color:" + s.color + "'>" + (s.reach / 1000000).toFixed(2) + "M</span>";
        html += "</div></div>";
    }
    container.innerHTML = html;
}

function drawVenn() {
    var svg = document.getElementById("venn");
    var valid = [];
    for (var i = 0; i < segments.length; i++) {
        if (segments[i].interests.length > 0) {
            valid.push({
                name: segments[i].name,
                color: segments[i].color,
                reach: calcSegmentReach(segments[i].interests)
            });
        }
    }
    
    if (valid.length === 0) {
        svg.innerHTML = "<text x='200' y='125' text-anchor='middle' fill='#64748b' font-size='14'>Interest ekleyin</text>";
        return;
    }
    
    var inter = calcIntersection();
    var union = calcUnion();
    var html = "";
    
    if (valid.length === 1) {
        var s = valid[0];
        html += "<circle cx='200' cy='110' r='70' fill='" + s.color + "' fill-opacity='0.3' stroke='" + s.color + "' stroke-width='3'/>";
        html += "<text x='200' y='100' text-anchor='middle' fill='white' font-size='12' font-weight='bold'>" + s.name + "</text>";
        html += "<text x='200' y='125' text-anchor='middle' fill='" + s.color + "' font-size='16' font-weight='bold'>" + (s.reach/1000000).toFixed(1) + "M</text>";
    } else if (valid.length === 2) {
        var s1 = valid[0], s2 = valid[1];
        html += "<circle cx='145' cy='110' r='65' fill='" + s1.color + "' fill-opacity='0.3' stroke='" + s1.color + "' stroke-width='3'/>";
        html += "<circle cx='255' cy='110' r='65' fill='" + s2.color + "' fill-opacity='0.3' stroke='" + s2.color + "' stroke-width='3'/>";
        html += "<text x='100' y='100' text-anchor='middle' fill='white' font-size='10'>" + s1.name + "</text>";
        html += "<text x='100' y='120' text-anchor='middle' fill='" + s1.color + "' font-size='13' font-weight='bold'>" + (s1.reach/1000000).toFixed(1) + "M</text>";
        html += "<text x='300' y='100' text-anchor='middle' fill='white' font-size='10'>" + s2.name + "</text>";
        html += "<text x='300' y='120' text-anchor='middle' fill='" + s2.color + "' font-size='13' font-weight='bold'>" + (s2.reach/1000000).toFixed(1) + "M</text>";
        html += "<text x='200' y='100' text-anchor='middle' fill='#a855f7' font-size='9'>Kesisim</text>";
        html += "<text x='200' y='120' text-anchor='middle' fill='#a855f7' font-size='14' font-weight='bold'>" + (inter/1000000).toFixed(2) + "M</text>";
    } else {
        var s1 = valid[0], s2 = valid[1], s3 = valid[2];
        html += "<circle cx='155' cy='85' r='55' fill='" + s1.color + "' fill-opacity='0.25' stroke='" + s1.color + "' stroke-width='3'/>";
        html += "<circle cx='245' cy='85' r='55' fill='" + s2.color + "' fill-opacity='0.25' stroke='" + s2.color + "' stroke-width='3'/>";
        html += "<circle cx='200' cy='155' r='55' fill='" + s3.color + "' fill-opacity='0.25' stroke='" + s3.color + "' stroke-width='3'/>";
        html += "<text x='110' y='70' text-anchor='middle' fill='white' font-size='9'>" + s1.name.substring(0,8) + "</text>";
        html += "<text x='110' y='85' text-anchor='middle' fill='" + s1.color + "' font-size='11' font-weight='bold'>" + (s1.reach/1000000).toFixed(1) + "M</text>";
        html += "<text x='290' y='70' text-anchor='middle' fill='white' font-size='9'>" + s2.name.substring(0,8) + "</text>";
        html += "<text x='290' y='85' text-anchor='middle' fill='" + s2.color + "' font-size='11' font-weight='bold'>" + (s2.reach/1000000).toFixed(1) + "M</text>";
        html += "<text x='200' y='205' text-anchor='middle' fill='white' font-size='9'>" + s3.name.substring(0,8) + "</text>";
        html += "<text x='200' y='220' text-anchor='middle' fill='" + s3.color + "' font-size='11' font-weight='bold'>" + (s3.reach/1000000).toFixed(1) + "M</text>";
        html += "<text x='200' y='115' text-anchor='middle' fill='#a855f7' font-size='9'>Kesisim</text>";
        html += "<text x='200' y='132' text-anchor='middle' fill='#a855f7' font-size='13' font-weight='bold'>" + (inter/1000000).toFixed(2) + "M</text>";
    }
    
    html += "<text x='200' y='245' text-anchor='middle' fill='#64748b' font-size='11'>Birlesim: " + (union/1000000).toFixed(2) + "M</text>";
    svg.innerHTML = html;
}

function exportJSON() {
    var data = { campaign: "PO Premium", segments: [], union: calcUnion(), intersection: calcIntersection() };
    for (var i = 0; i < segments.length; i++) {
        data.segments.push({
            name: segments[i].name,
            interests: segments[i].interests,
            reach: calcSegmentReach(segments[i].interests)
        });
    }
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    alert("JSON kopyalandi!");
}

function copyIntersection() {
    var valid = [];
    for (var i = 0; i < segments.length; i++) {
        if (segments[i].interests.length > 0) valid.push(segments[i]);
    }
    var flexSpec = [];
    for (var i = 0; i < valid.length; i++) {
        flexSpec.push({ interests: valid[i].interests });
    }
    var spec = {
        name: "PO Premium Kesisim",
        reach: calcIntersection(),
        targeting: { geo_locations: { countries: ["TR"] }, flexible_spec: flexSpec }
    };
    navigator.clipboard.writeText(JSON.stringify(spec, null, 2));
    alert("Kesisim kopyalandi!");
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", function() {
    addSegment();
});
</script>
</head>
<body class="bg-slate-900 text-white min-h-screen p-4">
<div class="max-w-7xl mx-auto">

<div class="flex items-center gap-4 mb-6">
    <div class="w-12 h-12 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-xl flex items-center justify-center font-bold text-xl">PO</div>
    <div>
        <h1 class="text-xl font-bold text-orange-400">Premium Audience Builder</h1>
        <p class="text-slate-400 text-sm">Gercek Zamanli Kesisim Analizi</p>
    </div>
</div>

<div class="bg-orange-500/10 border border-orange-500/30 rounded-xl p-3 mb-6">
    <p class="text-sm">Kategoriden interest secin, segment butonlarina tiklayin. Venn ve reach anlik guncellenir.</p>
</div>

<div class="grid lg:grid-cols-12 gap-4">

<div class="lg:col-span-3 space-y-4">
    <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h3 class="text-sm text-slate-400 mb-3">KATEGORILER</h3>
        <div class="grid grid-cols-2 gap-2">
            <button onclick="loadCategory('coffee')" class="p-2 bg-slate-700 hover:bg-slate-600 rounded text-sm">&#9749; Kahve</button>
            <button onclick="loadCategory('food')" class="p-2 bg-slate-700 hover:bg-slate-600 rounded text-sm">&#127869; Yemek</button>
            <button onclick="loadCategory('travel')" class="p-2 bg-slate-700 hover:bg-slate-600 rounded text-sm">&#9992; Seyahat</button>
            <button onclick="loadCategory('family')" class="p-2 bg-slate-700 hover:bg-slate-600 rounded text-sm">&#128106; Aile</button>
            <button onclick="loadCategory('wellness')" class="p-2 bg-slate-700 hover:bg-slate-600 rounded text-sm">&#129495; Saglik</button>
            <button onclick="loadCategory('tech')" class="p-2 bg-slate-700 hover:bg-slate-600 rounded text-sm">&#128241; Teknoloji</button>
            <button onclick="loadCategory('shopping')" class="p-2 bg-slate-700 hover:bg-slate-600 rounded text-sm">&#128722; Alisveris</button>
            <button onclick="loadCategory('entertainment')" class="p-2 bg-slate-700 hover:bg-slate-600 rounded text-sm">&#127916; Eglence</button>
            <button onclick="loadCategory('auto')" class="p-2 bg-slate-700 hover:bg-slate-600 rounded text-sm">&#128663; Otomotiv</button>
            <button onclick="loadCategory('premium')" class="p-2 bg-slate-700 hover:bg-slate-600 rounded text-sm">&#11088; Premium</button>
        </div>
    </div>
    
    <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h3 class="text-sm text-slate-400 mb-3" id="cat-title">INTERESTS</h3>
        <div id="interest-list" class="max-h-80 overflow-y-auto">
            <p class="text-slate-500 text-sm">Kategori secin</p>
        </div>
    </div>
</div>

<div class="lg:col-span-4">
    <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <div class="flex justify-between items-center mb-4">
            <h3 class="font-semibold">Segmentler</h3>
            <button onclick="addSegment()" class="px-3 py-1 bg-green-500/20 text-green-400 rounded text-sm hover:bg-green-500/30">+ Ekle</button>
        </div>
        <div id="segment-list"></div>
    </div>
</div>

<div class="lg:col-span-5 space-y-4">
    <div class="grid grid-cols-2 gap-4">
        <div class="bg-blue-500/20 rounded-xl p-4 border border-blue-500/30">
            <p class="text-xs text-slate-400">Birlesim (OR)</p>
            <p class="text-2xl font-bold text-blue-400" id="union-val">0</p>
        </div>
        <div class="bg-purple-500/20 rounded-xl p-4 border border-purple-500/30">
            <p class="text-xs text-slate-400">Kesisim (AND)</p>
            <p class="text-2xl font-bold text-purple-400" id="inter-val">0</p>
        </div>
    </div>
    
    <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h3 class="text-sm font-semibold mb-3">Venn Diagram</h3>
        <svg id="venn" viewBox="0 0 400 250" class="w-full bg-slate-900/50 rounded-lg">
            <text x="200" y="125" text-anchor="middle" fill="#64748b" font-size="14">Interest ekleyin</text>
        </svg>
    </div>
    
    <div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <h3 class="text-sm font-semibold mb-3">Segment Reach</h3>
        <div id="reach-list">
            <p class="text-slate-500 text-sm text-center py-2">Interest ekleyin</p>
        </div>
    </div>
    
    <div class="grid grid-cols-2 gap-2">
        <button onclick="exportJSON()" class="py-2 bg-green-500/20 text-green-400 rounded text-sm hover:bg-green-500/30">JSON Export</button>
        <button onclick="copyIntersection()" class="py-2 bg-purple-500/20 text-purple-400 rounded text-sm hover:bg-purple-500/30">Kesisim Kopyala</button>
    </div>
</div>

</div>
</div>
</body>
</html>'''

@app.route('/')
def index():
    html = HTML % json.dumps(INTERESTS)
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
