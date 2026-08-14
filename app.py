from flask import Flask, request, redirect, send_from_directory, Response
from functools import wraps
import pyodbc
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

EMAIL_SENDER = "khushiyewale150@gmail.com"
EMAIL_PASSWORD = "aweejzlvecclpopp"

# Admin login credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "choose-a-strong-password"   # change this


def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=103.159.239.101;"
        "DATABASE=nrpaytrack;"
        "UID=nrpaytrackuser;"
        "PWD=u8z6mM5_7ycx;"
    )
    return conn


def send_confirmation_email(to_email):
    body = """Hi there,

Thank you for subscribing to CampusConnect AI!

You're now part of a growing community of students who stay ahead — with real-time updates on campus events, mess menus, hostel openings, and placement drives, delivered straight to your inbox.

CampusConnect AI is an AI-powered platform built to simplify campus life by bringing together:
- Mess & Tiffin Finder
- Hostel Locator
- Library Locator
- Verified Student Chat
- Mentor Connect
- Live Campus Events & Placement Updates

We're glad to have you on board. Stay tuned — your first update is on its way!

Best regards,
Team CampusConnect AI
NRSolution4u"""

    msg = MIMEText(body)
    msg['Subject'] = 'Welcome to CampusConnect AI 🎓'
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())


# ---- Basic Auth helpers ----
def check_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def authenticate():
    return Response(
        "Login required", 401,
        {"WWW-Authenticate": 'Basic realm="Admin Area"'}
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
# -----------------------------


@app.route('/')
def home():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_files(path):
    if os.path.isfile(path):
        return send_from_directory('.', path)
    return "File not found", 404


@app.route('/invite', methods=['POST'])
def invite():
    email = request.form.get('email')
    if not email:
        return "Missing email", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO invitedb (email) VALUES (?)", (email,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB ERROR:", e)
        return f"Error: {e}", 500

    try:
        send_confirmation_email(email)
    except Exception as e:
        print("EMAIL ERROR:", e)

    return redirect(request.referrer)


@app.route('/admin/subscribers')
@requires_auth
def view_subscribers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM invitedb")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        return f"Error: {e}", 500

    table_rows = "".join(f"<tr><td>{i+1}</td><td>{row.email}</td></tr>" for i, row in enumerate(rows))

    html = f"""
    <html>
    <head>
        <title>Subscribers</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 30px; background: #f4f4f4; }}
            table {{ border-collapse: collapse; width: 100%; max-width: 600px; background: white; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background: #333; color: white; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h2>Subscribers ({len(rows)})</h2>
        <table>
            <tr><th>#</th><th>Email</th></tr>
            {table_rows}
        </table>
    </body>
    </html>
    """
    return html


if __name__ == '__main__':
    app.run(debug=True)