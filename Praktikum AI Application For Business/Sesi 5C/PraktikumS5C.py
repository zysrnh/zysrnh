# ==============================================================================
# PRAKTIKUM AI APPLICATION FOR BUSINESS - PERTEMUAN 5 (GABUNGAN LENGKAP + INPUT)
# TOPIK  : RULE-BASED CHATBOT BISNIS (INTEGRASI SESI 1-5: PREPROCESSING,
#          ENTITAS, IF-ELIF-ELSE, REGEX re.IGNORECASE, EKSTRAKSI ANGKA \d+)
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
# 1. MODUL PREPROCESSING & NORMALISASI SLANG/TYPO (MATERI SESI 3)
# ==============================================================================
KAMUS_SLANG = {
    "brp": "berapa",
    "hrg": "harga",
    "pricelistnya": "pricelist",
    "bgt": "banget",
    "cepet": "cepat",
    "ga": "tidak",
    "gak": "tidak",
    "yg": "yang",
    "dmn": "dimana",
    "almt": "alamat",
    "psn": "pesan",
    "uk": "ukuran",
    "sz": "size",
    "garansinya": "garansi",
    "ori": "original",
    "byr": "bayar"
}


def normalisasi_teks(teks):
    """Menyederhanakan huruf berulang (misal: 'halooo' -> 'halo') & menormalkan slang."""
    teks_norm = re.sub(r"([a-zA-Z])\1{2,}", r"\1", teks.strip())
    kata_list = teks_norm.split()
    hasil_kata = [KAMUS_SLANG.get(k.lower(), k) for k in kata_list]
    return " ".join(hasil_kata)


# ==============================================================================
# 2. MODUL EKSTRAKSI ENTITAS BISNIS (MATERI SESI 4)
# ==============================================================================
ENTITAS_BISNIS = {
    "PRODUK": ["sneaker", "running", "casual", "basket", "kaos kaki", "sandal"],
    "METODE_BAYAR": ["bca", "mandiri", "bni", "qris", "cod", "paylater", "gopay", "kredivo"]
}


def ekstrak_entitas(pesan):
    """Mendeteksi entitas produk dan metode pembayaran di dalam kalimat pelanggan."""
    ditemukan = {}
    pesan_lower = pesan.lower()
    for kategori, daftar_item in ENTITAS_BISNIS.items():
        for item in daftar_item:
            if item in pesan_lower:
                ditemukan[kategori] = item.upper()
                break
    return ditemukan


