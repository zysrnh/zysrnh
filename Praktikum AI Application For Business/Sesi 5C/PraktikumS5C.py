# ==============================================================================
# PRAKTIKUM AI APPLICATION FOR BUSINESS - PERTEMUAN 5 (LATIHAN MANDIRI / 5C)
# TOPIK  : PENGEMBANGAN RULE-BASED CHATBOT BISNIS MENGGUNAKAN REGEX & IF-ELIF-ELSE
# USAHA  : Toko Sepatu Official (Sneaker, Running Shoes, & Aksesoris Original)
# FILE   : PraktikumS5C.py (Siap Dijalankan Langsung di Google Colab)
# ==============================================================================

import re
import sys

# Menjaga kompatibilitas karakter output di terminal & Google Colab
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ==============================================================================
# FUNGSI UTAMA RULE-BASED CHATBOT BISNIS (INSTRUKSI 2, 3, 4, & 5)
# Disusun dari aturan paling spesifik (ekstraksi angka) ke aturan umum
# ==============================================================================
def chatbot_bisnis_sepatu(pesan_pelanggan):
    """
    Rule-Based Chatbot Toko Sepatu Official yang mengombinasikan struktur
    percabangan (if-elif-else) dan Regular Expressions (re.search) dengan
    flag re.IGNORECASE serta ekstraksi entitas angka (\\d+).
    """
    pesan = pesan_pelanggan.strip()

    # Deteksi opsional entitas angka ukuran sepatu (\d+)
    match_ukuran = re.search(r"\b(?:ukuran|size|nomor)\s*(\d+)\b", pesan, re.IGNORECASE)

    # --------------------------------------------------------------------------
    # ATURAN 1 (INSTRUKSI 4): Ekstraksi Entitas Angka Nomor Pesanan / Resi (\d+)
    # Menangkap pola seperti: "Pesanan: 889214", "Order #12045", "Resi 998123"
    # --------------------------------------------------------------------------
    match_pesanan = re.search(
        r"\b(?:pesanan|order|resi|invoice|nota)\s*[:#-]?\s*(\d+)",
        pesan,
        re.IGNORECASE
    )
    if match_pesanan:
        nomor_pesanan = match_pesanan.group(1)
        return (
            f"Chatbot: [LACAK PESANAN] Pesanan Anda dengan Nomor #{nomor_pesanan} "
            f"saat ini berstatus 'Sedang Dikemas & Siap Dikirim oleh Kurir Ekspedisi'. "
            f"Estimasi tiba 1-2 hari kerja."
        )

    # --------------------------------------------------------------------------
    # ATURAN 2 (INSTRUKSI 4): Ekstraksi Entitas Angka Jumlah Unit Pembelian (\d+)
    # Menangkap pola seperti: "pesan 3 pasang", "beli 2 unit"
    # --------------------------------------------------------------------------
    match_jumlah = re.search(
        r"\b(?:beli|pesan|order|ambil)\s+(\d+)\s*(?:pasang|unit|pcs|box|buah)?\b",
        pesan,
        re.IGNORECASE
    )
    if match_jumlah:
        jumlah_unit = int(match_jumlah.group(1))
        info_size = f" (Size {match_ukuran.group(1)})" if match_ukuran else ""
        promo_grosir = (
            "Selamat! Pembelian minimal 2 pasang otomatis mendapat diskon grosir 15%."
            if jumlah_unit >= 2
            else "Tersedia promo gratis ongkir ke seluruh Indonesia."
        )
        return (
            f"Chatbot: [ORDER UNIT] Siap Kak! Permintaan pembelian sebanyak {jumlah_unit} pasang sepatu"
            f"{info_size} telah kami catat. {promo_grosir}"
        )

    # --------------------------------------------------------------------------
    # ATURAN 3 (INSTRUKSI 4): Ekstraksi Entitas Angka Nomor ID Member (\d+)
    # Menangkap pola seperti: "ID Member: 55012", "ID Anggota 10294"
    # --------------------------------------------------------------------------
    match_member = re.search(
        r"\b(?:id\s*member|id\s*anggota|member|anggota)\s*[:#-]?\s*(\d+)",
        pesan,
        re.IGNORECASE
    )
    if match_member:
        id_member = match_member.group(1)
        return (
            f"Chatbot: [CEK MEMBER] Nomor ID Anggota #{id_member} terverifikasi AKTIF (Tier Gold). "
            f"Anda berhak mendapatkan potongan harga tambahan Rp 50.000 di setiap transaksi!"
        )

    # --------------------------------------------------------------------------
    # ATURAN 4 (FAQ 1): Kebijakan Garansi, Retur, & Tukar Ukuran (Size)
    # --------------------------------------------------------------------------
    elif re.search(
        r"\b(garansi|retur|rusak|cacat|tukar|ganti|kekecilan|kebesaran|komplain)\b",
        pesan,
        re.IGNORECASE
    ):
        return (
            "Chatbot: [GARANSI & RETUR] Seluruh produk kami bergaransi 100% Original. "
            "Kami menyediakan garansi retur 7 hari ganti baru jika cacat pabrik atau tukar ukuran (free exchange) "
            "jika ukuran sepatu kekecilan/kebesaran."
        )

    # --------------------------------------------------------------------------
    # ATURAN 5 (FAQ 2): Lokasi Toko Offline & Jam Operasional
    # --------------------------------------------------------------------------
    elif re.search(
        r"\b(lokasi|alamat|dimana|cabang|toko|offline|jam|buka|tutup|operasional)\b",
        pesan,
        re.IGNORECASE
    ):
        return (
            "Chatbot: [LOKASI & JAM BUKA] Store offline kami berlokasi di Jl. Soekarno-Hatta No. 456, Bandung. "
            "Buka setiap hari Senin - Minggu pukul 09.00 - 21.00 WIB."
        )

    # --------------------------------------------------------------------------
    # ATURAN 6 (FAQ 3): Informasi Harga, Biaya, Pricelist, & Diskon Promo
    # --------------------------------------------------------------------------
    elif re.search(
        r"\b(harga|biaya|tarif|pricelist|berapa\s*harga|berapaan|diskon|promo|cashback|murah)\b",
        pesan,
        re.IGNORECASE
    ):
        return (
            "Chatbot: [DAFTAR HARGA] Harga koleksi sepatu kami mulai dari Rp 250.000 hingga Rp 750.000: "
            "• Sneaker Casual: Rp 275.000 | • Sepatu Running Pro: Rp 450.000 | • Limited Series: Rp 750.000. "
            "Sedang ada promo diskon 10% minggu ini!"
        )

    # --------------------------------------------------------------------------
    # ATURAN 7 (FAQ 4): Metode Pembayaran, Transfer, QRIS, & COD
    # --------------------------------------------------------------------------
    elif re.search(
        r"\b(bayar|pembayaran|transfer|qris|cod|cicilan|paylater|bca|mandiri|gopay)\b",
        pesan,
        re.IGNORECASE
    ):
        return (
            "Chatbot: [METODE PEMBAYARAN] Kami melayani pembayaran via Transfer Bank (BCA/Mandiri/BNI), "
            "QRIS, E-Wallet, PayLater, serta COD (Bayar di Tempat)."
        )

    # --------------------------------------------------------------------------
    # ATURAN 8 (FAQ 5): Informasi Katalog Produk & Ketersediaan Stok
    # --------------------------------------------------------------------------
    elif re.search(
        r"\b(produk|katalog|jual|ready|stok|sepatu|sneaker|running|casual|olahraga|model)\b",
        pesan,
        re.IGNORECASE
    ):
        info_size = f" untuk ukuran {match_ukuran.group(1)}" if match_ukuran else " (tersedia ukuran 38 s/d 45)"
        return (
            f"Chatbot: [KATALOG PRODUK] Kami menyediakan koleksi Sepatu Running, Sneaker Casual, "
            f"Sepatu Basket, dan Kaos Kaki Olahraga Original{info_size}. Seluruh stok ready!"
        )

    # --------------------------------------------------------------------------
    # ATURAN 9 (FAQ 6): Sapaan Pelanggan & Pembuka Percakapan
    # --------------------------------------------------------------------------
    elif re.search(
        r"\b(halo|hai|hey|selamat\s*(pagi|siang|sore|malam)|permisi|assalamualaikum|min|admin)\b",
        pesan,
        re.IGNORECASE
    ):
        return (
            "Chatbot: Halo Kak! Selamat datang di Toko Sepatu Official. "
            "Ada yang bisa kami bantu seputar katalog produk, harga, lokasi toko, garansi, atau cek pesanan?"
        )

    # --------------------------------------------------------------------------
    # ATURAN 10 (INSTRUKSI 5): Penanganan Pesan Fallback (else)
    # --------------------------------------------------------------------------
    else:
        return (
            "Chatbot: [FALLBACK BANTUAN] Maaf Kak, pesan Anda belum sesuai dengan kata kunci sistem kami. "
            "Silakan gunakan kata kunci berikut:\n"
            "  • Ketik 'katalog' atau 'produk'  -> Melihat daftar sepatu & stok\n"
            "  • Ketik 'harga' atau 'promo'     -> Melihat daftar harga & diskon\n"
            "  • Ketik 'lokasi' atau 'jam buka' -> Info alamat & jam operasional toko\n"
            "  • Ketik 'garansi' atau 'retur'   -> Info garansi & tukar ukuran\n"
            "  • Ketik 'Pesanan: 889214'        -> Melacak status nomor pesanan Anda\n"
            "  • Ketik 'Beli 2 pasang'          -> Menghitung pesanan jumlah unit otomatis"
        )


