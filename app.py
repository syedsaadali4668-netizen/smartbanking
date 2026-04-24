"""
Smart Banking System - Professional Streamlit Application
A complete banking management system with custom data structures.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.banking_system import BankingSystem
from models.account import Account
from models.transaction import Transaction

# ============== PAGE CONFIGURATION ==============
st.set_page_config(
    page_title="Smart Banking System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== CUSTOM CSS ==============
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary: #1e3a5f;
        --secondary: #2d5a87;
        --accent: #00d4aa;
        --danger: #ff4757;
        --warning: #ffa502;
        --success: #2ed573;
        --bg-dark: #0f172a;
        --bg-card: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }

    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }

    .main-header h1 {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .main-header p {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* Card styling */
    .stCard {
        background: #1e293b;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #00d4aa;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #1e3a5f, #2d5a87);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(45, 90, 135, 0.4);
    }

    /* Input styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #f1f5f9;
    }

    /* Sidebar */
    .css-1d391kg {
        background: #0f172a;
    }

    /* Success/Error messages */
    .success-msg {
        background: rgba(46, 213, 115, 0.1);
        border-left: 4px solid #2ed573;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        color: #2ed573;
    }

    .error-msg {
        background: rgba(255, 71, 87, 0.1);
        border-left: 4px solid #ff4757;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        color: #ff4757;
    }

    .warning-msg {
        background: rgba(255, 165, 2, 0.1);
        border-left: 4px solid #ffa502;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        color: #ffa502;
    }

    /* Table styling */
    .dataframe {
        background: #1e293b !important;
        border-radius: 12px;
        overflow: hidden;
    }

    .dataframe th {
        background: #1e3a5f !important;
        color: #00d4aa !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 1px;
    }

    .dataframe td {
        color: #f1f5f9 !important;
        border-bottom: 1px solid #334155;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #1e293b;
        border-radius: 8px 8px 0 0;
        color: #94a3b8;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: #2d5a87 !important;
        color: white !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #1e293b;
        border-radius: 8px;
        color: #f1f5f9;
        font-weight: 600;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #0f172a;
    }

    ::-webkit-scrollbar-thumb {
        background: #2d5a87;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #00d4aa;
    }
</style>
""", unsafe_allow_html=True)

# ============== SESSION STATE ==============
def init_session_state():
    """Initialize session state variables."""
    if 'bank' not in st.session_state:
        st.session_state.bank = BankingSystem()
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if 'last_action' not in st.session_state:
        st.session_state.last_action = None
    if 'customer_account_id' not in st.session_state:
        st.session_state.customer_account_id = None

init_session_state()

bank = st.session_state.bank

# ============== HELPER FUNCTIONS ==============
def show_success(message):
    st.markdown(f'<div class="success-msg">✅ {message}</div>', unsafe_allow_html=True)

def show_error(message):
    st.markdown(f'<div class="error-msg">❌ {message}</div>', unsafe_allow_html=True)

def show_warning(message):
    st.markdown(f'<div class="warning-msg">⚠️ {message}</div>', unsafe_allow_html=True)

def format_currency(amount):
    return f"${amount:,.2f}"

def get_risk_badge(score):
    if score >= 80:
        return "🔴 CRITICAL"
    elif score >= 50:
        return "🟠 HIGH"
    elif score >= 25:
        return "🟡 MEDIUM"
    return "🟢 LOW"

