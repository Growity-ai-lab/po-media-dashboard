"""
PO Premium Market Dashboard v2.1
Flask + Meta API
"""
from flask import Flask, render_template_string, request, jsonify
import requests, json, os, random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'po-2024')

KUME_DATA = {
    "Yeni_Orta_Sinif": {"display": "Yeni Orta Sinif", "skor": 61.4, "pop": 13.81, "yas": "30-49", "color": "#FF6B00", "pen": 0.72, "dar": 0.35, "targeting": {"age_min": 30, "age_max": 49, "genders": [1,2], "geo_locations": {"countries": ["TR"]}, "flexible_spec": [{"interests": [{"id": "6003349442455", "name": "Online shopping"}, {"id": "6003384248805", "name": "Netflix"}]}]}},
    "Kirilgan_Orta_Yas": {"display": "Kirilgan Orta Yas", "skor": 64.1, "pop": 11.95, "yas": "30-49", "color": "#FFB800", "pen": 0.68, "dar": 0.38, "targeting": {"age_min": 30, "age_max": 49, "genders": [1,2], "geo_locations": {"countries": ["TR"]}, "flexible_spec": [{"interests": [{"id": "6003397425735", "name": "Family"}, {"id": "6003384248805", "name": "Netflix"}]}]}},
    "Karamsar_Gencler": {"display": "Karamsar Gencler", "skor": 63.7, "pop": 15.03, "yas": "18-29", "color": "#1E3A5F", "pen": 0.85, "dar": 0.32, "targeting": {"age_min": 18, "age_max": 29, "genders": [1,2], "geo_locations": {"countries": ["TR"]}, "flexible_spec": [{"interests": [{"id": "6003107902433", "name": "Coffee"}, {"id": "6003384248805", "name": "Netflix"}]}]}},
    "Kentli_Dijitaller": {"display": "Kentli Dijitaller", "skor": 62.4, "pop": 17.92, "yas": "30-49", "color": "#4A90A4", "pen": 0.78, "dar": 0.28, "targeting": {"age_min": 30, "age_max": 49, "genders": [1,2], "geo_locations": {"countries": ["TR"]}, "flexible_spec": [{"interests": [{"id": "6003139266461", "name": "Travel"}]}]}},
    "Kentli_Geleneksel": {"display": "Kentli Geleneksel", "skor": 58.7, "pop": 18.14, "yas": "35-55", "color": "#6B7280", "pen": 0.58, "dar": 0.42, "targeting": {"age_min": 35, "age_max": 55, "genders": [1,2], "geo_locations": {"countries": ["TR"]}, "flexible_spec": [{"interests": [{"id": "6003397425735", "name": "Family"}]}]}}
}

