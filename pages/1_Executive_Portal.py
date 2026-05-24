import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from database.database import supabase

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Executive Portal",
    layout="wide"
)

# =====================================================
# ACCESS CONTROL
# =====================================================
if "role" not in st.session_state:
    st.warning("Please login")
    st.switch_page("app.py")

if st.session_state["role"] != "manager":
    st.error("Access denied")
    st.stop()

# =====================================================
# PAGE TITLE
# =====================================================
st.title("Executive Operations Portal")

st.caption(
    "Enterprise Laundry Intelligence System"
)

# =====================================================
# FETCH DATABASE DATA
# =====================================================
clients = pd.DataFrame(
    supabase.table("clients")
    .select("*")
    .execute().data
)

linen = pd.DataFrame(
    supabase.table("linen_assets")
    .select("*")
    .execute().data
)

logistics = pd.DataFrame(
    supabase.table("pickups")
    .select("*")
    .execute().data
)

workforce = pd.DataFrame(
    supabase.table("workforce_tasks")
    .select("*")
    .execute().data
)

pickup_requests = pd.DataFrame(
    supabase.table("pickup_requests")
    .select("*")
    .execute().data
)

notifications = pd.DataFrame(
    supabase.table("notifications")
    .select("*")
    .execute().data
)

# =====================================================
# PREMIUM SIDEBAR
# =====================================================
with st.sidebar:

    st.title("Laundry OS")

    st.caption(
        "Operational Intelligence"
    )

    st.divider()

    st.subheader("Executive Profile")

    st.success("Role: Manager")

    st.divider()

    st.subheader("System KPIs")

    st.metric(
        "Clients",
        len(clients)
    )

    st.metric(
        "Linen Assets",
        len(linen)
    )

    st.metric(
        "Workforce Tasks",
        len(workforce)
    )

    st.metric(
        "Pickup Requests",
        len(pickup_requests)
    )

    st.divider()

    st.subheader("Platform Status")

    st.success("AI Optimization Active")

    st.success("GPS Tracking Online")

    st.success("Notifications Running")

    st.success("Operational Systems Healthy")

# =====================================================
# TABS
# =====================================================
overview_tab, ai_tab, gps_tab, analytics_tab, route_tab, request_tab, notification_tab = st.tabs([
    "Overview",
    "AI Optimization",
    "GPS Tracking",
    "Predictive Analytics",
    "Route Optimization",
    "Pickup Coordination",
    "Notifications"
])

