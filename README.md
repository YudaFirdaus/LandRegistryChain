# LandRegistryChain — Sistem Pendaftaran & Verifikasi Sertifikat Tanah NFT

Aplikasi web terdesentralisasi (_dApp_) untuk pencatatan aset pertanahan, validasi kepemilikan sah, dan pelacakan histori audit anti-mafia tanah berbasis standar NFT ERC-721.

## Teknologi yang Digunakan

- **Smart Contract:** Solidity (`^0.8.20`), OpenZeppelin ERC-721 (`ERC721URIStorage`), Hardhat
- **Integrasi Blockchain:** Web3.py, MetaMask (Localhost RPC `Chain ID: 31337`)
- **Antarmuka Pengguna (UI):** Python, Streamlit, Pandas

## Cara Menjalankan Aplikasi

1. **Instalasi Dependensi**
   Pastikan **Node.js** dan **Python 3** sudah terpasang, lalu jalankan perintah berikut di direktori proyek:

   ```bash
   npm install
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Inisiasi Terminal 1 (Jaringan Blockchain Lokal)**
   Jalankan server node lokal Hardhat:

   ```bash
   npx hardhat node
   ```

3. **Inisiasi Terminal 2 (Kompilasi & Deploy Smart Contract)**
   Buka terminal baru, lalu kompilasi dan _deploy_ kontrak ke jaringan lokal:

   ```bash
   npx hardhat compile
   npx hardhat run scripts/deploy.js --network localhost
   ```

4. **Menjalankan Antarmuka Web Streamlit**
   Masih di Terminal 2, jalankan aplikasi antarmuka:
   ```bash
   streamlit run App.py
   ```
   Buka `http://localhost:8501` di browser dan hubungkan ekstensi MetaMask ke jaringan `Localhost 8545` (`Chain ID: 31337`).
