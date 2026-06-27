import streamlit as st
import requests
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="TaskMaster Pro", page_icon="✅", layout="centered")

# Custom CSS for an "Impressive" look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4CAF50; color: white; }
    .todo-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .todo-completed {
        border-left: 5px solid #9e9e9e;
        opacity: 0.6;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# --- Helper Functions ---
def login(email, password):
    response = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})
    if response.status_code == 200:
        data = response.json()
        st.session_state.token = data["access_token"]
        st.session_state.user_email = email
        return True
    return False

def register(username, email, password):
    response = requests.post(f"{BASE_URL}/register", json={
        "username": username, "email": email, "password": password
    })
    return response.status_code == 200

def get_todos():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    response = requests.get(f"{BASE_URL}/todos", headers=headers)
    return response.json() if response.status_code == 200 else []

def add_todo(title):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    requests.post(f"{BASE_URL}/todos", json={"title": title}, headers=headers)

def toggle_todo(todo_id):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    requests.put(f"{BASE_URL}/todos/{todo_id}", headers=headers)

def delete_todo(todo_id):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    requests.delete(f"{BASE_URL}/todos/{todo_id}", headers=headers)

# --- UI Logic ---

# Sidebar Navigation
st.sidebar.title("🚀 TaskMaster")
if st.session_state.token:
    st.sidebar.write(f"Logged in as: **{st.session_state.user_email}**")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user_email = None
        st.rerun()
    menu = ["Todo List"]
else:
    menu = ["Login", "Register"]

choice = st.sidebar.selectbox("Navigation", menu)

# --- Register Page ---
if choice == "Register":
    st.title("📝 Create Account")
    with st.form("reg_form"):
        new_user = st.text_input("Username")
        new_email = st.text_input("Email")
        new_pass = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if register(new_user, new_email, new_pass):
                st.success("Account created! Please Login.")
            else:
                st.error("Registration failed. Email might already exist.")

# the Login Page section
elif choice == "Login":
    st.title("🔐 Welcome Back")
    with st.form("login_form"):
        email_input = st.text_input("Email", key="l_email")
        pass_input = st.text_input("Password", type="password", key="l_pass")
        submit = st.form_submit_button("Login")
        
        if submit:
            # STRIP HERE to be safe
            success = login(email_input.strip(), pass_input.strip())
            if success:
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials")

# --- Todo List Page (Protected) ---
elif choice == "Todo List":
    st.title("✅ My Tasks")
    
    # Input Area
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            new_task = st.text_input("Enter new task...", label_visibility="collapsed")
        with col2:
            if st.button("Add") and new_task:
                add_todo(new_task)
                st.rerun()

    st.divider()

    # Display Tasks
    todos = get_todos()
    if not todos:
        st.info("No tasks yet. Add one above!")
    
    for todo in todos:
        # Create a card-like container for each todo
        is_done = todo['is_completed']
        card_class = "todo-card todo-completed" if is_done else "todo-card"
        
        with st.container():
            # Using Markdown for custom styling
            status_text = "~~" + todo['title'] + "~~" if is_done else todo['title']
            
            col_text, col_check, col_del = st.columns([6, 1, 1])
            
            with col_text:
                st.markdown(f"**{status_text}**")
            
            with col_check:
                btn_label = "↩️" if is_done else "✅"
                if st.button(btn_label, key=f"check_{todo['id']}"):
                    toggle_todo(todo['id'])
                    st.rerun()
            
            with col_del:
                if st.button("🗑️", key=f"del_{todo['id']}"):
                    delete_todo(todo['id'])
                    st.rerun()