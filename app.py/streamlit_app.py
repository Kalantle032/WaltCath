import streamlit as st
from database.database import supabase

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="Laundry Intelligence Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================
# HIDE STREAMLIT SIDEBAR
# ==========================
hide_streamlit_style = """
<style>
[data-testid="stSidebarNav"] {
    display: none;
}

[data-testid="collapsedControl"] {
    display: none;
}
</style>
"""

st.markdown(
    hide_streamlit_style,
    unsafe_allow_html=True
)

# ==========================
# APP TITLE
# ==========================
st.title("Laundry Intelligence Platform")

st.subheader(
    "Enterprise Operations Intelligence"
)

# ==========================
# LOGIN FORM
# ==========================
email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

# ==========================
# LOGIN
# ==========================
if st.button("Login"):

    try:

        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        user = response.user

        # fetch role
        role_data = supabase.table(
            "user_roles"
        ).select("*")\
        .eq("id", user.id)\
        .execute()

        if not role_data.data:

            st.error(
                "No role assigned"
            )

            st.stop()

        role = role_data.data[0]["role"]

        # save session
        st.session_state["user"] = user.id
        st.session_state["role"] = role

        st.success(
            f"Login successful as {role}"
        )

        # ==========================
        # ROLE ROUTING
        # ==========================
        if role == "manager":

            st.switch_page(
                "pages/1_Executive_Portal.py"
            )

        elif role == "client":

            st.switch_page(
                "pages/2_Client_Portal.py"
            )

        elif role == "workforce":

            st.switch_page(
                "pages/3_Workforce_Console.py"
            )

        else:

            st.error(
                "Invalid role"
            )

    except Exception as e:

        st.error(str(e))