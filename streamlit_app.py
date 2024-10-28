import streamlit as st
from oauthlib.oauth2 import WebApplicationClient
import requests
import os
import json

# Configuration
GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Function to get provider configuration
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

# Streamlit app
st.title("Google Login Example")

# Login button
if "user_info" not in st.session_state:
    if st.button("Login with Google"):
        # Get authorization endpoint from Google
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Create the authorization URL
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri="http://localhost:8501",
            scope=["openid", "email", "profile"],
        )
        st.write("Please go to this URL and authorize:", request_uri)
else:
    st.write(f"Hello, {st.session_state['user_info']['email']}")

# Exchange authorization code for token
if "code" in st.experimental_get_query_params():
    code = st.experimental_get_query_params()["code"][0]

    # Get token endpoint
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare token request
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=st.experimental_get_query_params()["code"],
        redirect_url="http://localhost:8501",
        code=code,
    )

    # Send the token request
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the token response
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Get user info endpoint
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # Store user info in session
    st.session_state["user_info"] = userinfo_response.json()
    st.experimental_rerun()
