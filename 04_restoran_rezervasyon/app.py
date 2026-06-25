"""Restoran Rezervasyon Sistemi — Flask + SQLite.
Masa + tarih/saat yönetimi, çakışma kontrolü, müşteri kaydı.
"""
import os
import sqlite3, os
from flask import Flask, request, redirect, url_for, render_template_string, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "rezervasyon-demo")
DB = os.path.join(os.path.dirname(__file__), "rez.db")
TABLES = list(range(1, 11))          # 10 masa
SLOTS = [f"{h:02d}:00" for h in range(12, 23)]  # 12:00–22:00


def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c


def init():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS rez(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT,
            people INTEGER, table_no INTEGER, date TEXT, slot TEXT,
            UNIQUE(table_no,date,slot))""")


PAGE = """<!doctype html><html lang=tr><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>Rezervasyon</title><style>
body{font-family:system-ui,sans-serif;max-width:820px;margin:0 auto;padding:1rem;background:#fff7ed}
h1{color:#9a3412}a{color:#c2410c}
input,select{padding:.5rem;border:1px solid #fdba74;border-radius:6px;font:inherit;margin:.2rem 0}
button{background:#ea580c;color:#fff;border:0;padding:.55rem 1rem;border-radius:6px;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(64px,1fr));gap:.4rem;margin:1rem 0}
.t{padding:.7rem;text-align:center;border-radius:8px;font-weight:600}
.free{background:#dcfce7;color:#166534}.busy{background:#fee2e2;color:#991b1b}
.flash{background:#fef9c3;padding:.6rem;border-radius:6px;margin:.5rem 0}
table{width:100%;border-collapse:collapse;margin-top:1rem}td,th{border-bottom:1px solid #fed7aa;padding:.5rem;text-align:left}
form.book{display:flex;flex-wrap:wrap;gap:.5rem;align-items:end;background:#fff;padding:1rem;border-radius:10px}
label{display:flex;flex-direction:column;font-size:.85rem;color:#7c2d12}</style></head><body>
<h1>🍽 Restoran Rezervasyon</h1>
{% with m=get_flashed_messages() %}{% for x in m %}<div class=flash>{{x}}</div>{% endfor %}{% endwith %}
<form method=get>
<label>Tarih <input type=date name=date value="{{date}}"></label>
<label>Saat <select name=slot>{% for s in slots %}<option {{'selected' if s==slot}}>{{s}}</option>{% endfor %}</select></label>
<button>Göster</button></form>
<h3>{{date}} · {{slot}} — masa durumu</h3>
<div class=grid>{% for t in tables %}
<div class="t {{'busy' if t in busy else 'free'}}">{{t}}{% if t in busy %}<br><small>dolu</small>{% endif %}</div>
{% endfor %}</div>
<form class=book method=post action="/book">
<input type=hidden name=date value="{{date}}"><input type=hidden name=slot value="{{slot}}">
<label>Ad Soyad<input name=name required></label>
<label>Telefon<input name=phone required></label>
<label>Kişi<input type=number name=people min=1 max=12 value=2></label>
<label>Masa<select name=table_no>{% for t in tables if t not in busy %}<option>{{t}}</option>{% endfor %}</select></label>
<button>Rezerve Et</button></form>
<h3>Tüm Rezervasyonlar</h3>
<table><tr><th>#</th><th>Ad</th><th>Tel</th><th>Kişi</th><th>Masa</th><th>Tarih</th><th>Saat</th><th></th></tr>
{% for r in all %}<tr><td>{{r.id}}</td><td>{{r.name}}</td><td>{{r.phone}}</td><td>{{r.people}}</td>
<td>{{r.table_no}}</td><td>{{r.date}}</td><td>{{r.slot}}</td>
<td><a href="/cancel/{{r.id}}">iptal</a></td></tr>{% endfor %}</table></body></html>"""


@app.route("/")
def index():
    import datetime
    date = request.args.get("date") or datetime.date.today().isoformat()
    slot = request.args.get("slot") or SLOTS[0]
    with db() as c:
        busy = [r["table_no"] for r in c.execute(
            "SELECT table_no FROM rez WHERE date=? AND slot=?", (date, slot))]
        allr = c.execute("SELECT * FROM rez ORDER BY date,slot").fetchall()
    return render_template_string(PAGE, tables=TABLES, slots=SLOTS, date=date,
                                  slot=slot, busy=busy, all=allr)


@app.route("/book", methods=["POST"])
def book():
    f = request.form
    try:
        with db() as c:
            c.execute("INSERT INTO rez(name,phone,people,table_no,date,slot) VALUES(?,?,?,?,?,?)",
                      (f["name"], f["phone"], f["people"], f["table_no"], f["date"], f["slot"]))
        flash(f"✅ Masa {f['table_no']} rezerve edildi — {f['date']} {f['slot']}")
    except sqlite3.IntegrityError:
        flash("⚠️ Bu masa o saatte zaten dolu.")
    return redirect(url_for("index", date=f["date"], slot=f["slot"]))


@app.route("/cancel/<int:rid>")
def cancel(rid):
    with db() as c:
        c.execute("DELETE FROM rez WHERE id=?", (rid,))
    flash("Rezervasyon iptal edildi.")
    return redirect(url_for("index"))



# --- hardened ---
@app.errorhandler(404)
def _err_404(e):
    return "404 - Sayfa bulunamadı", 404


@app.errorhandler(500)
def _err_500(e):
    return "500 - Sunucu hatası", 500


if __name__ == "__main__":
    init()
    port = int(os.environ.get("PORT", "5000"))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)
