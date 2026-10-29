from flask import Flask, request, render_template, Response, redirect, url_for, session, jsonify, send_from_directory, abort
from functools import wraps
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
import smtplib
import json
import os
import secrets
import string
from email.mime.text import MIMEText
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask_cors import CORS
from werkzeug.utils import secure_filename


# override=True -> values in .env always win over Windows environment variables,
# so the app can't silently keep talking to an old database.
load_dotenv(override=True)
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175", "http://127.0.0.1:5176",
    "http://localhost:5173",  "http://localhost:5174",  "http://localhost:5175",  "http://localhost:5176",
])

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-change-this')

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',   # 'None' requires Secure=True, which Chrome enforces
    SESSION_COOKIE_SECURE=False,     # True in production over HTTPS
)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Admin login credentials
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:5000")

# Where each role lands after a successful login.
ADMIN_DASHBOARD_URL = os.environ.get("ADMIN_DASHBOARD_URL", "http://localhost:5173/")
CAMPUS_DASHBOARD_URL = os.environ.get("CAMPUS_DASHBOARD_URL", "http://localhost:5174/")
# NOTE: use 127.0.0.1 (same host as the Flask API on :5000) so the session
# cookie is sent from the student panel. localhost vs 127.0.0.1 = different site.
STUDENT_DASHBOARD_URL = os.environ.get("STUDENT_DASHBOARD_URL", "http://127.0.0.1:5175/")


def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.environ.get('DB_SERVER')};"
        f"DATABASE={os.environ.get('DB_NAME')};"
        f"UID={os.environ.get('DB_USER')};"
        f"PWD={os.environ.get('DB_PASSWORD')};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )
    return conn


# ============================================================
# EMAIL HELPERS (one shared template, so every mail looks the same)
# ============================================================
def _email_html(heading, body_html, button_text=None, button_url=None, after_html=""):
    button = ""
    if button_text and button_url:
        button = f"""
                                <div style="text-align:center; margin: 30px 0;">
                                    <a href="{button_url}" style="background-color:#fd7e14; color:#ffffff; text-decoration:none; padding: 14px 32px; border-radius:8px; font-weight:600; display:inline-block;">
                                        {button_text}
                                    </a>
                                </div>"""
    return f"""
    <html>
    <body style="margin:0; padding:0; background-color:#f4f4f7; font-family: 'Segoe UI', Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7; padding: 40px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:10px; overflow:hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">
                        <tr>
                            <td style="background-color:#2d2d3a; padding: 35px 40px; text-align:center;">
                                <h1 style="margin:0; color:#ffffff; font-size:24px;">
                                    <span style="color:#ff6b35;">CAMPUS</span>CONNECT AI
                                </h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 40px;">
                                <h2 style="color:#2d2d3a; margin-top:0;">{heading}</h2>
                                {body_html}
                                {button}
                                {after_html}
                            </td>
                        </tr>
                        <tr>
                            <td style="background-color:#f4f4f7; padding: 25px 40px; text-align:center; border-top:1px solid #eaeaea;">
                                <p style="color:#999999; font-size:13px; margin:0;">
                                    Best regards,<br>
                                    <strong style="color:#2d2d3a;">Team CampusConnect AI</strong><br>
                                    NRSolution4u
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def _send_mail(to_email, subject, body, subtype='html', reply_to=None):
    msg = MIMEText(body, subtype)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email
    if reply_to:
        msg['Reply-To'] = reply_to
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())


_P = 'color:#555555; font-size:15px; line-height:1.6;'


def send_confirmation_email(to_email):
    features = [
        "Mess &amp; Tiffin Finder", "Hostel Locator", "Library Locator",
        "Verified Student Chat", "Mentor Connect",
        "Live Campus Events &amp; Placement Updates",
    ]
    rows = "".join(
        f'<tr><td style="padding:8px 0; color:#555555; font-size:14px;">'
        f'<span style="color:#ff6b35; font-weight:bold;">&#10003;</span> {f}</td></tr>'
        for f in features
    )
    body = f"""
                                <p style="{_P}">Thank you for subscribing to <strong>CampusConnect AI</strong>!</p>
                                <p style="{_P}">
                                    You're now part of a growing community of students who stay ahead &mdash;
                                    with real-time updates on campus events, mess menus, hostel openings,
                                    and placement drives, delivered straight to your inbox.
                                </p>
                                <p style="color:#2d2d3a; font-size:16px; font-weight:600; margin-top:30px;">
                                    What you'll get access to:
                                </p>
                                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:10px;">{rows}</table>
                                <p style="{_P} margin-top:30px;">
                                    We're glad to have you on board. Stay tuned &mdash; your first update is on its way!
                                </p>"""
    _send_mail(to_email, 'Welcome to CampusConnect AI', _email_html("Hi there", body))


def generate_random_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_expert_login_email(to_email, name, password):
    login_url = f"{APP_BASE_URL}/login.html"
    body = f"""
                                <p style="{_P}">
                                    You've been added as an expert on <strong>CampusConnect AI</strong>.
                                    Your account is ready &mdash; here are your login details:
                                </p>
                                <table cellpadding="0" cellspacing="0" style="margin: 25px 0; width:100%; background:#f9f9fb; border-radius:8px;">
                                    <tr>
                                        <td style="padding: 18px 20px;">
                                            <p style="margin:0 0 8px 0; color:#555555; font-size:14px;">
                                                <strong style="color:#2d2d3a;">Email:</strong> {to_email}
                                            </p>
                                            <p style="margin:0; color:#555555; font-size:14px;">
                                                <strong style="color:#2d2d3a;">Password:</strong> {password}
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                                <p style="{_P}">
                                    For your security, we recommend changing this password after your first login.
                                </p>"""
    after = f"""
                                <p style="color:#999999; font-size:13px; line-height:1.6;">
                                    If the button above doesn't work, copy and paste this link into your browser:<br>
                                    <a href="{login_url}" style="color:#fd7e14;">{login_url}</a>
                                </p>"""
    html = _email_html(f"Welcome aboard, {name}!", body, "Log In to Your Account", login_url, after)
    _send_mail(to_email, 'Your CampusConnect AI Expert Login Details', html)


def send_campus_approved_email(to_email, name, college_name):
    """Sent when an admin approves a college registration."""
    login_url = f"{APP_BASE_URL}/login.html"
    body = f"""
                                <p style="{_P}">
                                    Hi {name}, the registration for <strong>{college_name}</strong> has been
                                    approved. You can now log in with the email and password you registered with.
                                </p>"""
    html = _email_html("Your campus account is approved", body, "Log In to Your Campus Panel", login_url)
    _send_mail(to_email, 'Your CampusConnect AI campus account is approved', html)


def send_student_approved_email(to_email, name):
    login_url = f"{APP_BASE_URL}/login.html"
    body = f"""
                                <p style="{_P}">
                                    Hi {name}, your <strong>student registration</strong> on CampusConnect AI has been
                                    approved. You can now log in with the email and password you registered with.
                                </p>"""
    html = _email_html("Your student account is approved", body, "Log In to Your Student Panel", login_url)
    _send_mail(to_email, 'Your CampusConnect AI student account is approved', html)


def send_invite_email(to_email, subject, message):
    """Plain-text invite/broadcast email."""
    _send_mail(to_email, subject or "CampusConnect AI", message, subtype='plain')


# ============================================================
# AUTH HELPERS
# ============================================================
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


def requires_college(f):
    """Guards the campus-panel APIs: only a logged-in college account."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'college' or not session.get('college_id'):
            return {"success": False, "error": "Not logged in."}, 401
        return f(*args, **kwargs)
    return decorated


