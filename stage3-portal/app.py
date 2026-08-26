"""
Stage 3 -- "The Internal Portal" (Web Security)

Deliberately vulnerable Flask app for the Northwind Logistics Breach CTF.

VULN_MODE controls which single vulnerability class is live, per the
"pick one, don't stack multiple" guidance in the stage spec:
  VULN_MODE=sqli  -> login form is vulnerable to SQL injection auth bypass
  VULN_MODE=idor  -> message viewer is vulnerable to IDOR (no ownership
                     check), reachable via a normal low-priv test account

Only the selected class is exploitable; the other code path stays safe
(parameterized query / ownership check) so there's exactly one intended
solve path, matching the testing plan's "unintended-path check."

Reset behaviour: the SQLite DB is rebuilt from scratch every time the
container starts (see init_db()), so `docker compose restart
stage3-portal` alone restores a clean state -- matches the stage's
documented reset/recovery procedure.
"""
import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, session, g

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-change-me")
VULN_MODE = os.environ.get("VULN_MODE", "sqli")  # "sqli" or "idor"
DB_PATH = "/tmp/portal.db"

FLAG = "NW{4uth_1s_h4rd3r_th4n_1t_l00ks}"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE users (
        id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, display_name TEXT
    )""")
    conn.execute("""CREATE TABLE messages (
        id INTEGER PRIMARY KEY, user_id INTEGER, subject TEXT, body TEXT
    )""")
    conn.executemany(
        "INSERT INTO users (id, username, password, display_name) VALUES (?,?,?,?)",
        [
            (1, "ravi", "R@v!Ch4ndran_9f2", "Ravi Chandran"),
            (2, "test", "test123", "Test Account"),
            (3, "priya", "fleetops2024", "Priya Wickramasinghe"),
        ],
    )
    conn.executemany(
        "INSERT INTO messages (user_id, subject, body) VALUES (?,?,?)",
        [
            (1, "To self -- don't forget",
             f"Flag: {FLAG}\n\nEncrypted the export before I left, key's the "
             "usual short one from the team wiki. Sent the ciphertext to my "
             "own inbox as a text attachment, should still be on the file "
             "share under the crypto stage."),
            (2, "Welcome", "Welcome to the Northwind internal portal, test account."),
            (3, "Fleet schedule", "Reminder: fleet maintenance schedule posted Fridays."),
        ],
    )
    conn.commit()
    conn.close()


@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        db = get_db()

        if VULN_MODE == "sqli":
            # Intentionally vulnerable: naive string-built query.
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            try:
                row = db.execute(query).fetchone()
            except sqlite3.Error:
                row = None
        else:
            # Safe, parameterized -- SQLi is not the intended path in this mode.
            row = db.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password),
            ).fetchone()

        if row:
            session["user_id"] = row["id"]
            session["display_name"] = row["display_name"]
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    msgs = db.execute(
        "SELECT id, subject FROM messages WHERE user_id = ?", (session["user_id"],)
    ).fetchall()
    return render_template("dashboard.html", name=session["display_name"], messages=msgs)


@app.route("/message/<int:msg_id>")
def message(msg_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()

    if VULN_MODE == "idor":
        # Intentionally vulnerable: no ownership check on msg_id.
        row = db.execute("SELECT * FROM messages WHERE id = ?", (msg_id,)).fetchone()
    else:
        # Safe: only the owning user can view their own message.
        row = db.execute(
            "SELECT * FROM messages WHERE id = ? AND user_id = ?",
            (msg_id, session["user_id"]),
        ).fetchone()

    if not row:
        return render_template("message.html", subject="Not found", body="No such message, or access denied."), 404
    return render_template("message.html", subject=row["subject"], body=row["body"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
