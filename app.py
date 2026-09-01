from flask import Flask, request, render_template, Response, redirect, url_for, session
from functools import wraps
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


load_dotenv()
app = Flask(__name__)
CORS(app)

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-change-this')

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


def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.environ.get('DB_SERVER')};"
        f"DATABASE={os.environ.get('DB_NAME')};"
        f"UID={os.environ.get('DB_USER')};"
        f"PWD={os.environ.get('DB_PASSWORD')};"
    )
    return conn


def send_confirmation_email(to_email):
    html_body = """
    <html>
    <body style="margin:0; padding:0; background-color:#f4f4f7; font-family: 'Segoe UI', Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f7; padding: 40px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:10px; overflow:hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">

                        <!-- Header -->
                        <tr>
                            <td style="background-color:#2d2d3a; padding: 35px 40px; text-align:center;">
                                <h1 style="margin:0; color:#ffffff; font-size:24px;">
                                    <span style="color:#ff6b35;">CAMPUS</span>CONNECT AI
                                </h1>
                            </td>
                        </tr>

                        <!-- Body -->
                        <tr>
                            <td style="padding: 40px;">
                                <h2 style="color:#2d2d3a; margin-top:0;">Hi there</h2>
                                <p style="color:#555555; font-size:15px; line-height:1.6;">
                                    Thank you for subscribing to <strong>CampusConnect AI</strong>!
                                </p>
                                <p style="color:#555555; font-size:15px; line-height:1.6;">
                                    You're now part of a growing community of students who stay ahead —
                                    with real-time updates on campus events, mess menus, hostel openings,
                                    and placement drives, delivered straight to your inbox.
                                </p>

                                <p style="color:#2d2d3a; font-size:16px; font-weight:600; margin-top:30px;">
                                    What you'll get access to:
                                </p>

                                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:10px;">
                                    <tr>
                                        <td style="padding:8px 0; color:#555555; font-size:14px;">
                                            <span style="color:#ff6b35; font-weight:bold;">&#10003;</span> Mess &amp; Tiffin Finder
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding:8px 0; color:#555555; font-size:14px;">
                                            <span style="color:#ff6b35; font-weight:bold;">&#10003;</span> Hostel Locator
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding:8px 0; color:#555555; font-size:14px;">
                                            <span style="color:#ff6b35; font-weight:bold;">&#10003;</span> Library Locator
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding:8px 0; color:#555555; font-size:14px;">
                                            <span style="color:#ff6b35; font-weight:bold;">&#10003;</span> Verified Student Chat
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding:8px 0; color:#555555; font-size:14px;">
                                            <span style="color:#ff6b35; font-weight:bold;">&#10003;</span> Mentor Connect
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding:8px 0; color:#555555; font-size:14px;">
                                            <span style="color:#ff6b35; font-weight:bold;">&#10003;</span> Live Campus Events &amp; Placement Updates
                                        </td>
                                    </tr>
                                </table>

                                <p style="color:#555555; font-size:15px; line-height:1.6; margin-top:30px;">
                                    We're glad to have you on board. Stay tuned — your first update is on its way!
                                </p>
                            </td>
                        </tr>

                        <!-- Footer -->
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

    msg = MIMEText(html_body, 'html')
    msg['Subject'] = 'Welcome to CampusConnect AI'
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())


def generate_random_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_expert_login_email(to_email, name, password):
    login_url = f"{APP_BASE_URL}/login.html"

    html_body = f"""
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
                                <h2 style="color:#2d2d3a; margin-top:0;">Welcome aboard, {name}!</h2>
                                <p style="color:#555555; font-size:15px; line-height:1.6;">
                                    You've been added as an expert on <strong>CampusConnect AI</strong>.
                                    Your account is ready — here are your login details:
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
                                <p style="color:#555555; font-size:15px; line-height:1.6;">
                                    For your security, we recommend changing this password after your first login.
                                </p>
                                <div style="text-align:center; margin: 30px 0;">
                                    <a href="{login_url}" style="background-color:#fd7e14; color:#ffffff; text-decoration:none; padding: 14px 32px; border-radius:8px; font-weight:600; display:inline-block;">
                                        Log In to Your Account
                                    </a>
                                </div>
                                <p style="color:#999999; font-size:13px; line-height:1.6;">
                                    If the button above doesn't work, copy and paste this link into your browser:<br>
                                    <a href="{login_url}" style="color:#fd7e14;">{login_url}</a>
                                </p>
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

    msg = MIMEText(html_body, 'html')
    msg['Subject'] = 'Your CampusConnect AI Expert Login Details'
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())


def send_invite_email(to_email, subject, message):
    """Plain-text invite/broadcast email used by /api/invite/send."""
    msg = MIMEText(message, 'plain')
    msg['Subject'] = subject or "CampusConnect AI"
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


# ---- Page routes: ab render_template use ho raha hai, templates/ folder se HTML padhega ----
@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    data = request.get_json()
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
        cursor.execute("SELECT ID, Photo, Domain FROM Expertdb ORDER BY ID DESC")
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
    return render_template('rojgarsetu.html')


@app.route('/advertisement.html')
def advertisement():
    return render_template('advertisement.html')