def requires_student(f):
    """Guards the student-panel APIs: only a logged-in student."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'student' or not session.get('student_id'):
            return {"success": False, "error": "Not logged in."}, 401
        return f(*args, **kwargs)
    return decorated


def requires_login(f):
    """Any logged-in user (admin / expert / college / student)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_email'):
            return {"success": False, "error": "Not logged in."}, 401
        return f(*args, **kwargs)
    return decorated


def debug_only(f):
    """Routes that only exist while Flask runs with debug=True (local dev)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not app.debug:
            abort(404)
        return f(*args, **kwargs)
    return decorated


# ============================================================
# STARTUP: create / migrate tables (safe to run on every start)
# ============================================================
def _run_startup_sql(label, statements):
    """Runs a list of SQL statements, one commit each. Never crashes startup."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for sql in statements:
            cursor.execute(sql)
            conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Could not ensure {label}:", e)


def ensure_college_status_columns():
    _run_startup_sql("collegedb status columns", [
        """IF NOT EXISTS (SELECT 1 FROM sys.columns
                          WHERE Name = N'Approved' AND Object_ID = Object_ID(N'collegedb'))
           ALTER TABLE collegedb ADD Approved BIT NOT NULL DEFAULT 0""",
        """IF NOT EXISTS (SELECT 1 FROM sys.columns
                          WHERE Name = N'Blocked' AND Object_ID = Object_ID(N'collegedb'))
           ALTER TABLE collegedb ADD Blocked BIT NOT NULL DEFAULT 0""",
    ])


def ensure_news_table():
    _run_startup_sql("News table", ["""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='News' AND xtype='U')
        CREATE TABLE News (
            NewsId INT IDENTITY(1,1) PRIMARY KEY,
            Title NVARCHAR(255) NOT NULL,
            Description NVARCHAR(MAX) NOT NULL,
            FilePath NVARCHAR(255) NULL,
            PostedOn DATETIME NOT NULL DEFAULT GETDATE()
        )"""])


def ensure_reviews_table():
    _run_startup_sql("Reviews table", ["""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Reviews' AND xtype='U')
        CREATE TABLE Reviews (
            ReviewId INT IDENTITY(1,1) PRIMARY KEY,
            Name NVARCHAR(255) NOT NULL,
            Message NVARCHAR(MAX) NOT NULL,
            Rating INT NOT NULL,
            PostedOn DATETIME NOT NULL DEFAULT GETDATE()
        )"""])


def ensure_student_table():
    _run_startup_sql("studentdb table", ["""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='studentdb' AND xtype='U')
        CREATE TABLE studentdb (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            Name NVARCHAR(255) NOT NULL,
            Email NVARCHAR(255) NOT NULL UNIQUE,
            MobileNo NVARCHAR(20) NOT NULL,
            CollegeName NVARCHAR(255) NOT NULL,
            Password NVARCHAR(255) NOT NULL,
            RegisteredOn DATE NOT NULL,
            Status NVARCHAR(10) NOT NULL DEFAULT 'Open',
            Approved BIT NOT NULL DEFAULT 0,
            Blocked BIT NOT NULL DEFAULT 0
        )"""])


def ensure_student_profile_columns():
    _run_startup_sql("studentdb profile columns", [
        """IF NOT EXISTS (SELECT 1 FROM sys.columns
                          WHERE Name = N'City' AND Object_ID = Object_ID(N'studentdb'))
           ALTER TABLE studentdb ADD City NVARCHAR(100) NULL""",
        """IF NOT EXISTS (SELECT 1 FROM sys.columns
                          WHERE Name = N'CollegeCode' AND Object_ID = Object_ID(N'studentdb'))
           ALTER TABLE studentdb ADD CollegeCode NVARCHAR(50) NULL""",
        """IF NOT EXISTS (SELECT 1 FROM sys.columns
                          WHERE Name = N'OtherCollege' AND Object_ID = Object_ID(N'studentdb'))
           ALTER TABLE studentdb ADD OtherCollege NVARCHAR(255) NULL""",
    ])


def ensure_chatbook_tables():
    _run_startup_sql("chatbook tables", [
        """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='chatbook_messages' AND xtype='U')
           CREATE TABLE chatbook_messages (
               id INT IDENTITY(1,1) PRIMARY KEY,
               sender_id INT NOT NULL,
               sender_name NVARCHAR(255) NOT NULL,
               text NVARCHAR(1000) NOT NULL,
               reply_to_id INT NULL,
               created_at DATETIME NOT NULL DEFAULT GETUTCDATE()
           )""",
        """IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='chatbook_presence' AND xtype='U')
           CREATE TABLE chatbook_presence (
               student_id INT PRIMARY KEY,
               name NVARCHAR(255) NOT NULL,
               last_seen DATETIME NOT NULL
           )""",
    ])


def ensure_applydb_table():
    """RojgarSetu 'Apply Now' applications. Only created if it is missing,
    so an existing applydb (with your data) is never touched."""
    _run_startup_sql("applydb table", ["""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='applydb' AND xtype='U')
        CREATE TABLE applydb (
            id INT IDENTITY(1,1) PRIMARY KEY,
            jobid INT NOT NULL,
            jobtitle NVARCHAR(255) NULL,
            company NVARCHAR(255) NULL,
            name NVARCHAR(255) NULL,
            email NVARCHAR(255) NOT NULL,
            profile NVARCHAR(MAX) NULL,
            salaryid NVARCHAR(100) NULL
        )"""])


ensure_college_status_columns()
ensure_news_table()
ensure_reviews_table()
ensure_student_table()
ensure_student_profile_columns()
ensure_chatbook_tables()
ensure_applydb_table()


def rows_to_dicts(cursor):
    """Fetch all rows as dicts; non-JSON types (dates, decimals) become str."""
    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    for r in rows:
        for k, v in r.items():
            if not isinstance(v, (str, int, float, type(None))):
                r[k] = str(v)
    return rows


# ============================================================
# PUBLIC PAGES
# ============================================================
@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    email = data.get('email')
    mobile = data.get('mobile')
    message = data.get('message')

    if not name or not email or not mobile:
        return {"success": False, "error": "Missing required fields"}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Enqdb (Name, Email, [Mobile No.], Message) VALUES (?, ?, ?, ?)",
            (name, email, mobile, message)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/')
