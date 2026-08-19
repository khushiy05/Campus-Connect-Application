from flask import Flask, request, render_template, Response, redirect, url_for, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
import smtplib
import json
import os
from email.mime.text import MIMEText
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask_cors import CORS

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
    return render_template('index.html')


@app.route('/about.html')
def about():
    return render_template('about.html')


@app.route('/career.html')
def career():
    return render_template('career.html')


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
    return render_template('registration.html')


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
        if row.role.lower() == "admin":

            session['logged_in'] = True
            session['user_email'] = row.email
            session['role'] = row.role

            return {
                "success": True,
                "role": "admin",
                "redirect": "http://localhost:5173/"
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
    
if __name__ == '__main__':
    app.run(debug=True)