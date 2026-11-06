# ==============================================================================
# PRAKTIKUM AI APPLICATION FOR BUSINESS - PERTEMUAN 5 (LATIHAN MANDIRI / 5C)
# TOPIK  : RULE-BASED CHATBOT BISNIS (IF-ELIF-ELSE & REGEX re.IGNORECASE + \d+)
#          DENGAN VALIDASI KETAT (NO RESI KEPOTONG, NO TELP ANEH, ANGKA TIDAK WAJAR)
# USAHA  : Toko Sepatu Official
# FILE   : PraktikumS5C.py (Siap Dijalankan di Google Colab)
# ==============================================================================

import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ==============================================================================
# DATA KATALOG & MEMORI OBROLAN KONTEKSTUAL
# ==============================================================================
KATALOG_SEPATU = {
    "running": {"nama": "Sepatu Running Pro", "harga": 450000, "min_size": 36, "max_size": 46},
    "sneaker": {"nama": "Sneaker Casual", "harga": 275000, "min_size": 36, "max_size": 45},
    "casual":  {"nama": "Sneaker Casual", "harga": 275000, "min_size": 36, "max_size": 45},
    "basket":  {"nama": "Sepatu Basket Elite", "harga": 550000, "min_size": 38, "max_size": 46},
    "sandal":  {"nama": "Sandal Trendy", "harga": 150000, "min_size": 36, "max_size": 44}
}

konteks = {
    "produk": None,
    "ukuran": None,
    "jumlah": None,
    "no_hp": None,
    "resi_terakhir": "889214"
}


def rupiah(nominal):
    return f"Rp {nominal:,.0f}".replace(",", ".")


# ==============================================================================
# FUNGSI VALIDASI KETAT ENTITAS ANGKA (RESI, TELEPON, UKURAN, JUMLAH UNIT)
# ==============================================================================
def validasi_nomor_telepon(teks_nomor):
    """
    Memvalidasi nomor telepon/HP Indonesia secara ketat:
    - Menolak jika terpotong spasi (misal '0812 3456 789') atau mengandung huruf
    - Wajib diawali '08' atau '+628' / '628'
    - Panjang digit wajib 10 s/d 13 angka
    - Menolak angka kembar tidak wajar (contoh: '08000000000' atau '08111111111')
    """
    raw = teks_nomor.strip()

    # 1. Cek jika nomor telepon terpotong spasi
    if re.search(r"\d+\s+\d+", raw):
        gabung = re.sub(r"\s+", "", raw)
        return (
            False,
            f"Nomor telepon '{raw}' terlihat terpotong spasi Kak. "
            f"Mohon ketik menyatu tanpa spasi ya (Contoh: {gabung})."
        )

    bersih = re.sub(r"[-]", "", raw)
    if bersih.startswith("+62"):
        bersih = "0" + bersih[3:]
    elif bersih.startswith("62"):
        bersih = "0" + bersih[2:]

    # 2. Cek jika ada huruf atau simbol aneh
    if not bersih.isdigit():
        return (
            False,
            f"Nomor telepon '{raw}' tidak valid karena mengandung huruf atau karakter aneh."
        )

    # 3. Cek awalan nomor HP Indonesia
    if not bersih.startswith("08"):
        return (
            False,
            f"Nomor '{raw}' tidak valid karena nomor HP Indonesia wajib diawali '08' atau '+628' (Contoh: 081234567890)."
        )

    # 4. Cek jika nomor telepon kepotong / terlalu pendek (< 10 digit)
    if len(bersih) < 10:
        return (
            False,
            f"Nomor '{raw}' terlalu pendek/kepotong (baru {len(bersih)} digit). Standar nomor HP aktif adalah 10-13 digit."
        )

    # 5. Cek jika nomor telepon terlalu panjang (> 13 digit)
    if len(bersih) > 13:
        return (
            False,
            f"Nomor '{raw}' kelebihan digit ({len(bersih)} angka). Maksimal nomor HP adalah 13 digit."
        )

    # 6. Cek jika angka berulang palsu
    if re.search(r"(\d)\1{6,}", bersih):
        return (
            False,
            f"Nomor '{raw}' terdeteksi sebagai deretan angka kembar yang tidak wajar."
        )

    return True, bersih