def home():
    experts = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Name, Photo, Domain FROM Expertdb ORDER BY ID DESC")
        columns = [col[0] for col in cursor.description]
        experts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB ERROR:", e)
    return render_template('index.html', experts=experts)


@app.route('/internship.html')
def internship():
    return render_template('internship.html')


@app.route('/rojgarsetu.html')
def rojgarsetu():
    jobs = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM RojgarSetu ORDER BY JobId DESC")
        columns = [col[0] for col in cursor.description]
        jobs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB ERROR:", e)
    return render_template('rojgarsetu.html', jobs=jobs)


@app.route('/advertisement.html')
def advertisement():
    return render_template('advertisement.html')


@app.route('/contact.html')
def contact():
    return render_template('contact.html')


@app.route('/campus-agent')
def campus_agent():
    return render_template('campus_agent.html')


@app.route('/auth/google')
def auth_google():
    redirect_uri = url_for('auth_google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/auth/google/callback')
def auth_google_callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')

    if not user_info:
        return redirect('/registration.html?error=google_failed')

    # Dedicated one-time "prefill" keys (NOT session['user_email'] / ['role'],
    # which track a real logged-in session).
    session['oauth_prefill_email'] = user_info.get('email')
    session['oauth_prefill_name'] = user_info.get('name')

    print(f"Signed in via Google: {user_info.get('name')} ({user_info.get('email')})")

    return redirect('/registration.html?google_success=1')


@app.route('/registration.html')
def registration():
    prefill_name = session.pop('oauth_prefill_name', '')
    prefill_email = session.pop('oauth_prefill_email', '')
    return render_template('registration.html', prefill_name=prefill_name, prefill_email=prefill_email)


@app.route('/login.html')
def login():
    return render_template('login.html')


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

    return "OK", 200


@app.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    """Emails collected via the 'Invite Us' box on the homepage (invitedb)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM invitedb")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # invitedb only stores the email itself, so we assign a synthetic id
        data = [{"id": i + 1, "email": row.email} for i, row in enumerate(rows)]
        return {"success": True, "data": data}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/invite/send', methods=['POST'])
def send_invite():
    """Admin > Invite page: sends the composed subject/message to every
    selected recipient email."""
    data = request.get_json(silent=True) or {}

    emails = data.get('emails') or []
    subject = (data.get('subject') or '').strip()
    message = (data.get('message') or '').strip()

    if not isinstance(emails, list) or len(emails) == 0:
        return {"success": False, "error": "No recipients provided."}, 400

    if not message:
        return {"success": False, "error": "Message body is required."}, 400

    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return {"success": False, "error": "Email sender is not configured on the server."}, 500

    sent = []
    failed = []

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)

            for to_email in emails:
                try:
                    msg = MIMEText(message, 'plain')
                    msg['Subject'] = subject or "CampusConnect AI"
                    msg['From'] = EMAIL_SENDER
                    msg['To'] = to_email
                    server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
                    sent.append(to_email)
                except Exception as e:
                    print("INVITE SEND ERROR for", to_email, ":", e)
                    failed.append(to_email)
    except Exception as e:
        print("SMTP CONNECTION ERROR:", e)
        return {"success": False, "error": f"Could not connect to mail server: {e}"}, 500

    if failed and not sent:
        return {"success": False, "error": f"Failed to send to: {', '.join(failed)}"}, 500

    if failed:
        return {
            "success": True,
            "sent": len(sent),
            "failed": failed,
            "message": f"Sent to {len(sent)} recipient(s); failed for {len(failed)}."
        }, 200

    return {"success": True, "sent": len(sent)}, 200


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


CITIES_JSON_PATH = os.path.join(app.root_path, "static", "data", "cities_by_state.json")


@app.route('/api/cities', methods=['GET'])
def get_cities():
    with open(CITIES_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# ============================================================
# CAMPUS REGISTRATION + LOGIN
# ============================================================
@app.route('/api/register', methods=['POST'])
def register_campus():
    """Campus (college) registration. Student registration is separate:
    /api/student-register."""
    data = request.get_json(silent=True) or {}

    name = data.get('name')
    email = (data.get('email') or '').strip()
    mobile = data.get('mobile')
    city = data.get('city')
    college_name = data.get('college_name')
    college_code = data.get('college_code')
    password = data.get('password')

    if not name or not email or not mobile or not city or not college_name or not college_code or not password:
        return {"success": False, "error": "Missing required fields"}, 400

    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters."}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM collegedb WHERE Email = ?", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "error": "This email is already registered."}, 409

        cursor.execute("SELECT 1 FROM studentdb WHERE Email = ?", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "error": "This email is already used by a student account. Please use a different email."}, 409

        cursor.execute(
            "INSERT INTO collegedb (Name, Email, MobileNo, City, CollegeName, CollegeCode, Password) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, mobile, city, college_name, college_code, generate_password_hash(password))
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 201
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


def _clear_panel_ids():
    session.pop('college_id', None)
    session.pop('student_id', None)


def student_login(email, password, next_url):
    """Called by /api/login when the email isn't in logindb or collegedb.
    Returns a (json, status) tuple, or None if no such student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ID, Email, Password, Approved, Blocked FROM studentdb WHERE Email = ?",
        (email,)
    )
    st = cursor.fetchone()
    cursor.close()
    conn.close()

    if not st:
        return None

    try:
        password_ok = check_password_hash(st.Password, password)
    except Exception:
        password_ok = False

    if not password_ok:
        print(f"LOGIN: student {email} found, but password does not match the stored hash")
        return {"success": False, "error": "Invalid email or password."}, 401
    if st.Blocked:
        return {"success": False, "error": "Your account has been blocked. Please contact the admin."}, 403
    if not st.Approved:
        return {"success": False, "error": "Your registration is still awaiting admin approval."}, 403

    session['logged_in'] = True
    session['user_email'] = st.Email
    session['role'] = 'student'
    session['student_id'] = st.ID
    session.pop('college_id', None)

    return {"success": True, "role": "student", "redirect": next_url or STUDENT_DASHBOARD_URL}, 200


