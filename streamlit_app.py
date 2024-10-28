import streamlit as st
import openai
import streamlit_authenticator as stauth
from google.oauth2 import id_token
from google.auth.transport import requests

# Set up OpenAI API Key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Streamlit page configuration
st.set_page_config(page_title="Chatbot", layout="centered")

# Authentication configuration
authenticator = stauth.Authenticate(
    credentials={
        "usernames": {
            "user": {"email": "user@example.com", "name": "User", "password": "your_password"}
        }
    },
    cookie_name="your_cookie_name",
    key="your_cookie_key",
    cookie_expiry_days=30,
)

# Add Google authentication
def login_with_google():
    token = st.text_input("Enter Google ID Token", type="password")
    if token:
        try:
            id_info = id_token.verify_oauth2_token(token, requests.Request(), "YOUR_GOOGLE_CLIENT_ID")
            st.session_state["user"] = id_info["email"]
            st.success("Logged in successfully")
            return True
        except ValueError:
            st.error("Invalid token. Please try again.")
            return False
    return False

# Google login prompt
if "user" not in st.session_state:
    st.title("Login with Google")
    if login_with_google():
        st.experimental_rerun()
else:
    st.title(f"Welcome, {st.session_state['user']}")
    st.write("Chatbot powered by OpenAI")
    user_input = st.text_input("You:", "")

    if st.button("Send"):
        if user_input:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_input}]
            )
            bot_reply = response.choices[0].message["content"]
            st.write(f"Chatbot: {bot_reply}")

    if st.button("Logout"):
        del st.session_state["user"]
        st.experimental_rerun()
