import streamlit as st
import pandas as pd
import plotly.express as px
from database.database import supabase

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Client Portal",
    layout="wide"
)

# =====================================================
# ACCESS CONTROL
# =====================================================
if "role" not in st.session_state:
    st.warning("Please login")
    st.switch_page("streamlit_app.py")

if st.session_state["role"] != "client":
    st.error("Access denied")
    st.stop()

# =====================================================
# PAGE TITLE
# =====================================================
st.title("Client Operations Portal")

st.caption(
    "Laundry Coordination & Visibility Platform"
)

# =====================================================
# FETCH AUTH USER
# =====================================================
auth_user = supabase.auth.get_user()

client_email = auth_user.user.email

# =====================================================
# FETCH CLIENT PROFILE
# =====================================================
client_response = supabase.table(
    "clients"
).select("*")\
.eq("email", client_email)\
.execute()

client_df = pd.DataFrame(
    client_response.data
)

if client_df.empty:

    st.error(
        "No client profile found"
    )

    st.stop()

client_name = client_df.iloc[0][
    "company_name"
]

# =====================================================
# FETCH CLIENT DATA
# =====================================================
linen_df = pd.DataFrame(
    supabase.table("linen_assets")
    .select("*")
    .eq("client_name", client_name)
    .execute().data
)

logistics_df = pd.DataFrame(
    supabase.table("pickups")
    .select("*")
    .eq("client_name", client_name)
    .execute().data
)

pickup_df = pd.DataFrame(
    supabase.table("pickup_requests")
    .select("*")
    .eq("client_name", client_name)
    .execute().data
)

notifications_df = pd.DataFrame(
    supabase.table("notifications")
    .select("*")
    .eq("recipient_role", "client")
    .eq("recipient_name", client_name)
    .execute().data
)

# =====================================================
# PREMIUM SIDEBAR
# =====================================================
with st.sidebar:

    st.title("Client Portal")

    st.caption(
        "Operational Visibility"
    )

    st.divider()

    st.subheader("Client Profile")

    st.success(client_name)

    st.divider()

    st.subheader("Operational KPIs")

    st.metric(
        "Linen Assets",
        len(linen_df)
    )

    st.metric(
        "Deliveries",
        len(logistics_df)
    )

    st.metric(
        "Pickup Requests",
        len(pickup_df)
    )

    ready_count = 0

    if not linen_df.empty and "status" in linen_df.columns:

        ready_count = len(
            linen_df[
                linen_df["status"] == "Ready"
            ]
        )

    st.metric(
        "Ready Linen",
        ready_count
    )

    st.divider()

    st.subheader(
        "Estimated Turnaround"
    )

    if not linen_df.empty and "status" in linen_df.columns:

        latest_status = linen_df.iloc[0]["status"]

        turnaround_map = {
            "In Transit": "8 Hours",
            "Processing": "6 Hours",
            "Washing": "4 Hours",
            "Drying": "2 Hours",
            "Folding": "1 Hour",
            "Ready": "Ready For Delivery",
            "Delivered": "Completed"
        }

        estimate = turnaround_map.get(
            latest_status,
            "Awaiting Processing"
        )

        st.info(estimate)

    st.divider()

    st.subheader("Platform Status")

    st.success(
        "Tracking Enabled"
    )

    st.success(
        "Notifications Active"
    )

    st.success(
        "Operations Connected"
    )

# =====================================================
# ENTERPRISE TABS
# =====================================================
overview_tab, logistics_tab, pickup_tab, notifications_tab = st.tabs([
    "Overview",
    "Logistics",
    "Pickup Requests",
    "Notifications"
])

# =====================================================
# OVERVIEW TAB
# =====================================================
with overview_tab:

    st.subheader(
        "Operational Overview"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Linen Assets",
        len(linen_df)
    )

    col2.metric(
        "Deliveries",
        len(logistics_df)
    )

    col3.metric(
        "Pickup Requests",
        len(pickup_df)
    )

    col4.metric(
        "Notifications",
        len(notifications_df)
    )

    st.divider()

    st.subheader(
        "Estimated Turnaround Time"
    )

    if not linen_df.empty and "status" in linen_df.columns:

        latest_status = linen_df.iloc[0]["status"]

        turnaround_map = {
            "In Transit": "Estimated Completion: 8 Hours",
            "Processing": "Estimated Completion: 6 Hours",
            "Washing": "Estimated Completion: 4 Hours",
            "Drying": "Estimated Completion: 2 Hours",
            "Folding": "Estimated Completion: 1 Hour",
            "Ready": "Ready For Delivery",
            "Delivered": "Completed"
        }

        estimated = turnaround_map.get(
            latest_status,
            "Awaiting Processing"
        )

        st.success(estimated)

    else:

        st.info(
            "No active processing"
        )

    st.divider()

    if not linen_df.empty and "status" in linen_df.columns:

        fig = px.pie(
            linen_df,
            names="status",
            title="Linen Status Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    st.subheader(
        "Recent Linen Assets"
    )

    if not linen_df.empty:

        st.table(linen_df)

    else:

        st.warning(
            "No linen assets found"
        )

# =====================================================
# LOGISTICS TAB
# =====================================================
with logistics_tab:

    st.subheader(
        "Delivery Coordination"
    )

    if not logistics_df.empty:

        st.table(logistics_df)

        if "pickup_location" in logistics_df.columns:

            fig2 = px.histogram(
                logistics_df,
                x="pickup_location",
                title="Pickup Activity"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

    else:

        st.info(
            "No logistics activity"
        )

# =====================================================
# PICKUP REQUEST TAB
# =====================================================
with pickup_tab:

    st.subheader(
        "Schedule Pickup"
    )

    pickup_location = st.text_input(
        "Pickup Location"
    )

    pickup_date = st.date_input(
        "Pickup Date"
    )

    linen_quantity = st.number_input(
        "Estimated Linen Quantity",
        min_value=1,
        step=1
    )

    urgency = st.selectbox(
        "Urgency",
        [
            "Normal",
            "Urgent",
            "Critical"
        ]
    )

    if st.button("Request Pickup"):

        supabase.table(
            "pickup_requests"
        ).insert({
            "client_name": client_name,
            "pickup_location": pickup_location,
            "pickup_date": str(pickup_date),
            "linen_quantity": linen_quantity,
            "urgency": urgency,
            "status": "Pending"
        }).execute()

        st.success(
            "Pickup request submitted"
        )

    st.divider()

    st.subheader(
        "Pickup Request History"
    )

    if not pickup_df.empty:

        st.table(pickup_df)

    else:

        st.info(
            "No pickup requests"
        )

# =====================================================
# NOTIFICATIONS TAB
# =====================================================
with notifications_tab:

    st.subheader(
        "Operational Notifications"
    )

    if not notifications_df.empty:

        st.table(notifications_df)

    else:

        st.info(
            "No notifications available"
        )

# =====================================================
# LOGOUT
# =====================================================
if st.button("Logout"):

    st.session_state.clear()

    st.switch_page("streamlit_app.py")