@app.route('/api/login', methods=['POST'])
def login_user():
    """One login endpoint for every kind of account:

      1. admin / expert   -> logindb
      2. college (campus) -> collegedb
      3. student          -> studentdb

    Colleges / students may only get in once an admin has approved them
    (Approved = 1) and hasn't blocked them (Blocked = 0).
    """
    data = request.get_json(silent=True) or {}

    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    # Optional ?next= page to return to after login. Only same-site relative
    # paths are accepted (prevents open redirects).
    next_url = data.get('next')
    if not next_url or not isinstance(next_url, str) or not next_url.startswith('/'):
        next_url = None

    if not email or not password:
        return {"success": False, "error": "Email and password are required."}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ---- 1. admin / expert accounts (logindb) ----
        cursor.execute(
            "SELECT login_id, email, password, role FROM logindb WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()

        if row:
            # logindb may hold legacy plain-text passwords next to hashed ones.
            try:
                password_ok = check_password_hash(row.password, password)
            except Exception:
                password_ok = False
            if not password_ok and row.password == password:
                password_ok = True

            if not password_ok:
                cursor.close()
                conn.close()
                print(f"LOGIN: {email} found in logindb, password mismatch")
                return {"success": False, "error": "Invalid email or password."}, 401

            role = (row.role or '').lower()

            if role in ("admin", "expert"):
                session['logged_in'] = True
                session['user_email'] = row.email
                session['role'] = row.role
                _clear_panel_ids()
                cursor.close()
                conn.close()
                default_url = ADMIN_DASHBOARD_URL if role == "admin" else "/"
                return {"success": True, "role": role, "redirect": next_url or default_url}, 200

            cursor.close()
            conn.close()
            return {"success": False, "error": "You are not authorized to access this page."}, 403

        # ---- 2. college / campus accounts (collegedb) ----
        cursor.execute(
            "SELECT ID, Name, Email, Password, CollegeName, Approved, Blocked FROM collegedb WHERE Email = ?",
            (email,)
        )
        college = cursor.fetchone()
        cursor.close()
        conn.close()

        # ---- 3. student accounts (studentdb) ----
        if not college:
            student_resp = student_login(email, password, next_url)
            if student_resp:
                return student_resp
            print(f"LOGIN: {email} not found in logindb, collegedb or studentdb "
                  f"(connected to DB: {os.environ.get('DB_NAME')})")
            return {"success": False, "error": "Invalid email or password."}, 401

        try:
            password_ok = check_password_hash(college.Password, password)
        except Exception:
            password_ok = False

        if not password_ok:
            print(f"LOGIN: college {email} found, password mismatch")
            return {"success": False, "error": "Invalid email or password."}, 401

        # Blocked wins over approved.
        if college.Blocked:
            return {"success": False, "error": "Your account has been blocked. Please contact the admin."}, 403

        if not college.Approved:
            return {"success": False, "error": "Your registration is still awaiting admin approval."}, 403

        session['logged_in'] = True
        session['user_email'] = college.Email
        session['role'] = 'college'
        session['college_id'] = college.ID
        session.pop('student_id', None)

        return {"success": True, "role": "college", "redirect": next_url or CAMPUS_DASHBOARD_URL}, 200

    except Exception as e:
        print("LOGIN DB ERROR:", e)
        return {"success": False, "error": "Database connection error."}, 500


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return {"success": True}, 200


# ============================================================
# CAMPUS PANEL APIs (the logged-in college's own data)
# ============================================================
@app.route('/api/campus/profile', methods=['GET'])
@requires_college
def campus_profile():
    """Campus panel header data: college details + the logo uploaded on the
    Advertisement page (matched on Advertisement.Name == CollegeName)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT ID, Name, Email, MobileNo, City, CollegeName, CollegeCode FROM collegedb WHERE ID = ?",
            (session['college_id'],)
        )
        college = cursor.fetchone()

        if not college:
            cursor.close()
            conn.close()
            session.clear()
            return {"success": False, "error": "Account no longer exists."}, 404

        cursor.execute(
            """
            SELECT TOP 1 Name, LogoPath
            FROM Advertisement
            WHERE Name = ? AND LogoPath IS NOT NULL
            ORDER BY RegistrationDate DESC
            """,
            (college.CollegeName,)
        )
        ad = cursor.fetchone()

        cursor.close()
        conn.close()

        return {
            "success": True,
            "data": {
                "id": college.ID,
                "name": college.Name,
                "email": college.Email,
                "mobile": college.MobileNo,
                "city": college.City,
                "college_name": college.CollegeName,
                "college_code": college.CollegeCode,
                "logo_url": (
                    f"/static/uploads/advertisements/{ad.LogoPath}"
                    if ad and ad.LogoPath else None
                )
            }
        }, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/campus/session', methods=['GET'])
def campus_session():
    if session.get('role') == 'college' and session.get('college_id'):
        return {"success": True, "logged_in": True, "email": session.get('user_email')}, 200
    return {"success": True, "logged_in": False}, 200


@app.route('/api/campus/profile', methods=['PUT'])
@requires_college
def update_campus_profile():
    """Campus can edit ONLY mobile and city."""
    data = request.get_json(silent=True) or {}
    mobile = (data.get('mobile') or '').strip()
    city = (data.get('city') or '').strip()

    if not mobile or not city:
        return {"success": False, "error": "Mobile and city are required."}, 400
    if not mobile.isdigit() or not (10 <= len(mobile) <= 15):
        return {"success": False, "error": "Enter a valid mobile number."}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE collegedb SET MobileNo = ?, City = ? WHERE ID = ?",
            (mobile, city, session['college_id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/campus/password', methods=['PUT'])
@requires_college
def change_campus_password():
    data = request.get_json(silent=True) or {}
    current_password = data.get('current_password') or ''
    new_password = data.get('new_password') or ''

    if len(new_password) < 6:
        return {"success": False, "error": "New password must be at least 6 characters."}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Password FROM collegedb WHERE ID = ?", (session['college_id'],))
        row = cursor.fetchone()

        if not row or not check_password_hash(row.Password, current_password):
            cursor.close()
            conn.close()
            return {"success": False, "error": "Current password is incorrect."}, 400

        cursor.execute(
            "UPDATE collegedb SET Password = ? WHERE ID = ?",
            (generate_password_hash(new_password), session['college_id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


# ============================================================
# ADMIN PANEL: enquiries, campus registrations
# ============================================================
@app.route('/api/enquiries', methods=['GET'])
def get_enquiries():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID, Name, Email, [Mobile No.], Message FROM Enqdb")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        data = [
            {"id": r[0], "name": r[1], "email": r[2], "mobile": r[3], "message": r[4]}
            for r in rows
        ]
        return {"success": True, "data": data}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


def _execute_one(sql, params, not_found_msg):
    """Runs one UPDATE/DELETE and returns the JSON response tuple."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        if affected == 0:
            return {"success": False, "error": not_found_msg}, 404
        return {"success": True}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/enquiries/<int:enquiry_id>', methods=['DELETE'])
def delete_enquiry(enquiry_id):
    return _execute_one("DELETE FROM Enqdb WHERE ID = ?", (enquiry_id,), "Enquiry not found.")


@app.route('/api/registrations', methods=['GET'])
def get_registrations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, Name, Email, MobileNo, City, CollegeName, RegisteredOn, Approved, Blocked FROM collegedb"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        data = [
            {
                "id": r[0],
                "name": r[1],
                "email": r[2],
                "mobile": r[3],
                "city": r[4],
                "college_name": r[5],
                "registered_on": str(r[6]) if r[6] else "",
                "approved": bool(r[7]),
                "blocked": bool(r[8])
            }
            for r in rows
        ]
        return {"success": True, "data": data}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/registrations/<int:reg_id>/approve', methods=['PUT'])
