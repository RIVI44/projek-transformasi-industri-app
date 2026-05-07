import streamlit as st

st.set_page_config(
    page_title="Ayam Geprek AKA",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main { background-color: #0f0f0f; }

    .stApp {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1200 100%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1c1300 0%, #0f0a00 100%);
        border-right: 1px solid #ff6b00;
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: #fff !important;
        font-weight: 600;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #1e1200;
        border: 1px solid #ff6b0040;
        border-radius: 12px;
        padding: 16px;
    }

    [data-testid="metric-container"] label {
        color: #ff9a3c !important;
    }

    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #fff !important;
        font-weight: 800;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b00, #ff9a00);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        font-family: 'Plus Jakarta Sans', sans-serif;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff8c00, #ffb300);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px #ff6b0060;
    }

    /* Dataframe */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Input fields */
    .stSelectbox > div, .stNumberInput > div, .stTextInput > div {
        background: #1e1200 !important;
        border-color: #ff6b0040 !important;
        color: white !important;
    }

    /* Headers */
    h1, h2, h3 { color: #ff9a3c !important; }

    .brand-header {
        text-align: center;
        padding: 20px 0 10px;
    }
    .brand-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #ff9a3c;
        letter-spacing: -0.5px;
    }
    .brand-sub {
        font-size: 0.75rem;
        color: #ff6b0080;
        margin-top: 2px;
    }

    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-success { background: #00c85120; color: #00c851; border: 1px solid #00c85140; }
    .badge-warning { background: #ffa00020; color: #ffa000; border: 1px solid #ffa00040; }
    .badge-danger  { background: #ff3d0020; color: #ff3d00; border: 1px solid #ff3d0040; }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div class="brand-header">
        <div style="font-size:2.5rem">🍗</div>
        <div class="brand-title">Ayam Geprek POS</div>
        <div class="brand-sub">Cloud Point of Sale</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    menu = st.radio(
        "Navigasi",
        ["🏠 Dashboard", "🛒 Kasir", "📦 Stok", "📊 Laporan"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(
        "<div style='color:#ff6b0060; font-size:0.7rem; text-align:center'>v1.0 · Supabase Cloud</div>",
        unsafe_allow_html=True
    )

# Route views
if menu == "🏠 Dashboard":
    from views.dashboard import show
    show()
elif menu == "🛒 Kasir":
    from views.kasir import show
    show()
elif menu == "📦 Stok":
    from views.stok import show
    show()
elif menu == "📊 Laporan":
    from views.laporan import show
    show()

