import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, date, timedelta
import random
import string

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Chick & Juice Faeyza",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── USERS & ROLES ─────────────────────────────────────────────
USERS = {
    "admin":  {"password": "faeyza",   "role": "admin"},
    "kasir":  {"password": "kasir123", "role": "kasir"},
}

MENU_BY_ROLE = {
    "admin": ["🏠 Dashboard", "🛒 Kasir", "📦 Stok", "📊 Laporan"],
    "kasir": ["🛒 Kasir", "📦 Stok"],
}

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    background-color: #FFF8F0 !important;
    color: #2C1810 !important;
    font-family: 'Poppins', 'Segoe UI', sans-serif !important;
}

/* ── Animated gradient background ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #FFF8F0 0%, #FFF0E0 50%, #FFF8F0 100%) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #C0392B 0%, #7B241C 60%, #641E16 100%) !important;
    min-width: 210px !important;
    max-width: 225px !important;
    border-right: 3px solid #F1C40F !important;
    box-shadow: 4px 0 20px rgba(192,57,43,0.3) !important;
}
[data-testid="stSidebar"] * { color: #fff !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 6px 0 !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.8) !important;
    font-size: 12px;
}

/* ── Arrow toggle putih ── */
[data-testid="collapsedControl"] svg { color: #fff !important; fill: #fff !important; }
button[kind="header"] svg { color: #fff !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #fff 60%, #FFF8E1 100%) !important;
    border-radius: 16px !important;
    padding: 20px 16px !important;
    border-top: 4px solid #F1C40F !important;
    border-left: none !important;
    box-shadow: 0 6px 20px rgba(192,57,43,0.10) !important;
    color: #2C1810 !important;
}
[data-testid="metric-container"] label { color: #7B241C !important; font-weight: 700 !important; }
[data-testid="metric-container"] div   { color: #2C1810 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 10px 22px !important;
    box-shadow: 0 4px 14px rgba(231,76,60,0.35) !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #F1C40F 0%, #D4AC0D 100%) !important;
    color: #2C1810 !important;
    box-shadow: 0 6px 18px rgba(241,196,15,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Cards ── */
.card {
    background: linear-gradient(135deg, #fff 70%, #FFF8E1 100%);
    border-radius: 16px;
    border-top: 3px solid #F1C40F;
    box-shadow: 0 4px 16px rgba(192,57,43,0.08);
    padding: 18px;
    margin-bottom: 14px;
}
.card:hover {
    box-shadow: 0 8px 24px rgba(192,57,43,0.15);
    transform: translateY(-2px);
    transition: all 0.2s ease;
}

/* ── Login box ── */
.login-box {
    background: #fff;
    border-radius: 20px;
    padding: 44px;
    max-width: 420px;
    margin: 50px auto;
    box-shadow: 0 8px 32px rgba(192,57,43,0.15);
    border-top: 5px solid #F1C40F;
    border-bottom: 2px solid #E74C3C;
}

/* ── Badge role ── */
.badge-admin {
    background: linear-gradient(135deg, #E74C3C, #C0392B);
    color: #fff;
    padding: 4px 14px; border-radius: 20px;
    font-size: 12px; font-weight: 700;
    box-shadow: 0 2px 8px rgba(231,76,60,0.35);
}
.badge-kasir {
    background: linear-gradient(135deg, #F1C40F, #D4AC0D);
    color: #2C1810;
    padding: 4px 14px; border-radius: 20px;
    font-size: 12px; font-weight: 700;
    box-shadow: 0 2px 8px rgba(241,196,15,0.35);
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input {
    border-radius: 10px !important;
    border: 2px solid #F5CBA7 !important;
    background: #FFFDF7 !important;
    color: #2C1810 !important;
}
.stTextInput input:focus { border-color: #E74C3C !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #fff !important;
    border-radius: 12px !important;
    padding: 4px !important;
    box-shadow: 0 2px 10px rgba(192,57,43,0.08) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #E74C3C, #C0392B) !important;
    color: #fff !important;
    border-radius: 10px !important;
}

/* ── Tables ── */
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 16px rgba(192,57,43,0.08) !important;
    border: 1px solid #F5CBA7 !important;
}

/* ── Progress bar ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #E74C3C, #F1C40F) !important;
    border-radius: 8px !important;
}

/* ── Alerts ── */
.stSuccess { background: #EAFAF1 !important; border-left: 4px solid #27AE60 !important; border-radius: 10px !important; }
.stWarning { background: #FEF9E7 !important; border-left: 4px solid #F1C40F !important; border-radius: 10px !important; }
.stError   { background: #FDEDEC !important; border-left: 4px solid #E74C3C !important; border-radius: 10px !important; }

/* ── General text ── */
h1, h2, h3 { color: #7B241C !important; font-weight: 800 !important; }
h4, h5, p, label, span { color: #2C1810 !important; }
hr { border-color: #F5CBA7 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #FFF0E0; }
::-webkit-scrollbar-thumb { background: #E74C3C; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──────────────────────────────────────────────────
def format_rupiah(amount) -> str:
    return f"Rp {int(amount):,}".replace(",", ".")

def generate_order_number() -> str:
    now = datetime.now()
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{now.strftime('%Y%m%d')}-{suffix}"

def get_wib_now():
    """Ambil waktu sekarang dalam WIB (UTC+7)."""
    from datetime import timezone, timedelta
    wib = timezone(timedelta(hours=7))
    return datetime.now(wib)

def get_greeting() -> str:
    h = get_wib_now().hour
    if h < 11:   return "Selamat Pagi 🌅"
    elif h < 15: return "Selamat Siang ☀️"
    elif h < 18: return "Selamat Sore 🌤️"
    else:        return "Selamat Malam 🌙"

def get_datetime_str() -> str:
    """Format: Minggu, 10 Mei 2026 • 20:56 WIB"""
    HARI = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
    BULAN = ["","Januari","Februari","Maret","April","Mei","Juni",
             "Juli","Agustus","September","Oktober","November","Desember"]
    now = get_wib_now()
    hari   = HARI[now.weekday()]
    tgl    = now.day
    bln    = BULAN[now.month]
    thn    = now.year
    jam    = now.strftime("%H:%M")
    return f"{hari}, {tgl} {bln} {thn} • {jam} WIB"


# ── SUPABASE ─────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ══════════════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════════════
def show_login():
    st.markdown("""
    <div class="login-box">
        <div style="text-align:center;margin-bottom:24px">
            <span style="font-size:48px">🍗</span>
            <h2 style="color:#C0392B;margin:8px 0 4px;font-weight:800">Chick & Juice Faeyza</h2>
            <p style="color:#888;font-size:14px">Sistem Kasir Cloud</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin / kasir")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("🔐 Masuk", use_container_width=True)

            if submitted:
                user = USERS.get(username)
                if user and user["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username  = username
                    st.session_state.role      = user["role"]
                    st.rerun()
                else:
                    st.error("❌ Username atau password salah!")

        st.markdown("""
        <div style="text-align:center;margin-top:16px;color:#aaa;font-size:12px">
            <b>Admin:</b> username <code>admin</code> · password <code>faeyza</code><br>
            <b>Kasir:</b> username <code>kasir</code> · password <code>kasir123</code>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
def show_sidebar():
    role = st.session_state.role
    username = st.session_state.username

    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:16px 0 10px">
            <span style="font-size:40px">🍗</span>
            <h3 style="margin:6px 0 2px;color:#fff;font-weight:800;letter-spacing:0.5px">Chick & Juice</h3>
            <p style="font-size:12px;color:#F1C40F;margin:0;font-weight:700;letter-spacing:2px">FAEYZA</p>
        </div>
        <hr style="border-color:#F1C40F;opacity:0.4;margin:8px 0">
        <div style="text-align:center;margin-bottom:14px">
            <span class="badge-{'admin' if role=='admin' else 'kasir'}">
                {'👑 Admin' if role=='admin' else '🧑‍💼 Kasir'}
            </span>
            <p style="font-size:12px;color:rgba(255,255,255,0.85);margin:8px 0 0;font-weight:600">{username}</p>
        </div>
        """, unsafe_allow_html=True)

        menu_options = MENU_BY_ROLE[role]
        menu = st.radio("", menu_options, label_visibility="collapsed")

        st.markdown("<hr style='border-color:rgba(255,255,255,0.2);margin-top:auto'>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    return menu


# ══════════════════════════════════════════════════════════════
# DASHBOARD (admin only)
# ══════════════════════════════════════════════════════════════
def show_dashboard():
    supabase = get_supabase()
    now_str = get_datetime_str()
    st.markdown(f"## 🏠 {get_greeting()}, Admin!")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#fff 60%,#FFF8E1 100%);
    border-radius:12px;padding:10px 18px;display:inline-block;
    border-left:4px solid #F1C40F;margin-bottom:8px;
    box-shadow:0 2px 10px rgba(192,57,43,0.08)">
        <span style="color:#7B241C;font-weight:700;font-size:15px">📅 {now_str}</span>
    </div>
    """, unsafe_allow_html=True)

    today = date.today().isoformat()
    try:
        res = supabase.table("transaksi").select("total,created_at").execute()
        df_all = pd.DataFrame(res.data) if res.data else pd.DataFrame(columns=["total","created_at"])

        if not df_all.empty:
            df_all["created_at"] = pd.to_datetime(df_all["created_at"])
            df_all["tanggal"]    = df_all["created_at"].dt.date
            df_today = df_all[df_all["tanggal"] == date.today()]
        else:
            df_today = pd.DataFrame(columns=["total","tanggal"])

        omset_hari_ini = int(df_today["total"].sum()) if not df_today.empty else 0
        trx_hari_ini   = len(df_today)
        rata_rata      = int(df_today["total"].mean()) if not df_today.empty else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Omset Hari Ini", format_rupiah(omset_hari_ini))
        col2.metric("🧾 Transaksi",       trx_hari_ini)
        col3.metric("📊 Rata-rata",        format_rupiah(rata_rata))

        # Grafik 7 hari
        st.markdown("---")
        st.markdown("### 📈 Omset 7 Hari Terakhir")
        if not df_all.empty:
            last7  = [(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
            omset7 = [int(df_all[df_all["tanggal"]==d]["total"].sum()) for d in last7]
            label7 = [d.strftime("%d %b") for d in last7]
            df_chart = pd.DataFrame({"Tanggal": label7, "Omset (Rp)": omset7}).set_index("Tanggal")

            # Grafik pakai plotly supaya warna bisa disesuaikan
            import plotly.express as px
            fig = px.bar(
                df_chart.reset_index(),
                x="Tanggal", y="Omset (Rp)",
                color_discrete_sequence=["#C0392B"],
                template="plotly_white",
            )
            fig.update_layout(
                plot_bgcolor="#FFF8F0",
                paper_bgcolor="#FFF8F0",
                font_color="#1a1a1a",
                showlegend=False,
                margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(
                    gridcolor="#F5CBA7",
                    tickfont=dict(color="#1a1a1a", size=12),
                    title_font=dict(color="#1a1a1a"),
                ),
                xaxis=dict(
                    showgrid=False,
                    tickfont=dict(color="#1a1a1a", size=12),
                    title_font=dict(color="#1a1a1a"),
                ),
            )
            fig.update_traces(marker_line_width=0, marker_color="#C0392B")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data transaksi.")

        # Stok kritis — baca dari session state (bukan Supabase)
        st.markdown("---")
        st.markdown("### ⚠️ Stok Kritis")
        if "data_stok" not in st.session_state:
            # Init dulu kalau belum ada
            st.session_state.data_stok = {
                item["nama"]: {
                    "stok": item["stok"], "satuan": item["satuan"],
                    "minimum": item["minimum"], "kategori": item["kategori"]
                }
                for item in STOK_DEFAULT
            }

        data_stok = st.session_state.data_stok
        kritis_list = {k: v for k, v in data_stok.items() if v["stok"] <= v["minimum"]}

        if kritis_list:
            for nama, info in kritis_list.items():
                st.markdown(f"""
                <div style="background:#FDEDEC;border-left:4px solid #E74C3C;border-radius:10px;
                padding:10px 16px;margin-bottom:8px">
                    <span style="color:#C0392B;font-weight:700">🔴 {nama}</span>
                    <span style="color:#888;font-size:13px"> — stok: <b>{info['stok']} {info['satuan']}</b>
                    (min: {info['minimum']})</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#EAFAF1;border-left:4px solid #27AE60;border-radius:10px;padding:10px 16px">
                <span style="color:#1E8449;font-weight:700">✅ Semua stok aman.</span>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════
# KASIR
# ══════════════════════════════════════════════════════════════
MENU_AYAM = [
    {"nama": "Ayam Dada",       "harga": 9000,  "emoji": "🍗", "deskripsi": "Rendah lemak"},
    {"nama": "Ayam Paha Bawah", "harga": 9000,  "emoji": "🍗", "deskripsi": "Juicy & gurih"},
    {"nama": "Ayam Paha Atas",  "harga": 9000,  "emoji": "🍗", "deskripsi": "Daging tebal"},
    {"nama": "Ayam Sayap",      "harga": 9000,  "emoji": "🍗", "deskripsi": "Crispy & renyah"},
]

MENU_GEPREK = [
    {"nama": "Paha Bawah Geprek", "harga": 12000, "emoji": "🍗", "deskripsi": "Juicy & pedas"},
    {"nama": "Paha Atas Geprek",  "harga": 12000, "emoji": "🍗", "deskripsi": "Daging tebal"},
    {"nama": "Dada Geprek",       "harga": 12000, "emoji": "🍗", "deskripsi": "Rendah lemak"},
    {"nama": "Sayap Geprek",      "harga": 12000, "emoji": "🍗", "deskripsi": "Crispy & renyah"},
]

MENU_NASI = [
    {"nama": "Nasi", "harga": 5000, "emoji": "🍚", "deskripsi": "Nasi putih hangat"},
]

MENU_MINUMAN = [
    {"nama": "Ice Tea Solo", "harga": 5000, "emoji": "🧋", "deskripsi": "Teh manis dingin"},
]

def show_kasir():
    supabase = get_supabase()

    if "keranjang" not in st.session_state:
        st.session_state.keranjang = {}
    if "step" not in st.session_state:
        st.session_state.step = "menu"

    # ── STEP 1: MENU ──
    if st.session_state.step == "menu":
        st.markdown("## 🛒 Kasir — Pilih Menu")

        try:
            res  = supabase.table("menu").select("*").eq("tersedia", True).execute()
            menu_db = res.data if res.data else []
        except:
            menu_db = []

        tabs = st.tabs(["🍗 Ayam", "🌶️ Ayam Geprek", "🍚 Nasi", "🥤 Minuman"])

        def render_menu_items(items, prefix):
            cols = st.columns(3)
            for i, item in enumerate(items):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="card" style="text-align:center">
                        <div style="font-size:36px">{item['emoji']}</div>
                        <b style="font-size:14px;color:#2C1810">{item['nama']}</b><br>
                        <span style="color:#999;font-size:12px">{item['deskripsi']}</span><br>
                        <span style="color:#C0392B;font-weight:800;font-size:15px">{format_rupiah(item['harga'])}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    qty = st.number_input("Qty", min_value=0, max_value=99,
                        value=st.session_state.keranjang.get(item['nama'], {}).get("qty", 0),
                        key=f"{prefix}_{i}", label_visibility="collapsed")
                    if qty > 0:
                        st.session_state.keranjang[item['nama']] = {"qty": qty, "harga": item['harga']}
                    elif item['nama'] in st.session_state.keranjang:
                        del st.session_state.keranjang[item['nama']]

        with tabs[0]:
            render_menu_items(MENU_AYAM, "ayam")

        with tabs[1]:
            render_menu_items(MENU_GEPREK, "geprek")

        with tabs[2]:
            render_menu_items(MENU_NASI, "nasi")

        with tabs[3]:
            render_menu_items(MENU_MINUMAN, "minuman")

        # Ringkasan keranjang
        st.markdown("---")
        st.markdown("### 🧺 Keranjang")
        if st.session_state.keranjang:
            total_sebelum = 0
            for nama, d in st.session_state.keranjang.items():
                subtotal = d['qty'] * d['harga']
                total_sebelum += subtotal
                st.write(f"• **{nama}** × {d['qty']} = {format_rupiah(subtotal)}")

            # ── Hitung diskon paket ──
            nama_keranjang = list(st.session_state.keranjang.keys())
            punya_ayam = any(
                n in nama_keranjang for n in
                ["Ayam Dada","Ayam Paha Bawah","Ayam Paha Atas","Ayam Sayap"]
            )
            punya_geprek = any(
                n in nama_keranjang for n in
                ["Paha Bawah Geprek","Paha Atas Geprek","Dada Geprek","Sayap Geprek"]
            )
            punya_nasi = "Nasi" in nama_keranjang

            diskon = 0
            pesan_diskon = []
            if punya_ayam and punya_nasi:
                diskon += 2000
                pesan_diskon.append("🎉 Paket Ayam + Nasi")
            if punya_geprek and punya_nasi:
                diskon += 2000
                pesan_diskon.append("🎉 Paket Geprek + Nasi")

            if diskon > 0:
                st.markdown("---")
                for p in pesan_diskon:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#FFF8E1,#FFF3CD);border-radius:10px;
                    padding:10px 16px;border-left:4px solid #F1C40F;margin-bottom:6px">
                        <span style="color:#7B241C;font-weight:700">{p}</span>
                        <span style="color:#C0392B;font-weight:800;float:right">- Rp 2.000</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"<p style='color:#888;text-decoration:line-through;font-size:14px'>Subtotal: {format_rupiah(total_sebelum)}</p>", unsafe_allow_html=True)

            total = total_sebelum - diskon
            st.markdown(f"### 💰 Total: **{format_rupiah(total)}**" + (f" ~~{format_rupiah(total_sebelum)}~~" if diskon > 0 else ""))

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Kosongkan", use_container_width=True):
                    st.session_state.keranjang = {}
                    st.rerun()
            with col2:
                if st.button("💳 Lanjut Bayar →", use_container_width=True):
                    st.session_state.total_diskon = diskon
                    st.session_state.step = "bayar"
                    st.rerun()
        else:
            st.info("Belum ada item dipilih.")

    # ── STEP 2: BAYAR ──
    elif st.session_state.step == "bayar":
        st.markdown("## 💳 Pembayaran")

        keranjang = st.session_state.keranjang
        total_sebelum = sum(d['qty'] * d['harga'] for d in keranjang.values())
        diskon = st.session_state.get("total_diskon", 0)
        total  = total_sebelum - diskon

        for nama, d in keranjang.items():
            st.write(f"• {nama} × {d['qty']} = {format_rupiah(d['qty'] * d['harga'])}")

        if diskon > 0:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#FFF8E1,#FFF3CD);border-radius:10px;
            padding:10px 16px;border-left:4px solid #F1C40F;margin:8px 0">
                <span style="color:#7B241C;font-weight:700">🎉 Diskon Paket</span>
                <span style="color:#C0392B;font-weight:800;float:right">- {format_rupiah(diskon)}</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<p style='color:#888;font-size:13px'>Subtotal: <s>{format_rupiah(total_sebelum)}</s></p>", unsafe_allow_html=True)

        st.markdown(f"### 💰 Total Bayar: **{format_rupiah(total)}**")
        st.markdown("---")

        metode = st.radio("Metode Pembayaran", ["💵 Tunai", "📱 QRIS"], horizontal=True)

        if metode == "💵 Tunai":
            uang = st.number_input("Uang Diterima (Rp)", min_value=0, step=1000, value=total)
            kembalian = max(0, uang - total)
            st.info(f"💵 Kembalian: **{format_rupiah(kembalian)}**")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Kembali"):
                    st.session_state.step = "menu"
                    st.rerun()
            with col2:
                if uang >= total and st.button("✅ Konfirmasi Bayar", use_container_width=True):
                    _simpan_transaksi(supabase, keranjang, total, "Tunai", uang, kembalian)

        else:  # QRIS
            nomor_order = generate_order_number()
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=QRIS-{nomor_order}-{total}"
            st.markdown(f"""
            <div style="text-align:center;padding:28px;background:linear-gradient(135deg,#fff 60%,#FFF8E1 100%);border-radius:20px;border:2px dashed #E74C3C;box-shadow:0 6px 20px rgba(192,57,43,0.12)">
                <img src="{qr_url}" style="border-radius:12px;width:220px;border:3px solid #F1C40F">
                <p style="color:#C0392B;font-weight:800;font-size:20px;margin:14px 0 4px">{format_rupiah(total)}</p>
                <p style="color:#7B241C;font-size:13px;font-weight:600">Order: {nomor_order}</p>
                <p style="color:#888;font-size:12px">Scan QR ini dengan aplikasi e-wallet / mobile banking</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Kembali"):
                    st.session_state.step = "menu"
                    st.rerun()
            with col2:
                if st.button("✅ Pembayaran Diterima", use_container_width=True):
                    _simpan_transaksi(supabase, keranjang, total, "QRIS", total, 0)

    # ── STEP 3: SUKSES ──
    elif st.session_state.step == "sukses":
        st.success("🎉 Transaksi berhasil disimpan!")
        st.balloons()
        st.markdown(f"**Order:** `{st.session_state.get('last_order','')}`")
        st.markdown(f"**Total:** {format_rupiah(st.session_state.get('last_total', 0))}")
        if st.button("🛒 Transaksi Baru", use_container_width=True):
            st.session_state.keranjang = {}
            st.session_state.step = "menu"
            st.rerun()


def _simpan_transaksi(supabase, keranjang, total, metode, uang, kembalian):
    try:
        nomor = generate_order_number()
        res = supabase.table("transaksi").insert({
            "nomor_order": nomor, "total": total,
            "metode_bayar": metode, "uang_bayar": uang,
            "kembalian": kembalian, "status": "selesai"
        }).execute()
        trx_id = res.data[0]["id"]
        details = [{"transaksi_id": trx_id, "menu_id": None,
                    "nama_menu": nama, "harga": d["harga"],
                    "qty": d["qty"], "subtotal": d["qty"]*d["harga"]}
                   for nama, d in keranjang.items()]
        supabase.table("detail_transaksi").insert(details).execute()
        st.session_state.last_order = nomor
        st.session_state.last_total = total
        st.session_state.step = "sukses"
        st.rerun()
    except Exception as e:
        st.error(f"Gagal simpan: {e}")


# ══════════════════════════════════════════════════════════════
# DATA STOK DEFAULT
# ══════════════════════════════════════════════════════════════
STOK_DEFAULT = [
    {"nama": "Ayam Potong",    "satuan": "kg",   "stok": 20.0, "minimum": 5.0,  "kategori": "🍗 Bahan Utama"},
    {"nama": "Tepung Bumbu",   "satuan": "kg",   "stok": 10.0, "minimum": 3.0,  "kategori": "🍗 Bahan Utama"},
    {"nama": "Minyak Goreng",  "satuan": "liter","stok": 15.0, "minimum": 3.0,  "kategori": "🍗 Bahan Utama"},
    {"nama": "Cabai Merah",    "satuan": "kg",   "stok": 5.0,  "minimum": 1.0,  "kategori": "🍗 Bahan Utama"},
    {"nama": "Bawang Putih",   "satuan": "kg",   "stok": 3.0,  "minimum": 0.5,  "kategori": "🍗 Bahan Utama"},
    {"nama": "Garam",          "satuan": "kg",   "stok": 2.0,  "minimum": 0.5,  "kategori": "🍗 Bahan Utama"},
    {"nama": "Beras",          "satuan": "kg",   "stok": 30.0, "minimum": 10.0, "kategori": "🍗 Bahan Utama"},
    {"nama": "Gula Pasir",     "satuan": "kg",   "stok": 5.0,  "minimum": 1.0,  "kategori": "🍗 Bahan Utama"},
    {"nama": "Merica",         "satuan": "kg",   "stok": 0.5,  "minimum": 0.1,  "kategori": "🍗 Bahan Utama"},
    {"nama": "Tepung Tapioka", "satuan": "kg",   "stok": 3.0,  "minimum": 1.0,  "kategori": "🍗 Bahan Utama"},
    {"nama": "Penyedap Rasa",  "satuan": "pcs",  "stok": 20.0, "minimum": 5.0,  "kategori": "🍗 Bahan Utama"},
    {"nama": "Kecap Manis",    "satuan": "botol","stok": 6.0,  "minimum": 2.0,  "kategori": "🧂 Bumbu"},
    {"nama": "Saos Sambal",    "satuan": "botol","stok": 6.0,  "minimum": 2.0,  "kategori": "🧂 Bumbu"},
    {"nama": "Bawang Merah",   "satuan": "kg",   "stok": 2.0,  "minimum": 0.5,  "kategori": "🧂 Bumbu"},
    {"nama": "Kemiri",         "satuan": "kg",   "stok": 0.5,  "minimum": 0.1,  "kategori": "🧂 Bumbu"},
    {"nama": "Teh Celup",      "satuan": "kotak","stok": 10.0, "minimum": 2.0,  "kategori": "🥤 Minuman"},
    {"nama": "Air Galon",      "satuan": "galon","stok": 5.0,  "minimum": 2.0,  "kategori": "🥤 Minuman"},
    {"nama": "Es Batu",        "satuan": "kg",   "stok": 10.0, "minimum": 3.0,  "kategori": "🥤 Minuman"},
    {"nama": "Styrofoam Box",  "satuan": "pcs",  "stok": 200.0,"minimum": 50.0, "kategori": "📦 Kemasan"},
    {"nama": "Cup Minuman",    "satuan": "pcs",  "stok": 150.0,"minimum": 50.0, "kategori": "📦 Kemasan"},
    {"nama": "Plastik Kresek", "satuan": "pack", "stok": 20.0, "minimum": 5.0,  "kategori": "📦 Kemasan"},
    {"nama": "Sedotan",        "satuan": "pack", "stok": 15.0, "minimum": 3.0,  "kategori": "📦 Kemasan"},
    {"nama": "Tissue",         "satuan": "pack", "stok": 20.0, "minimum": 5.0,  "kategori": "📦 Kemasan"},
    {"nama": "Kantong Nasi",   "satuan": "pack", "stok": 10.0, "minimum": 3.0,  "kategori": "📦 Kemasan"},
]

# ══════════════════════════════════════════════════════════════
# STOK
# ══════════════════════════════════════════════════════════════
def show_stok():
    st.markdown("## 📦 Manajemen Stok")

    if "data_stok" not in st.session_state:
        st.session_state.data_stok = {
            item["nama"]: {
                "stok": item["stok"], "satuan": item["satuan"],
                "minimum": item["minimum"], "kategori": item["kategori"]
            }
            for item in STOK_DEFAULT
        }

    data = st.session_state.data_stok
    kategori_list = ["🍗 Bahan Utama", "🧂 Bumbu", "🥤 Minuman", "📦 Kemasan"]

    # Ringkasan
    total_kritis = sum(1 for v in data.values() if v["stok"] <= v["minimum"])
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Item", len(data))
    col2.metric("⚠️ Stok Kritis", total_kritis)
    col3.metric("✅ Stok Aman", len(data) - total_kritis)
    st.markdown("---")

    # Tampilkan per kategori
    for kat in kategori_list:
        items_kat = {k: v for k, v in data.items() if v["kategori"] == kat}
        if not items_kat:
            continue
        st.markdown(f"### {kat}")
        for nama, info in items_kat.items():
            stok_now = info["stok"]
            minimum  = info["minimum"]
            satuan   = info["satuan"]
            persen   = min(100, int(stok_now / max(minimum, 0.01) * 100))
            if stok_now <= minimum:
                status = "🔴"
            elif stok_now <= minimum * 1.5:
                status = "🟡"
            else:
                status = "🟢"
            c1, c2, c3, c4 = st.columns([3, 1.2, 2.5, 1.5])
            c1.markdown(f"{status} **{nama}**")
            c2.markdown(f"`{stok_now} {satuan}`")
            c3.progress(min(persen, 100))
            if stok_now <= minimum:
                c4.markdown("<span style='color:#E74C3C;font-size:12px;font-weight:700'>⚠️ Kritis!</span>", unsafe_allow_html=True)
            else:
                c4.markdown(f"<span style='color:#888;font-size:12px'>min: {minimum}</span>", unsafe_allow_html=True)
        st.markdown("")

    st.markdown("---")

    # Update stok
    st.markdown("### ✏️ Update Stok")
    c1, c2 = st.columns(2)
    with c1:
        pilih = st.selectbox("Pilih bahan", list(data.keys()))
    with c2:
        info_pilih = data[pilih]
        stok_baru = st.number_input(
            f"Stok baru ({info_pilih['satuan']})",
            value=float(info_pilih["stok"]), min_value=0.0, step=0.5
        )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Simpan Perubahan", use_container_width=True):
            st.session_state.data_stok[pilih]["stok"] = stok_baru
            st.success(f"✅ Stok **{pilih}** → {stok_baru} {info_pilih['satuan']}")
            st.rerun()
    with c2:
        if st.button("🔄 Reset ke Default", use_container_width=True):
            del st.session_state.data_stok
            st.info("Stok direset ke nilai awal.")
            st.rerun()

    # Tambah bahan baru
    st.markdown("---")
    st.markdown("### ➕ Tambah Bahan Baru")
    with st.expander("Klik untuk tambah bahan baru"):
        c1, c2, c3 = st.columns(3)
        nama_baru   = c1.text_input("Nama bahan")
        satuan_baru = c2.selectbox("Satuan", ["kg","liter","pcs","pack","kotak","botol","galon","butir"])
        kat_baru    = c3.selectbox("Kategori", ["🍗 Bahan Utama","🧂 Bumbu","🥤 Minuman","📦 Kemasan"])
        c4, c5 = st.columns(2)
        stok_awal = c4.number_input("Stok awal", min_value=0.0, step=1.0)
        min_stok  = c5.number_input("Stok minimum", min_value=0.0, step=1.0)
        if st.button("➕ Tambahkan Bahan", use_container_width=True):
            if nama_baru.strip():
                st.session_state.data_stok[nama_baru.strip()] = {
                    "stok": stok_awal, "satuan": satuan_baru,
                    "minimum": min_stok, "kategori": kat_baru
                }
                st.success(f"✅ **{nama_baru}** berhasil ditambahkan!")
                st.rerun()
            else:
                st.warning("Nama bahan tidak boleh kosong.")

# ══════════════════════════════════════════════════════════════
# LAPORAN (admin only)
# ══════════════════════════════════════════════════════════════
def show_laporan():
    supabase = get_supabase()
    st.markdown("## 📊 Laporan Penjualan")

    col1, col2 = st.columns(2)
    with col1:
        tgl_awal = st.date_input("Dari tanggal", value=date.today() - timedelta(days=7))
    with col2:
        tgl_akhir = st.date_input("Sampai tanggal", value=date.today())

    try:
        res = supabase.table("transaksi").select("*").execute()
        if not res.data:
            st.info("Belum ada data transaksi.")
            return
        df = pd.DataFrame(res.data)
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["tanggal"]    = df["created_at"].dt.date
        df_filter = df[(df["tanggal"] >= tgl_awal) & (df["tanggal"] <= tgl_akhir)]

        if df_filter.empty:
            st.info("Tidak ada transaksi di rentang tanggal tersebut.")
            return

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Omset",   format_rupiah(df_filter["total"].sum()))
        col2.metric("🧾 Transaksi",      len(df_filter))
        col3.metric("📊 Rata-rata/hari", format_rupiah(df_filter["total"].mean()))

        st.markdown("---")
        st.markdown("### 📈 Grafik Omset Harian")
        grafik = df_filter.groupby("tanggal")["total"].sum().reset_index()
        grafik["tanggal"] = grafik["tanggal"].astype(str)

        import plotly.express as px
        fig = px.bar(
            grafik, x="tanggal", y="total",
            labels={"tanggal": "Tanggal", "total": "Omset (Rp)"},
            color_discrete_sequence=["#C0392B"],
            template="plotly_white",
        )
        fig.update_layout(
            plot_bgcolor="#FFF8F0",
            paper_bgcolor="#FFF8F0",
            font_color="#1a1a1a",
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(gridcolor="#F5CBA7", tickfont=dict(color="#1a1a1a", size=12)),
            xaxis=dict(showgrid=False, tickfont=dict(color="#1a1a1a", size=12)),
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📄 Riwayat Transaksi")
        tampil = df_filter[["nomor_order","total","metode_bayar","status","tanggal"]].copy()
        tampil["total"] = tampil["total"].apply(format_rupiah)
        st.dataframe(tampil, use_container_width=True)

        st.download_button("⬇️ Export CSV", df_filter.to_csv(index=False).encode("utf-8"),
                           "laporan.csv", "text/csv", use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    # Init session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        show_login()
        return

    menu = show_sidebar()
    role = st.session_state.role

    # Akses kontrol
    if menu == "🏠 Dashboard":
        if role == "admin":
            show_dashboard()
        else:
            st.warning("⛔ Akses ditolak. Menu ini hanya untuk Admin.")

    elif menu == "🛒 Kasir":
        show_kasir()

    elif menu == "📦 Stok":
        show_stok()

    elif menu == "📊 Laporan":
        if role == "admin":
            show_laporan()
        else:
            st.warning("⛔ Akses ditolak. Menu ini hanya untuk Admin.")


if __name__ == "__main__":
    main()
