# coding=utf-8

# https://googleapis.com/auth/spreadsheets
# https://googleapis.com/auth/drive
import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow

# Use the client_secret.json file to identify the application requesting auth.
# The client ID (from same file), as well as access scope is required.
state = flask.session['state']
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secret.json', scopes=['https://googleapis.com/auth/spreadsheets'], state=state)

flow.redirect_uri = flask.url_for('oath2_callback', _external=True)

authorization_response = flask.request.url
flow.fetch_token(authorization_response=authorization_response)

# Store the credentials in the session.
# ACTION ITEM for developers:
#     Store user's access and refresh tokens in your data store if
#     incorporating this code into your real app.

credentials = flow.credentials
flask.session['credentials'] = {
    'token': credentials.token,
    'refresh_token': credentials.refresh_token,
    'token_uri': credentials.token_uri,
    'client_id': credentials.client_id,
    'client_secret': credentials.client_secret,
    'scopes': credentials.scopes
}

# generate URL for request to Google's oAuth 2.0 server.
# Use kwargs to set optional request params
authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')


# return flask.redirect(authorization_url)