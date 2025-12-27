"""
PO Premium Market - Audience Intersection Dashboard
Erislebilir Premium Hedef Kitle Analizi - Dummy Data
"""
from flask import Flask, render_template_string, request, jsonify
import json, os, random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'po-premium-2024')

# PO PREMIUM - DUMMY INTEREST DATA
DUMMY_INTERESTS = {
    "coffee": [
        {"id": "6003107902433", "name": "Coffee", "size": 12500000, "cat": "Kahve"},
        {"id": "6003263791733", "name": "Starbucks", "size": 8200000, "cat": "Kahve"},
        {"id": "6003297800210", "name": "Cafe culture", "size": 4500000, "cat": "Kahve"},
    ],
    "food": [
        {"id": "6003139266461", "name": "Restaurants", "size": 18000000, "cat": "Yemek"},
        {"id": "6003348604123", "name": "Brunch", "size": 5200000, "cat": "Yemek"},
        {"id": "6003678901235", "name": "Organic food", "size": 6500000, "cat": "Yemek"},
    ],
    "travel": [
        {"id": "6003139266462", "name": "Travel", "size": 22000000, "cat": "Seyahat"},
        {"id": "6003567890123", "name": "Weekend getaways", "size": 4800000, "cat": "Seyahat"},
        {"id": "6003789012345", "name": "Road trips", "size": 5200000, "cat": "Seyahat"},
    ],
    "family": [
        {"id": "6003397425735", "name": "Family", "size": 28000000, "cat": "Aile"},
        {"id": "6003020834693", "name": "Parenting", "size": 12000000, "cat": "Aile"},
        {"id": "6003890123456", "name": "Child safety", "size": 4200000, "cat": "Aile"},
    ],
    "wellness": [
        {"id": "6003348604980", "name": "Health and wellness", "size": 15000000, "cat": "Saglik"},
        {"id": "6003012345678", "name": "Fitness", "size": 11000000, "cat": "Saglik"},
        {"id": "6003234567890", "name": "Self-care", "size": 7200000, "cat": "Saglik"},
    ],
    "tech": [
        {"id": "6003020834694", "name": "Technology", "size": 19000000, "cat": "Teknoloji"},
        {"id": "6003222333444", "name": "Online shopping", "size": 21000000, "cat": "Teknoloji"},
        {"id": "6003333444555", "name": "Mobile apps", "size": 18000000, "cat": "Teknoloji"},
    ],
    "shopping": [
        {"id": "6003349442455", "name": "Online shopping", "size": 21000000, "cat": "Alisveris"},
        {"id": "6002714895372", "name": "Engaged shoppers", "size": 16000000, "cat": "Alisveris"},
        {"id": "6003555666777", "name": "Quality products", "size": 7500000, "cat": "Alisveris"},
    ],
    "entertainment": [
        {"id": "6003384248805", "name": "Netflix", "size": 14000000, "cat": "Eglence"},
        {"id": "6003888999000", "name": "Streaming services", "size": 11000000, "cat": "Eglence"},
        {"id": "6003999000111", "name": "Podcasts", "size": 5500000, "cat": "Eglence"},
    ],
    "auto": [
        {"id": "6003222333445", "name": "Cars", "size": 18000000, "cat": "Otomotiv"},
        {"id": "6003333444556", "name": "Car owners", "size": 15000000, "cat": "Otomotiv"},
        {"id": "6003555666778", "name": "Car maintenance", "size": 6500000, "cat": "Otomotiv"},
    ],
    "premium": [
        {"id": "6003777888991", "name": "Quality conscious", "size": 6200000, "cat": "Premium"},
        {"id": "6003888999002", "name": "Premium services", "size": 4800000, "cat": "Premium"},
        {"id": "6003111222336", "name": "Convenience seekers", "size": 8900000, "cat": "Premium"},
    ],
}

CATEGORIES = [
    {"key": "coffee", "name": "Kahve", "icon": "☕"},
    {"key": "food", "name": "Yemek", "icon": "🍽️"},
    {"key": "travel", "name": "Seyahat", "icon": "✈️"},
    {"key": "family", "name": "Aile", "icon": "👨‍👩‍👧"},
    {"key": "wellness", "name": "Saglik", "icon": "🧘"},
    {"key": "tech", "name": "Teknoloji", "icon": "📱"},
    {"key": "shopping", "name": "Alisveris", "icon": "🛒"},
    {"key": "entertainment", "name": "Eglence", "icon": "🎬"},
    {"key": "auto", "name": "Otomotiv", "icon": "🚗"},
    {"key": "premium", "name": "Premium", "icon": "⭐"},
]

