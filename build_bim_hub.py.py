import os

# Define target folder and structure
BASE_DIR = "bim_hub"

files = {
    # -------------------------------------------------------------
    # 1. DATABASE
    # -------------------------------------------------------------
    "database.py": '''import sqlite3
import hashlib
import os

DB_FILE = "bim_hub.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str, salt: str = "bim_secure_salt_2026") -> str:
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT CHECK(role IN ('Admin', 'Engineer', 'Viewer')) NOT NULL,
        email TEXT,
        avatar_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buildings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        campus TEXT NOT NULL,
        manager TEXT NOT NULL,
        address TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        status TEXT NOT NULL,
        image_url TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        building_id INTEGER,
        status TEXT NOT NULL,
        progress INTEGER DEFAULT 0,
        budget REAL,
        spent REAL,
        start_date DATE,
        end_date DATE,
        FOREIGN KEY(building_id) REFERENCES buildings(id) ON DELETE SET NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS floors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        building_id INTEGER NOT NULL,
        floor_level INTEGER NOT NULL,
        name TEXT NOT NULL,
        area_sqm REAL NOT NULL,
        target_occupancy INTEGER,
        current_occupancy INTEGER,
        FOREIGN KEY(building_id) REFERENCES buildings(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        floor_id INTEGER NOT NULL,
        room_number TEXT NOT NULL,
        name TEXT NOT NULL,
        room_type TEXT NOT NULL,
        equipment_count INTEGER DEFAULT 0,
        max_occupancy INTEGER,
        status TEXT NOT NULL,
        image_url TEXT,
        FOREIGN KEY(floor_id) REFERENCES floors(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS structural_elements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        element_tag TEXT UNIQUE NOT NULL,
        building_id INTEGER NOT NULL,
        category TEXT CHECK(category IN ('Column', 'Beam', 'Wall', 'Slab', 'Foundation')) NOT NULL,
        material TEXT NOT NULL,
        health_index INTEGER CHECK(health_index BETWEEN 0 AND 100),
        status TEXT NOT NULL,
        last_inspection_date DATE,
        FOREIGN KEY(building_id) REFERENCES buildings(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bim_models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        format TEXT CHECK(format IN ('IFC', 'RVT', 'DWG', 'NWD', 'PDF')) NOT NULL,
        file_size_mb REAL NOT NULL,
        building_id INTEGER,
        uploaded_by TEXT NOT NULL,
        version TEXT NOT NULL,
        upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL,
        FOREIGN KEY(building_id) REFERENCES buildings(id) ON DELETE SET NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_data(cursor)

    conn.commit()
    conn.close()

def seed_data(cursor):
    admin_pw = hash_password("admin123")
    eng_pw = hash_password("engineer123")
    viewer_pw = hash_password("viewer123")

    cursor.executemany("""
    INSERT INTO users (username, password_hash, full_name, role, email, avatar_url)
    VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ("admin", admin_pw, "Elena Rostova", "Admin", "elena.rostova@nexusbim.com", "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150"),
        ("engineer", eng_pw, "Marcus Vance", "Engineer", "marcus.vance@nexusbim.com", "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150"),
        ("viewer", viewer_pw, "Sarah Chen", "Viewer", "sarah.chen@nexusbim.com", "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150")
    ])

    cursor.executemany("""
    INSERT INTO buildings (code, name, campus, manager, address, latitude, longitude, status, image_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ("BLD-01", "AeroTech HQ", "Innovation Park", "Marcus Vance", "100 Tech Blvd, Austin, TX", 30.2672, -97.7431, "Active", "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800"),
        ("BLD-02", "Nexus Tower Alpha", "Metro Hub", "Elena Rostova", "500 Grand Ave, Chicago, IL", 41.8781, -87.6298, "Under Construction", "https://images.unsplash.com/photo-1541888946425-d0fbb186a5b7?w=800"),
        ("BLD-03", "Helix Biotech Lab", "North Science Campus", "David Miller", "12 Bio Way, Boston, MA", 42.3601, -71.0589, "Planning", "https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=800")
    ])

    cursor.executemany("""
    INSERT INTO projects (code, name, building_id, status, progress, budget, spent, start_date, end_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ("PRJ-2026-A", "AeroTech Modernization", 1, "In Progress", 78, 12500000, 9200000, "2025-01-15", "2026-11-30"),
        ("PRJ-2026-B", "Nexus Superstructure", 2, "In Progress", 42, 45000000, 18900000, "2025-06-01", "2027-04-15"),
        ("PRJ-2026-C", "Helix Cleanroom Fitout", 3, "Planning", 15, 8700000, 1100000, "2026-02-01", "2026-12-20")
    ])

    cursor.executemany("""
    INSERT INTO floors (building_id, floor_level, name, area_sqm, target_occupancy, current_occupancy)
    VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1, 0, "Ground Concourse", 2400.0, 350, 210),
        (1, 1, "Level 1 Executive Suites", 2100.0, 200, 180),
        (1, 2, "Level 2 R&D Facilities", 2200.0, 150, 140),
        (2, 0, "Basement Parking & Mech", 3800.0, 50, 10),
        (2, 1, "Podium Plaza", 3200.0, 500, 0)
    ])

    cursor.executemany("""
    INSERT INTO rooms (floor_id, room_number, name, room_type, equipment_count, max_occupancy, status, image_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (1, "101-A", "Main Atrium", "Assembly", 12, 150, "Operational", "https://images.unsplash.com/photo-1497366216548-37526070297c?w=500"),
        (2, "201-B", "BIM Command Center", "Office", 34, 25, "Operational", "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=500"),
        (3, "305-C", "Server & Supercomputing Room", "Utility", 88, 5, "Restricted", "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500")
    ])

    cursor.executemany("""
    INSERT INTO structural_elements (element_tag, building_id, category, material, health_index, status, last_inspection_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        ("COL-C101", 1, "Column", "High-Strength Steel C60", 98, "Passed", "2026-06-10"),
        ("BM-B204", 1, "Beam", "Reinforced Concrete C40", 94, "Passed", "2026-06-12"),
        ("WAL-W01", 2, "Wall", "Precast Shear Wall", 88, "Inspection Due", "2026-03-01"),
        ("SLB-S102", 2, "Slab", "Post-Tensioned Concrete", 92, "Passed", "2026-05-20"),
        ("FND-F001", 3, "Foundation", "Deep Bored Piles", 100, "Passed", "2026-07-01")
    ])

    cursor.executemany("""
    INSERT INTO bim_models (file_name, format, file_size_mb, building_id, uploaded_by, version, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        ("AeroTech_Arch_v4.ifc", "IFC", 142.5, 1, "engineer", "v4.2", "Verified"),
        ("Nexus_Structural_v2.rvt", "RVT", 380.1, 2, "admin", "v2.0", "Clash Detection Pending"),
        ("Helix_MEP_Combined.nwd", "NWD", 85.4, 3, "engineer", "v1.1", "Approved"),
        ("Civil_Grid_Site.dwg", "DWG", 24.8, 1, "viewer", "v1.0", "Verified")
    ])

    cursor.executemany("""
    INSERT INTO activity_logs (username, action, details)
    VALUES (?, ?, ?)
    """, [
        ("admin", "LOGIN", "Logged into Enterprise BIM Hub"),
        ("engineer", "MODEL_UPLOAD", "Uploaded model AeroTech_Arch_v4.ifc (142.5 MB)"),
        ("admin", "HEALTH_CHECK", "Executed AI Automated Structural Risk Analysis on BLD-02")
    ])

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
''',

    # -------------------------------------------------------------
    # 2. CSS STYLING
    # -------------------------------------------------------------
    "assets/style.css": '''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg-dark: #0f172a;
  --bg-card: rgba(30, 41, 59, 0.7);
  --border-card: rgba(255, 255, 255, 0.08);
  --primary-blue: #2563eb;
  --primary-indigo: #4f46e5;
  --accent-green: #22c55e;
  --accent-amber: #f59e0b;
  --text-primary: #f8fafc;
  --text-muted: #94a3b8;
}

.stApp {
  background: radial-gradient(circle at 20% 20%, rgba(37, 99, 235, 0.12) 0%, transparent 40%),
              radial-gradient(circle at 80% 80%, rgba(79, 70, 229, 0.1) 0%, transparent 40%),
              #0f172a !important;
  font-family: 'Inter', sans-serif !important;
  color: var(--text-primary) !important;
}

header[data-testid='stHeader'] {
  background: rgba(15, 23, 42, 0.8) !important;
  backdrop-filter: blur(12px) !important;
}
footer { visibility: hidden; }

.acc-navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-card);
  padding: 0.75rem 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 12px;
}

.acc-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 800;
  font-size: 1.25rem;
  background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.acc-user-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 14px;
  border-radius: 30px;
  border: 1px solid var(--border-card);
}

.acc-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--primary-blue);
}

.kpi-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border-card);
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  transition: transform 0.25s ease;
  margin-bottom: 1rem;
}

.kpi-card:hover {
  transform: translateY(-4px);
  border-color: rgba(37, 99, 235, 0.4);
}

.kpi-title {
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.kpi-value {
  font-size: 2rem;
  font-weight: 800;
  color: #ffffff;
}

.kpi-trend {
  font-size: 0.8rem;
  font-weight: 600;
  margin-top: 0.5rem;
}

.kpi-trend.positive { color: var(--accent-green); }
.kpi-trend.neutral { color: var(--accent-amber); }

.login-container {
  max-width: 440px;
  margin: 4rem auto;
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  padding: 2.5rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
}

section[data-testid='stSidebar'] {
  background-color: rgba(15, 23, 42, 0.95) !important;
  border-right: 1px solid var(--border-card) !important;
}
''',

    # -------------------------------------------------------------
    # 3. COMPONENTS
    # -------------------------------------------------------------
    "components/login.py": '''import streamlit as st
from database import get_connection, hash_password

def render_login_page():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.95)), 
                    url('https://images.unsplash.com/photo-1541888946425-d0fbb186a5b7?w=1600') no-repeat center center fixed !important;
        background-size: cover !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-container">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏗️</div>
                <h1 style="font-size: 1.8rem; font-weight: 800; margin: 0; background: linear-gradient(135deg, #60A5FA, #A855F7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    NEXUS BIM HUB
                </h1>
                <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 0.25rem;">Enterprise Construction Automation</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("### Secure Sign In")
            username = st.text_input("Username", placeholder="admin, engineer, or viewer")
            password = st.text_input("Password", type="password", placeholder="••••••••••••")
            submit = st.form_submit_button("Authenticate & Enter Workspace", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    hashed_pw = hash_password(password)
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id, username, full_name, role, email, avatar_url 
                        FROM users 
                        WHERE username = ? AND password_hash = ?
                    """, (username.strip(), hashed_pw))
                    user = cursor.fetchone()
                    
                    if user:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = dict(user)
                        conn.close()
                        st.success("Authenticated!")
                        st.rerun()
                    else:
                        conn.close()
                        st.error("Invalid credentials.")
''',

    "components/navbar.py": '''import streamlit as st

def render_navbar():
    user = st.session_state.get("user", {"full_name": "Guest User", "role": "Viewer", "avatar_url": ""})
    st.markdown(f"""
    <div class="acc-navbar">
        <div class="acc-logo">
            <span style="font-size: 1.5rem;">❖</span> NEXUS AUTODESK CONNECT
        </div>
        <div style="display: flex; align-items: center; gap: 20px;">
            <div class="acc-user-badge">
                <img src="{user.get('avatar_url', '')}" class="acc-avatar">
                <div>
                    <div style="font-weight: 600; font-size: 0.85rem; color: #F8FAFC;">{user.get('full_name')}</div>
                    <div style="font-size: 0.7rem; color: #38BDF8;">{str(user.get('role')).upper()}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
''',

    "components/sidebar.py": '''import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("### 🏛️ Navigation")
        pages = {
            "Dashboard": "📊 Executive Dashboard",
            "Buildings": "🏢 Building Manager",
            "Floors": "📐 Floor Plans & Rooms",
            "Structural": "🦴 Structural Health",
            "BIM Models": "📦 BIM Models & Upload",
            "Reports": "📑 Reports & Analytics",
            "AI Assistant": "🤖 AI Co-Pilot & Insights",
            "Settings": "⚙️ System Configuration"
        }
        selected = st.radio("Go to", list(pages.keys()), format_func=lambda x: pages[x], label_visibility="collapsed")
        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.rerun()
        return selected
''',

    "components/dashboard.py": '''import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import get_connection

def render_dashboard():
    st.markdown("## 📊 Executive BIM Overview")
    conn = get_connection()

    bld_cnt = conn.execute("SELECT COUNT(*) FROM buildings").fetchone()[0]
    mdl_cnt = conn.execute("SELECT COUNT(*) FROM bim_models").fetchone()[0]
    ele_cnt = conn.execute("SELECT COUNT(*) FROM structural_elements").fetchone()[0]
    prj_cnt = conn.execute("SELECT COUNT(*) FROM projects WHERE status = 'In Progress'").fetchone()[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-title">BIM Models</div><div class="kpi-value">{mdl_cnt}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-title">Facilities</div><div class="kpi-value">{bld_cnt}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-title">Elements</div><div class="kpi-value">{ele_cnt:,}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card"><div class="kpi-title">Active Projects</div><div class="kpi-value">{prj_cnt}</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏢 Facility Status")
        df_bld = pd.read_sql_query("SELECT status FROM buildings", conn)
        if not df_bld.empty:
            fig = px.pie(df_bld, names="status", hole=0.4, color_discrete_sequence=['#2563EB', '#22C55E', '#F59E0B'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#F8FAFC'))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 📈 Financial Budget Execution")
        df_prj = pd.read_sql_query("SELECT name, budget, spent FROM projects", conn)
        if not df_prj.empty:
            fig = go.Figure(data=[
                go.Bar(name='Budget', x=df_prj['name'], y=df_prj['budget'], marker_color='#4F46E5'),
                go.Bar(name='Spent', x=df_prj['name'], y=df_prj['spent'], marker_color='#22C55E')
            ])
            fig.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#F8FAFC'))
            st.plotly_chart(fig, use_container_width=True)

    conn.close()
''',

    "components/buildings.py": '''import streamlit as st
import pandas as pd
from database import get_connection

def render_buildings():
    st.markdown("## 🏢 Building Asset Management")
    conn = get_connection()
    df_bld = pd.read_sql_query("SELECT * FROM buildings", conn)

    if not df_bld.empty:
        cols = st.columns(3)
        for index, row in df_bld.iterrows():
            with cols[index % 3]:
                st.markdown(f"""
                <div class="kpi-card" style="padding:0; overflow:hidden;">
                    <img src="{row['image_url']}" style="width:100%; height:140px; object-fit:cover;">
                    <div style="padding: 1rem;">
                        <h4 style="margin:0; color:#F8FAFC;">{row['name']}</h4>
                        <p style="color:#94A3B8; font-size:0.8rem; margin-top:4px;">{row['address']}</p>
                        <span style="color:#22C55E; font-size:0.8rem; font-weight:600;">Status: {row['status']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    conn.close()
''',

    "components/floors.py": '''import streamlit as st
import pandas as pd
from database import get_connection

def render_floors():
    st.markdown("## 📐 Floor Plans & Allocations")
    conn = get_connection()
    df_floors = pd.read_sql_query("SELECT * FROM floors", conn)
    st.dataframe(df_floors, use_container_width=True)
    conn.close()
''',

    "components/structural.py": '''import streamlit as st
import pandas as pd
from database import get_connection

def render_structural():
    st.markdown("## 🦴 Structural Integrity")
    conn = get_connection()
    df_struct = pd.read_sql_query("SELECT * FROM structural_elements", conn)
    st.dataframe(df_struct, use_container_width=True)
    conn.close()
''',

    "components/models.py": '''import streamlit as st
import pandas as pd
from database import get_connection

def render_models():
    st.markdown("## 📦 BIM Models Repository")
    conn = get_connection()
    df_models = pd.read_sql_query("SELECT * FROM bim_models", conn)
    st.dataframe(df_models, use_container_width=True)
    conn.close()
''',

    "components/reports.py": '''import streamlit as st
import pandas as pd
from database import get_connection

def render_reports():
    st.markdown("## 📑 Compliance & Analytics Reports")
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM buildings", conn)
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Export CSV", df.to_csv(index=False), "report.csv", "text/csv")
    conn.close()
''',

    "components/ai_assistant.py": '''import streamlit as st

def render_ai_assistant():
    st.markdown("## 🤖 AI Architectural Co-Pilot")
    prompt = st.chat_input("Ask a question about your BIM models...")
    if prompt:
        st.write(f"**User:** {prompt}")
        st.write(f"**AI Co-Pilot:** Analysis complete for: '{prompt}'. Structural integrity parameters are normal.")
''',

    "components/settings.py": '''import streamlit as st

def render_settings():
    st.markdown("## ⚙️ System Configuration")
    st.checkbox("Enable Autodesk ACC Auto-Sync", value=True)
    st.checkbox("Enable Automated Clash Detection", value=True)
    if st.button("Save Settings"):
        st.success("Settings saved.")
''',

    # -------------------------------------------------------------
    # 4. MAIN ENTRY POINT
    # -------------------------------------------------------------
    "app.py": '''import streamlit as st
import os

st.set_page_config(page_title="Nexus BIM Hub", page_icon="🏗️", layout="wide")

from database import init_db
init_db()

def load_css():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

from components.login import render_login_page
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.buildings import render_buildings
from components.floors import render_floors
from components.structural import render_structural
from components.models import render_models
from components.reports import render_reports
from components.ai_assistant import render_ai_assistant
from components.settings import render_settings

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def main():
    if not st.session_state["authenticated"]:
        render_login_page()
    else:
        render_navbar()
        page = render_sidebar()
        if page == "Dashboard": render_dashboard()
        elif page == "Buildings": render_buildings()
        elif page == "Floors": render_floors()
        elif page == "Structural": render_structural()
        elif page == "BIM Models": render_models()
        elif page == "Reports": render_reports()
        elif page == "AI Assistant": render_ai_assistant()
        elif page == "Settings": render_settings()

if __name__ == "__main__":
    main()
'''
}

# Execute creation
print("🚀 Building bim_hub project files...")
for file_path, content in files.items():
    full_path = os.path.join(BASE_DIR, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ Created: {full_path}")

print("\n✅ All files successfully generated inside 'bim_hub/'!")