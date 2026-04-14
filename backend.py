from flask import Flask, request, Response
import sqlite3
import json
import os

app = Flask(__name__)

# 🔥 Render için DB path (aynı klasörde)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "serino.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/vergi")
def vergi():
    tc = request.args.get("tc", "").strip()
    no = request.args.get("no", "").strip()
    ad = request.args.get("ad", "").strip()
    soyad = request.args.get("soyad", "").strip()

    conn = db()
    cur = conn.cursor()

    sql = "SELECT * FROM serino WHERE 1=1"
    params = []

    # 🔥 TC (en hızlı)
    if tc:
        sql += " AND TC = ?"
        params.append(tc)

    # 🔥 vergi no / seri no
    if no:
        sql += " AND SERINO LIKE ?"
        params.append(f"%{no}%")

    # 🔥 ad
    if ad:
        sql += " AND ADI LIKE ?"
        params.append(f"%{ad}%")

    # 🔥 soyad
    if soyad:
        sql += " AND SOYADI LIKE ?"
        params.append(f"%{soyad}%")

    sql += " LIMIT 50"

    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    return Response(
        json.dumps(
            {"status": "success", "count": len(rows), "data": rows},
            ensure_ascii=False
        ),
        content_type="application/json; charset=utf-8"
    )

@app.route("/")
def home():
    return {
        "status": "ok",
        "service": "serino api",
        "endpoints": {
            "/vergi?tc=": "TC ile sorgu",
            "/vergi?no=": "Vergi / seri no",
            "/vergi?ad=": "Ad ile sorgu",
            "/vergi?ad=&soyad=": "Ad soyad"
        }
    }

# 🔥 Render port fix
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