def validasi_nomor_resi(raw_resi):
    """
    Memvalidasi nomor pesanan/resi secara ketat:
    - Menolak jika terpotong spasi (misal '88 92 14') atau strip ('88-92-14')
    - Menolak jika mengandung huruf ('88A21')
    - Wajib angka utuh 6 s/d 10 digit
    - Menolak angka 0 semua ('000000') atau kembar semua
    """
    raw_resi = raw_resi.strip()

    # 1. Cek jika resi terpotong spasi atau strip di tengah
    if re.search(r"\d+[\s-]+\d+", raw_resi):
        gabung = re.sub(r"[\s-]+", "", raw_resi)
        return (
            False,
            f"Nomor pesanan/resi '{raw_resi}' terlihat terpotong spasi/tanda hubung Kak. "
            f"Maksud Kakak 'Resi: {gabung}'? Mohon ketik menyatu tanpa spasi ya (6-10 digit angka)."
        )

    # 2. Cek jika mengandung huruf/karakter aneh
    if not raw_resi.isdigit():
        return (
            False,
            f"Format nomor pesanan/resi '{raw_resi}' tidak valid karena mengandung huruf/simbol. "
            f"Nomor resi resmi hanya berupa 6-10 digit angka (Contoh: Resi: 889214)."
        )

    # 3. Cek jika kepotong / terlalu pendek (< 6 digit)
    if len(raw_resi) < 6:
        return (
            False,
            f"Nomor pesanan/resi #{raw_resi} kayaknya kepotong Kak (baru {len(raw_resi)} digit). "
            f"Nomor resi resmi kami wajib 6 sampai 10 digit angka (Contoh: Resi: 889214)."
        )

    # 4. Cek jika terlalu panjang (> 10 digit)
    if len(raw_resi) > 10:
        return (
            False,
            f"Nomor pesanan/resi #{raw_resi} kelebihan digit ({len(raw_resi)} angka). "
            f"Nomor resi maksimal 10 digit angka ya Kak."
        )

    # 5. Cek jika angka 0 semua atau kembar tidak wajar
    if int(raw_resi) == 0 or re.match(r"^(\d)\1+$", raw_resi):
        return (
            False,
            f"Nomor pesanan/resi #{raw_resi} tidak terdaftar (angka tidak wajar). "
            f"Silakan cek kembali struk pembelian Anda atau hubungi CS di 0812-3456-7890."
        )

    return True, raw_resi