SUGGESTED = [
    {"name": "Yolcu Aileler", "desc": "Aile + Seyahat + Guvenlik", "ids": ["6003397425735", "6003789012345", "6003890123456"], "color": "#10B981"},
    {"name": "Sehirli Profesyoneller", "desc": "Kahve + Teknoloji + Hiz", "ids": ["6003107902433", "6003333444555", "6003111222336"], "color": "#3B82F6"},
    {"name": "Kalite Arayanlar", "desc": "Premium + Saglik + Kalite", "ids": ["6003777888991", "6003348604980", "6003555666777"], "color": "#8B5CF6"},
    {"name": "Dijital Yerliler", "desc": "Online + Streaming + Mobil", "ids": ["6003222333444", "6003384248805", "6002714895372"], "color": "#F59E0B"},
]

def get_interest(iid):
    for ints in DUMMY_INTERESTS.values():
        for i in ints:
            if i["id"] == iid:
                return i
    return None

def calc_reach(interests):
    sizes = [get_interest(i["id"])["size"] for i in interests if get_interest(i["id"])]
    if not sizes: return 0
    sizes.sort(reverse=True)
    reach = sizes[0]
    for i, s in enumerate(sizes[1:], 1):
        reach += int(s * (0.35 / i))
    return int(reach * (0.9 + random.random() * 0.2))

def calc_intersection(segs):
    if len(segs) < 2: return calc_reach(segs[0]["interests"]) if segs else 0
    reaches = [calc_reach(s["interests"]) for s in segs if s.get("interests")]
    if not reaches: return 0
    return int(min(reaches) * (0.15 + 0.05 * len(segs)))

def calc_union(segs):
    total = sum(calc_reach(s["interests"]) for s in segs if s.get("interests"))
    if len(segs) > 1:
        total = int(total * 0.7)
    return min(total, 35000000)

