import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import hashlib

st.set_page_config(page_title="Union Routes", layout="wide")
st.title("🚛 Union Routes - HGV Planner")

# Database
def init_db():
    conn = sqlite3.connect("union_routes.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password_hash TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                    account_code TEXT UNIQUE, name TEXT, address TEXT, lat REAL, lng REAL,
                    opening_time TEXT, key_code TEXT, instructions TEXT, hgv_accessible INTEGER)''')
    admin_hash = hashlib.sha256("Alanjohn1".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users VALUES (?,?,?)", ("Alannorton", admin_hash, "admin"))
    conn.commit()
    conn.close()

init_db()

def hash_password(pw): return hashlib.sha256(pw.encode()).hexdigest()

# Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("Login to Union Routes")
    username = st.text_input("Username", "Alannorton")
    password = st.text_input("Password", type="password", value="Alanjohn1")
    if st.button("Login"):
        conn = sqlite3.connect("union_routes.db")
        c = conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        row = c.fetchone()
        if row and row[0] == hash_password(password):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong username or password")
    st.stop()

st.success(f"Logged in as {st.session_state.get('username', 'User')}")

menu = st.sidebar.selectbox("Menu", ["Route Planner", "Add Customer", "View Customers"])

if menu == "Add Customer":
    st.header("➕ Add New Customer")
    with st.form("add"):
        name = st.text_input("Business Name")
        code = st.text_input("Account Code (e.g. NER588)")
        address = st.text_area("Full Address")
        open_time = st.text_input("Opening Time (HH:MM)", "06:00")
        key_code = st.text_input("Key Code / Access")
        instructions = st.text_area("Delivery Instructions")
        hgv = st.checkbox("HGV Accessible", value=True)
        if st.form_submit_button("Save Customer"):
            try:
                geo = RateLimiter(Nominatim(user_agent="unionroutes").geocode, min_delay_seconds=1)(address + ", UK")
                if geo:
                    conn = sqlite3.connect("union_routes.db")
                    conn.execute("INSERT OR REPLACE INTO customers VALUES (?,?,?,?,?,?,?,?,?)",
                        (code, name, address, geo.latitude, geo.longitude, open_time, key_code, instructions, int(hgv)))
                    conn.commit()
                    conn.close()
                    st.success("Customer saved!")
            except:
                st.error("Could not find address. Try again.")

if menu == "View Customers":
    st.header("All Customers")
    conn = sqlite3.connect("union_routes.db")
    df = pd.read_sql_query("SELECT * FROM customers", conn)
    conn.close()
    st.dataframe(df)

if menu == "Route Planner":
    st.header("Plan Route from Lynas Coleraine")
    codes = st.text_input("Account Codes (comma separated)", "NER588,NORTDC")
    if st.button("Calculate Route"):
        # Simple version for now
        st.info("Route planning coming soon with full HGV mapping.")

st.caption("Union Routes - Northern Ireland HGV Tool")