@app.route('/contact.html')
def contact():
    return render_template('contact.html')


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

    session['user_email'] = user_info.get('email')
    session['user_name'] = user_info.get('name')

    print(f"Signed in via Google: {user_info.get('name')} ({user_info.get('email')})")

    return redirect('/registration.html?google_success=1')


@app.route('/registration.html')
def registration():
    prefill_name = session.pop('user_name', '')
    prefill_email = session.pop('user_email', '')
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
    """Emails collected via the 'Invite Us' newsletter box on the homepage
    (stored in invitedb). Used as a source for the Admin > Invite page."""
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
    """Used by the Admin > Invite page: sends the composed subject/message
    to every selected recipient email."""
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
        # Couldn't even connect/login to the SMTP server at all
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


@app.route('/api/register', methods=['POST'])
def register_student():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
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

        cursor.execute("SELECT 1 FROM collegedb WHERE Email = ?", email)
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"success": False, "error": "This email is already registered."}, 409

        # Hash the password before storing — never store plain text
        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO collegedb (Name, Email, MobileNo, City, CollegeName, CollegeCode, Password) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, mobile, city, college_name, college_code, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}, 201
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/login', methods=['POST'])
def login_student():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return {
            "success": False,
            "error": "Email and password are required."
        }, 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check the login credentials in logindb
        cursor.execute(
            """
            SELECT login_id, email, password, role
            FROM logindb
            WHERE email = ?
            """,
            (email,)
        )

        row = cursor.fetchone()

        cursor.close()
        conn.close()

        # Email not found
        if not row:
            return {
                "success": False,
                "error": "Invalid email or password."
            }, 401

        # Check password
        if row.password != password:
            return {
                "success": False,
                "error": "Invalid email or password."
            }, 401

        # Check role
        role = row.role.lower()

        if role == "admin":
            session['logged_in'] = True
            session['user_email'] = row.email
            session['role'] = row.role

            return {
                "success": True,
                "role": "admin",
                "redirect": "http://localhost:5173/"
            }, 200

        if role == "expert":
            session['logged_in'] = True
            session['user_email'] = row.email
            session['role'] = row.role

            return {
                "success": True,
                "role": "expert"
            }, 200

        return {
            "success": False,
            "error": "You are not authorized to access this page."
        }, 403

    except Exception as e:
        print("LOGIN DB ERROR:", e)

        return {
            "success": False,
            "error": "Database connection error."
        }, 500


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


@app.route('/api/enquiries/<int:enquiry_id>', methods=['DELETE'])
def delete_enquiry(enquiry_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Enqdb WHERE ID = ?", (enquiry_id,))
        conn.commit()
        deleted = cursor.rowcount
        cursor.close()
        conn.close()

        if deleted == 0:
            return {"success": False, "error": "Enquiry not found."}, 404

        return {"success": True}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


@app.route('/api/registrations', methods=['GET'])
def get_registrations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ID, Name, Email, MobileNo, City, CollegeName, RegisteredOn, Approved FROM collegedb"
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
                "approved": bool(r[7])
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
        cursor.execute("UPDATE collegedb SET Approved = 1 WHERE ID = ?", (reg_id,))
        conn.commit()
        updated = cursor.rowcount
        cursor.close()
        conn.close()

        if updated == 0:
            return {"success": False, "error": "Registration not found."}, 404

        return {"success": True}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


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
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        for r in rows:
            for k, v in r.items():
                if not isinstance(v, (str, int, float, type(None))):
                    r[k] = str(v)
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

        # Only create login credentials if this email doesn't already have an account
        cursor.execute("SELECT 1 FROM logindb WHERE email = ?", (email,))
        already_has_login = cursor.fetchone() is not None

        if not already_has_login:
            cursor.execute(
                "INSERT INTO logindb (email, password, role) VALUES (?, ?, ?)",
                (email, generated_password, 'expert')
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
            print("EMAIL ERROR:", e)
            # Expert + login were still created; email delivery is best-effort

    return {"success": True}, 201


@app.route('/expert/<int:expert_id>')
def expert_detail(expert_id):
    if not session.get('user_email'):
        return redirect(url_for('login') + f'?next=/expert/{expert_id}')

    expert = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Expertdb WHERE ID = ?", expert_id)
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Expertdb WHERE ID = ?", (expert_id,))
        conn.commit()
        deleted = cursor.rowcount
        cursor.close()
        conn.close()

        if deleted == 0:
            return {"success": False, "error": "Expert not found."}, 404

        return {"success": True}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


# ---- Advertisement routes ----
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
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        for r in rows:
            for k, v in r.items():
                if not isinstance(v, (str, int, float, type(None))):
                    r[k] = str(v)
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
    registration_date = request.form.get('registration_date')  # yyyy-mm-dd from <input type="date">

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

        # ExpiryDate is a computed column in SQL Server — do NOT insert it here
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Advertisement WHERE AdvertisementId = ?", (adv_id,))
        conn.commit()
        deleted = cursor.rowcount
        cursor.close()
        conn.close()

        if deleted == 0:
            return {"success": False, "error": "Advertisement not found."}, 404

        return {"success": True}, 200
    except Exception as e:
        print("DB ERROR:", e)
        return {"success": False, "error": str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)