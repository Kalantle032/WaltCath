import streamlit as st
import qrcode
from io import BytesIO

# =====================================================
# ACCESS CONTROL
# =====================================================
if "role" not in st.session_state:
    st.warning("Please login")
    st.switch_page("app.py")

if st.session_state["role"] != "manager":
    st.error("Access denied")
    st.stop()

st.title("QR Code Generator")

qr_text = st.text_input("Enter Linen QR Code")

if st.button("Generate QR"):

    qr = qrcode.make(qr_text)

    buf = BytesIO()
    qr.save(buf)

    st.image(buf.getvalue(), caption="Generated QR Code")