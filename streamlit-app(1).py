import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from supabase import create_client, Client
import random
import string

# ─────────────────────────────────────────────
#  CONFIG & CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="POS Ayam Geprek",
    page_icon="🍗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0f0f 0%, #1a1200 100%); }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1c1300 0%, #0f0a00 100%);
        border-right: 1px solid #ff6b00;
    }
    section[data-testid="stSidebar"] .stRadio label { color: #fff !important; font-weight: 600; }
    [data-testid="metric-container"] {
        background: #1e1200;
        border: 1px solid #ff6b0040;
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="metric-container"] label { color: #ff9a3c !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #fff !important; font-weight: 800; }
    .stButton > button {
        background: linear-gradient(135deg, #ff6b00, #ff9a00);
        color: white; border: none; border-radius: 10px;
        font-weight: 700; transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff8c00, #ffb300);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px #ff6b0060;
    }
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    h1, h2, h3 { color: #ff9a3c !important; }
    .brand-title { font-size: 1.4rem; font-weight: 800; color: #ff9a3c; }
    .brand-sub { font-size: 0.75rem; color: #ff6b0080; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  UTILS
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def format_rupiah(amount) -> str:
    return f"Rp {int(amount):,}".replace(",", ".")

def generate_order_number() -> str:
    now = datetime.now()
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{now.strftime('%Y%m%d')}-{suffix}"

def get_greeting() -> str:
    h = datetime.now().hour
    if h < 11: return "Selamat Pagi"
    elif h < 15: return "Selamat Siang"
    elif h < 18: return "Selamat Sore"
    else: return "Selamat Malam"


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px'>
        <div style='font-size:2.5rem'>🍗</div>
        <div class='brand-title'>Ayam Geprek POS</div>
        <div class='brand-sub'>Cloud Point of Sale</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("Navigasi", ["🏠 Dashboard", "🛒 Kasir", "📦 Stok", "📊 Laporan"],
                    label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<div style='color:#ff6b0060;font-size:0.7rem;text-align:center'>v1.0 · Supabase Cloud</div>",
                unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HALAMAN: DASHBOARD
# ─────────────────────────────────────────────
if menu == "🏠 Dashboard":
    supabase = get_supabase()
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    st.markdown("## 🏠 Dashboard")
    st.markdown(f"**{get_greeting()}, Selamat datang di POS Ayam Geprek!** · {date.today().strftime('%A, %d %B %Y')}")
    st.markdown("---")

    try:
        res_today = supabase.table("transaksi").select("total") \
            .gte("created_at", f"{today}T00:00:00").lte("created_at", f"{today}T23:59:59").execute()
        omset_today = sum(r["total"] for r in res_today.data)

        res_yesterday = supabase.table("transaksi").select("total") \
            .gte("created_at", f"{yesterday}T00:00:00").lte("created_at", f"{yesterday}T23:59:59").execute()
        omset_yesterday = sum(r["total"] for r in res_yesterday.data)

        delta_omset = omset_today - omset_yesterday
        total_trx = len(res_today.data)

        res_detail = supabase.table("detail_transaksi").select("qty, transaksi(created_at)").execute()
        item_today = sum(r["qty"] for r in res_detail.data
                         if r.get("transaksi") and r["transaksi"]["created_at"].startswith(today))

        res_stok = supabase.table("stok").select("*").execute()
        stok_kritis = sum(1 for s in res_stok.data if s["stok_saat_ini"] <= s["stok_minimum"])

    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        omset_today = omset_yesterday = total_trx = item_today = stok_kritis = delta_omset = 0
        res_stok = type('obj', (object,), {'data': []})()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Omset Hari Ini", format_rupiah(omset_today),
                delta=format_rupiah(delta_omset) if delta_omset != 0 else None)
    col2.metric("🧾 Transaksi", f"{total_trx} order")
    col3.metric("📈 Rata-rata/Order", format_rupiah(omset_today // total_trx if total_trx > 0 else 0))
    col4.metric("⚠️ Stok Kritis", f"{stok_kritis} bahan",
                delta=f"-{stok_kritis} perlu restok" if stok_kritis > 0 else None, delta_color="inverse")

    st.markdown("---")
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 📈 Omset 7 Hari Terakhir")
        try:
            dates = [(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
            omset_list = []
            for d in dates:
                d_str = d.isoformat()
                res = supabase.table("transaksi").select("total") \
                    .gte("created_at", f"{d_str}T00:00:00").lte("created_at", f"{d_str}T23:59:59").execute()
                omset_list.append(sum(r["total"] for r in res.data))
            df_chart = pd.DataFrame({"Tanggal": [d.strftime("%d/%m") for d in dates],
                                     "Omset (Rp)": omset_list}).set_index("Tanggal")
            st.bar_chart(df_chart, color="#ff6b00")
        except:
            st.info("Belum ada data transaksi untuk grafik.")

    with col_right:
        st.markdown("### ⚠️ Stok Hampir Habis")
        try:
            kritis = [s for s in res_stok.data if s["stok_saat_ini"] <= s["stok_minimum"]]
            if kritis:
                df_k = pd.DataFrame(kritis)[["nama_bahan", "stok_saat_ini", "satuan", "stok_minimum"]]
                df_k.columns = ["Bahan", "Stok", "Satuan", "Min."]
                st.dataframe(df_k, use_container_width=True, hide_index=True)
            else:
                st.success("✅ Semua stok aman!")
        except:
            st.info("Tidak ada data stok.")

    st.markdown("### 🧾 Transaksi Terbaru Hari Ini")
    try:
        res_trx = supabase.table("transaksi").select("*") \
            .gte("created_at", f"{today}T00:00:00").order("created_at", desc=True).limit(10).execute()
        if res_trx.data:
            df_trx = pd.DataFrame(res_trx.data)
            df_trx["total"] = df_trx["total"].apply(format_rupiah)
            df_trx["created_at"] = pd.to_datetime(df_trx["created_at"]).dt.strftime("%H:%M")
            df_trx = df_trx[["nomor_order", "total", "metode_bayar", "status", "created_at"]]
            df_trx.columns = ["No. Order", "Total", "Pembayaran", "Status", "Jam"]
            st.dataframe(df_trx, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada transaksi hari ini.")
    except Exception as e:
        st.error(f"Error: {e}")


# ─────────────────────────────────────────────
#  HALAMAN: KASIR
# ─────────────────────────────────────────────
elif menu == "🛒 Kasir":
    supabase = get_supabase()

    st.markdown("## 🛒 Kasir")
    st.markdown("Pilih menu, atur quantity, lalu proses pembayaran.")
    st.markdown("---")

    if "keranjang" not in st.session_state:
        st.session_state.keranjang = []

    try:
        res_menu = supabase.table("menu").select("*").eq("tersedia", True).order("kategori").execute()
        menu_data = res_menu.data
    except Exception as e:
        st.error(f"Gagal memuat menu: {e}")
        st.stop()

    col_menu, col_cart = st.columns([3, 2])

    with col_menu:
        st.markdown("### 🍽️ Daftar Menu")
        kategori_list = sorted(set(m["kategori"] for m in menu_data))
        tab_list = st.tabs(kategori_list)

        for tab, kat in zip(tab_list, kategori_list):
            with tab:
                items = [m for m in menu_data if m["kategori"] == kat]
                cols = st.columns(2)
                for i, item in enumerate(items):
                    with cols[i % 2]:
                        with st.container(border=True):
                            st.markdown(f"**{item['nama']}**")
                            st.markdown(f"<span style='color:#ff9a3c;font-weight:700'>{format_rupiah(item['harga'])}</span>",
                                        unsafe_allow_html=True)
                            qty = st.number_input("Qty", min_value=0, max_value=50, value=0,
                                                  key=f"qty_{item['id']}", label_visibility="collapsed")
                            if st.button("➕ Tambah", key=f"add_{item['id']}", use_container_width=True):
                                if qty > 0:
                                    found = False
                                    for k in st.session_state.keranjang:
                                        if k["menu_id"] == item["id"]:
                                            k["qty"] += qty
                                            k["subtotal"] = k["qty"] * k["harga"]
                                            found = True
                                            break
                                    if not found:
                                        st.session_state.keranjang.append({
                                            "menu_id": item["id"], "nama": item["nama"],
                                            "harga": item["harga"], "qty": qty,
                                            "subtotal": item["harga"] * qty
                                        })
                                    st.success(f"✅ {item['nama']} x{qty} ditambahkan!")
                                    st.rerun()
                                else:
                                    st.warning("Qty harus > 0")

    with col_cart:
        st.markdown("### 🧺 Keranjang")
        if not st.session_state.keranjang:
            st.info("Keranjang kosong. Pilih menu di sebelah kiri.")
        else:
            for idx, item in enumerate(st.session_state.keranjang):
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.markdown(f"**{item['nama']}**")
                        st.caption(f"{format_rupiah(item['harga'])} × {item['qty']}")
                    with c2:
                        st.markdown(f"<div style='color:#ff9a3c;font-weight:700;padding-top:10px'>"
                                    f"{format_rupiah(item['subtotal'])}</div>", unsafe_allow_html=True)
                    with c3:
                        if st.button("🗑️", key=f"del_{idx}"):
                            st.session_state.keranjang.pop(idx)
                            st.rerun()

            st.markdown("---")
            total = sum(i["subtotal"] for i in st.session_state.keranjang)
            st.markdown(f"### Total: <span style='color:#ff9a3c'>{format_rupiah(total)}</span>",
                        unsafe_allow_html=True)

            st.markdown("#### 💳 Pembayaran")
            metode = st.selectbox("Metode Bayar", ["Tunai", "QRIS", "Transfer Bank", "Kartu Debit"])

            uang_bayar = 0
            kembalian = 0
            if metode == "Tunai":
                uang_bayar = st.number_input("Uang Bayar (Rp)", min_value=0, step=1000, value=total)
                kembalian = max(0, uang_bayar - total)
                if kembalian > 0:
                    st.success(f"💵 Kembalian: **{format_rupiah(kembalian)}**")
                elif uang_bayar < total:
                    st.error(f"❌ Uang kurang {format_rupiah(total - uang_bayar)}")

            col_bayar, col_reset = st.columns(2)
            with col_bayar:
                bayar_ok = metode != "Tunai" or uang_bayar >= total
                if st.button("✅ Bayar Sekarang", type="primary", use_container_width=True, disabled=not bayar_ok):
                    try:
                        nomor = generate_order_number()
                        res = supabase.table("transaksi").insert({
                            "nomor_order": nomor, "total": total, "metode_bayar": metode,
                            "uang_bayar": uang_bayar, "kembalian": kembalian, "status": "selesai"
                        }).execute()
                        trx_id = res.data[0]["id"]
                        details = [{
                            "transaksi_id": trx_id, "menu_id": item["menu_id"],
                            "nama_menu": item["nama"], "harga": item["harga"],
                            "qty": item["qty"], "subtotal": item["subtotal"]
                        } for item in st.session_state.keranjang]
                        supabase.table("detail_transaksi").insert(details).execute()
                        st.session_state.keranjang = []
                        st.success(f"🎉 Transaksi **{nomor}** berhasil! Total: {format_rupiah(total)}")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan transaksi: {e}")
            with col_reset:
                if st.button("🗑️ Kosongkan", use_container_width=True):
                    st.session_state.keranjang = []
                    st.rerun()


# ─────────────────────────────────────────────
#  HALAMAN: STOK
# ─────────────────────────────────────────────
elif menu == "📦 Stok":
    supabase = get_supabase()

    st.markdown("## 📦 Manajemen Stok")
    st.markdown("Pantau dan update stok bahan baku.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📋 Stok Bahan Baku", "🍽️ Kelola Menu", "➕ Tambah Bahan"])

    with tab1:
        try:
            res = supabase.table("stok").select("*").order("nama_bahan").execute()
            stok_data = res.data
        except Exception as e:
            st.error(f"Gagal memuat stok: {e}")
            st.stop()

        if not stok_data:
            st.info("Belum ada data stok.")
        else:
            kritis = [s for s in stok_data if s["stok_saat_ini"] <= s["stok_minimum"]]
            aman = [s for s in stok_data if s["stok_saat_ini"] > s["stok_minimum"]]
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Bahan", len(stok_data))
            c2.metric("✅ Stok Aman", len(aman))
            c3.metric("⚠️ Stok Kritis", len(kritis),
                      delta=f"-{len(kritis)}" if kritis else None, delta_color="inverse")
            st.markdown("---")

            df = pd.DataFrame(stok_data)
            df["status"] = df.apply(lambda r: "🔴 Habis" if r["stok_saat_ini"] <= 0
                                    else ("🟡 Hampir Habis" if r["stok_saat_ini"] <= r["stok_minimum"]
                                          else "🟢 Aman"), axis=1)
            df_show = df[["nama_bahan", "stok_saat_ini", "satuan", "stok_minimum", "status"]].copy()
            df_show.columns = ["Nama Bahan", "Stok Saat Ini", "Satuan", "Stok Minimum", "Status"]
            st.dataframe(df_show, use_container_width=True, hide_index=True)

            st.markdown("### ✏️ Update Stok")
            bahan_options = {s["nama_bahan"]: s for s in stok_data}
            selected = st.selectbox("Pilih Bahan", list(bahan_options.keys()))
            if selected:
                item = bahan_options[selected]
                col_a, col_b = st.columns(2)
                with col_a:
                    st.info(f"Stok saat ini: **{item['stok_saat_ini']} {item['satuan']}**")
                with col_b:
                    aksi = st.radio("Aksi", ["Tambah Stok", "Set Stok Baru"], horizontal=True)
                jumlah = st.number_input(f"Jumlah ({item['satuan']})", min_value=0.0, step=0.5, value=1.0)
                if st.button("💾 Simpan Perubahan", type="primary"):
                    try:
                        stok_baru = item["stok_saat_ini"] + jumlah if aksi == "Tambah Stok" else jumlah
                        supabase.table("stok").update({"stok_saat_ini": stok_baru}) \
                            .eq("id", item["id"]).execute()
                        st.success(f"✅ Stok **{selected}** diperbarui: {stok_baru} {item['satuan']}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal update: {e}")

    with tab2:
        try:
            res_menu = supabase.table("menu").select("*").order("kategori").execute()
            menu_data = res_menu.data
        except Exception as e:
            st.error(f"Gagal memuat menu: {e}")
            st.stop()

        st.markdown("### 📋 Daftar Menu")
        df_menu = pd.DataFrame(menu_data)
        if not df_menu.empty:
            df_menu["harga_fmt"] = df_menu["harga"].apply(format_rupiah)
            df_menu["tersedia"] = df_menu["tersedia"].map({True: "✅ Aktif", False: "❌ Nonaktif"})
            st.dataframe(df_menu[["nama", "kategori", "harga_fmt", "tersedia"]],
                         column_config={"nama": "Nama Menu", "kategori": "Kategori",
                                        "harga_fmt": "Harga", "tersedia": "Status"},
                         use_container_width=True, hide_index=True)

        st.markdown("### ➕ Tambah Menu Baru")
        col1, col2 = st.columns(2)
        with col1:
            nama_menu = st.text_input("Nama Menu")
            harga_menu = st.number_input("Harga (Rp)", min_value=0, step=500)
        with col2:
            kat_menu = st.selectbox("Kategori", ["Ayam", "Nasi", "Minuman", "Lauk", "Lainnya"])
            tersedia = st.checkbox("Tersedia / Aktif", value=True)
        if st.button("💾 Simpan Menu", type="primary"):
            if nama_menu and harga_menu > 0:
                try:
                    supabase.table("menu").insert({"nama": nama_menu, "kategori": kat_menu,
                                                   "harga": harga_menu, "tersedia": tersedia}).execute()
                    st.success(f"✅ Menu **{nama_menu}** berhasil ditambahkan!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal: {e}")
            else:
                st.warning("Nama menu dan harga harus diisi.")

    with tab3:
        st.markdown("### ➕ Tambah Bahan Baru")
        col1, col2 = st.columns(2)
        with col1:
            nama_bahan = st.text_input("Nama Bahan")
            satuan = st.selectbox("Satuan", ["kg", "gram", "liter", "ml", "pcs", "butir", "ikat", "bungkus"])
        with col2:
            stok_awal = st.number_input("Stok Awal", min_value=0.0, step=0.5)
            stok_min = st.number_input("Stok Minimum (alert)", min_value=0.0, step=0.5)
        if st.button("💾 Tambah Bahan", type="primary"):
            if nama_bahan:
                try:
                    supabase.table("stok").insert({"nama_bahan": nama_bahan, "satuan": satuan,
                                                   "stok_saat_ini": stok_awal, "stok_minimum": stok_min}).execute()
                    st.success(f"✅ Bahan **{nama_bahan}** berhasil ditambahkan!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal: {e}")
            else:
                st.warning("Nama bahan harus diisi.")


# ─────────────────────────────────────────────
#  HALAMAN: LAPORAN
# ─────────────────────────────────────────────
elif menu == "📊 Laporan":
    supabase = get_supabase()

    st.markdown("## 📊 Laporan Penjualan")
    st.markdown("Analisis real-time omset dan performa menu.")
    st.markdown("---")

    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        tgl_awal = st.date_input("Dari Tanggal", value=date.today() - timedelta(days=7))
    with col_f2:
        tgl_akhir = st.date_input("Sampai Tanggal", value=date.today())
    with col_f3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        st.button("🔄 Refresh", use_container_width=True)

    if tgl_awal > tgl_akhir:
        st.error("Tanggal awal tidak boleh lebih besar dari tanggal akhir.")
        st.stop()

    try:
        res_trx = supabase.table("transaksi").select("*") \
            .gte("created_at", f"{tgl_awal}T00:00:00") \
            .lte("created_at", f"{tgl_akhir}T23:59:59") \
            .order("created_at", desc=True).execute()
        trx_list = res_trx.data

        res_detail = supabase.table("detail_transaksi").select("*, transaksi(created_at)").execute()
        detail_list = [d for d in res_detail.data
                       if d.get("transaksi") and
                       tgl_awal.isoformat() <= d["transaksi"]["created_at"][:10] <= tgl_akhir.isoformat()]
    except Exception as e:
        st.error(f"Gagal memuat laporan: {e}")
        st.stop()

    if not trx_list:
        st.info("Tidak ada transaksi pada periode yang dipilih.")
        st.stop()

    total_omset = sum(t["total"] for t in trx_list)
    total_trx = len(trx_list)
    total_item = sum(d["qty"] for d in detail_list)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Omset", format_rupiah(total_omset))
    c2.metric("🧾 Jumlah Transaksi", total_trx)
    c3.metric("📈 Rata-rata/Transaksi", format_rupiah(total_omset // total_trx if total_trx > 0 else 0))
    c4.metric("🍗 Item Terjual", total_item)

    st.markdown("---")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown("### 📈 Omset per Hari")
        df_trx = pd.DataFrame(trx_list)
        df_trx["tanggal"] = pd.to_datetime(df_trx["created_at"]).dt.date
        omset_harian = df_trx.groupby("tanggal")["total"].sum().reset_index()
        omset_harian.columns = ["Tanggal", "Omset (Rp)"]
        st.bar_chart(omset_harian.set_index("Tanggal"), color="#ff6b00")

    with col_r:
        st.markdown("### 💳 Metode Pembayaran")
        metode_count = df_trx["metode_bayar"].value_counts().reset_index()
        metode_count.columns = ["Metode", "Jumlah"]
        st.dataframe(metode_count, use_container_width=True, hide_index=True)

        st.markdown("### ⏰ Jam Tersibuk")
        df_trx["jam"] = pd.to_datetime(df_trx["created_at"]).dt.hour
        jam_count = df_trx.groupby("jam").size().reset_index(name="Transaksi")
        if not jam_count.empty:
            peak = jam_count.loc[jam_count["Transaksi"].idxmax()]
            st.info(f"🔥 Jam paling ramai: **{int(peak['jam']):02d}:00** ({peak['Transaksi']} transaksi)")

    st.markdown("---")
    st.markdown("### 🏆 Menu Terlaris")
    if detail_list:
        df_detail = pd.DataFrame(detail_list)
        menu_laris = df_detail.groupby("nama_menu").agg(
            Total_Qty=("qty", "sum"), Total_Pendapatan=("subtotal", "sum")
        ).sort_values("Total_Qty", ascending=False).reset_index()
        menu_laris["Total_Pendapatan"] = menu_laris["Total_Pendapatan"].apply(format_rupiah)
        menu_laris.columns = ["Nama Menu", "Qty Terjual", "Total Pendapatan"]

        col_rank, col_chart = st.columns([2, 3])
        with col_rank:
            st.dataframe(menu_laris, use_container_width=True, hide_index=True)
        with col_chart:
            top5 = df_detail.groupby("nama_menu")["qty"].sum().nlargest(5)
            st.bar_chart(top5, color="#ff9a00")

    st.markdown("---")
    st.markdown("### 🧾 Riwayat Transaksi")
    df_show = df_trx[["nomor_order", "total", "metode_bayar", "status", "created_at"]].copy()
    df_show["total"] = df_show["total"].apply(format_rupiah)
    df_show["created_at"] = pd.to_datetime(df_show["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
    df_show.columns = ["No. Order", "Total", "Pembayaran", "Status", "Waktu"]
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    csv = df_show.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv,
                       file_name=f"laporan_{tgl_awal}_{tgl_akhir}.csv", mime="text/csv")