# ==============================================================================
# FUNGSI UTAMA RULE-BASED CHATBOT (IF-ELIF-ELSE + re.search + re.IGNORECASE)
# ==============================================================================
def respon_chatbot(pesan_user):
    pesan = pesan_user.strip()

    # --------------------------------------------------------------------------
    # 0. VALIDASI AWAL: JIKA INPUT HANYA SIMBOL ANEH ATAU ANGKA TANPA KONTEKS
    # --------------------------------------------------------------------------
    if re.match(r"^[^a-zA-Z0-9]+$", pesan):
        return (
            "Maaf Kak, pesan hanya berisi simbol yang tidak bisa saya pahami. "
            "Jika butuh bantuan langsung, hubungi Call Center kami di (022) 731-8899 / WA 0812-3456-7890."
        )

    if re.match(r"^[\d\s+-]+$", pesan):
        angka_saja = re.sub(r"\D", "", pesan)
        if angka_saja.startswith(("08", "628")):
            valid_hp, info_hp = validasi_nomor_telepon(pesan)
            if not valid_hp:
                return f"Waduh Kak, {info_hp}"
            konteks["no_hp"] = info_hp
            return f"Siap Kak, nomor HP {info_hp} sudah kami catat untuk konfirmasi pengiriman pesanan!"
        return (
            f"Maaf Kak, angka '{pesan}' yang Kakak ketik belum jelas untuk apa (apakah Ukuran, Jumlah Pasang, Nomor Resi, atau Nomor HP?).\n"
            f"  • Lacak resi (6-10 digit)  : ketik 'Resi: 889214'\n"
            f"  • Pilih ukuran (36-46)     : ketik 'Ukuran 42'\n"
            f"  • Jumlah beli (1-50)       : ketik 'Beli 2 pasang'\n"
            f"  • Simpan No HP (10-13 dgt) : ketik 'No HP: 081234567890'\n"
            f"  • Butuh bantuan CS? Hubungi WA 0812-3456-7890."
        )

    # Simpan konteks jika pelanggan menyebut nama model sepatu yang valid
    for key, info in KATALOG_SEPATU.items():
        if re.search(rf"\b{key}\b", pesan, re.IGNORECASE):
            konteks["produk"] = info
            break

    # --------------------------------------------------------------------------
    # 1. VALIDASI KETAT NOMOR TELEPON / WA PELANGGAN (\d+)
    # Contoh: "no hp saya 08123", "no hp saya 1234567890", "wa: 0812 3456 7890"
    # --------------------------------------------------------------------------
    match_input_hp = re.search(
        r"\b(?:no\s*hp|nomor\s*hp|hp|no\s*wa|nomor\s*wa|wa|no\s*telp|nomor\s*telepon|telepon|telp|nomor)(?:\s+(?:saya|aku|kami|aktif|ini))?\s*[:#-]?\s*([+\d][a-zA-Z0-9\s-]{1,})",
        pesan,
        re.IGNORECASE
    )
    if match_input_hp or re.search(r"(?:\+62|62|0)8[\d\s-]{2,}", pesan):
        if match_input_hp:
            calon_hp = match_input_hp.group(1).strip()
        else:
            calon_hp = re.search(r"(?:\+62|62|0)8[a-zA-Z0-9\s-]*", pesan).group(0).strip()

        calon_hp = re.split(r"\b(?:ya|kak|min|dong|tolong)\b", calon_hp, flags=re.IGNORECASE)[0].strip()
        valid_hp, pesan_hp = validasi_nomor_telepon(calon_hp)
        if not valid_hp:
            return f"Maaf Kak, {pesan_hp}"
        konteks["no_hp"] = pesan_hp
        return f"Terima kasih Kak! Nomor WhatsApp/HP aktif ({pesan_hp}) sudah berhasil kami verifikasi dan simpan."

    # --------------------------------------------------------------------------
    # 2. VALIDASI KETAT NOMOR RESI / PESANAN (\d+) - DETEKSI RESI KEPOTONG/ANEH
    # Contoh: "Resi: 889214", "Resi: 123" (kepotong), "Pesanan: 88 92 14" (spasi)
    # --------------------------------------------------------------------------
    match_resi = re.search(
        r"\b(?:resi|pesanan|order|invoice|nota)\s*[:#-]\s*([^\n]+)",
        pesan,
        re.IGNORECASE
    )
    if not match_resi:
        match_resi = re.search(
            r"\b(?:resi|pesanan|order|invoice|nota)\s+([a-zA-Z0-9\s-]*\d+[a-zA-Z0-9\s-]*)",
            pesan,
            re.IGNORECASE
        )

    if match_resi:
        kandidat_resi = match_resi.group(1).strip()
        kandidat_resi = re.split(r"\b(?:dong|ya|kak|min|tolong|saya)\b", kandidat_resi, flags=re.IGNORECASE)[0].strip()
        valid_r, hasil_r = validasi_nomor_resi(kandidat_resi)
        if not valid_r:
            return hasil_r

        konteks["resi_terakhir"] = hasil_r
        return (
            f"Baik Kak, Nomor Resi/Pesanan #{hasil_r} terverifikasi valid! "
            f"Status paket saat ini sedang dibawa kurir menuju alamat tujuan (estimasi tiba 1-2 hari kerja)."
        )

    # --------------------------------------------------------------------------
    # 3. VALIDASI KETAT ANGKA UKURAN SEPATU (\d+) - MENOLAK UKURAN ANEH
    # Contoh: "ukuran 42" (valid), "ukuran 99" / "ukuran 5" / "ukuran -40" (aneh)
    # --------------------------------------------------------------------------
    match_ukuran = re.search(r"\b(?:ukuran|size|uk)\s*[:#-]?\s*(-?\d+)\b", pesan, re.IGNORECASE)
    if match_ukuran:
        angka_uk = int(match_ukuran.group(1))
        if angka_uk < 36 or angka_uk > 46:
            return (
                f"Waduh Kak, ukuran sepatu '{angka_uk}' tidak wajar / tidak tersedia di toko kami. "
                f"Ukuran resmi yang tersedia hanya dari Size 36 sampai Size 46 ya Kak. Mau pilih ukuran berapa?"
            )
        konteks["ukuran"] = str(angka_uk)

    # --------------------------------------------------------------------------
    # 4. VALIDASI KETAT JUMLAH UNIT PEMBELIAN (\d+) - MENOLAK ANGKA 0 / EKSTREM
    # Contoh: "beli 2 pasang" (valid), "beli 0 pasang" / "beli 500 pasang" (aneh)
    # --------------------------------------------------------------------------
    match_jumlah = re.search(
        r"(?:\b(?:beli|pesan|order|ambil)\s+(-?\d+)\s*(?:pasang|unit|pcs|box|buah)?\b|\b(-?\d+)\s+(?:pasang|unit|pcs|box)\b)",
        pesan,
        re.IGNORECASE
    )
    if match_jumlah:
        jml = int(match_jumlah.group(1) or match_jumlah.group(2))

        if jml <= 0:
            return (
                f"Maaf Kak, jumlah pembelian '{jml} pasang' tidak valid. "
                f"Minimal pemesanan adalah 1 pasang sepatu ya Kak."
            )
        if jml > 50:
            return (
                f"Wah, pemesanan sebanyak '{jml} pasang' melebihi batas transaksi ritel otomatis kami (maksimal 50 pasang). "
                f"Untuk pemesanan partai besar/grosir, silakan telepon langsung tim B2B kami di (022) 731-8899 atau WA 0812-3456-7890 ya Kak!"
            )

        konteks["jumlah"] = jml
        produk = konteks["produk"] or KATALOG_SEPATU["running"]
        ukuran = konteks["ukuran"] or "42"
        subtotal = jml * produk["harga"]

        if jml >= 2:
            diskon = int(subtotal * 0.10)
            total = subtotal - diskon
            ket_promo = f"Diskon 10% (-{rupiah(diskon)})"
        else:
            total = subtotal
            ket_promo = "Subsidi Gratis Ongkir"

        return (
            f"Siap Kak, pesanan kamu sudah valid dan langsung saya buatkan rinciannya:\n"
            f"  • Produk      : {produk['nama']} (Ukuran {ukuran})\n"
            f"  • Jumlah      : {jml} pasang x {rupiah(produk['harga'])}\n"
            f"  • Promo       : {ket_promo}\n"
            f"  • Total Bayar : {rupiah(total)}\n"
            f"  • No. Pesanan : #{konteks['resi_terakhir']}\n"
            f"  Kakak mau lanjut bayar pakai apa nih? (QRIS / Transfer BCA / Mandiri / COD)"
        )

    # --------------------------------------------------------------------------
    # 5. FAQ KONTAK / NOMOR TELEPON / WHATSAPP CS
    # --------------------------------------------------------------------------
    elif re.search(r"\b(kontak|no\s*telp|telepon|telpon|wa|whatsapp|hubungi|call\s*center|cs)\b", pesan, re.IGNORECASE):
        return (
            "Untuk ngobrol atau konsultasi langsung dengan CS manusia, silakan hubungi:\n"
            "  • WhatsApp CS : 0812-3456-7890\n"
            "  • Call Center : (022) 731-8899\n"
            "  • Email       : cs@tokosepatu.co.id"
        )

    # --------------------------------------------------------------------------
    # 6. FAQ ALAMAT TOKO & JAM OPERASIONAL
    # --------------------------------------------------------------------------
    elif re.search(r"\b(alamat|lokasi|dimana|cabang|toko\s*offline|posisi|jam\s*buka|buka\s*jam|operasional)\b", pesan, re.IGNORECASE):
        return (
            "Toko offline kami ada di Jl. Soekarno-Hatta No. 456, Bandung ya Kak. "
            "Kita buka setiap hari Senin - Minggu dari jam 08.00 pagi sampai 21.00 malam WIB."
        )

    # --------------------------------------------------------------------------
    # 7. FAQ KEBIJAKAN GARANSI, RETUR & TUKAR UKURAN
    # --------------------------------------------------------------------------
    elif re.search(r"\b(garansi|retur|rusak|cacat|tukar|ganti|kekecilan|kebesaran|komplain)\b", pesan, re.IGNORECASE):
        return (
            "Tenang Kak! Semua sepatu di toko kami bergaransi retur 7 hari ganti baru "
            "kalau ada cacat pabrik, dan gratis tukar ukuran (size) kalau pas dicoba kekecilan atau kebesaran."
        )

    # --------------------------------------------------------------------------
    # 8. FAQ HARGA, PRICELIST & PROMO DISKON
    # --------------------------------------------------------------------------
    elif re.search(r"\b(harga|biaya|tarif|pricelist|berapa|berapaan|diskon|promo|murah)\b", pesan, re.IGNORECASE):
        if konteks["produk"]:
            p = konteks["produk"]
            return (
                f"Untuk {p['nama']} harganya {rupiah(p['harga'])} per pasang Kak (Ready Size {p['min_size']}-{p['max_size']}). "
                f"Kalau beli minimal 2 pasang, otomatis dapet diskon 10%! Mau ambil berapa pasang Kak?"
            )
        return (
            "Ini daftar harga resmi sepatu di toko kami Kak:\n"
            "  • Sepatu Running Pro  : Rp 450.000 (Size 36-46)\n"
            "  • Sneaker Casual      : Rp 275.000 (Size 36-45)\n"
            "  • Sepatu Basket Elite : Rp 550.000 (Size 38-46)\n"
            "  • Sandal Trendy       : Rp 150.000 (Size 36-44)\n"
            "  (Beli minimal 2 pasang otomatis diskon 10%!). Kakak tertarik model yang mana?"
        )

    # --------------------------------------------------------------------------
    # 9. FAQ METODE PEMBAYARAN & ONGKIR
    # --------------------------------------------------------------------------
    elif re.search(r"\b(bayar|pembayaran|transfer|qris|cod|bca|mandiri|bni|cicilan|paylater)\b", pesan, re.IGNORECASE):
        if konteks["jumlah"]:
            return (
                f"Mantap Kak! Pembayaran untuk pesanan #{konteks['resi_terakhir']} sudah kami catat. "
                f"Barang segera dikemas hari ini. Untuk cek kiriman nanti tinggal ketik 'Resi: {konteks['resi_terakhir']}' ya!"
            )
        return (
            "Pembayaran bisa lewat QRIS, Transfer Bank (BCA/Mandiri/BNI), "
            "PayLater, atau COD (Bayar di Tempat pas kurir sampai) ya Kak."
        )

    elif re.search(r"\b(ongkir|ongkos\s*kirim|ekspedisi|kurir|pengiriman|kirim)\b", pesan, re.IGNORECASE):
        return (
            "Pengiriman ke seluruh Indonesia bisa pakai JNE, J&T, atau SiCepat Kak. "
            "Hari ini lagi ada promo subsidi Gratis Ongkir!"
        )

    # --------------------------------------------------------------------------
    # 10. FAQ PILIH UKURAN ATAU MODEL SEPATU SPESIFIK
    # --------------------------------------------------------------------------
    elif match_ukuran:
        uk = konteks["ukuran"]
        nama_p = konteks["produk"]["nama"] if konteks["produk"] else "sepatu pilihan Kakak"
        return (
            f"Sip Kak, untuk {nama_p} ukuran {uk} stoknya ready! "
            f"Mau pesan berapa pasang nih? (Contoh ketik: 'Beli 2 pasang')"
        )

    elif re.search(r"\b(running|sneaker|casual|basket|sandal)\b", pesan, re.IGNORECASE):
        p = konteks["produk"]
        return (
            f"Pilihan mantap Kak! {p['nama']} harganya {rupiah(p['harga'])} (Ready Size {p['min_size']}-{p['max_size']}). "
            f"Kakak pakai ukuran berapa dan mau pesan berapa pasang?"
        )

    # --------------------------------------------------------------------------
    # 11. FAQ KATALOG / SEPATU APA SAJA YANG DIJUAL
    # --------------------------------------------------------------------------
    elif re.search(r"\b(produk|katalog|jual|ready|stok|sepatu|model|koleksi|apa\s*aja|apa\s*saja|cari|beli|pesan)\b", pesan, re.IGNORECASE):
        return (
            "Di Toko Sepatu Official kita punya 4 koleksi unggulan 100% Original Kak:\n"
            "  1. Sepatu Running Pro  - Rp 450.000 (Size 36-46)\n"
            "  2. Sneaker Casual      - Rp 275.000 (Size 36-45)\n"
            "  3. Sepatu Basket Elite - Rp 550.000 (Size 38-46)\n"
            "  4. Sandal Trendy       - Rp 150.000 (Size 36-44)\n"
            "  Kakak lagi pengen lihat model yang mana nih?"
        )

    # --------------------------------------------------------------------------
    # 12. FAQ PANDUAN LACAK RESI TANPA ANGKA
    # --------------------------------------------------------------------------
    elif re.search(r"\b(resi|lacak|posisi\s*paket|kiriman|status)\b", pesan, re.IGNORECASE):
        return "Boleh Kak, untuk cek posisi paket silakan ketik nomor resinya (6-10 digit angka), contoh: 'Resi: 889214'."

    # --------------------------------------------------------------------------
    # 13. SAPAAN & TERIMA KASIH (NGOBROL SANTAI)
    # --------------------------------------------------------------------------
    elif re.search(r"\b(halo|hai|hey|selamat\s*(pagi|siang|sore|malam)|pagi|siang|sore|malam|permisi|assalamualaikum|min|admin|kak)\b", pesan, re.IGNORECASE):
        return (
            "Halo juga Kak! Selamat datang di Toko Sepatu Official. "
            "Mau tanya sepatu apa aja, cek harga, alamat toko, atau lacak nomor pesanan nih?"
        )

    elif re.search(r"\b(makasih|terima\s*kasih|thanks|thx|oke|ok|sip|siap|mantap)\b", pesan, re.IGNORECASE):
        return "Sama-sama Kak! Kalau ada yang mau ditanyain lagi seputar sepatu atau pesanan, langsung chat aja ya!"

    # --------------------------------------------------------------------------
    # 14. FALLBACK (else): JIKA KALIMAT TIDAK JELAS -> ARAHKAN KE NO TELEPON/WA CS
    # --------------------------------------------------------------------------
    else:
        return (
            "Maaf Kak, maksud kalimatnya belum tertangkap oleh sistem otomatis kami.\n"
            "  Jika ada kendala khusus, silakan telepon/WhatsApp langsung CS kami di:\n"
            "  • WhatsApp Resmi : 0812-3456-7890  |  Call Center : (022) 731-8899\n"
            "  • Atau gunakan kata kunci: 'sepatu apa aja', 'harga', 'alamat', 'garansi', 'kontak', 'beli 2 pasang', atau 'Resi: 889214'."
        )