HTML = '''<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PO Premium Audience Builder</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>body{font-family:system-ui,-apple-system,sans-serif}</style>
</head><body class="bg-slate-900 text-white min-h-screen p-4">
<div class="max-w-7xl mx-auto">

<div class="flex items-center gap-4 mb-6">
<div class="w-12 h-12 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-xl flex items-center justify-center font-bold text-xl">PO</div>
<div><h1 class="text-xl font-bold text-orange-400">Premium Audience Builder</h1>
<p class="text-slate-400 text-sm">Erislebilir Premium - Kesisim Analizi</p></div>
</div>

<div class="bg-orange-500/10 border border-orange-500/30 rounded-xl p-4 mb-6">
<p class="text-sm"><strong class="text-orange-400">Erislebilir Premium:</strong> Luks degil, kaliteli hizmet arayan. Kendine deger veren, pratik cozum isteyen kitle.</p>
</div>

<div class="grid lg:grid-cols-12 gap-4">

<div class="lg:col-span-4 space-y-4">
<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<h3 class="text-sm text-slate-400 mb-3">KATEGORILER</h3>
<div class="grid grid-cols-5 gap-2" id="cats"></div>
</div>

<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<h3 class="font-semibold mb-3">Interest Arama</h3>
<div class="flex gap-2 mb-3">
<input type="text" id="search" placeholder="Ara..." class="flex-1 bg-slate-700 rounded px-3 py-2 text-sm border border-slate-600" onkeypress="if(event.key==='Enter')doSearch()">
<button onclick="doSearch()" class="px-4 py-2 bg-orange-500 rounded">Ara</button>
</div>
<div id="results" class="space-y-2 max-h-64 overflow-y-auto"></div>
</div>

<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<h3 class="text-sm text-slate-400 mb-3">ONERILEN</h3>
<div id="suggested" class="space-y-2"></div>
</div>
</div>

<div class="lg:col-span-4">
<div class="bg-slate-800 rounded-xl p-4 border border-slate-700 h-full">
<div class="flex justify-between items-center mb-4">
<h3 class="font-semibold">Segmentler</h3>
<button onclick="addSeg()" class="px-3 py-1 bg-green-500/20 text-green-400 rounded text-sm">+ Ekle</button>
</div>
<div id="segs" class="space-y-3 max-h-[500px] overflow-y-auto"></div>
</div>
</div>

<div class="lg:col-span-4 space-y-4">
<button onclick="calculate()" class="w-full py-3 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl font-semibold">Reach Hesapla</button>

<div class="bg-blue-500/20 rounded-xl p-4 border border-blue-500/30">
<div class="flex justify-between"><div><p class="text-sm text-slate-400">Birlesim</p><p class="text-xs text-slate-500">En az birinde</p></div>
<div class="text-right"><div class="text-2xl font-bold text-blue-400" id="union">-</div><div class="text-xs text-slate-500" id="union-pct"></div></div></div>
</div>

<div class="bg-purple-500/20 rounded-xl p-4 border border-purple-500/30">
<div class="flex justify-between"><div><p class="text-sm text-slate-400">Kesisim (AND)</p><p class="text-xs text-slate-500">Tumunde ortak</p></div>
<div class="text-right"><div class="text-2xl font-bold text-purple-400" id="inter">-</div><div class="text-xs text-slate-500" id="inter-pct"></div></div></div>
</div>

<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<h3 class="text-sm font-semibold mb-3">Segment Reach</h3>
<div id="seg-reaches" class="space-y-2"></div>
</div>

<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<h3 class="text-sm font-semibold mb-2">Venn</h3>
<svg id="venn" viewBox="0 0 300 120" class="w-full h-28"></svg>
</div>

<div class="grid grid-cols-2 gap-2">
<button onclick="exportAll()" class="px-4 py-2 bg-green-500/20 text-green-400 rounded text-sm">JSON Export</button>
<button onclick="copyInter()" class="px-4 py-2 bg-purple-500/20 text-purple-400 rounded text-sm">Kesisim Kopyala</button>
</div>
</div>

</div></div>

<script>
var cats=''' + json.dumps(CATEGORIES) + ''';
var data=''' + json.dumps(DUMMY_INTERESTS) + ''';
var sugg=''' + json.dumps(SUGGESTED) + ''';
var segs=[];
var segC=0;
var results=[];
var colors=['#FF6B00','#3B82F6','#10B981','#F59E0B','#8B5CF6','#EC4899'];

document.addEventListener('DOMContentLoaded',function(){
renderCats();renderSugg();addSeg();
});

function renderCats(){
var h='';
for(var i=0;i<cats.length;i++){
var c=cats[i];
h+='<button onclick="loadCat(\\''+c.key+'\\\')" class="p-2 bg-slate-700 hover:bg-slate-600 rounded text-center"><div class="text-lg">'+c.icon+'</div><div class="text-xs truncate">'+c.name+'</div></button>';
}
document.getElementById('cats').innerHTML=h;
}

function renderSugg(){
var h='';
for(var i=0;i<sugg.length;i++){
var s=sugg[i];
h+='<button onclick="loadSugg('+i+')" class="w-full text-left p-2 bg-slate-700/50 hover:bg-slate-700 rounded border-l-4" style="border-color:'+s.color+'"><div class="text-sm font-medium">'+s.name+'</div><div class="text-xs text-slate-400">'+s.desc+'</div></button>';
}
document.getElementById('suggested').innerHTML=h;
}

function loadCat(key){
results=data[key]||[];
document.getElementById('search').value='';
renderResults();
}

function doSearch(){
var q=document.getElementById('search').value.toLowerCase();
if(!q)return;
results=[];
for(var k in data){
if(k.indexOf(q)>=0){results=results.concat(data[k]);continue;}
for(var i=0;i<data[k].length;i++){
if(data[k][i].name.toLowerCase().indexOf(q)>=0){
var ex=results.some(function(r){return r.id===data[k][i].id;});
if(!ex)results.push(data[k][i]);
}}}
renderResults();
}

function renderResults(){
var r=document.getElementById('results');
if(!results.length){r.innerHTML='<p class="text-slate-500 text-sm text-center py-4">Sonuc yok</p>';return;}
var h='';
for(var i=0;i<results.length;i++){
var it=results[i];
h+='<div class="bg-slate-700/50 rounded p-2 flex justify-between items-center">';
h+='<div><div class="text-sm">'+it.name+'</div><div class="text-xs text-slate-500">'+(it.size/1000000).toFixed(1)+'M</div></div>';
h+='<div class="flex gap-1">';
for(var j=0;j<segs.length;j++){
var s=segs[j];
var isIn=s.ints.some(function(x){return x.id===it.id;});
h+='<button onclick="toggle('+s.id+',\\''+it.id+'\\',\\''+it.name.replace(/'/g,'')+'\\',\\''+it.cat+'\\\')" class="w-6 h-6 rounded text-xs font-bold '+(isIn?'text-white':'text-slate-300 border-2')+'" style="'+(isIn?'background:'+s.color:'border-color:'+s.color)+'">'+(isIn?'✓':(j+1))+'</button>';
}
h+='</div></div>';
}
r.innerHTML=h;
}

function loadSugg(idx){
var s=sugg[idx];
segC++;
var seg={id:segC,name:s.name,color:s.color,ints:[],reach:null};
for(var i=0;i<s.ids.length;i++){
for(var k in data){
var found=data[k].find(function(x){return x.id===s.ids[i];});
if(found){seg.ints.push({id:found.id,name:found.name,cat:found.cat});break;}
}}
segs.push(seg);
renderSegs();renderResults();
}

function addSeg(){
segC++;
segs.push({id:segC,name:'Segment '+segC,color:colors[(segC-1)%colors.length],ints:[],reach:null});
renderSegs();if(results.length)renderResults();
}

function remSeg(id){
segs=segs.filter(function(s){return s.id!==id;});
renderSegs();updateDisp();drawVenn();if(results.length)renderResults();
}

function rename(id,n){
var s=segs.find(function(x){return x.id===id;});
if(s)s.name=n;
}

function toggle(sid,iid,iname,icat){
var s=segs.find(function(x){return x.id===sid;});
if(!s)return;
var ex=s.ints.some(function(i){return i.id===iid;});
if(ex){s.ints=s.ints.filter(function(i){return i.id!==iid;});}
else{s.ints.push({id:iid,name:iname,cat:icat});}
renderSegs();renderResults();
}

function remInt(sid,iid){
var s=segs.find(function(x){return x.id===sid;});
if(s){s.ints=s.ints.filter(function(i){return i.id!==iid;});renderSegs();if(results.length)renderResults();}
}

function renderSegs(){
var c=document.getElementById('segs');
if(!segs.length){c.innerHTML='<p class="text-slate-500 text-sm text-center py-8">Segment ekleyin</p>';return;}
var h='';
for(var i=0;i<segs.length;i++){
var s=segs[i];
var rt=s.reach?(s.reach/1000000).toFixed(2)+'M':'-';
h+='<div class="bg-slate-700/30 rounded-lg p-3 border-l-4" style="border-color:'+s.color+'">';
h+='<div class="flex justify-between items-center mb-2">';
h+='<div class="flex items-center gap-2"><div class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white" style="background:'+s.color+'">'+(i+1)+'</div>';
h+='<input type="text" value="'+s.name+'" onchange="rename('+s.id+',this.value)" class="bg-transparent border-none text-sm font-semibold w-28 focus:outline-none"></div>';
h+='<div class="flex items-center gap-2"><span class="text-sm" style="color:'+s.color+'">'+rt+'</span>';
h+='<button onclick="remSeg('+s.id+')" class="text-red-400 text-lg">×</button></div></div>';
h+='<div class="flex flex-wrap gap-1 min-h-[28px]">';
if(!s.ints.length){h+='<span class="text-slate-500 text-xs">Interest ekleyin</span>';}
else{for(var j=0;j<s.ints.length;j++){
var it=s.ints[j];
h+='<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs" style="background:'+s.color+'22;color:'+s.color+';border:1px solid '+s.color+'44"><span class="truncate max-w-[80px]">'+it.name+'</span><button onclick="remInt('+s.id+',\\''+it.id+'\\\')" class="opacity-60 hover:opacity-100">×</button></span>';
}}
h+='</div></div>';
}
c.innerHTML=h;
}

function calculate(){
var valid=segs.filter(function(s){return s.ints.length>0;});
if(!valid.length){alert('Interest ekleyin');return;}
fetch('/api/calc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({segs:valid.map(function(s){return{id:s.id,name:s.name,ints:s.ints};})})})
.then(function(r){return r.json();})
.then(function(d){
for(var i=0;i<segs.length;i++){
var res=d.segs.find(function(x){return x.id===segs[i].id;});
if(res)segs[i].reach=res.reach;
}
renderSegs();
document.getElementById('union').textContent=d.union?(d.union/1000000).toFixed(2)+'M':'-';
document.getElementById('union-pct').textContent=d.union?'TR Meta %'+((d.union/35000000)*100).toFixed(1):'';
document.getElementById('inter').textContent=d.inter?(d.inter/1000000).toFixed(2)+'M':'-';
document.getElementById('inter-pct').textContent=d.inter&&d.union?'Birlesimin %'+((d.inter/d.union)*100).toFixed(1):'';
updateDisp();drawVenn();
});
}

function updateDisp(){
var c=document.getElementById('seg-reaches');
var valid=segs.filter(function(s){return s.reach!==null;});
if(!valid.length){c.innerHTML='<p class="text-slate-500 text-sm text-center py-4">Hesaplayin</p>';return;}
valid.sort(function(a,b){return b.reach-a.reach;});
var h='';
for(var i=0;i<valid.length;i++){
var s=valid[i];
var pct=valid[0].reach?((s.reach/valid[0].reach)*100).toFixed(0):100;
h+='<div class="relative"><div class="absolute inset-0 rounded opacity-20" style="background:'+s.color+';width:'+pct+'%"></div>';
h+='<div class="relative flex justify-between p-2"><div class="flex items-center gap-2"><div class="w-3 h-3 rounded-full" style="background:'+s.color+'"></div><span class="text-sm">'+s.name+'</span></div>';
h+='<span class="font-medium" style="color:'+s.color+'">'+(s.reach/1000000).toFixed(2)+'M</span></div></div>';
}
c.innerHTML=h;
}

function drawVenn(){
var svg=document.getElementById('venn');
var valid=segs.filter(function(s){return s.reach!==null;});
if(!valid.length){svg.innerHTML='<text x="150" y="60" text-anchor="middle" fill="#64748b" font-size="12">Hesaplayin</text>';return;}
var h='';
if(valid.length===1){
h+='<circle cx="150" cy="60" r="45" fill="'+valid[0].color+'" fill-opacity="0.3" stroke="'+valid[0].color+'" stroke-width="2"/>';
h+='<text x="150" y="65" text-anchor="middle" fill="white" font-size="10">'+valid[0].name+'</text>';
}else if(valid.length===2){
h+='<circle cx="115" cy="60" r="40" fill="'+valid[0].color+'" fill-opacity="0.3" stroke="'+valid[0].color+'" stroke-width="2"/>';
h+='<circle cx="185" cy="60" r="40" fill="'+valid[1].color+'" fill-opacity="0.3" stroke="'+valid[1].color+'" stroke-width="2"/>';
h+='<text x="80" y="60" text-anchor="middle" fill="white" font-size="8">'+valid[0].name.substring(0,8)+'</text>';
h+='<text x="220" y="60" text-anchor="middle" fill="white" font-size="8">'+valid[1].name.substring(0,8)+'</text>';
h+='<text x="150" y="65" text-anchor="middle" fill="#a855f7" font-size="12" font-weight="bold">∩</text>';
}else{
h+='<circle cx="120" cy="45" r="35" fill="'+valid[0].color+'" fill-opacity="0.25" stroke="'+valid[0].color+'" stroke-width="2"/>';
h+='<circle cx="180" cy="45" r="35" fill="'+valid[1].color+'" fill-opacity="0.25" stroke="'+valid[1].color+'" stroke-width="2"/>';
h+='<circle cx="150" cy="85" r="35" fill="'+valid[2].color+'" fill-opacity="0.25" stroke="'+valid[2].color+'" stroke-width="2"/>';
h+='<text x="150" y="60" text-anchor="middle" fill="#a855f7" font-size="11" font-weight="bold">∩</text>';
}
svg.innerHTML=h;
}

function exportAll(){
var d={campaign:"PO Premium",segs:segs.map(function(s){return{name:s.name,ints:s.ints,reach:s.reach,targeting:{geo_locations:{countries:["TR"]},age_min:25,age_max:54,flexible_spec:[{interests:s.ints}]}};})};
navigator.clipboard.writeText(JSON.stringify(d,null,2));
alert('JSON kopyalandi!');
}

function copyInter(){
var valid=segs.filter(function(s){return s.ints.length>0;});
var spec={name:"PO Premium Kesisim",targeting:{geo_locations:{countries:["TR"]},age_min:25,age_max:54,flexible_spec:valid.map(function(s){return{interests:s.ints};})}};
navigator.clipboard.writeText(JSON.stringify(spec,null,2));
alert('Kesisim kopyalandi!');
}
</script></body></html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/calc', methods=['POST'])
def api_calc():
    d = request.json
    segs = d.get('segs', [])
    res = {"segs": [], "union": 0, "inter": 0}
    
    for s in segs:
        if not s.get('ints'): continue
        reach = calc_reach(s['ints'])
        res['segs'].append({'id': s['id'], 'name': s['name'], 'reach': reach})
    
    res['union'] = calc_union(segs)
    res['inter'] = calc_intersection(segs)
    return jsonify(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