def get_reach(token, account, spec):
    try:
        r = requests.get(f"https://graph.facebook.com/v18.0/{account}/reachestimate", params={"access_token": token, "targeting_spec": json.dumps(spec), "optimize_for": "REACH"}, timeout=10)
        d = r.json()
        if "error" in d: return None
        lo = d.get("data", {}).get("users_lower_bound") or d.get("users_lower_bound", 0)
        hi = d.get("data", {}).get("users_upper_bound") or d.get("users_upper_bound", 0)
        return {"lo": lo, "hi": hi, "est": (lo+hi)//2, "src": "api"}
    except: return None

def test_conn(token, account):
    try:
        r = requests.get(f"https://graph.facebook.com/v18.0/{account}", params={"access_token": token, "fields": "name"}, timeout=10)
        d = r.json()
        if "error" in d: return {"ok": False, "err": d["error"].get("message", "Error")}
        return {"ok": True, "name": d.get("name", "OK")}
    except Exception as e: return {"ok": False, "err": str(e)}

def search_int(token, q):
    try:
        r = requests.get("https://graph.facebook.com/v18.0/search", params={"access_token": token, "type": "adinterest", "q": q, "limit": 15}, timeout=10)
        d = r.json()
        if "error" in d: return []
        return [{"id": i.get("id"), "name": i.get("name")} for i in d.get("data", [])]
    except: return []

def sim_reach(k):
    d = KUME_DATA[k]
    base = 85000000 * (d["pop"]/100) * d["pen"] * {"18-29": 0.28, "30-49": 0.42, "35-55": 0.35}.get(d["yas"], 0.35) * d["dar"]
    est = int(base * (0.9 + random.random() * 0.2))
    return {"lo": int(est*0.85), "hi": int(est*1.15), "est": est, "src": "sim", "cpm": round(22 + random.random()*13, 2)}

HTML = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PO Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-slate-900 text-white p-4">
<div class="max-w-6xl mx-auto">
<div class="flex items-center gap-3 mb-6">
<div class="w-12 h-12 bg-gradient-to-br from-orange-500 to-yellow-500 rounded-xl flex items-center justify-center font-bold text-xl">PO</div>
<div><h1 class="text-xl font-bold text-orange-400">Premium Market Dashboard</h1><p class="text-slate-400 text-sm">Meta API + TDY Kume</p></div>
</div>

<div class="bg-slate-800 rounded-xl p-4 mb-4 border border-slate-700">
<div class="grid grid-cols-1 md:grid-cols-4 gap-3">
<input type="password" id="token" placeholder="Access Token" class="bg-slate-700 rounded px-3 py-2 text-sm border border-slate-600">
<input type="text" id="account" value="act_" placeholder="act_xxx" class="bg-slate-700 rounded px-3 py-2 text-sm border border-slate-600">
<button onclick="testAPI()" class="bg-orange-500 hover:bg-orange-600 rounded px-4 py-2 font-medium">Test</button>
<div id="status" class="bg-slate-700 rounded px-4 py-2 text-center text-sm">Bagli degil</div>
</div>
</div>

<div class="flex gap-2 mb-4 overflow-x-auto">
<button onclick="showTab('overview')" class="tab-btn px-4 py-2 rounded bg-orange-500 text-sm" data-tab="overview">Genel</button>
<button onclick="showTab('reach')" class="tab-btn px-4 py-2 rounded bg-slate-700 text-sm" data-tab="reach">Reach</button>
<button onclick="showTab('interest')" class="tab-btn px-4 py-2 rounded bg-slate-700 text-sm" data-tab="interest">Interest</button>
<button onclick="showTab('export')" class="tab-btn px-4 py-2 rounded bg-slate-700 text-sm" data-tab="export">Export</button>
</div>

<div id="tab-overview" class="tab-content">
<div class="grid md:grid-cols-3 gap-4">
<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<h3 class="font-semibold mb-3">Kumeler</h3>
<div id="kume-list" class="space-y-2"></div>
</div>
<div class="md:col-span-2 grid grid-cols-2 gap-4">
<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<p class="text-slate-400 text-sm">Butce</p>
<div class="text-3xl font-bold text-orange-400" id="budget-display">200M</div>
<input type="range" id="budget" min="50" max="500" value="200" class="w-full mt-2 accent-orange-500" oninput="document.getElementById('budget-display').textContent=this.value+'M'">
</div>
<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<p class="text-slate-400 text-sm">Reach</p>
<div class="text-3xl font-bold text-blue-400" id="reach-display">-</div>
</div>
</div>
</div>
</div>

<div id="tab-reach" class="tab-content hidden">
<div class="grid md:grid-cols-2 gap-4">
<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<div class="flex justify-between mb-4">
<h3 class="font-semibold">Reach Hesapla</h3>
<button onclick="calcReach()" class="px-4 py-1 bg-blue-500 rounded text-sm">Hesapla</button>
</div>
<div id="reach-results" class="space-y-2 text-sm"></div>
</div>
<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<canvas id="chart" height="200"></canvas>
</div>
</div>
</div>

<div id="tab-interest" class="tab-content hidden">
<div class="grid md:grid-cols-2 gap-4">
<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<div class="flex gap-2 mb-4">
<input type="text" id="search-input" placeholder="Coffee, Travel..." class="flex-1 bg-slate-700 rounded px-3 py-2 text-sm border border-slate-600" onkeypress="if(event.key=='Enter')searchInt()">
<button onclick="searchInt()" class="px-4 py-2 bg-orange-500 rounded">Ara</button>
</div>
<div class="flex gap-2 mb-3 flex-wrap">
<button onclick="qSearch('Coffee')" class="text-xs px-2 py-1 bg-slate-700 rounded">Coffee</button>
<button onclick="qSearch('Travel')" class="text-xs px-2 py-1 bg-slate-700 rounded">Travel</button>
<button onclick="qSearch('Shopping')" class="text-xs px-2 py-1 bg-slate-700 rounded">Shopping</button>
<button onclick="qSearch('Family')" class="text-xs px-2 py-1 bg-slate-700 rounded">Family</button>
</div>
<div id="int-results" class="space-y-2 max-h-64 overflow-y-auto"></div>
</div>
<div class="bg-slate-800 rounded-xl p-4 border border-slate-700">
<div class="flex justify-between mb-3">
<h3 class="font-semibold">Secili</h3>
<button onclick="selInt=[];updateSel()" class="text-xs px-2 py-1 bg-red-500/20 text-red-400 rounded">Temizle</button>
</div>
<div id="sel-int" class="flex flex-wrap gap-2 min-h-[80px] p-2 bg-slate-700/50 rounded border border-dashed border-slate-600 mb-3"></div>
<button onclick="copyInt()" class="w-full py-2 bg-green-500/20 text-green-400 rounded text-sm">JSON Kopyala</button>
</div>
</div>
</div>

<div id="tab-export" class="tab-content hidden">
<div class="bg-slate-800 rounded-xl p-4 border border-slate-700 mb-4">
<button onclick="copyAll()" class="px-4 py-2 bg-green-500/20 text-green-400 rounded text-sm">Tumunu Kopyala</button>
</div>
<div id="export-list" class="grid md:grid-cols-3 gap-4"></div>
</div>

</div>
<script>
var kumeData=''' + json.dumps({k: {"display": v["display"], "skor": v["skor"], "pop": v["pop"], "yas": v["yas"], "color": v["color"], "targeting": v["targeting"]} for k, v in KUME_DATA.items()}) + ''';
var selKume=["Yeni_Orta_Sinif","Kirilgan_Orta_Yas","Karamsar_Gencler"];
var selInt=[];
var reachData={};
var chart=null;

document.addEventListener("DOMContentLoaded",function(){initKume();});

function initKume(){
var c=document.getElementById("kume-list");c.innerHTML="";
for(var k in kumeData){
var d=kumeData[k];
var ch=selKume.indexOf(k)>=0;
c.innerHTML+='<label class="flex items-center gap-2 p-2 bg-slate-700/50 rounded cursor-pointer"><input type="checkbox" class="accent-orange-500" '+(ch?'checked':'')+' onchange="toggleKume(\\''+k+'\\',this.checked)"><div class="w-2 h-2 rounded-full" style="background:'+d.color+'"></div><span class="text-sm">'+d.display+'</span><span class="ml-auto text-xs text-slate-400">'+d.skor+'</span></label>';
}}

function toggleKume(k,v){if(v){if(selKume.indexOf(k)<0)selKume.push(k);}else{selKume=selKume.filter(function(x){return x!=k;});}}

function showTab(id){
document.querySelectorAll(".tab-content").forEach(function(e){e.classList.add("hidden");});
document.querySelectorAll(".tab-btn").forEach(function(e){e.classList.remove("bg-orange-500");e.classList.add("bg-slate-700");});
document.getElementById("tab-"+id).classList.remove("hidden");
document.querySelector('[data-tab="'+id+'"]').classList.remove("bg-slate-700");
document.querySelector('[data-tab="'+id+'"]').classList.add("bg-orange-500");
if(id=="export")updateExport();
}

function testAPI(){
var t=document.getElementById("token").value;
var a=document.getElementById("account").value;
var s=document.getElementById("status");
if(!t||!a){s.textContent="Token/ID gerekli";s.className="bg-red-500/20 text-red-400 rounded px-4 py-2 text-center text-sm";return;}
s.textContent="Test...";s.className="bg-yellow-500/20 text-yellow-400 rounded px-4 py-2 text-center text-sm";
fetch("/api/test",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:t,account:a})})
.then(function(r){return r.json();})
.then(function(d){
if(d.ok){s.textContent="OK: "+d.name;s.className="bg-green-500/20 text-green-400 rounded px-4 py-2 text-center text-sm";}
else{s.textContent="Hata";s.className="bg-red-500/20 text-red-400 rounded px-4 py-2 text-center text-sm";}
});
}

