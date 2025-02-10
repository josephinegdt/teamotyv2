import streamlit as st
import sqlite3
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import time

# Database Setup
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# Add user to database
def add_user(username, name, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, name, password) VALUES (?, ?, ?)", (username, name, password))
    conn.commit()
    conn.close()

# Fetch users
def fetch_users():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT username, password FROM users")
    users = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return users

# Store message
def store_message(username, message):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO messages (username, message, timestamp) VALUES (?, ?, ?)", (username, message, timestamp))
    conn.commit()
    conn.close()

# Fetch messages
def fetch_messages():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT username, message, timestamp FROM messages ORDER BY id ASC")
    messages = c.fetchall()
    conn.close()
    return messages

# Initialise database
init_db()

# Authentication setup
users = fetch_users()
config = {
    "credentials": {
        "usernames": {user: {"name": user, "password": passw} for user, passw in users.items()}
    },
    "cookie": {"expiry_days": 30, "key": "random_key", "name": "auth_cookie"},
    "preauthorized": []
}

authenticator = stauth.Authenticate(
    config["credentials"], config["cookie"]["name"], config["cookie"]["key"], config["cookie"]["expiry_days"]
)

# Streamlit UI
st.title("Multi-User Chat App")

# User authentication
name, authentication_status, username = authenticator.login("Login")

if authentication_status:
    st.sidebar.write(f"Welcome, {username}!")
    authenticator.logout("Logout", "sidebar")
    
    # Chat interface
    st.subheader("Chat Room")
    chat_area = st.empty()
    
    # Display messages
    messages = fetch_messages()
    with chat_area.container():
        for msg in messages:
            st.write(f"{msg[2]} - {msg[0]}: {msg[1]}")
    
    # Message input
    message = st.text_input("Type a message:", "")
    if st.button("Send"):
        if message:
            store_message(username, message)
            st.experimental_rerun()

elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")