# ==============================================================================
# TAMPILAN AWAL CLEAN & INTERAKTIF (DENGAN DAFTAR TAG PANDUAN)
# ==============================================================================
def mulai_chat():
    print("=" * 78)
    print("               TOKO SEPATU OFFICIAL - VIRTUAL CUSTOMER SERVICE                ")
    print("=" * 78)
    print("  Tag Obrolan yang Tersedia:")
    print("  • 'Sepatu apa aja' / 'Katalog'    • 'Garansi' / 'Tukar ukuran'")
    print("  • 'Harga' / 'Promo'               • 'Beli 2 pasang ukuran 42' (Ukuran 36-46)")
    print("  • 'Alamat' / 'Jam buka'           • 'Resi: 889214'            (6-10 Digit)")
    print("  • 'Kontak' / 'No Telepon CS'      • 'No HP: 081234567890'     (10-13 Digit)")
    print("  (Ketik 'exit' kapan saja untuk mengakhiri obrolan)")
    print("-" * 78)
    print("Bot  : Halo Kak! Selamat datang di Toko Sepatu Official.")
    print("       Mau tanya sepatu apa aja, cek harga, alamat toko, atau lacak resi nih?")

    while True:
        try:
            pesan_user = input("\nAnda : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot  : Terima kasih sudah mampir di Toko Sepatu Official. Sampai jumpa Kak!")
            break

        if not pesan_user:
            continue

        if pesan_user.lower() in ["exit", "keluar", "quit", "selesai", "bye"]:
            print("Bot  : Terima kasih sudah ngobrol sama kami Kak! Kalau butuh bantuan cepat,")
            print("       silakan hubungi WA 0812-3456-7890 / (022) 731-8899. Semoga harimu menyenangkan!")
            print("=" * 78)
            break

        balasan = respon_chatbot(pesan_user)
        print(f"Bot  : {balasan}")


if __name__ == "__main__":
    mulai_chat()