function calcReach(){
var t=document.getElementById("token").value;
var a=document.getElementById("account").value;
var r=document.getElementById("reach-results");
r.innerHTML="<p>Hesaplaniyor...</p>";
fetch("/api/reach",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({kumeler:selKume,token:t,account:a})})
.then(function(res){return res.json();})
.then(function(d){
reachData=d;var html="";var total=0;
for(var k in d){
var v=d[k];total+=v.est;
html+='<div class="flex justify-between p-2 bg-slate-700/50 rounded"><span>'+k+'</span><span class="text-blue-400">'+(v.est/1000000).toFixed(2)+'M</span></div>';
}
html+='<div class="flex justify-between p-3 bg-blue-500/20 rounded mt-2 font-bold"><span>Toplam</span><span class="text-blue-400">'+(total/1000000).toFixed(1)+'M</span></div>';
r.innerHTML=html;
document.getElementById("reach-display").textContent=(total/1000000).toFixed(1)+"M";
updateChart(d);
});
}

function updateChart(d){
var ctx=document.getElementById("chart").getContext("2d");
var labels=[];var values=[];var colors=[];
for(var k in d){labels.push(k.split("_")[0]);values.push(d[k].est/1000000);colors.push(kumeData[k]?kumeData[k].color:"#666");}
if(chart)chart.destroy();
chart=new Chart(ctx,{type:"bar",data:{labels:labels,datasets:[{data:values,backgroundColor:colors,borderRadius:6}]},options:{plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,grid:{color:"#334155"}},x:{grid:{display:false}}}}});
}

