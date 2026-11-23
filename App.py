import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from web3 import Web3

# =========================================================
# 1. KONFIGURASI HALAMAN & STYLES
# =========================================================

st.set_page_config(
    page_title="LandRegistryChain - Portal Pertanahan Digital",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .header-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .header-title { font-size: 28px; font-weight: 700; margin: 0; color: #ffffff; }
    .header-subtitle { font-size: 14px; color: #e0e6ed; margin-top: 5px; }
    .cert-card {
        background-color: #ffffff;
        border: 2px solid #dfb15b;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    }
    .cert-header {
        border-bottom: 2px dashed #dfb15b;
        padding-bottom: 12px;
        margin-bottom: 16px;
        text-align: center;
    }
    .cert-title { color: #8b6b23; font-weight: 800; letter-spacing: 1px; margin: 0; }
    .badge-active {
        background-color: #28a745; color: white; padding: 4px 12px;
        border-radius: 20px; font-size: 12px; font-weight: bold;
    }
    .badge-revoked {
        background-color: #dc3545; color: white; padding: 4px 12px;
        border-radius: 20px; font-size: 12px; font-weight: bold;
    }
    .stButton>button { border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. KONEKSI WEB3.PY & SMART CONTRACT
# =========================================================

RPC_URL = "http://127.0.0.1:8545"
PROJECT_DIR = Path(__file__).parent
DEPLOYMENT_PATH = PROJECT_DIR / "deployment.json"
ARTIFACT_PATH = (
    PROJECT_DIR
    / "artifacts"
    / "contracts"
    / "LandRegistryChain.sol"
    / "LandRegistryChain.json"
)

w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 5}))

if not w3.is_connected():
    st.error("🚨 Hardhat Node tidak terhubung. Jalankan 'npx hardhat node' pada Terminal 1.")
    st.stop()

if not DEPLOYMENT_PATH.exists() or not ARTIFACT_PATH.exists():
    st.error("⚠️ Berkas deployment.json atau Artifact ABI tidak ditemukan. Jalankan compile & deploy terlebih dahulu.")
    st.stop()

with open(DEPLOYMENT_PATH, "r") as f:
    CONTRACT_ADDRESS = Web3.to_checksum_address(json.load(f)["address"])

with open(ARTIFACT_PATH, "r") as f:
    CONTRACT_ABI = json.load(f)["abi"]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

try:
    bpn_admin = contract.functions.bpnAdmin().call()
except Exception:
    bpn_admin = "Unknown"

def fetch_all_certificates():
    """Mengambil seluruh daftar sertifikat yang sudah terdaftar dari smart contract."""
    records = []
    token_id = 1
    while True:
        try:
            data = contract.functions.sertifikats(token_id).call()
            if not data[6]:  # isExist == False
                break
            records.append({
                "Token ID": data[0],
                "NIB": data[1],
                "Pemilik Sah": data[2],
                "Lokasi Tanah": data[3],
                "Luas (m²)": data[4],
                "Status": "AKTIF" if data[5] == 1 else "DIBATALKAN",
            })
            token_id += 1
        except Exception:
            break
    return records

# =========================================================
# 3. SIDEBAR STATUS JARINGAN & KONTRAK
# =========================================================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/land-sales.png", width=70)
    st.title("LandRegistryChain")
    st.caption("Sistem Anti-Mafia Tanah Berbasis NFT")
    st.divider()

    st.markdown("### 🌐 Status Blockchain")
    col_sb1, col_sb2 = st.columns(2)
    col_sb1.metric("Chain ID", w3.eth.chain_id)
    col_sb2.metric("Block", w3.eth.block_number)

    st.markdown("### 📍 Smart Contract")
    st.caption("Alamat Kontrak Aktif:")
    st.code(CONTRACT_ADDRESS, language="text")
    st.caption("Otoritas Admin BPN:")
    st.code(bpn_admin, language="text")

# =========================================================
# 4. HEADER & WALLET CONNECTION
# =========================================================

st.markdown("""
<div class="header-card">
    <h1 class="header-title">📜 Portal Pendaftaran & Verifikasi Tanah Digital</h1>
    <p class="header-subtitle">Implementasi UI LandRegistryChain — Transparansi Kepemilikan & Audit Pertanahan Berbasis Blockchain</p>
</div>
""", unsafe_allow_html=True)

metamask_html = """
<div style="font-family: sans-serif; display: flex; align-items: center; background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid #e0e6ed; margin-bottom: 16px;">
  <button id="btn-connect" style="padding: 9px 18px; background-color: #f6851b; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">
    🦊 Connect MetaMask
  </button>
  <span id="wallet-addr" style="margin-left: 15px; color: #4a5568; font-size: 14px; font-weight: 600;">Status Wallet: Belum Terhubung</span>
</div>
<script>
  function getEthereum() {
    if (window.ethereum) return window.ethereum;
    if (window.parent && window.parent.ethereum) return window.parent.ethereum;
    return null;
  }
  async function checkWallet() {
    const eth = getEthereum();
    if (eth) {
      try {
        const accounts = await eth.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
          document.getElementById("wallet-addr").innerHTML = "🟢 Wallet Terhubung: <code style='color:#2b6cb0'>" + accounts[0] + "</code>";
        }
      } catch (err) { console.error(err); }
    }
  }
  document.getElementById("btn-connect").onclick = async () => {
    const eth = getEthereum();
    if (eth) {
      try {
        const accounts = await eth.request({ method: 'eth_requestAccounts' });
        document.getElementById("wallet-addr").innerHTML = "🟢 Wallet Terhubung: <code style='color:#2b6cb0'>" + accounts[0] + "</code>";
      } catch (err) { alert(err.message); }
    } else {
      alert("Ekstensi MetaMask tidak terdeteksi!");
    }
  };
  checkWallet();
</script>
"""
components.html(metamask_html, height=72)

# =========================================================
# 5. NAVIGASI 5 HALAMAN SESUAI MODUL 11-12
# =========================================================

tab_dash, tab_detail, tab_mint, tab_transfer, tab_history = st.tabs([
    "📊 Dashboard & Daftar Tanah",
    "🔍 Detail Sertifikat",
    "✍️ Registrasi & Pembatalan (BPN)",
    "🔄 Transfer Kepemilikan",
    "📜 Riwayat Audit Blockchain",
])

# ---------------------------------------------------------
# PAGE 1: DASHBOARD & DATA MANAGEMENT (TABEL ASET TANAH)
# ---------------------------------------------------------
with tab_dash:
    st.subheader("Ringkasan Sistem & Daftar Bidang Tanah Terdaftar")
    all_certs = fetch_all_certificates()

    total_tanah = len(all_certs)
    total_aktif = sum(1 for c in all_certs if c["Status"] == "AKTIF")
    total_batal = sum(1 for c in all_certs if c["Status"] == "DIBATALKAN")
    pemilik_unik = len(set(c["Pemilik Sah"] for c in all_certs if c["Status"] == "AKTIF"))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Bidang Tanah", total_tanah)
    m2.metric("Sertifikat Aktif", total_aktif)
    m3.metric("Sertifikat Dibatalkan", total_batal)
    m4.metric("Pemilik Terdaftar", pemilik_unik)

    st.divider()
    st.markdown("#### 📋 Tabel Data Sertifikat Tanah (On-Chain Land Registry)")
    if all_certs:
        df = pd.DataFrame(all_certs)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada bidang tanah yang didaftarkan. Silakan terbitkan sertifikat pertama melalui tab **Registrasi & Pembatalan (BPN)**.")

# ---------------------------------------------------------
# PAGE 2: DETAIL DATA SERTIFIKAT
# ---------------------------------------------------------
with tab_detail:
    st.subheader("Detail & Verifikasi Keabsahan Sertifikat")
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_id = st.number_input("Masukkan Token ID Sertifikat:", min_value=1, step=1, value=1)
    with col_s2:
        st.markdown("<br>", unsafe_allow_html=True)
        btn_cek = st.button("🔎 Cari Sertifikat", use_container_width=True, type="primary")

    if btn_cek or search_id:
        try:
            data = contract.functions.sertifikats(int(search_id)).call()
            if data[6]:
                is_active = data[5] == 1
                badge = '<span class="badge-active">VALID & AKTIF</span>' if is_active else '<span class="badge-revoked">DIBATALKAN</span>'
                st.markdown(f"""
                <div class="cert-card">
                    <div class="cert-header">
                        <h3 class="cert-title">REPUBLIK INDONESIA — BADAN PERTANAHAN NASIONAL</h3>
                        <p style="margin:4px 0 0 0; font-size: 13px; color: #666;">SERTIFIKAT HAK MILIK DIGITAL (NFT TOKEN ID #{data[0]})</p>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                        <div><strong>Status Dokumen:</strong> {badge}</div>
                        <div><strong>NIB:</strong> <code>{data[1]}</code></div>
                    </div>
                    <hr style="border: none; border-top: 1px solid #eee;">
                    <p><strong>📍 Lokasi Bidang Tanah:</strong><br>{data[3]}</p>
                    <p><strong>📐 Luas Bidang Tanah:</strong><br>{data[4]} m²</p>
                    <p><strong>👤 Pemilik Sah (Pemegang Hak):</strong><br><code>{data[2]}</code></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"⚠️ Sertifikat dengan Token ID #{search_id} belum terdaftar di blockchain.")
        except Exception as e:
            st.error(f"Gagal membaca data kontrak: {e}")

# ---------------------------------------------------------
# PAGE 3: FORM INPUT (MINTING & REVOKE BY BPN)
# ---------------------------------------------------------
with tab_mint:
    st.subheader("Registrasi Sertifikat Tanah Baru (Otoritas BPN)")
    with st.form("form_mint_land"):
        c1, c2 = st.columns(2)
        with c1:
            nib_in = st.text_input("NIB (Nomor Identifikasi Bidang)", value="32.09.01.001.2026")
            lokasi_in = st.text_input("Lokasi Lengkap Bidang Tanah", value="Jl. Tuparev No. 70, Cirebon")
        with c2:
            luas_in = st.number_input("Luas Bidang Tanah (m²)", min_value=1, value=250, step=10)
            pemilik_in = st.text_input("Alamat Wallet Pemilik Sah (0x...)", placeholder="0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
        uri_in = st.text_input("Hash / Metadata URI Dokumen", value="ipfs://QmSertifikatTanah001")

        submit_mint = st.form_submit_button("✍️ Terbitkan Sertifikat (Mint NFT)", type="primary", use_container_width=True)

        if submit_mint:
            if not nib_in.strip() or not lokasi_in.strip() or not pemilik_in.strip():
                st.error("⚠️ Validasi Gagal: NIB, Lokasi, dan Alamat Wallet Pemilik wajib diisi.")
            elif not Web3.is_address(pemilik_in.strip()):
                st.error("⚠️ Validasi Gagal: Format alamat wallet Ethereum tidak valid.")
            else:
                with st.spinner("Menunggu konfirmasi transaksi minting..."):
                    try:
                        target_addr = Web3.to_checksum_address(pemilik_in.strip())
                        tx_hash = contract.functions.mintCertificate(
                            nib_in.strip(), target_addr, lokasi_in.strip(), int(luas_in), uri_in.strip()
                        ).transact({"from": bpn_admin})
                        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                        st.success(f"✅ Sertifikat berhasil diterbitkan! TX Hash: `{receipt.transactionHash.hex()}`")
                    except Exception as e:
                        st.error(f"❌ Transaksi ditolak smart contract: {e}")

    st.divider()
    st.subheader("Pembatalan Sertifikat Bermasalah (Revoke — Khusus BPN)")
    with st.form("form_revoke_land"):
        r1, r2 = st.columns([1, 2])
        with r1:
            revoke_id = st.number_input("Token ID yang Dibatalkan", min_value=1, step=1, value=1)
        with r2:
            alasan_in = st.text_input("Alasan Pembatalan Resmi", placeholder="Contoh: Putusan Pengadilan Sengketa Lahan")
        submit_revoke = st.form_submit_button("🚫 Batalkan Sertifikat", use_container_width=True)

        if submit_revoke:
            if not alasan_in.strip():
                st.error("⚠️ Validasi Gagal: Alasan pembatalan wajib diisi.")
            else:
                with st.spinner("Memproses pembatalan sertifikat..."):
                    try:
                        tx_hash = contract.functions.revokeCertificate(
                            int(revoke_id), alasan_in.strip()
                        ).transact({"from": bpn_admin})
                        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                        st.success(f"✅ Sertifikat #{revoke_id} berhasil dibatalkan. TX Hash: `{receipt.transactionHash.hex()}`")
                    except Exception as e:
                        st.error(f"❌ Pembatalan gagal: {e}")

# ---------------------------------------------------------
# PAGE 4: OWNERSHIP TRANSFER
# ---------------------------------------------------------
with tab_transfer:
    st.subheader("Pemindahan Hak Kepemilikan Sertifikat")
    st.info("🛡️ Proteksi Anti-Mafia: Transaksi hanya berhasil jika pengirim adalah pemilik sah NFT saat ini.")

    with st.form("form_transfer_land"):
        tr_id = st.number_input("Token ID Sertifikat", min_value=1, step=1, value=1)
        t1, t2 = st.columns(2)
        with t1:
            sender_in = st.text_input("Alamat Wallet Pemilik Saat Ini (Pengirim)", placeholder="0x...")
        with t2:
            receiver_in = st.text_input("Alamat Wallet Pemilik Baru (Penerima)", placeholder="0x...")

        submit_tr = st.form_submit_button("🔄 Proses Transfer Kepemilikan", type="primary", use_container_width=True)

        if submit_tr:
            if not Web3.is_address(sender_in.strip()) or not Web3.is_address(receiver_in.strip()):
                st.error("⚠️ Validasi Gagal: Pastikan alamat pengirim dan penerima adalah alamat wallet yang valid.")
            else:
                with st.spinner("Memverifikasi kepemilikan & mengirim transaksi..."):
                    try:
                        s_addr = Web3.to_checksum_address(sender_in.strip())
                        r_addr = Web3.to_checksum_address(receiver_in.strip())
                        tx_hash = contract.functions.transferCertificateOwnership(
                            int(tr_id), r_addr
                        ).transact({"from": s_addr})
                        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                        st.success(f"🎉 Kepemilikan berhasil dipindahkan! TX Hash: `{receipt.transactionHash.hex()}`")
                    except Exception as e:
                        st.error(f"🛡️ Transaksi Diblokir Smart Contract: {e}")

# ---------------------------------------------------------
# PAGE 5: OWNERSHIP HISTORY (IMMUTABLE AUDIT LOG)
# ---------------------------------------------------------
with tab_history:
    st.subheader("Riwayat Kepemilikan & Jejak Audit Kriptografis")
    h1, h2 = st.columns([3, 1])
    with h1:
        hist_id = st.number_input("Masukkan Token ID untuk Melihat Riwayat:", min_value=1, step=1, value=1, key="hist_token")
    with h2:
        st.markdown("<br>", unsafe_allow_html=True)
        btn_hist = st.button("📜 Muat Riwayat", use_container_width=True)

    if btn_hist or hist_id:
        try:
            history = contract.functions.getHistoryByTokenId(int(hist_id)).call()
            if history:
                for idx, blk in enumerate(history):
                    aksi = blk[0]
                    icon = "🟢" if aksi == "MINT" else ("🔵" if aksi == "TRANSFER" else "🔴")
                    waktu = datetime.fromtimestamp(blk[8]).strftime("%Y-%m-%d %H:%M:%S")
                    with st.expander(f"{icon} Blok #{idx+1} | {aksi} — {waktu}", expanded=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**NIB:** `{blk[2]}`")
                            st.write(f"**Dari:** `{blk[3]}`")
                            st.write(f"**Ke:** `{blk[4]}`")
                            st.write(f"**Keterangan:** {blk[5]}")
                        with col_b:
                            st.write("**Previous Hash:**")
                            st.code(blk[6].hex(), language="text")
                            st.write("**Current Hash:**")
                            st.code(blk[7].hex(), language="text")
            else:
                st.info(f"Belum ada riwayat transaksi untuk Token ID #{hist_id}.")
        except Exception as e:
            st.error(f"Gagal memuat riwayat audit: {e}")