# ==============================================================================
# 3. FUNGSI UTAMA RULE-BASED CHATBOT REGEX & IF-ELIF-ELSE (MATERI SESI 5)
# ==============================================================================
def chatbot_bisnis_sepatu(pesan_pelanggan):
    """
    Rule-Based Chatbot Toko Sepatu Official yang menyatukan:
    - Normalisasi Slang (Sesi 3)
    - Deteksi Entitas Produk & Pembayaran (Sesi 4)
    - Logika If-Elif-Else + Regex re.search(re.IGNORECASE) + Ekstraksi Angka \\d+ (Sesi 5)
    """
    # Tahap A: Normalisasi teks masukan pelanggan
    pesan = normalisasi_teks(pesan_pelanggan)

    # Tahap B: Ekstraksi entitas produk & metode pembayaran
    entitas = ekstrak_entitas(pesan)
    info_produk = f" kategori {entitas['PRODUK']}" if "PRODUK" in entitas else ""
    info_bayar = f" via {entitas['METODE_BAYAR']}" if "METODE_BAYAR" in entitas else ""

    # Tahap C: Deteksi opsional entitas angka ukuran sepatu (\d+)
    match_ukuran = re.search(r"\b(?:ukuran|size|nomor)\s*(\d+)\b", pesan, re.IGNORECASE)

    # --------------------------------------------------------------------------
    # ATURAN 1 (INSTRUKSI 4): Ekstraksi Entitas Angka Nomor Pesanan / Resi (\d+)
    # Contoh: "Pesanan: 889214", "Resi: 987654321", "Order #12045"
    # --------------------------------------------------------------------------
    match_pesanan = re.search(
        r"\b(?:pesanan|order|resi|invoice|nota)\s*[:#-]?\s*(\d+)",
        pesan,
        re.IGNORECASE
    )
    if match_pesanan:
        nomor_pesanan = match_pesanan.group(1)
        return (
            f"Chatbot: [LACAK PESANAN] Pesanan Anda dengan Nomor #{nomor_pesanan}{info_produk} "
            f"saat ini berstatus 'Sedang Dikemas & Siap Dikirim oleh Kurir Ekspedisi'. "
            f"Estimasi tiba 1-2 hari kerja."
        )

    # --------------------------------------------------------------------------
    # ATURAN 2 (INSTRUKSI 4): Ekstraksi Entitas Angka Jumlah Unit Pembelian (\d+)
    # Contoh: "pesan 3 pasang", "beli 2 unit"
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
            f"{info_produk}{info_size}{info_bayar} telah kami catat. {promo_grosir}"
        )

    # --------------------------------------------------------------------------
    # ATURAN 3 (INSTRUKSI 4): Ekstraksi Entitas Angka Nomor ID Member (\d+)
    # Contoh: "ID Member: 55012", "Member 10294"
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
            f"Chatbot: [GARANSI & RETUR] Seluruh produk{info_produk} kami bergaransi 100% Original. "
            f"Kami menyediakan garansi retur 7 hari ganti baru jika cacat pabrik atau tukar ukuran (free exchange) "
            f"jika ukuran sepatu kekecilan/kebesaran."
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
        r"\b(harga|biaya|tarif|pricelist|berapa|berapaan|diskon|promo|cashback|murah)\b",
        pesan,
        re.IGNORECASE
    ):
        return (
            f"Chatbot: [DAFTAR HARGA] Harga koleksi sepatu{info_produk} kami mulai dari Rp 250.000 hingga Rp 750.000: "
            f"• Sneaker Casual: Rp 275.000 | • Sepatu Running Pro: Rp 450.000 | • Limited Series: Rp 750.000. "
            f"Sedang ada promo diskon 10% minggu ini!"
        )

    # --------------------------------------------------------------------------
    # ATURAN 7 (FAQ 4): Metode Pembayaran, Transfer, QRIS, & COD
    # --------------------------------------------------------------------------
    elif re.search(
        r"\b(bayar|pembayaran|transfer|qris|cod|cicilan|paylater|bca|mandiri|bni|gopay|kredivo)\b",
        pesan,
        re.IGNORECASE
    ):
        return (
            f"Chatbot: [METODE PEMBAYARAN] Kami melayani pembayaran{info_bayar} via Transfer Bank (BCA/Mandiri/BNI), "
            f"QRIS, E-Wallet, PayLater, serta COD (Bayar di Tempat)."
        )

    # --------------------------------------------------------------------------
    # ATURAN 8 (FAQ 5): Informasi Katalog Produk & Ketersediaan Stok
    # --------------------------------------------------------------------------
    elif re.search(
        r"\b(produk|katalog|jual|ready|stok|sepatu|sneaker|running|casual|basket|olahraga|model)\b",
        pesan,
        re.IGNORECASE
    ):
        info_size = f" untuk ukuran {match_ukuran.group(1)}" if match_ukuran else " (tersedia ukuran 38 s/d 45)"
        return (
            f"Chatbot: [KATALOG PRODUK] Kami menyediakan koleksi Sepatu Running, Sneaker Casual, "
            f"Sepatu Basket, dan Kaos Kaki Olahraga Original{info_produk}{info_size}. Seluruh stok ready!"
        )

    # --------------------------------------------------------------------------
    # ATURAN 9 (FAQ 6): Panduan Lacak Resi / Pesanan Tanpa Angka
    # --------------------------------------------------------------------------
    elif re.search(r"\b(resi|lacak|posisi paket|kiriman|status)\b", pesan, re.IGNORECASE):
        return (
            "Chatbot: Untuk melacak paket atau pesanan, silakan ketik dengan angka seperti: "
            "'Pesanan: 889214' atau 'Resi: 987654321'."
        )

    # --------------------------------------------------------------------------
    # ATURAN 10 (FAQ 7): Sapaan Pelanggan & Ucapan Terima Kasih
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

    elif re.search(r"\b(makasih|terima\s*kasih|thanks|thx|oke|ok|sip|siap)\b", pesan, re.IGNORECASE):
        return "Chatbot: Sama-sama Kak! Senang bisa membantu Anda di Toko Sepatu Official."

    # --------------------------------------------------------------------------
    # ATURAN 11 (INSTRUKSI 5): Penanganan Pesan Fallback (else)
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
# 4. EKSEKUSI UJI OTOMATIS (INSTRUKSI 6) + LIVE CHAT INTERAKTIF DENGAN input()
# ==============================================================================
def jalankan_program():
    print("=" * 85)
    print("   BAGIAN A: SIMULASI UJI OTOMATIS 6 KALIMAT PELANGGAN (SYARAT INSTRUKSI 6)   ")
    print("=" * 85)

    daftar_pertanyaan_uji = [
        "Selamat pagi admin, mau tanya-tanya dong!",
        "Apakah stok sepatu running ukuran 42 masih ready?",
        "Berapa pricelist harga sepatu dan apakah ada diskon?",
        "Saya mau pesan 3 pasang sneaker ukuran 42 bayar pake qris",
        "Tolong cek status pengiriman saya dengan Pesanan: 889214",
        "Apakah besok di Bandung bakal turun hujan deras?"  # Uji Fallback (else)
    ]

    for nomor, kalimat_uji in enumerate(daftar_pertanyaan_uji, start=1):
        print(f"\n[Uji #{nomor:02d}] Pelanggan : \"{kalimat_uji}\"")
        print(f"          {chatbot_bisnis_sepatu(kalimat_uji)}")

    print("\n" + "=" * 85)
    print("   BAGIAN B: MODE LIVE CHAT INTERAKTIF PELANGGAN (MENGGUNAKAN input())   ")
    print("   Contoh ketik: 'harga sepatu running', 'Pesanan: 889214', 'beli 2 pasang'   ")
    print("   (Ketik 'exit' atau 'keluar' untuk mengakhiri percakapan)   ")
    print("=" * 85)

    while True:
        try:
            pesan_user = input("\nAnda    : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nChatbot : Sesi chat diakhiri. Terima kasih telah mengunjungi Toko Sepatu Official!")
            break

        if not pesan_user:
            continue

        if pesan_user.lower() in ["exit", "keluar", "quit", "selesai", "stop", "bye"]:
            print("Chatbot : Terima kasih telah menghubungi Toko Sepatu Official. Sampai jumpa Kak!")
            print("=" * 85)
            break

        balasan = chatbot_bisnis_sepatu(pesan_user)
        print(balasan)


if __name__ == "__main__":
    jalankan_program()