def approve_registration(reg_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE collegedb SET Approved = 1, Blocked = 0 WHERE ID = ?", (reg_id,))
        conn.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return {"success": False, "error": "Registration not found."}, 404

        cursor.execute("SELECT Name, Email, CollegeName FROM collegedb WHERE ID = ?", (reg_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500

    if row and row.Email:
        try:
            send_campus_approved_email(row.Email, row.Name, row.CollegeName)
        except Exception as e:
            print("EMAIL ERROR:", e)  # approval already saved; email is best-effort

    return {"success": True}, 200


@app.route('/api/registrations/<int:reg_id>/block', methods=['PUT'])
def block_registration(reg_id):
    return _execute_one("UPDATE collegedb SET Blocked = 1 WHERE ID = ?", (reg_id,), "Registration not found.")


@app.route('/api/registrations/<int:reg_id>/unblock', methods=['PUT'])
def unblock_registration(reg_id):
    return _execute_one("UPDATE collegedb SET Blocked = 0 WHERE ID = ?", (reg_id,), "Registration not found.")


@app.route('/api/registrations/<int:reg_id>', methods=['DELETE'])
def delete_registration(reg_id):
    return _execute_one("DELETE FROM collegedb WHERE ID = ?", (reg_id,), "Registration not found.")


# ============================================================
# EXPERTS
# ============================================================
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads', 'experts')
ALLOWED_EXT = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


@app.route('/api/experts', methods=['GET'])
def get_experts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Expertdb ORDER BY ID DESC")
        rows = rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return {"success": True, "data": rows}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/experts', methods=['POST'])
def add_expert():
    name = request.form.get('name')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    domain = request.form.get('domain_select')
    if domain == 'Other':
        domain = request.form.get('domain_other')
    linkedin = request.form.get('linkedin')
    city = request.form.get('city')
    plan_type = request.form.get('plan_type', 'Yearly')
    amount = request.form.get('amount', 1200)
    transaction_id = request.form.get('transaction_id')
    payment_date = request.form.get('payment_date')
    expiry_date = request.form.get('expiry_date')

    if not name or not email or not mobile or not domain:
        return {"success": False, "error": "Missing required fields"}, 400

    photo_filename = None
    photo = request.files.get('photo')
    if photo and photo.filename and allowed_file(photo.filename):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        photo_filename = secure_filename(f"{mobile}_{photo.filename}")
        photo.save(os.path.join(UPLOAD_FOLDER, photo_filename))

    generated_password = generate_random_password()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO Expertdb
               (Name, Email, Mobile, Domain, LinkedinURL, Photo, City,
                PlanType, Amount, TransactionID, PaymentDate, ExpiryDate)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, email, mobile, domain, linkedin, photo_filename, city,
             plan_type, amount, transaction_id, payment_date, expiry_date)
        )

        # Only create login credentials if this email has no account yet
        cursor.execute("SELECT 1 FROM logindb WHERE email = ?", (email,))
        already_has_login = cursor.fetchone() is not None

        if not already_has_login:
            cursor.execute(
                "INSERT INTO logindb (email, password, role) VALUES (?, ?, ?)",
                (email, generate_password_hash(generated_password), 'expert')
            )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500

    if not already_has_login:
        try:
            send_expert_login_email(email, name, generated_password)
        except Exception as e:
            print("EMAIL ERROR:", e)  # expert + login exist; email is best-effort

    return {"success": True}, 201


@app.route('/expert/<int:expert_id>')
def expert_detail(expert_id):
    if not session.get('user_email'):
        return redirect(url_for('login') + f'?next=/expert/{expert_id}')

    expert = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Expertdb WHERE ID = ?", (expert_id,))
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            expert = dict(zip(columns, row))
    except Exception as e:
        print("DB ERROR:", e)

    if not expert:
        return "Expert not found", 404

    return render_template('expert_detail.html', expert=expert)


@app.route('/api/experts/<int:expert_id>', methods=['DELETE'])
def delete_expert(expert_id):
    return _execute_one("DELETE FROM Expertdb WHERE ID = ?", (expert_id,), "Expert not found.")


# ============================================================
# ADVERTISEMENTS
# ============================================================
ADV_UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads', 'advertisements')
ALLOWED_ADV_EXT = {'png', 'jpg', 'jpeg'}


def allowed_adv_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_ADV_EXT


@app.route('/api/advertisements', methods=['GET'])
def get_advertisements():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Advertisement ORDER BY AdvertisementId DESC")
        rows = rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return {"success": True, "data": rows}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/advertisements', methods=['POST'])
def add_advertisement():
    name = request.form.get('name')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    cost = request.form.get('cost', 1200)
    duration = request.form.get('duration', '6 Months')
    registration_date = request.form.get('registration_date')  # yyyy-mm-dd

    if not name or not email or not mobile or not registration_date:
        return {"success": False, "error": "Missing required fields"}, 400

    logo_filename = None
    logo = request.files.get('logo')
    if logo and logo.filename and allowed_adv_file(logo.filename):
        os.makedirs(ADV_UPLOAD_FOLDER, exist_ok=True)
        logo_filename = secure_filename(f"{mobile}_{logo.filename}")
        logo.save(os.path.join(ADV_UPLOAD_FOLDER, logo_filename))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # ExpiryDate is a computed column in SQL Server - do NOT insert it
        cursor.execute(
            """INSERT INTO Advertisement
               (Name, Email, Mobile, LogoPath, Cost, Duration, RegistrationDate)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, email, mobile, logo_filename, cost, duration, registration_date)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 201
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/advertisements/<int:adv_id>', methods=['DELETE'])
def delete_advertisement(adv_id):
    return _execute_one("DELETE FROM Advertisement WHERE AdvertisementId = ?", (adv_id,), "Advertisement not found.")


@app.route('/api/advertisements/active', methods=['GET'])
def get_active_advertisements():
    """Public: only non-expired ads with a logo, no personal fields."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Name, LogoPath
            FROM Advertisement
            WHERE LogoPath IS NOT NULL
              AND ExpiryDate >= ?
            ORDER BY RegistrationDate DESC
        """, (date.today(),))

        rows = cursor.fetchall()
        data = [{"Name": r.Name, "LogoPath": r.LogoPath} for r in rows]
        cursor.close()
        conn.close()

        return {"success": True, "data": data}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


# ============================================================
# INTERNSHIPS
# ============================================================
@app.route('/api/internships', methods=['GET'])
def get_internships():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT InternshipId, Company AS company, Email AS email, Mobile AS mobile,
                   CompanyType AS companyType, Duration AS duration, Stipend AS stipend,
                   ApplicationLink AS link, Location AS location, Branch AS branch,
                   Status AS status, PostedOn AS postedOn
            FROM Internship ORDER BY InternshipId DESC
        """)
        rows = rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return {"success": True, "data": rows}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/internships', methods=['POST'])
def add_internship():
    # Keys match the Vue form: company, email, mobile, companyType, duration,
    # stipend, link, location, branch, status
    data = request.get_json(silent=True) or {}

    company = data.get('company')
    email = data.get('email')
    mobile = data.get('mobile')

    if not company or not email or not mobile:
        return {"success": False, "error": "Company, Email and Mobile are required"}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO Internship
               (Company, Email, Mobile, CompanyType, Duration, Stipend, ApplicationLink, Location, Branch, Status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (company, email, mobile, data.get('companyType'), data.get('duration'),
             data.get('stipend'), data.get('link'), data.get('location'),
             data.get('branch'), data.get('status'))
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 201
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/internships/<int:internship_id>', methods=['DELETE'])
def delete_internship(internship_id):
    return _execute_one("DELETE FROM Internship WHERE InternshipId = ?", (internship_id,), "Internship not found.")


@app.route('/api/internships/<int:internship_id>/status', methods=['PATCH'])
def update_internship_status(internship_id):
    data = request.get_json(silent=True) or {}
    status = data.get('status')

    if status not in ('Open', 'Closed'):
        return {"success": False, "error": "Status must be 'Open' or 'Closed'."}, 400

    return _execute_one(
        "UPDATE Internship SET Status = ? WHERE InternshipId = ?",
        (status, internship_id), "Internship not found."
    )


# ============================================================
# NEWS
# ============================================================
NEWS_UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads', 'news')
ALLOWED_NEWS_EXT = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}


def allowed_news_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_NEWS_EXT


@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM News ORDER BY NewsId DESC")
        rows = rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return {"success": True, "data": rows}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/news', methods=['POST'])
def add_news():
    title = request.form.get('title')
    description = request.form.get('description')

    if not title or not description:
        return {"success": False, "error": "Title and Description are required"}, 400

    file_filename = None
    uploaded_file = request.files.get('file')
    if uploaded_file and uploaded_file.filename:
        if not allowed_news_file(uploaded_file.filename):
            return {"success": False, "error": "Unsupported file type."}, 400
        os.makedirs(NEWS_UPLOAD_FOLDER, exist_ok=True)
        file_filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(NEWS_UPLOAD_FOLDER, file_filename))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO News (Title, Description, FilePath) VALUES (?, ?, ?)",
            (title, description, file_filename)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 201
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    return _execute_one("DELETE FROM News WHERE NewsId = ?", (news_id,), "News not found.")


