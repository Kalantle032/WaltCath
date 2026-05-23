import streamlit as st
import pandas as pd
from database.database import supabase
from datetime import date

# =====================================================
# ACCESS CONTROL
# =====================================================
if "role" not in st.session_state:
    st.warning("Please login")
    st.switch_page("streamlit_app.py")

if st.session_state["role"] != "manager":
    st.error("Access denied")
    st.stop()

st.title("Pickup & Delivery Logistics")

client_name = st.text_input("Client Name")

pickup_location = st.text_input("Pickup Location")

delivery_location = st.text_input("Delivery Location")

pickup_date = st.date_input("Pickup Date", date.today())

driver_name = st.text_input("Driver Name")

status = st.selectbox(
    "Status",
    ["Scheduled", "Picked Up", "In Transit", "Delivered"]
)

if st.button("Save Logistics"):

    supabase.table("pickups").insert({
        "client_name": client_name,
        "pickup_location": pickup_location,
        "delivery_location": delivery_location,
        "pickup_date": str(pickup_date),
        "driver_name": driver_name,
        "status": status
    }).execute()

    st.success("Logistics saved")

# fetch logistics
response = supabase.table("pickups")\
    .select("*")\
    .order("created_at", desc=True)\
    .execute()

df = pd.DataFrame(response.data)

st.subheader("Logistics Dashboard")

st.dataframe(df)

st.metric("Total Deliveries", len(df))