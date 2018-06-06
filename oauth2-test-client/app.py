import os
import urllib
from uuid import uuid4
from textwrap import dedent

import requests
from flask import Flask, request, abort

USE_FORM_PAYLOADS = False

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


def get_token_response(code: str) -> dict:
    return token_request(data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    })


def get_refreshed_token(refresh_token : str) -> dict:
    return token_request(data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        # Optional reduction of scope
        "scope": "building:read",
    })


def token_request(data: dict) -> dict:
    """Helper function that makes requests to the TOKEN_ENDPOINT"""
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    if USE_FORM_PAYLOADS:
        response = requests.post(
            url=TOKEN_ENDPOINT,
            auth=client_auth,
            data=data,
        )
    else:
        url = f'{TOKEN_ENDPOINT}?{urllib.parse.urlencode(data)}'
        response = requests.post(
            url,
            auth=client_auth,
        )
    return response.json()


def get_protected_data(token: str) -> str:
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
    assert "access_token" in token_response
    assert "expires_in" in token_response
    assert "token_type" in token_response
    assert "refresh_token" in token_response
    protected_data = get_protected_data(
        token_response['access_token'],
    )
    new_token = get_refreshed_token(
        token_response['refresh_token'],
    )['access_token']
    protected_data_with_new_token = get_protected_data(new_token)
    new_token2 = get_refreshed_token(
        token_response['refresh_token'],
    )['access_token']
    protected_data_with_new_token2 = get_protected_data(new_token2)

    return dedent(f"""\
    <p>Authorization response args: {dict(request.args)}</p>

    <p>Token response URL PARAMS: {token_response}</p>

    <p>Protected Data: {protected_data}</p>

    <p>Refreshed Token: {new_token}</p>

    <p>Protected Data using new_token: {protected_data_with_new_token}</p>
    <p>Refreshed Token2: {new_token2}</p>
    <p>Protected Data using new_token2 from the same refresh_token: {protected_data_with_new_token2}</p>
    """)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