function qSearch(t){document.getElementById("search-input").value=t;searchInt();}

function searchInt(){
var q=document.getElementById("search-input").value;
var t=document.getElementById("token").value;
var r=document.getElementById("int-results");
r.innerHTML="<p>Araniyor...</p>";
fetch("/api/interests",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({q:q,token:t})})
.then(function(res){return res.json();})
.then(function(d){
var html="";
for(var i=0;i<d.length;i++){
var it=d[i];
var isSel=selInt.some(function(x){return x.id==it.id;});
html+='<div class="flex justify-between items-center p-2 bg-slate-700/50 rounded"><div><div class="text-sm">'+it.name+'</div><div class="text-xs text-slate-400">'+it.id+'</div></div><button onclick="addInt(\\''+it.id+'\\',\\''+it.name.replace(/'/g,"")+'\\\')" class="px-2 py-1 rounded text-xs '+(isSel?'bg-green-500/20 text-green-400':'bg-orange-500/20 text-orange-400')+'">'+(isSel?'OK':'Ekle')+'</button></div>';
}
r.innerHTML=html||"<p class='text-slate-400'>Sonuc yok</p>";
});
}

function addInt(id,name){
if(!selInt.some(function(x){return x.id==id;})){selInt.push({id:id,name:name});updateSel();searchInt();}
}

function updateSel(){
var c=document.getElementById("sel-int");
if(selInt.length==0){c.innerHTML="<span class='text-slate-500 text-sm'>Bos</span>";return;}
var html="";
for(var i=0;i<selInt.length;i++){
html+='<span class="px-2 py-1 bg-orange-500/20 text-orange-400 rounded text-xs">'+selInt[i].name+' <button onclick="remInt(\\''+selInt[i].id+'\\')">x</button></span>';
}
c.innerHTML=html;
}

function remInt(id){selInt=selInt.filter(function(x){return x.id!=id;});updateSel();}

function copyInt(){
if(selInt.length==0){alert("Bos");return;}
navigator.clipboard.writeText(JSON.stringify({interests:selInt},null,2));
alert("Kopyalandi!");
}

function updateExport(){
var c=document.getElementById("export-list");
var html="";
for(var i=0;i<selKume.length;i++){
var k=selKume[i];
var d=kumeData[k];
if(!d)continue;
var spec={name:"PO-"+k,targeting:d.targeting};
html+='<div class="bg-slate-800 rounded-xl p-4 border border-slate-700"><div class="flex justify-between mb-2"><span class="font-semibold text-sm" style="color:'+d.color+'">'+d.display+'</span><button onclick="copySpec(\\''+k+'\\\')" class="text-xs px-2 py-1 bg-slate-700 rounded">Kopyala</button></div><pre class="text-xs bg-slate-900 p-2 rounded overflow-x-auto" id="spec-'+k+'">'+JSON.stringify(spec,null,2)+'</pre></div>';
}
c.innerHTML=html||"<p class='text-slate-400'>Kume secin</p>";
}

function copySpec(k){
var el=document.getElementById("spec-"+k);
if(el){navigator.clipboard.writeText(el.textContent);alert("Kopyalandi!");}
}

function copyAll(){
var specs=[];
for(var i=0;i<selKume.length;i++){
var k=selKume[i];var d=kumeData[k];
if(d)specs.push({name:"PO-"+k,targeting:d.targeting});
}
navigator.clipboard.writeText(JSON.stringify(specs,null,2));
alert("Tumunu kopyalandi!");
}
</script>
</body></html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/test', methods=['POST'])
def api_test():
    d = request.json
    r = test_conn(d.get('token'), d.get('account'))
    return jsonify(r)

@app.route('/api/reach', methods=['POST'])
def api_reach():
    d = request.json
    res = {}
    for k in d.get('kumeler', []):
        if k not in KUME_DATA: continue
        if d.get('token') and d.get('account'):
            r = get_reach(d['token'], d['account'], KUME_DATA[k]['targeting'])
            if r: res[k] = r
            else: res[k] = sim_reach(k)
        else: res[k] = sim_reach(k)
    return jsonify(res)

@app.route('/api/interests', methods=['POST'])
def api_interests():
    d = request.json
    if d.get('token'):
        return jsonify(search_int(d['token'], d.get('q', '')))
    return jsonify([{"id": "123", "name": d.get('q', 'test')}])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