# ============================================================
# ROJGARSETU (job postings)
# ============================================================
@app.route('/api/rojgarsetu', methods=['GET'])
def get_job_postings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM RojgarSetu ORDER BY JobId DESC")
        rows = rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return {"success": True, "data": rows}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/rojgarsetu', methods=['POST'])
def add_job_posting():
    # Keys match the Vue form: category, jobTitle, companyName, location,
    # email, mobile, experience, salary, link
    data = request.get_json(silent=True) or {}

    job_title = data.get('jobTitle')
    company_name = data.get('companyName')

    if not job_title or not company_name:
        return {"success": False, "error": "Job Title and Company Name are required"}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO RojgarSetu
               (JobCategory, JobTitle, CompanyName, Location, Email, Mobile, Experience, SalaryLPA, ApplicationLink)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.get('category'), job_title, company_name, data.get('location'),
             data.get('email'), data.get('mobile'), data.get('experience'),
             data.get('salary'), data.get('link'))
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 201
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/rojgarsetu/<int:job_id>', methods=['DELETE'])
def delete_job_posting(job_id):
    return _execute_one("DELETE FROM RojgarSetu WHERE JobId = ?", (job_id,), "Job posting not found.")


# ============================================================
# REVIEWS
# ============================================================
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Reviews ORDER BY ReviewId DESC")
        rows = rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return {"success": True, "data": rows}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/reviews', methods=['POST'])
def add_review():
    # Keys match the Vue ReviewForm: name, message, rating
    data = request.get_json(silent=True) or {}

    name = data.get('name')
    message = data.get('message')
    rating = data.get('rating')

    if not name or not message or not rating:
        return {"success": False, "error": "Name, Message and Rating are required"}, 400

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return {"success": False, "error": "Rating must be a number."}, 400

    if rating < 1 or rating > 5:
        return {"success": False, "error": "Rating must be between 1 and 5."}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Reviews (Name, Message, Rating) VALUES (?, ?, ?)",
            (name, message, rating)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 201
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    return _execute_one("DELETE FROM Reviews WHERE ReviewId = ?", (review_id,), "Review not found.")


# ============================================================
# STATIC PANEL BUILDS
# ============================================================
@app.route('/admin')
@app.route('/admin/<path:path>')
def admin_dashboard(path='index.html'):
    return send_from_directory('static/admin', path)


@app.route('/campus')
@app.route('/campus/<path:path>')
def campus_dashboard(path='index.html'):
    return send_from_directory('static/campus', path)


# ============================================================
# STUDENT FLOW
#
#   1. Student registers   -> /student-registration  (Flask form, :5000)
#   2. Row goes to studentdb with Approved = 0
#   3. Admin approves      -> admin panel "Register Student" page (:5173)
#   4. Student logs in     -> /api/login  -> redirect to student panel (:5175)
#   5. Student panel calls /api/student/session:
#        has_college = False (college = 'Other') -> only Profile menu
#        has_college = True                      -> all menus
#   6. On the Profile page the student picks / types a college
#        -> PUT /api/student/profile -> menus unlock
# ============================================================
@app.route('/student-registration')
def student_registration():
    return render_template('student_registration.html')


@app.route('/api/colleges', methods=['GET'])
def get_colleges():
    """Every college registered through Campus Registration (collegedb).
    To show only approved ones, add:  WHERE Approved = 1"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT CollegeName FROM collegedb ORDER BY CollegeName")
        names = [r[0] for r in cursor.fetchall() if r[0]]
        cursor.close()
        conn.close()
        return {"success": True, "data": names}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/student-register', methods=['POST'])
def register_student_account():
    data = request.get_json(silent=True) or {}

    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    mobile = (data.get('mobile') or '').strip()
    college_name = (data.get('college_name') or '').strip()
    other_college = (data.get('other_college') or '').strip()
    password = data.get('password') or ''
    status = data.get('status') or 'Open'

    if not name or not email or not mobile or not college_name or not password:
        return {"success": False, "error": "Missing required fields"}, 400
    if college_name != 'Other':
        other_college = ''
    if not mobile.isdigit() or not (10 <= len(mobile) <= 15):
        return {"success": False, "error": "Enter a valid mobile number."}, 400
    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters."}, 400
    if status not in ('Open', 'Close'):
        return {"success": False, "error": "Status must be 'Open' or 'Close'."}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM studentdb WHERE Email = ?", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "error": "This email is already registered."}, 409

        # An email that belongs to a campus account can't also be a student
        # (login checks collegedb first, so it would open the campus panel).
        cursor.execute("SELECT 1 FROM collegedb WHERE Email = ?", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "error": "This email is already used by a campus account. Please use a different email."}, 409

        # College must be a registered campus, or the literal "Other"
        if college_name != 'Other':
            cursor.execute("SELECT 1 FROM collegedb WHERE CollegeName = ?", (college_name,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return {"success": False, "error": "Please choose a college from the list."}, 400

        cursor.execute(
            """INSERT INTO studentdb
               (Name, Email, MobileNo, CollegeName, OtherCollege, Password, RegisteredOn, Status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, email, mobile, college_name, other_college or None,
             generate_password_hash(password), date.today(), status)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 201
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


