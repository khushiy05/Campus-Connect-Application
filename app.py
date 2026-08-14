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


if __name__ == '__main__':
    app.run(debug=True)