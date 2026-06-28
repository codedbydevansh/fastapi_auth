import streamlit as st
import requests
import time

# --- Configuration ---
#BASE_URL = "http://127.0.0.1:8000"

BASE_URL = "https://fastapi-auth-y1nr.onrender.com"

st.set_page_config(
    page_title="TaskMaster Pro | Productivity Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Modern UI Styling (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #f8fafc; }

    /* Custom Task Card */
    .task-card {
        background: white;
        padding: 24px;
        border-radius: 20px;
        margin-bottom: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-left: 8px solid #3b82f6;
        transition: all 0.3s ease;
    }
    .task-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    .task-completed {
        border-left: 8px solid #94a3b8;
        background-color: #f1f5f9;
        opacity: 0.8;
    }
    .task-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
    }
    .task-done-text {
        text-decoration: line-through;
        color: #64748b;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #3b82f6 , #2563eb);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Session State Initialization ---
if "token" not in st.session_state: st.session_state.token = None
if "user_email" not in st.session_state: st.session_state.user_email = None
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "reg_email" not in st.session_state: st.session_state.reg_email = ""

# --- API Helper Functions ---

def api_request_otp(email):
    try:
        res = requests.post(f"{BASE_URL}/request-otp", json={"email": email})
        if res.status_code == 200:
            return True, "Success"
        else:
            # Get the error message from the backend
            error_detail = res.json().get('detail', 'Unknown Error')
            return False, error_detail
    except Exception as e:
        return False, str(e)


def api_register(username, email, password, otp):
    try:
        payload = {"username": username, "email": email, "password": password, "otp_code": otp}
        res = requests.post(f"{BASE_URL}/register", json=payload)
        return res.status_code == 200
    except: return False

def api_login(email, password):
    try:
        res = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.session_state.user_email = email
            return True
        return False
    except: return False

def api_get_todos():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    res = requests.get(f"{BASE_URL}/todos", headers=headers)
    return res.json() if res.status_code == 200 else []

def api_add_todo(title):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    requests.post(f"{BASE_URL}/todos", json={"title": title}, headers=headers)

def api_toggle_todo(todo_id):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    requests.put(f"{BASE_URL}/todos/{todo_id}", headers=headers)

def api_delete_todo(todo_id):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    requests.delete(f"{BASE_URL}/todos/{todo_id}", headers=headers)

# --- UI Logic ---

# Sidebar Navigation
with st.sidebar:
    st.markdown("## 🚀 TaskMaster Pro")
    if st.session_state.token:
        st.markdown(f"**Welcome back,**\n{st.session_state.user_email}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.rerun()
        menu = ["Dashboard"]
    else:
        menu = ["Login", "Register"]
    
    choice = st.radio("Navigation", menu)

# --- Register Page ---
if choice == "Register":
    st.title("✨ Join TaskMaster Pro")
    st.write("Secure your account with Gmail verification.")

    if not st.session_state.otp_sent:
        with st.container():
            email_input = st.text_input("Enter your Gmail Address", placeholder="name@gmail.com")
            if st.button("Send Verification Code", type="primary"):
                success, message = api_request_otp(email_input) # Updated
                if success:
                    st.session_state.otp_sent = True
                    st.session_state.reg_email = email_input
                    st.success("Verification code sent to your Gmail!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Error: {message}")
    else:
        st.info(f"📧 Verification code sent to: **{st.session_state.reg_email}**")
        with st.form("reg_form"):
            otp = st.text_input("Enter 6-Digit Code")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Complete Registration", use_container_width=True):
                if api_register(username, st.session_state.reg_email, password, otp):
                    st.success("Account Created! You can now Login.")
                    st.session_state.otp_sent = False
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Invalid Code or details. Please try again.")
        if st.button("Wrong email? Edit"):
            st.session_state.otp_sent = False
            st.rerun()

# --- Login Page ---
elif choice == "Login":
    st.title("🔐 Welcome Back")
    with st.container():
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Login", type="primary", use_container_width=True):
            if api_login(email, pwd):
                st.success("Access Granted!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid credentials.")

# --- Main Dashboard ---
elif choice == "Dashboard":
    # Header & Progress
    col_title, col_prog = st.columns([2, 1])
    todos = api_get_todos()
    total = len(todos)
    done = len([t for t in todos if t['is_completed']])
    
    with col_title:
        st.title("🏠 My Dashboard")
        st.write(f"You have **{total - done}** tasks remaining for today.")
    
    with col_prog:
        st.write("") # Spacer
        progress = (done / total) if total > 0 else 0
        st.write(f"**Completion: {int(progress*100)}%**")
        st.progress(progress)

    st.markdown("---")

    # Add New Task Input
    with st.expander("➕ Add New Task", expanded=True):
        c1, c2 = st.columns([4, 1])
        with c1:
            task_title = st.text_input("Task Title", placeholder="Ex: Buy groceries", label_visibility="collapsed")
        with c2:
            if st.button("Add Task", use_container_width=True, type="primary"):
                if task_title:
                    api_add_todo(task_title)
                    st.rerun()

    # Columns for Pending vs Completed
    col_pending, col_done = st.columns(2)

    with col_pending:
        st.subheader("📌 To-Do")
        pending_list = [t for t in todos if not t['is_completed']]
        if not pending_list:
            st.caption("No pending tasks. You're all caught up! ✨")
        for t in pending_list:
            with st.container():
                st.markdown(f"""
                <div class="task-card">
                    <div class="task-title">{t['title']}</div>
                    <div style="color: #3b82f6; font-size: 0.8rem; font-weight: bold; margin-top: 5px;">PENDING</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Inline Buttons using columns
                b1, b2, b_sp = st.columns([1, 1, 4])
                with b1:
                    if st.button("✅", key=f"done_{t['id']}", help="Mark Complete"):
                        api_toggle_todo(t['id'])
                        st.rerun()
                with b2:
                    if st.button("🗑️", key=f"del_p_{t['id']}", help="Delete"):
                        api_delete_todo(t['id'])
                        st.rerun()

    with col_done:
        st.subheader("🎉 Completed")
        done_list = [t for t in todos if t['is_completed']]
        if not done_list:
            st.caption("Finish some tasks to see them here!")
        for t in done_list:
            with st.container():
                st.markdown(f"""
                <div class="task-card task-completed">
                    <div class="task-title task-done-text">{t['title']}</div>
                    <div style="color: #64748b; font-size: 0.8rem; font-weight: bold; margin-top: 5px;">COMPLETED</div>
                </div>
                """, unsafe_allow_html=True)
                
                b1, b2, b_sp = st.columns([1, 1, 4])
                with b1:
                    if st.button("↩️", key=f"undo_{t['id']}", help="Move to Pending"):
                        api_toggle_todo(t['id'])
                        st.rerun()
                with b2:
                    if st.button("🗑️", key=f"del_c_{t['id']}", help="Delete Permanently"):
                        api_delete_todo(t['id'])
                        st.rerun()

# Footer
st.markdown("<br><br><center><p style='color: #94a3b8;'>TaskMaster Pro v2.5 | Crafted for Productivity</p></center>", unsafe_allow_html=True)