# ---- Admin panel: student registrations ----
@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, Name, Email, MobileNo, CollegeName, RegisteredOn, Status, Approved, Blocked, OtherCollege "
            "FROM studentdb ORDER BY ID DESC"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        data = [
            {
                "id": r[0], "name": r[1], "email": r[2], "mobile": r[3],
                "college_name": (f"Other - {r[9]}" if r[4] == 'Other' and r[9] else r[4]),
                "registered_on": str(r[5]) if r[5] else "",
                "status": r[6], "approved": bool(r[7]), "blocked": bool(r[8])
            }
            for r in rows
        ]
        return {"success": True, "data": data}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/students/<int:student_id>/approve', methods=['PUT'])
def approve_student(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE studentdb SET Approved = 1, Blocked = 0 WHERE ID = ?", (student_id,))
        conn.commit()
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return {"success": False, "error": "Student not found."}, 404
        cursor.execute("SELECT Name, Email FROM studentdb WHERE ID = ?", (student_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500

    if row and row.Email:
        try:
            send_student_approved_email(row.Email, row.Name)
        except Exception as e:
            print("EMAIL ERROR:", e)  # approval already saved; email is best-effort

    return {"success": True}, 200


@app.route('/api/students/<int:student_id>/block', methods=['PUT'])
def block_student(student_id):
    return _execute_one("UPDATE studentdb SET Blocked = 1 WHERE ID = ?", (student_id,), "Student not found.")


@app.route('/api/students/<int:student_id>/unblock', methods=['PUT'])
def unblock_student(student_id):
    return _execute_one("UPDATE studentdb SET Blocked = 0 WHERE ID = ?", (student_id,), "Student not found.")


@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    return _execute_one("DELETE FROM studentdb WHERE ID = ?", (student_id,), "Student not found.")


# ---- Student panel APIs (the logged-in student's own data) ----
@app.route('/api/student/session', methods=['GET'])
def student_session():
    """Student panel calls this on load.
    has_college = False  -> only the Profile menu (college is 'Other')
    has_college = True   -> all menus
    """
    if session.get('role') != 'student' or not session.get('student_id'):
        return {"success": True, "logged_in": False}, 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Name, Email, CollegeName, Approved, Blocked FROM studentdb WHERE ID = ?",
            (session['student_id'],)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500

    if not row:
        session.clear()
        return {"success": True, "logged_in": False}, 200

    has_college = bool(row.CollegeName) and row.CollegeName != 'Other'

    return {
        "success": True,
        "logged_in": True,
        "approved": bool(row.Approved),
        "blocked": bool(row.Blocked),
        "name": row.Name,
        "email": row.Email,
        "college_name": row.CollegeName,
        "has_college": has_college,
        "profile_completed": has_college
    }, 200


@app.route('/api/student/profile', methods=['GET'])
@requires_student
def get_student_profile():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, Name, Email, MobileNo, CollegeName, RegisteredOn, City, CollegeCode, OtherCollege "
            "FROM studentdb WHERE ID = ?",
            (session['student_id'],)
        )
        r = cursor.fetchone()
        cursor.close()
        conn.close()

        if not r:
            session.clear()
            return {"success": False, "error": "Account no longer exists."}, 404

        return {
            "success": True,
            "data": {
                "id": r.ID,
                "name": r.Name,
                "email": r.Email,
                "mobile": r.MobileNo,
                "college_name": r.CollegeName,
                "registered_on": str(r.RegisteredOn) if r.RegisteredOn else "",
                "city": r.City,
                "college_code": r.CollegeCode,
                "other_college": r.OtherCollege,
                "has_college": bool(r.CollegeName) and r.CollegeName != 'Other'
            }
        }, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/student/profile', methods=['PUT'])
@requires_student
def update_student_profile():
    """Profile page: student sets their college (only while it is 'Other').
    It can be one from the list OR a name the student typed."""
    data = request.get_json(silent=True) or {}
    college_name = (data.get('college_name') or '').strip()
    city = (data.get('city') or '').strip()

    if not college_name or college_name.lower() == 'other':
        return {"success": False, "error": "Please choose your college or type its name."}, 400
    if len(college_name) > 255:
        return {"success": False, "error": "College name is too long."}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT CollegeName FROM studentdb WHERE ID = ?", (session['student_id'],))
        current = cursor.fetchone()
        if not current:
            cursor.close()
            conn.close()
            return {"success": False, "error": "Student not found."}, 404
        if current.CollegeName != 'Other':
            cursor.close()
            conn.close()
            return {"success": False, "error": "College is already set."}, 403

        cursor.execute(
            "UPDATE studentdb SET CollegeName = ?, City = ?, OtherCollege = NULL WHERE ID = ?",
            (college_name, city or None, session['student_id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/student/')
@app.route('/student/<path:path>')
def student(path=''):
    return render_template('student.html')


@app.route('/api/student/dashboard-counts', methods=['GET'])
@requires_student
def student_dashboard_counts():
    """Total counts for the student dashboard cards (same style as admin)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        def count(sql):
            cursor.execute(sql)
            return cursor.fetchone()[0]

        data = {
            "services": count("SELECT COUNT(*) FROM Internship"),
            "rojgarsetu": count("SELECT COUNT(*) FROM RojgarSetu"),
            "expertise": count("SELECT COUNT(*) FROM Expertdb"),
            "review": count("SELECT COUNT(*) FROM Reviews"),
            "chatbook": count("SELECT COUNT(*) FROM chatbook_messages"),
        }

        cursor.close()
        conn.close()
        return {"success": True, **data}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


# ============================================================
# CHATBOOK (student group chat)
# ============================================================
CHATBOOK_ONLINE_SECONDS = 20


@app.route('/api/chatbook/sync', methods=['GET'])
@requires_student
def chatbook_sync():
    """One call does everything: marks this student online, returns who is
    online, and returns any messages newer than ?after_id=."""
    student_id = session['student_id']
    try:
        after_id = int(request.args.get('after_id', 0))
    except ValueError:
        after_id = 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT Name FROM studentdb WHERE ID = ?", (student_id,))
        me_row = cursor.fetchone()
        if not me_row:
            cursor.close()
            conn.close()
            session.clear()
            return {"success": False, "error": "Account no longer exists."}, 401
        my_name = me_row.Name

        # 1. mark me online
        cursor.execute(
            "UPDATE chatbook_presence SET last_seen = GETUTCDATE(), name = ? WHERE student_id = ?",
            (my_name, student_id)
        )
        if cursor.rowcount == 0:
            cursor.execute(
                "INSERT INTO chatbook_presence (student_id, name, last_seen) VALUES (?, ?, GETUTCDATE())",
                (student_id, my_name)
            )

        # 2. who is online right now
        cursor.execute(
            "SELECT student_id, name FROM chatbook_presence "
            "WHERE last_seen >= DATEADD(SECOND, ?, GETUTCDATE()) ORDER BY name",
            (-CHATBOOK_ONLINE_SECONDS,)
        )
        online = [{"id": r.student_id, "name": r.name} for r in cursor.fetchall()]

        # 3. messages (first load = last 100, after that only new ones)
        select = """
            SELECT {top} m.id, m.sender_id, m.sender_name, m.text, m.created_at,
                   r.id AS r_id, r.sender_id AS r_sender_id,
                   r.sender_name AS r_sender_name, r.text AS r_text
            FROM chatbook_messages m
            LEFT JOIN chatbook_messages r ON r.id = m.reply_to_id
            WHERE m.id > ?
            ORDER BY m.id {direction}
        """
        if after_id == 0:
            cursor.execute(select.format(top="TOP 100", direction="DESC"), (after_id,))
            rows = list(reversed(cursor.fetchall()))
        else:
            cursor.execute(select.format(top="", direction="ASC"), (after_id,))
            rows = cursor.fetchall()

        messages = [
            {
                "id": r.id,
                "senderId": r.sender_id,
                "sender": r.sender_name,
                "text": r.text,
                "time": r.created_at.isoformat() + "Z",
                "replyTo": (
                    {"id": r.r_id, "senderId": r.r_sender_id,
                     "sender": r.r_sender_name, "text": r.r_text}
                    if r.r_id else None
                ),
            }
            for r in rows
        ]

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "success": True,
            "me": {"id": student_id, "name": my_name},
            "online": online,
            "messages": messages,
        }, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/chatbook/messages', methods=['POST'])
@requires_student
def chatbook_send():
    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()[:1000]
    reply_to_id = data.get('reply_to_id')

    if not text:
        return {"success": False, "error": "Empty message."}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT Name FROM studentdb WHERE ID = ?", (session['student_id'],))
        me_row = cursor.fetchone()
        if not me_row:
            cursor.close()
            conn.close()
            return {"success": False, "error": "Account no longer exists."}, 401

        cursor.execute(
            "INSERT INTO chatbook_messages (sender_id, sender_name, text, reply_to_id) VALUES (?, ?, ?, ?)",
            (session['student_id'], me_row.Name, text, reply_to_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 201
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


# ============================================================
# ROJGARSETU: student applications (applydb)
# ============================================================
@app.route('/api/apply', methods=['POST'])
@requires_student
def apply_job():
    data = request.get_json(silent=True) or {}

    jobid = data.get('jobid')
    jobtitle = (data.get('jobtitle') or '').strip()
    company = (data.get('company') or '').strip()
    salaryid = data.get('salaryid')

    if not jobid or not jobtitle or not company:
        return {"success": False, "message": "Missing required fields"}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # name / email come from the logged-in student's studentdb row
        cursor.execute("SELECT Name, Email FROM studentdb WHERE ID = ?", (session['student_id'],))
        st = cursor.fetchone()
        if not st:
            cursor.close()
            conn.close()
            session.clear()
            return {"success": False, "message": "Account no longer exists."}, 401

        # one application per student per job
        cursor.execute("SELECT 1 FROM applydb WHERE jobid = ? AND email = ?", (jobid, st.Email))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "message": "Already applied to this job"}, 409

        cursor.execute(
            """INSERT INTO applydb (jobid, jobtitle, company, name, email, profile, salaryid)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (jobid, jobtitle, company, st.Name, st.Email, None, salaryid)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True, "message": "Applied successfully"}, 201
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "message": str(e)}, 500


@app.route('/api/applied', methods=['GET'])
@requires_student
def applied_jobs():
    """Job ids the logged-in student has already applied to."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Email FROM studentdb WHERE ID = ?", (session['student_id'],))
        st = cursor.fetchone()
        if not st:
            cursor.close()
            conn.close()
            return {"success": True, "data": []}, 200

        cursor.execute("SELECT jobid FROM applydb WHERE email = ?", (st.Email,))
        ids = [r[0] for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"success": True, "data": ids}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "message": str(e)}, 500


# ============================================================
# CONNECT PAGE: message an expert
# (the expert LIST reuses GET /api/experts)
# ============================================================
@app.route('/api/connect/send', methods=['POST'])
@requires_login
def connect_send():
    """Emails the message to the chosen expert. The expert's address is
    looked up on the server, so it is never exposed to the browser."""
    data = request.get_json(silent=True) or {}
    expert_id = data.get('expert_id')
    from_email = (data.get('from_email') or session.get('user_email') or '').replace('\r', '').replace('\n', '').strip()
    subject = (data.get('subject') or '').replace('\r', '').replace('\n', ' ').strip()
    message = (data.get('message') or '').strip()

    if not expert_id or not from_email or not subject or not message:
        return {"success": False, "error": "Email, subject and message are required."}, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Name, Email FROM Expertdb WHERE ID = ?", (expert_id,))
        expert = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500

    if not expert or not expert.Email:
        return {"success": False, "error": "Expert not found."}, 404

    body = f"You have a new message on CampusConnect AI from {from_email}.\n\n{message}"
    try:
        _send_mail(expert.Email, subject, body, subtype='plain', reply_to=from_email)
    except Exception as e:
        print("EMAIL ERROR:", e)
        return {"success": False, "error": "Could not send the email."}, 500

    return {"success": True}, 200


# ============================================================
# DEBUG ROUTES (only work while Flask runs with debug=True)
# ============================================================
@app.route('/debug/db-test')
@debug_only
def debug_db_test():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME(), @@SERVERNAME")
        r = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"db_connect": "success", "database": r[0], "server": r[1]}, 200
    except Exception as e:
        return {"db_connect": "failed", "error": str(e)}, 500


@app.route('/debug/who')
@debug_only
def debug_who():
    """/debug/who?email=someone@gmail.com  -> shows which table the email is
    in and what the stored password looks like (first 10 characters only)."""
    email = request.args.get('email', '').strip()
    out = {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DB_NAME(), @@SERVERNAME")
        r = cursor.fetchone()
        out["connected_db"] = r[0]
        out["server"] = r[1]

        for tbl, email_col, pw_col in (
            ("logindb", "email", "password"),
            ("collegedb", "Email", "Password"),
            ("studentdb", "Email", "Password"),
        ):
            try:
                cursor.execute(
                    f"SELECT {pw_col}, LEN({pw_col}) FROM {tbl} WHERE {email_col} = ?", (email,)
                )
                row = cursor.fetchone()
                out[tbl] = (
                    {"found": True, "stored_starts_with": str(row[0])[:10], "length": row[1]}
                    if row else {"found": False}
                )
            except Exception as e:
                out[tbl] = {"error": str(e)}

        cursor.close()
        conn.close()
    except Exception as e:
        out["connection_error"] = str(e)
    return out


if __name__ == '__main__':
    # reloader_type='stat' stops the endless "Detected change in ...unicode_escape.py" restarts
    app.run(debug=True, reloader_type='stat')