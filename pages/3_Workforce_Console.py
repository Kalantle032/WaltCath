import streamlit as st
import pandas as pd
import plotly.express as px
import cv2
import numpy as np
from PIL import Image
from database.database import supabase

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Workforce Console",
    layout="wide"
)

# =====================================================
# ACCESS CONTROL
# =====================================================
if "role" not in st.session_state:
    st.warning("Please login")
    st.switch_page("streamlit_app.py")

if st.session_state["role"] != "workforce":
    st.error("Access denied")
    st.stop()

# =====================================================
# PAGE TITLE
# =====================================================
st.title("Workforce Operations Console")

st.caption(
    "Live Laundry Execution & QR Operations"
)

# =====================================================
# WORKER PROFILE
# =====================================================
worker_name = st.text_input(
    "Worker Name"
)

assigned_location = st.text_input(
    "Assigned Location"
)

# =====================================================
# FETCH DATABASE DATA
# =====================================================
tasks_df = pd.DataFrame(
    supabase.table("workforce_tasks")
    .select("*")
    .eq("worker_name", worker_name)
    .execute().data
)

movement_df = pd.DataFrame(
    supabase.table("linen_movements")
    .select("*")
    .eq("scanned_by", worker_name)
    .execute().data
)

notifications_df = pd.DataFrame(
    supabase.table("notifications")
    .select("*")
    .eq("recipient_role", "workforce")
    .eq("recipient_name", worker_name)
    .execute().data
)

# =====================================================
# PREMIUM SIDEBAR
# =====================================================
with st.sidebar:

    st.title("Workforce Console")

    st.caption(
        "Operational Execution Center"
    )

    st.divider()

    st.subheader("Worker Profile")

    if worker_name:
        st.success(worker_name)
    else:
        st.info("Enter worker name")

    st.divider()

    st.subheader("Operational KPIs")

    st.metric(
        "Assigned Tasks",
        len(tasks_df)
    )

    completed_tasks = 0

    if not tasks_df.empty and "status" in tasks_df.columns:

        completed_tasks = len(
            tasks_df[
                tasks_df["status"] == "Completed"
            ]
        )

    st.metric(
        "Completed Tasks",
        completed_tasks
    )

    st.metric(
        "QR Scans",
        len(movement_df)
    )

    st.divider()

    st.subheader("System Status")

    st.success(
        "QR Scanner Active"
    )

    st.success(
        "Notifications Online"
    )

    st.success(
        "Task System Connected"
    )

    st.divider()

    if completed_tasks > 5:

        st.success(
            "High Productivity"
        )

    else:

        st.info(
            "Normal Operations"
        )

# =====================================================
# ENTERPRISE TABS
# =====================================================
overview_tab, tasks_tab, qr_tab, notifications_tab = st.tabs([
    "Overview",
    "Tasks",
    "QR Operations",
    "Notifications"
])

# =====================================================
# OVERVIEW TAB
# =====================================================
with overview_tab:

    st.subheader(
        "Operational Overview"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Assigned Tasks",
        len(tasks_df)
    )

    col2.metric(
        "Completed Tasks",
        completed_tasks
    )

    col3.metric(
        "QR Scans",
        len(movement_df)
    )

    st.divider()

    if not tasks_df.empty and "status" in tasks_df.columns:

        fig = px.pie(
            tasks_df,
            names="status",
            title="Task Status Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    st.subheader(
        "Recent QR Activity"
    )

    if not movement_df.empty:

        st.table(movement_df)

    else:

        st.info(
            "No QR activity"
        )

# =====================================================
# TASKS TAB
# =====================================================
with tasks_tab:

    st.subheader(
        "Assigned Tasks"
    )

    if not tasks_df.empty:

        st.table(tasks_df)

        task_ids = tasks_df["id"].tolist()

        selected_task = st.selectbox(
            "Select Task",
            task_ids
        )

        task_status = st.selectbox(
            "Update Task Status",
            [
                "Pending",
                "In Progress",
                "Completed"
            ]
        )

        if st.button("Update Task"):

            supabase.table(
                "workforce_tasks"
            ).update({
                "status": task_status
            })\
            .eq("id", selected_task)\
            .execute()

            st.success(
                "Task updated successfully"
            )

    else:

        st.warning(
            "No tasks assigned"
        )

# =====================================================
# QR OPERATIONS TAB
# =====================================================
with qr_tab:

    st.subheader(
        "Live QR Scanner"
    )

    camera_image = st.camera_input(
        "Scan Linen QR Code"
    )

    if camera_image:

        image = Image.open(camera_image)

        image_np = np.array(image)

        detector = cv2.QRCodeDetector()

        data, bbox, _ = detector.detectAndDecode(
            image_np
        )

        if data:

            st.success(
                f"QR Detected: {data}"
            )

            linen_response = supabase.table(
                "linen_assets"
            ).select("*")\
            .eq("qr_code", data)\
            .execute()

            linen_df = pd.DataFrame(
                linen_response.data
            )

            if not linen_df.empty:

                st.subheader(
                    "Linen Asset"
                )

                st.table(linen_df)

                movement_map = {
                    "Picked Up": "In Transit",
                    "In Laundry": "Processing",
                    "Washing": "Washing",
                    "Drying": "Drying",
                    "Folding": "Folding",
                    "Ready": "Ready",
                    "Delivered": "Delivered"
                }

                movement_type = st.selectbox(
                    "Processing Action",
                    list(movement_map.keys())
                )

                if st.button(
                    "Process QR Scan"
                ):

                    # update linen status
                    supabase.table(
                        "linen_assets"
                    ).update({
                        "status":
                            movement_map[
                                movement_type
                            ]
                    })\
                    .eq("qr_code", data)\
                    .execute()

                    # lifecycle tracking
                    if "lifecycle_count" in linen_df.columns:

                        current_count = linen_df.iloc[0][
                            "lifecycle_count"
                        ]

                        if current_count is None:
                            current_count = 0

                        new_count = current_count + 1

                        supabase.table(
                            "linen_assets"
                        ).update({
                            "lifecycle_count":
                                new_count
                        })\
                        .eq("qr_code", data)\
                        .execute()

                    # movement log
                    supabase.table(
                        "linen_movements"
                    ).insert({
                        "qr_code": data,
                        "movement_type": movement_type,
                        "location": assigned_location,
                        "scanned_by": worker_name
                    }).execute()

                    # automated client notification
                    if "client_name" in linen_df.columns:

                        client_name = linen_df.iloc[0][
                            "client_name"
                        ]

                        supabase.table(
                            "notifications"
                        ).insert({
                            "recipient_role":
                                "client",
                            "recipient_name":
                                client_name,
                            "message":
                                f"Linen QR {data} updated to {movement_map[movement_type]}"
                        }).execute()

                    st.success(
                        f"Linen updated successfully → {movement_map[movement_type]}"
                    )

            else:

                st.error(
                    "QR code not linked to linen asset"
                )

        else:

            st.error(
                "No QR code detected"
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