# ============== LOGIN PAGE ==============
def login_page():
    st.markdown("""
    <div class="main-header">
        <h1>🏦 Smart Banking System</h1>
        <p>Professional Banking Management Platform</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="background: #1e293b; padding: 2rem; border-radius: 16px; border: 1px solid #334155;">
            <h2 style="text-align: center; color: #00d4aa; margin-bottom: 1.5rem;">🔐 Secure Login</h2>
        </div>
        """, unsafe_allow_html=True)

        login_type = st.radio("Login As", ["👤 Customer", "🔧 Admin"], horizontal=True)

        if "Customer" in login_type:
            st.info("👋 Enter your Account ID and PIN to access your account.")
            cust_id = st.text_input("🪪 Account ID", placeholder="ACC1001")
            cust_pin = st.text_input("🔑 PIN", type="password", placeholder="1234")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🚀 Login", use_container_width=True):
                    if not cust_id or not cust_pin:
                        show_error("Please enter your Account ID and PIN!")
                    else:
                        # Normalize: strip whitespace, uppercase (IDs are like ACC1001)
                        cust_id_clean = cust_id.strip().upper()
                        cust_pin_clean = cust_pin.strip()

                        # Always read from session state to get latest bank object
                        current_bank = st.session_state.bank
                        account = current_bank.get_account(cust_id_clean)

                        if account is None:
                            # Debug: show all known IDs so user can verify
                            all_ids = [a.id for a in current_bank.get_all_accounts()]
                            if all_ids:
                                show_error(f"Account not found! Available accounts: {', '.join(all_ids)}")
                            else:
                                show_error("No accounts exist yet. Please ask admin to create one.")
                        elif not account.is_active:
                            show_error("Your account is inactive. Contact support.")
                        elif account.pin != cust_pin_clean:
                            show_error("Incorrect PIN!")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.is_admin = False
                            st.session_state.customer_account_id = cust_id_clean
                            show_success(f"Welcome back, {account.name}!")
                            time.sleep(0.8)
                            st.rerun()
            with col_b:
                st.caption("Don't have an account? Ask your bank admin to create one.")
        else:
            username = st.text_input("👤 Username", placeholder="admin")
            password = st.text_input("🔑 Password", type="password", placeholder="admin123")

            if st.button("🔐 Login as Admin", use_container_width=True):
                if bank.verify_admin(username, password):
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    show_success("Welcome, Administrator!")
                    time.sleep(1)
                    st.rerun()
                else:
                    show_error("Invalid credentials! Try: admin / admin123")

        st.markdown("""
        <div style="margin-top: 2rem; text-align: center; color: #64748b; font-size: 0.85rem;">
            <p>🔒 Built with custom data structures: BST, Hash Table, Linked List, Stack & Queue</p>
            <p>🛡️ Advanced fraud detection with real-time risk scoring</p>
        </div>
        """, unsafe_allow_html=True)

# ============== SIDEBAR NAVIGATION ==============
def sidebar_nav():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #00d4aa; margin: 0;">🏦 SmartBank</h2>
            <p style="color: #64748b; font-size: 0.8rem;">Professional Banking System</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Navigation
        pages = ["📊 Dashboard", "🏦 Accounts", "💰 Transactions", "🔍 Search", "📈 Analytics"]
        if st.session_state.is_admin:
            pages.extend(["⚙️ Admin Panel", "🛡️ Fraud Monitor"])

        selected = st.radio("Navigation", pages, label_visibility="collapsed")
        st.session_state.current_page = selected

        st.divider()

        # Quick stats in sidebar
        st.markdown("#### 📊 Quick Stats")

        if st.session_state.is_admin:
            stats = bank.get_system_stats()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Accounts", stats["total_accounts"])
            with col2:
                st.metric("Balance", f"${stats['total_balance']:,.0f}")
        else:
            acc = bank.get_account(st.session_state.customer_account_id)
            if acc:
                st.metric("Your Balance", f"${acc.balance:,.2f}")
                st.metric("Account", acc.account_type)

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.customer_account_id = None
            st.rerun()

        st.markdown("""
        <div style="position: fixed; bottom: 1rem; left: 1rem; color: #475569; font-size: 0.7rem;">
            v2.0 | Custom Data Structures
        </div>
        """, unsafe_allow_html=True)