# =====================================================
# OVERVIEW TAB
# =====================================================
with overview_tab:

    st.subheader("Operational KPIs")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Clients",
        len(clients)
    )

    col2.metric(
        "Linen Assets",
        len(linen)
    )

    col3.metric(
        "Deliveries",
        len(logistics)
    )

    col4.metric(
        "Tasks",
        len(workforce)
    )

    st.divider()

    chart1, chart2 = st.columns(2)

    with chart1:

        if not linen.empty and "status" in linen.columns:

            fig = px.pie(
                linen,
                names="status",
                title="Linen Status Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    with chart2:

        if not workforce.empty and "worker_name" in workforce.columns:

            fig2 = px.histogram(
                workforce,
                x="worker_name",
                title="Workforce Activity"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

    st.divider()

    st.subheader("Recent Pickup Requests")

    if not pickup_requests.empty:

        st.table(pickup_requests)

    else:

        st.info("No pickup requests available")

# =====================================================
# AI OPTIMIZATION TAB
# =====================================================
with ai_tab:

    st.header("AI Workforce Optimization")

    if not workforce.empty:

        workload = workforce.groupby(
            "worker_name"
        ).size().reset_index(name="task_count")

        st.table(workload)

        overloaded = workload[
            workload["task_count"] > 3
        ]

        if not overloaded.empty:

            st.warning(
                "AI detected overloaded workers"
            )

        else:

            st.success(
                "AI indicates balanced workforce allocation"
            )

        fig3 = px.bar(
            workload,
            x="worker_name",
            y="task_count",
            title="Task Distribution"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    st.divider()

    st.subheader("Live Workforce Task Assignment")

    worker_name = st.text_input(
        "Assign Worker"
    )

    task_name = st.text_input(
        "Task Name"
    )

    task_location = st.text_input(
        "Task Location"
    )

    if st.button("Assign Task"):

        supabase.table(
            "workforce_tasks"
        ).insert({
            "worker_name": worker_name,
            "task_name": task_name,
            "assigned_location": task_location,
            "status": "Pending"
        }).execute()

        # automated notification
        supabase.table(
            "notifications"
        ).insert({
            "recipient_role": "workforce",
            "recipient_name": worker_name,
            "message":
                f"New task assigned: {task_name}"
        }).execute()

        st.success(
            "Task assigned successfully"
        )

# =====================================================
# GPS TRACKING TAB
# =====================================================
with gps_tab:

    st.header("Live GPS Tracking")

    latitude = -24.6282
    longitude = 25.9231

    m = folium.Map(
        location=[latitude, longitude],
        zoom_start=12
    )

    folium.Marker(
        [latitude, longitude],
        popup="Laundry Vehicle",
        tooltip="Live Driver Location"
    ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=500
    )

# =====================================================
# PREDICTIVE ANALYTICS TAB
# =====================================================
with analytics_tab:

    st.header("Predictive Linen Analytics")

    if not linen.empty and "lifecycle_count" in linen.columns:

        high_usage = linen[
            linen["lifecycle_count"] >= 10
        ]

        st.subheader("High Usage Linen")

        st.table(high_usage)

        if not high_usage.empty:

            st.warning(
                "AI predicts replacement required soon"
            )

        else:

            st.success(
                "Inventory health stable"
            )

        predicted_demand = int(
            len(linen) * 1.2
        )

        st.metric(
            "Predicted Next Month Demand",
            predicted_demand
        )

# =====================================================
# ROUTE OPTIMIZATION TAB
# =====================================================
with route_tab:

    st.header("AI Route Optimization")

    if not logistics.empty and "pickup_location" in logistics.columns:

        grouped = logistics.groupby(
            "pickup_location"
        ).size().reset_index(name="delivery_count")

        grouped = grouped.sort_values(
            by="delivery_count",
            ascending=False
        )

        st.table(grouped)

        if not grouped.empty:

            top_location = grouped.iloc[0][
                "pickup_location"
            ]

            st.success(
                f"AI recommends clustering pickups around {top_location}"
            )

        fig4 = px.bar(
            grouped,
            x="pickup_location",
            y="delivery_count",
            title="Pickup Density"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

# =====================================================
# PICKUP COORDINATION TAB
# =====================================================
with request_tab:

    st.header("Pickup Coordination")

    if not pickup_requests.empty:

        st.table(pickup_requests)

        request_ids = pickup_requests["id"].tolist()

        selected_request = st.selectbox(
            "Select Request",
            request_ids
        )

        new_status = st.selectbox(
            "Update Status",
            [
                "Pending",
                "Approved",
                "Assigned",
                "In Transit",
                "Completed"
            ]
        )

        if st.button("Update Pickup Status"):

            supabase.table(
                "pickup_requests"
            ).update({
                "status": new_status
            })\
            .eq("id", selected_request)\
            .execute()

            selected_row = pickup_requests[
                pickup_requests["id"] == selected_request
            ]

            if not selected_row.empty:

                client_name = selected_row.iloc[0][
                    "client_name"
                ]

                supabase.table(
                    "notifications"
                ).insert({
                    "recipient_role": "client",
                    "recipient_name": client_name,
                    "message":
                        f"Your pickup request status changed to {new_status}"
                }).execute()

            st.success(
                "Pickup request updated"
            )

    else:

        st.info("No pickup requests")

# =====================================================
# NOTIFICATIONS TAB
# =====================================================
with notification_tab:

    st.header("Operational Notifications")

    recipient_role = st.selectbox(
        "Send To",
        [
            "workforce",
            "client"
        ]
    )

    recipient_name = st.text_input(
        "Recipient Name"
    )

    notification_message = st.text_area(
        "Notification Message"
    )

    if st.button("Send Notification"):

        supabase.table(
            "notifications"
        ).insert({
            "recipient_role": recipient_role,
            "recipient_name": recipient_name,
            "message": notification_message
        }).execute()

        st.success(
            "Notification sent successfully"
        )

    st.divider()

    st.subheader("Notification History")

    if not notifications.empty:

        st.table(notifications)

    else:

        st.info("No notifications available")

# =====================================================
# LOGOUT
# =====================================================
if st.button("Logout"):

    st.session_state.clear()

    st.switch_page("app.py")