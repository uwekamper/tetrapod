import cgi
import json
import click
import os
import datetime
from urllib.parse import parse_qs
from oauthlib.oauth2 import MobileApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

AUTHORIZATION_BASE_URL = 'https://podio.com/oauth/authorize'
TOKEN_URL = 'https://podio.com/oauth/access_token'
REFRESH_URL = 'https://podio.com/oauth/authorize'
KEEP_RUNNING = True

credentials = None


def keep_running():
    return KEEP_RUNNING


class CouldNotAcquireToken(Exception):
    """ Common base class for all non-exit exceptions. """
    pass


class OAuth2CallbackHandler(BaseHTTPRequestHandler):
    # These two static members will be overwritten by a (dynamically generated) subclass
    # of OAuth2CallbackHandler.

    def do_GET(self):
        """Respond to a GET request that contains the 'code'."""
        if self.path == '/':
            self.send_response(200)
            self.send_header(b"Content-type", b"text/html")
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), 'authpage.html'), mode='r') as fh:
                page = fh.readlines()
                for line in page:
                    self.wfile.write(line.encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header(b"Content-type", b"application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')

    def do_POST(self):
        """Handle POST requests that contain the fragment code we get from Podio."""
        # http://stackoverflow.com/questions/4233218/python-basehttprequesthandler-post-variables
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)

        # Respond
        self.send_response(200)
        self.send_header(b"Content-type", b"text/html")
        self.end_headers()
        self.wfile.write(b'Done!')

        # Store the credentials outside of this object so the main thread can access it.
        global credentials
        credentials = parse_qs(post_body.decode('utf-8'))

        # Stop the server
        global KEEP_RUNNING
        KEEP_RUNNING = False


def MakeHandlerClass(client_id, client_secret=None):
    """
    Factory method that will create a subclass of OAuth2CallbackHandler that additionally contains
    client_id and client_secret.
    :param client_id: The Podio client ID
    :param client_secret: the Podio client secret
    :return: A HTTPRequestHandler subclass that can be used with http.server().
    """
    class CustomHandler(OAuth2CallbackHandler):
        def __init__(self, *args, **kwargs):
            self.client_id = client_id
            super(CustomHandler, self).__init__(*args, **kwargs)
    return CustomHandler


def authorize(client_id, client_secret=None):
    """
    :param client_id:
    :param client_secret:
    :return:
    """
    # The HTTP request handler stores the credentials in a module-global
    # variable, make sure it is clean.
    global credentials
    credentials = None

    # Create a temporary class that extends the handler class above. This will add the
    # client-ID and client secret as static members to OAuth2CallbackHandler.
    server = HTTPServer(('localhost', 0), MakeHandlerClass(client_id, client_secret))

    port = server.socket.getsockname()[1]
    client = MobileApplicationClient(client_id=client_id)# client_secret=client_secret)
    podio = OAuth2Session(client=client, scope=['global:all'],
                          redirect_uri='http://localhost:%d/' % port)
    # Try the client-side flow
    authorization_url, state = podio.authorization_url(AUTHORIZATION_BASE_URL)

    click.echo('Opening authorization flow in the ')
    click.launch(authorization_url)
    try:
        # Getting a valid POST request from the logged in user will set KEEP_RUNNING to False
        # which will stop this while-loop.
        while keep_running():
            server.handle_request()
    except KeyboardInterrupt:
        server.server_close()
        raise CouldNotAcquireToken()
    server.server_close()
    # Check the credentials
    if credentials is None:
        raise CouldNotAcquireToken()
    # Transform the credentials a little bit.
    token = {
        'client_id': client_id,
        'access_token': credentials['access_token'][0],
        'refresh_token': credentials['refresh_token'][0],
        'token_type': credentials['token_type'][0],
        'expires_in': credentials['expires_in'][0],
    }
    return token


def make_client(client_id, token, check=True):
    expires_at = datetime.datetime.utcfromtimestamp(token['expires_at'])

    token['expires_in'] = (expires_at - datetime.datetime.utcnow()).total_seconds()
    #client = OAuth2Session(client_id, token=token)
    extra = {
        'client_id': client_id,
        'client_token': 'MAqHHrNIkbJdZ1xIL4xMR0TXuUqXgXW6ayQENhXT0kIcwFEi9wybBGWgd5d1ezV3'
    }
    client = OAuth2Session(client_id, token=token, auto_refresh_url=REFRESH_URL,
                           auto_refresh_kwargs=extra, token_updater=save_token)
    if check is True:
        r = client.get('https://api.podio.com/user/profile/')
        r.raise_for_status()
        #if r.status_code != 200:
        #    refresh_token = token['refresh_token']
        #    new_token = client.refresh_token(REFRESH_URL, refresh_token=refresh_token, client_id=client_id)
        #    save_token(new_token)
        #    client = OAuth2Session(client_id, token=new_token)
        #    r = client.get('https://api.podio.com/user/profile/')
        print('Logged in as "{}"'.format(r.json()['name']))
    return client


def save_token(token):
    with open('.tetrapod_credentials.json', mode='w') as fh:
        expires_at = datetime.datetime.utcnow() \
                     + datetime.timedelta(seconds=int(token.get('expires_in', 0)))
        token['expires_at'] = int(expires_at.strftime("%s"))
        json.dump(token, fh, indent=2, sort_keys=True)


def load_token():
    with open('.tetrapod_credentials.json', mode='r') as fh:
        token = json.load(fh)
        return token
