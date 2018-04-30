import os
import urllib
from uuid import uuid4
from textwrap import dedent

import requests
from flask import Flask, request, abort

AUTH_ENDPOINT = os.getenv('AUTH_ENDPOINT')
TOKEN_ENDPOINT = os.getenv('TOKEN_ENDPOINT')
VERIFY_ENDPOINT = os.getenv('VERIFY_ENDPOINT')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SCOPES = os.getenv('SCOPES')
REDIRECT_URI = os.getenv('REDIRECT_URI')
STATE = uuid4().hex

assert all((
    AUTH_ENDPOINT,
    TOKEN_ENDPOINT,
    VERIFY_ENDPOINT,
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    SCOPES,
)), "Please set Environment Variables"

app = Flask(__name__)


@app.route('/')
def homepage():
    return (f'<a href="{make_authorization_url()}">'
            'Authenticate with Auth Server</a>')


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "state": STATE,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    url = f'{AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}'
    return url


def get_token_response(code):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(
        TOKEN_ENDPOINT,
        auth=client_auth,
        json=data,
    )
    return response.json()


def get_refreshed_token(refresh_token):
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        # Optional reduction of scope
        "scope": "building:read",
    }
    response = requests.post(
        TOKEN_ENDPOINT,
        auth=client_auth,
        json=data,
    )
    return response.json()['access_token']


def get_protected_data(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        VERIFY_ENDPOINT,
        headers=headers,
    )
    return response.text


@app.route('/api_callback')
def cloud_api_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not state == STATE:
        abort(403)
    auth_code = request.args.get('code')
    token_response = get_token_response(auth_code)
    protected_data = get_protected_data(
        token_response['access_token'],
    )
    new_token = get_refreshed_token(token_response['refresh_token'])
    protected_data_with_new_token = get_protected_data(new_token)

    return dedent(f"""\
    <p>Authorization response args: {dict(request.args)}</p>

    <p>Token response: {token_response}</p>

    <p>Protected Data: {protected_data}</p>

    <p>Refreshed Token: {new_token}</p>

    <p>Protected Data using new_token: {protected_data_with_new_token}</p>
    """)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