# ============== DASHBOARD PAGE ==============
def dashboard_page():
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard</h1>
        <p>Real-time overview of your banking system</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- CUSTOMER VIEW ----
    if not st.session_state.is_admin:
        acc = bank.get_account(st.session_state.customer_account_id)
        if not acc:
            show_error("Could not load your account. Please log out and try again.")
            return

        cols = st.columns(3)
        with cols[0]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">💰 Your Balance</div>
                <div class="metric-value">{format_currency(acc.balance)}</div>
            </div>""", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🏦 Account Type</div>
                <div class="metric-value" style="font-size:1.3rem;">{acc.account_type}</div>
            </div>""", unsafe_allow_html=True)
        with cols[2]:
            status_color = "#2ed573" if acc.is_active else "#ff4757"
            status_text = "Active" if acc.is_active else "Inactive"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">✅ Status</div>
                <div class="metric-value" style="color:{status_color}; font-size:1.3rem;">{status_text}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📜 Your Recent Transactions")
        if acc.transactions:
            txn_df = pd.DataFrame(acc.transactions)
            txn_df = txn_df.sort_values("timestamp", ascending=False)
            st.dataframe(txn_df, use_container_width=True, hide_index=True)
        else:
            st.info("No transactions yet.")
        return

    # ---- ADMIN VIEW ----
    stats = bank.get_system_stats()

    # Top metrics row
    cols = st.columns(4)
    metrics = [
        ("Total Accounts", stats["total_accounts"], "👥"),
        ("Total Balance", format_currency(stats["total_balance"]), "💰"),
        ("Active Accounts", stats["active_accounts"], "✅"),
        ("Avg Balance", format_currency(stats["average_balance"]), "📈"),
    ]

    for col, (label, value, icon) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{icon} {label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Second row
    cols2 = st.columns(4)
    metrics2 = [
        ("Savings", stats["savings_accounts"], "🏦"),
        ("Checking", stats["checking_accounts"], "💳"),
        ("Suspicious", stats["suspicious_accounts"], "🚨"),
        ("Pending Txn", stats["pending_transactions"], "⏳"),
    ]

    for col, (label, value, icon) in zip(cols2, metrics2):
        with col:
            color = "#ff4757" if label == "Suspicious" and value > 0 else "#00d4aa"
            st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%);">
                <div class="metric-label">{icon} {label}</div>
                <div class="metric-value" style="color: {color};">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts section
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📊 Account Type Distribution")
        if stats["total_accounts"] > 0:
            fig = go.Figure(data=[go.Pie(
                labels=["Savings", "Checking"],
                values=[stats["savings_accounts"], stats["checking_accounts"]],
                hole=0.4,
                marker_colors=["#00d4aa", "#2d5a87"]
            )])
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#f1f5f9",
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No accounts yet. Create one to see analytics!")

    with col_right:
        st.markdown("#### 📈 Data Structure Stats")
        ht_stats = stats["hash_table_stats"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["Size", "Capacity", "Filled Buckets", "Max Chain"],
            y=[ht_stats["size"], ht_stats["capacity"], ht_stats["filled_buckets"], ht_stats["max_chain_length"]],
            marker_color=["#00d4aa", "#2d5a87", "#ffa502", "#ff4757"]
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#f1f5f9",
            xaxis_title="Metric",
            yaxis_title="Count",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(f"BST Height: {stats['bst_height']} | Load Factor: {ht_stats['load_factor']}")

# ============== ACCOUNTS PAGE ==============
def accounts_page():
    st.markdown("""
    <div class="main-header">
        <h1>🏦 Account Management</h1>
        <p>Create, view, and manage bank accounts</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- CUSTOMER VIEW: only their own account ----
    if not st.session_state.is_admin:
        account = bank.get_account(st.session_state.customer_account_id)
        if not account:
            show_error("Could not load your account.")
            return

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background: #1e293b; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155;">
                <h3 style="color: #00d4aa; margin-top: 0;">👤 {account.name}</h3>
                <p><strong>ID:</strong> <code>{account.id}</code></p>
                <p><strong>Type:</strong> {account.account_type}</p>
                <p><strong>Status:</strong> {"🟢 Active" if account.is_active else "🔴 Inactive"}</p>
                <p><strong>Created:</strong> {account.created_at}</p>
                <hr style="border-color: #334155;">
                <h2 style="color: #00d4aa; margin: 0;">{format_currency(account.balance)}</h2>
                <p style="color: #64748b; margin: 0;">Current Balance</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("#### 📊 Risk Analysis")
            risk_level, emoji = bank.fraud_detector.get_risk_level(account.risk_score)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=account.risk_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Risk Score {emoji}", 'font': {'color': '#f1f5f9'}},
                gauge={
                    'axis': {'range': [None, 100], 'tickcolor': '#f1f5f9'},
                    'bar': {'color': '#ff4757' if account.risk_score >= 50 else '#ffa502' if account.risk_score >= 25 else '#2ed573'},
                    'bgcolor': '#1e293b',
                    'borderwidth': 2,
                    'bordercolor': '#334155',
                    'steps': [
                        {'range': [0, 25], 'color': 'rgba(46, 213, 115, 0.2)'},
                        {'range': [25, 50], 'color': 'rgba(255, 165, 2, 0.2)'},
                        {'range': [50, 100], 'color': 'rgba(255, 71, 87, 0.2)'}
                    ],
                }
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#f1f5f9", height=250)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 📜 Transaction History")
        if account.transactions:
            txn_df = pd.DataFrame(account.transactions)
            txn_df = txn_df.sort_values("timestamp", ascending=False)
            st.dataframe(txn_df, use_container_width=True, hide_index=True)
        else:
            st.info("No transactions yet.")
        return

    # ---- ADMIN VIEW ----
    tab1, tab2, tab3 = st.tabs(["➕ Create Account", "📋 All Accounts", "📄 Account Details"])

    # Tab 1: Create Account
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📝 New Account")
            with st.form("create_account_form"):
                name = st.text_input("Full Name *", placeholder="John Doe")
                account_type = st.selectbox("Account Type", ["Savings", "Checking"])
                initial_balance = st.number_input("Initial Balance ($)", min_value=0.0, value=100.0, step=10.0)
                pin = st.text_input("Set PIN (4 digits)", value="1234", max_chars=4, type="password")

                submitted = st.form_submit_button("✨ Create Account", use_container_width=True)

                if submitted:
                    if not name:
                        show_error("Name is required!")
                    elif len(pin) != 4 or not pin.isdigit():
                        show_error("PIN must be exactly 4 digits!")
                    else:
                        success, msg, account = bank.create_account(name, initial_balance, account_type, pin)
                        if success:
                            show_success(msg)
                            st.balloons()
                            st.info(f"💡 Please save your Account ID: **{account.id}**")
                        else:
                            show_error(msg)

        with col2:
            st.markdown("#### ℹ️ Account Types")
            st.info("""
            **Savings Account**
            - Higher interest rates
            - Limited withdrawals per month
            - Best for long-term savings

            **Checking Account**
            - Unlimited transactions
            - Easy access to funds
            - Best for daily use
            """)

            st.markdown("#### 🔐 Security Tips")
            st.warning("""
            - Keep your Account ID and PIN confidential
            - Use a unique PIN (not 1234)
            - Monitor your transactions regularly
            """)

    # Tab 2: All Accounts
    with tab2:
        accounts = bank.get_all_accounts()

        if not accounts:
            st.info("No accounts found. Create your first account above!")
        else:
            sort_option = st.selectbox("Sort By", ["Balance (Low to High)", "Balance (High to Low)", "Name (A-Z)", "Name (Z-A)", "Date Created"])

            if sort_option == "Balance (Low to High)":
                accounts = bank.get_sorted_by_balance()
            elif sort_option == "Balance (High to Low)":
                accounts = bank.get_sorted_by_balance(reverse=True)
            elif sort_option == "Name (A-Z)":
                accounts = bank.get_sorted_by_name()
            elif sort_option == "Name (Z-A)":
                accounts = bank.get_sorted_by_name(reverse=True)

            # Display as dataframe
            df_data = []
            for acc in accounts:
                df_data.append({
                    "ID": acc.id,
                    "Name": acc.name,
                    "Type": acc.account_type,
                    "Balance": f"${acc.balance:,.2f}",
                    "Status": "🟢 Active" if acc.is_active else "🔴 Inactive",
                    "Risk": get_risk_badge(acc.risk_score),
                    "Created": acc.created_at
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.caption(f"Showing {len(accounts)} account(s)")

    # Tab 3: Account Details
    with tab3:
        account_id = st.text_input("Enter Account ID", placeholder="ACC1001")

        if account_id:
            account = bank.get_account(account_id)
            if account:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    <div style="background: #1e293b; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155;">
                        <h3 style="color: #00d4aa; margin-top: 0;">👤 {account.name}</h3>
                        <p><strong>ID:</strong> <code>{account.id}</code></p>
                        <p><strong>Type:</strong> {account.account_type}</p>
                        <p><strong>Status:</strong> {"🟢 Active" if account.is_active else "🔴 Inactive"}</p>
                        <p><strong>Created:</strong> {account.created_at}</p>
                        <hr style="border-color: #334155;">
                        <h2 style="color: #00d4aa; margin: 0;">{format_currency(account.balance)}</h2>
                        <p style="color: #64748b; margin: 0;">Current Balance</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("#### 📊 Risk Analysis")
                    risk_level, emoji = bank.fraud_detector.get_risk_level(account.risk_score)

                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=account.risk_score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': f"Risk Score {emoji}", 'font': {'color': '#f1f5f9'}},
                        gauge={
                            'axis': {'range': [None, 100], 'tickcolor': '#f1f5f9'},
                            'bar': {'color': '#ff4757' if account.risk_score >= 50 else '#ffa502' if account.risk_score >= 25 else '#2ed573'},
                            'bgcolor': '#1e293b',
                            'borderwidth': 2,
                            'bordercolor': '#334155',
                            'steps': [
                                {'range': [0, 25], 'color': 'rgba(46, 213, 115, 0.2)'},
                                {'range': [25, 50], 'color': 'rgba(255, 165, 2, 0.2)'},
                                {'range': [50, 100], 'color': 'rgba(255, 71, 87, 0.2)'}
                            ],
                        }
                    ))
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#f1f5f9", height=250)
                    st.plotly_chart(fig, use_container_width=True)

                # Transaction history
                st.markdown("#### 📜 Transaction History")
                if account.transactions:
                    txn_df = pd.DataFrame(account.transactions)
                    txn_df = txn_df.sort_values("timestamp", ascending=False)
                    st.dataframe(txn_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No transactions yet.")
            else:
                show_error("Account not found!")

# ============== TRANSACTIONS PAGE ==============
def transactions_page():
    st.markdown("""
    <div class="main-header">
        <h1>💰 Transactions</h1>
        <p>Deposit, withdraw, and transfer funds securely</p>
    </div>
    """, unsafe_allow_html=True)

    # For customers, lock the account ID to their own
    is_customer = not st.session_state.is_admin
    locked_id = st.session_state.customer_account_id if is_customer else None

    tab1, tab2, tab3, tab4 = st.tabs(["💵 Deposit", "💸 Withdraw", "🔄 Transfer", "↩️ Undo"])

    # Tab 1: Deposit
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            with st.form("deposit_form"):
                st.markdown("#### 💵 Make a Deposit")
                if is_customer:
                    st.info(f"Account: **{locked_id}**")
                    acc_id = locked_id
                else:
                    acc_id = st.text_input("Account ID", placeholder="ACC1001")
                amount = st.number_input("Amount ($)", min_value=0.01, value=100.0, step=10.0)
                desc = st.text_input("Description (optional)", placeholder="Salary deposit")

                if st.form_submit_button("💵 Deposit", use_container_width=True):
                    if not acc_id:
                        show_error("Account ID is required!")
                    else:
                        success, msg, result = bank.deposit(acc_id, amount, desc)
                        if success:
                            show_success(msg)
                        else:
                            if isinstance(result, list):  # Fraud alerts
                                show_warning(msg)
                                for alert in result:
                                    st.warning(alert)
                            else:
                                show_error(msg)

        with col2:
            st.info("""
            **Deposit Guidelines:**
            - Minimum deposit: $0.01
            - Deposits over $10,000 may trigger fraud review
            - Funds are available immediately for amounts under review threshold
            """)

    # Tab 2: Withdraw
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            with st.form("withdraw_form"):
                st.markdown("#### 💸 Make a Withdrawal")
                if is_customer:
                    st.info(f"Account: **{locked_id}**")
                    acc_id = locked_id
                else:
                    acc_id = st.text_input("Account ID", placeholder="ACC1001", key="w_id")
                pin = st.text_input("PIN", type="password", placeholder="1234", key="w_pin")
                amount = st.number_input("Amount ($)", min_value=0.01, value=50.0, step=10.0, key="w_amt")
                desc = st.text_input("Description (optional)", placeholder="ATM withdrawal", key="w_desc")

                if st.form_submit_button("💸 Withdraw", use_container_width=True):
                    if not acc_id or not pin:
                        show_error("Account ID and PIN are required!")
                    else:
                        success, msg, result = bank.withdraw(acc_id, amount, pin, desc)
                        if success:
                            show_success(msg)
                        else:
                            if isinstance(result, list):
                                show_warning(msg)
                                for alert in result:
                                    st.warning(alert)
                            else:
                                show_error(msg)

        with col2:
            st.info("""
            **Withdrawal Guidelines:**
            - PIN verification required
            - Cannot exceed available balance
            - Large withdrawals may be flagged for review
            - Daily velocity limit: $50,000
            """)

    # Tab 3: Transfer
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            with st.form("transfer_form"):
                st.markdown("#### 🔄 Transfer Funds")
                if is_customer:
                    st.info(f"From Account: **{locked_id}**")
                    from_id = locked_id
                else:
                    from_id = st.text_input("From Account ID", placeholder="ACC1001")
                to_id = st.text_input("To Account ID", placeholder="ACC1002")
                pin = st.text_input("Your PIN", type="password", placeholder="1234")
                amount = st.number_input("Amount ($)", min_value=0.01, value=100.0, step=10.0)
                desc = st.text_input("Description (optional)", placeholder="Rent payment")

                if st.form_submit_button("🔄 Transfer", use_container_width=True):
                    if not from_id or not to_id or not pin:
                        show_error("All fields are required!")
                    else:
                        success, msg, result = bank.transfer(from_id, to_id, amount, pin, desc)
                        if success:
                            show_success(msg)
                        else:
                            show_error(msg)

        with col2:
            st.info("""
            **Transfer Guidelines:**
            - Both accounts must be active
            - PIN verification required for source account
            - Cannot transfer to the same account
            - Transfers are immediate for approved amounts
            """)

    # Tab 4: Undo
    with tab4:
        st.markdown("#### ↩️ Undo Last Transaction")

        history = bank.get_undo_history()
        if not history:
            st.info("No transactions to undo.")
        else:
            st.write(f"Available undo operations: **{len(history)}**")

            # Show recent history
            with st.expander("📜 Recent Transaction History"):
                for i, action in enumerate(reversed(history[-5:])):
                    st.write(f"{i+1}. **{action['action'].title()}** - ${action['amount']:,.2f} ({action['timestamp']})")

            if st.button("↩️ Undo Last Transaction", use_container_width=True):
                success, msg, action = bank.undo_last_transaction()
                if success:
                    show_success(msg)
                    time.sleep(1)
                    st.rerun()
                else:
                    show_error(msg)

# ============== SEARCH PAGE ==============
def search_page():
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Search</h1>
        <p>Find accounts using multiple search methods</p>
    </div>
    """, unsafe_allow_html=True)

    # Customers can only look up their own account
    if not st.session_state.is_admin:
        account = bank.get_account(st.session_state.customer_account_id)
        if account:
            st.success(f"Showing your account — **{account.id}**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Name", account.name)
            col2.metric("Balance", format_currency(account.balance))
            col3.metric("Type", account.account_type)
        else:
            show_error("Account not found.")
        return

    search_type = st.selectbox("Search Method", ["By Account ID (Hash Table - O(1))", "By Name (Linear Search - O(n))", "By Balance Range (Filter)"])

    if "Account ID" in search_type:
        account_id = st.text_input("Enter Account ID", placeholder="ACC1001")
        if st.button("🔍 Search", use_container_width=True):
            account = bank.search_account_by_id(account_id)
            if account:
                st.success(f"Found account in **O(1)** time using Hash Table!")

                col1, col2, col3 = st.columns(3)
                col1.metric("Name", account.name)
                col2.metric("Balance", format_currency(account.balance))
                col3.metric("Type", account.account_type)

                st.code(
                    f"Hash Table Lookup:\n"
                    f"  Index: {hash(account_id) % 101}\n"
                    f"  Key: {account_id}\n"
                    f"  Value: Account({account.name})"
                )
            else:
                show_error("Account not found!")

    elif "Name" in search_type:
        name = st.text_input("Enter Name", placeholder="John Doe")
        if st.button("🔍 Search", use_container_width=True):
            account = bank.search_account_by_name(name)
            if account:
                st.success(f"Found account using **Linear Search - O(n)**!")
                col1, col2, col3 = st.columns(3)
                col1.metric("ID", account.id)
                col2.metric("Balance", format_currency(account.balance))
                col3.metric("Type", account.account_type)
            else:
                show_error("No account found with that name!")

    else:
        col1, col2 = st.columns(2)
        min_bal = col1.number_input("Minimum Balance", min_value=0.0, value=0.0)
        max_bal = col2.number_input("Maximum Balance", min_value=0.0, value=100000.0)

        if st.button("🔍 Search", use_container_width=True):
            results = bank.search_accounts_by_balance_range(min_bal, max_bal)
            if results:
                st.success(f"Found {len(results)} account(s) in range!")
                df_data = [{"ID": acc.id, "Name": acc.name, "Balance": f"${acc.balance:,.2f}", "Type": acc.account_type} for acc in results]
                st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
            else:
                st.info("No accounts found in this range.")

# ============== ANALYTICS PAGE ==============
def analytics_page():
    st.markdown("""
    <div class="main-header">
        <h1>📈 Analytics</h1>
        <p>Visualize banking data and system performance</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- CUSTOMER VIEW ----
    if not st.session_state.is_admin:
        account = bank.get_account(st.session_state.customer_account_id)
        if not account:
            show_error("Could not load your account.")
            return

        st.markdown("#### 💰 Your Transaction History")
        if not account.transactions:
            st.info("No transactions yet.")
            return

        txn_df = pd.DataFrame(account.transactions)
        txn_df["amount"] = pd.to_numeric(txn_df["amount"], errors="coerce")

        fig = px.bar(
            txn_df,
            x="timestamp", y="amount",
            color="transaction_type",
            labels={"timestamp": "Date", "amount": "Amount ($)", "transaction_type": "Type"},
            color_discrete_map={"deposit": "#2ed573", "withdrawal": "#ff4757", "transfer": "#ffa502"}
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#f1f5f9",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
        return

    # ---- ADMIN VIEW ----
    accounts = bank.get_all_accounts()

    if not accounts:
        st.info("No data available. Create accounts to see analytics!")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💰 Balance Distribution")
        balances = [acc.balance for acc in accounts]
        names = [acc.name for acc in accounts]

        fig = px.bar(
            x=names, y=balances,
            labels={"x": "Account Holder", "y": "Balance ($)"},
            color=balances,
            color_continuous_scale="Teal"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#f1f5f9",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 📊 Balance Range Analysis")
        ranges = {"$0-1K": 0, "$1K-5K": 0, "$5K-10K": 0, "$10K+": 0}
        for acc in accounts:
            bal = acc.balance
            if bal < 1000:
                ranges["$0-1K"] += 1
            elif bal < 5000:
                ranges["$1K-5K"] += 1
            elif bal < 10000:
                ranges["$5K-10K"] += 1
            else:
                ranges["$10K+"] += 1

        fig = px.pie(
            values=list(ranges.values()),
            names=list(ranges.keys()),
            color=list(ranges.keys()),
            color_discrete_map={"$0-1K": "#2ed573", "$1K-5K": "#00d4aa", "$5K-10K": "#ffa502", "$10K+": "#ff4757"}
        )
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#f1f5f9")
        st.plotly_chart(fig, use_container_width=True)

    # Data Structure Performance
    st.markdown("#### ⚡ Data Structure Performance")
    stats = bank.get_system_stats()
    ht_stats = stats["hash_table_stats"]

    perf_data = {
        "Operation": ["Hash Table Lookup", "BST Search", "Linear Search", "Quick Sort", "Merge Sort"],
        "Time Complexity": ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n log n)"],
        "Space Complexity": ["O(n)", "O(n)", "O(1)", "O(log n)", "O(n)"],
        "Status": ["✅ Active", "✅ Active", "✅ Active", "✅ Active", "✅ Active"]
    }
    st.dataframe(pd.DataFrame(perf_data), use_container_width=True, hide_index=True)

# ============== ADMIN PANEL ==============
def admin_page():
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Admin Panel</h1>
        <p>System administration and management tools</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Account Control", "⏳ Pending Reviews", "📊 System Info", "🗑️ System Reset"])

    with tab1:
        st.markdown("#### 🔧 Manage Accounts")
        account_id = st.text_input("Account ID to Manage", placeholder="ACC1001")

        if account_id:
            account = bank.get_account(account_id)
            if account:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🚫 Delete Account", use_container_width=True):
                        success, msg = bank.delete_account(account_id)
                        if success:
                            show_success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            show_error(msg)

                with col2:
                    new_status = "Activate" if not account.is_active else "Deactivate"
                    if st.button(f"🔄 {new_status} Account", use_container_width=True):
                        success, msg = bank.toggle_account_status(account_id)
                        if success:
                            show_success(msg)
                            time.sleep(1)
                            st.rerun()
                        else:
                            show_error(msg)

                st.markdown("#### Account Details")
                st.json(account.to_dict())
            else:
                show_error("Account not found!")

    with tab2:
        st.markdown("#### ⏳ Pending Transaction Reviews")
        pending = bank.get_pending_transactions()

        if not pending:
            st.info("No pending transactions.")
        else:
            for txn in pending:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{txn.transaction_id}** | {txn.transaction_type} | ${txn.amount:,.2f} | {txn.account_id}")
                    with col2:
                        if st.button("✅ Approve", key=f"app_{txn.transaction_id}"):
                            success, msg = bank.approve_transaction(txn.transaction_id)
                            if success:
                                show_success(msg)
                                time.sleep(1)
                                st.rerun()
                    with col3:
                        if st.button("❌ Reject", key=f"rej_{txn.transaction_id}"):
                            success, msg = bank.reject_transaction(txn.transaction_id)
                            if success:
                                show_success(msg)
                                time.sleep(1)
                                st.rerun()
                    st.divider()

    with tab3:
        st.markdown("#### 📊 System Information")
        stats = bank.get_system_stats()

        col1, col2 = st.columns(2)
        with col1:
            st.json({
                "Total Accounts": stats["total_accounts"],
                "Total Balance": stats["total_balance"],
                "Active Accounts": stats["active_accounts"],
                "Inactive Accounts": stats["inactive_accounts"],
                "Suspicious Accounts": stats["suspicious_accounts"],
                "Pending Transactions": stats["pending_transactions"]
            })

        with col2:
            st.json({
                "Hash Table": stats["hash_table_stats"],
                "BST Height": stats["bst_height"],
                "Undo History Size": stats["undo_history_size"]
            })

        st.markdown("#### 🏗️ Data Structures Used")
        st.info("""
        - **Hash Table** (Separate Chaining): O(1) account lookup by ID
        - **Binary Search Tree**: O(log n) sorted account storage by balance
        - **Linked List**: Customer record management
        - **Stack**: LIFO undo transaction history
        - **Queue**: FIFO pending transaction processing
        """)

    with tab4:
        st.markdown("#### 🗑️ System Reset")
        st.warning("⚠️ This will delete ALL data permanently!")

        confirm = st.text_input("Type 'RESET' to confirm", placeholder="RESET")
        if st.button("💥 Reset System", use_container_width=True):
            if confirm == "RESET":
                success, msg = bank.reset_system()
                if success:
                    show_success(msg)
                    time.sleep(1)
                    st.rerun()
            else:
                show_error("Type 'RESET' to confirm!")

# ============== FRAUD MONITOR ==============
def fraud_page():
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ Fraud Monitor</h1>
        <p>Real-time fraud detection and risk analysis</p>
    </div>
    """, unsafe_allow_html=True)

    suspicious = bank.fraud_detector.get_suspicious_accounts()

    st.markdown("#### 🚨 Suspicious Accounts")
    if not suspicious:
        st.success("✅ No suspicious accounts detected!")
    else:
        st.warning(f"⚠️ {len(suspicious)} suspicious account(s) detected!")

        for acc_id in suspicious:
            account = bank.get_account(acc_id)
            if account:
                with st.expander(f"🔴 {acc_id} - {account.name} (Risk: {account.risk_score})"):
                    col1, col2 = st.columns(2)
                    col1.metric("Balance", format_currency(account.balance))
                    col2.metric("Risk Score", account.risk_score)

                    if account.transactions:
                        st.write("Recent Transactions:")
                        recent = account.transactions[-5:]
                        for txn in recent:
                            st.write(f"- {txn['timestamp']}: {txn['transaction_type']} ${txn['amount']:,.2f}")

    st.markdown("#### 📋 Fraud Detection Rules")
    rules = bank.fraud_detector.fraud_rules

    col1, col2 = st.columns(2)
    with col1:
        st.info(f"""
        **Transaction Rules:**
        - Large Transaction Threshold: ${rules['large_transaction_threshold']:,.2f}
        - Daily Velocity Limit: ${rules['velocity_limit_per_day']:,.2f}
        - New Account Large TX: ${rules['new_account_large_tx_threshold']:,.2f}
        - New Account Period: {rules['new_account_days']} days
        """)

    with col2:
        st.info(f"""
        **Behavioral Rules:**
        - Rapid TX Threshold: {rules['rapid_transaction_threshold']} in {rules['rapid_transaction_window_minutes']} min
        - Unusual Hours: {rules['unusual_hour_start']}:00 - {rules['unusual_hour_end']}:00
        - Balance Drain: >90% of balance
        - Round Amount: Structuring detection
        """)

# ============== MAIN APP ==============
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        sidebar_nav()

        page = st.session_state.current_page

        if "Dashboard" in page:
            dashboard_page()
        elif "Accounts" in page:
            accounts_page()
        elif "Transactions" in page:
            transactions_page()
        elif "Search" in page:
            search_page()
        elif "Analytics" in page:
            analytics_page()
        elif "Admin" in page:
            admin_page()
        elif "Fraud" in page:
            fraud_page()
        else:
            dashboard_page()

if __name__ == "__main__":
    main()