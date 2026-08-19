import os
from flask import Flask, redirect, url_for, session, send_from_directory
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

# static_folder='.' serves your existing site as-is - no files need to move
app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-change-this')

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

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

    # For now, just prove it worked by printing to console.
    print(f"Signed in via Google: {user_info.get('name')} ({user_info.get('email')})")

    return redirect('/registration.html?google_success=1')


if __name__ == '__main__':
    app.run(debug=True, port=5000)