# ==============================================================================
# SIMULASI PENGUJIAN CHATBOT (INSTRUKSI 6: MINIMAL 5 KALIMAT BERBEDA)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 85)
    print("   TUGAS PRAKTIKUM PERTEMUAN 5: RULE-BASED CHATBOT BISNIS (REGEX & IF-ELIF-ELSE)   ")
    print("   Bidang Usaha : Toko Sepatu Official                                             ")
    print("=" * 85)

    daftar_pertanyaan_uji = [
        "Selamat pagi admin, mau tanya-tanya dong!",
        "Apakah stok sepatu running ukuran 42 masih ready?",
        "Berapa pricelist harga sepatu dan apakah ada diskon?",
        "Saya mau pesan 3 pasang ukuran 42 untuk tim olahraga",
        "Tolong cek status pengiriman saya dengan Pesanan: 889214",
        "Cek benefit untuk ID Member: 55012 dong min",
        "Kalau sepatu yang dikirim kekecilan apakah ada garansi retur?",
        "Toko offline di Bandung buka jam berapa dan dimana alamatnya?",
        "Apakah besok di Bandung bakal turun hujan deras?"  # Pengujian Fallback (else)
    ]

    for nomor, kalimat_uji in enumerate(daftar_pertanyaan_uji, start=1):
        print(f"\n[Uji #{nomor:02d}] Pelanggan : \"{kalimat_uji}\"")
        respon = chatbot_bisnis_sepatu(kalimat_uji)
        print(f"          {respon}")

    print("\n" + "=" * 85)
    print(">> Pengujian selesai: Seluruh FAQ, Ekstraksi Angka Regex (\\d+), dan Fallback berjalan sukses!")
    print("=" * 85)
