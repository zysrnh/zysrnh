# ==============================================================================
# PRAKTIKUM AI APPLICATION FOR BUSINESS - MODUL 5
# TOPIK: PENGEMBANGAN RULE-BASED CHATBOT BISNIS MENGGUNAKAN REGEX & PERCABANGAN
# Bidang Usaha : iTech Gadget Store (Toko Gadget & Service Center Resmi)
# File         : PraktikumS5.py
# ==============================================================================

import re
import sys

# Menjaga encoding terminal UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def chatbot_gadget(pesan_pelanggan):
    """
    Fungsi Rule-Based Chatbot Toko Gadget menggunakan kombinasi percabangan
    if-elif-else dan modul regular expressions (re.search) dengan flag re.IGNORECASE.
    """
    pesan = pesan_pelanggan.strip()
    
    # --------------------------------------------------------------------------
    # 1. ATURAN REGEX 1: Ekstraksi Entitas Angka Nomor Nota Servis (\d+)
    # --------------------------------------------------------------------------
    # Menangkap format 'Nota: 889214', 'Invoice #12345', 'Nota: 12 34 56', 'Servis 88124', dsb.
    match_nota = re.search(r'(?:nota|invoice|inv|resi|servis|service|tiket)[^\d\n]*(\d+(?:[\s-]+\d+)*)', pesan, re.IGNORECASE)
    if match_nota:
        no_nota_bersih = re.sub(r'\D', '', match_nota.group(1))
        return (f"[CS iTech]: Pelacakan Ditemukan! Perangkat dengan Nomor Nota #{no_nota_bersih} "
                f"saat ini berstatus 'Dalam Perbaikan oleh Teknisi Resmi' di Service Center iTech. "
                f"Estimasi selesai 1-2 hari kerja.")

    # --------------------------------------------------------------------------
    # 2. ATURAN REGEX 2: Ekstraksi Varian Kapasitas / Storage (\d+ GB / TB)
    # --------------------------------------------------------------------------
    match_storage = re.search(r'(\d+)\s*(?:gb|tb)', pesan, re.IGNORECASE)
    info_storage = f" varian {match_storage.group(0).upper()}" if match_storage else ""

    # --------------------------------------------------------------------------
    # 3. ATURAN REGEX 3: Ucapan Terima Kasih & Penutup
    # --------------------------------------------------------------------------
    if re.search(r'\b(makasih|terima\s*kasih|makasi|thanks|thx|tengkyu|matur\s*nuwun|nuhun|ok\s*makasih|sip|siap|bye|dadah|oke|ok)\b', pesan, re.IGNORECASE):
        return "[CS iTech]: Sama-sama Kak! Senang bisa membantu Anda di iTech Gadget Store. Semoga harimu menyenangkan!"

    # --------------------------------------------------------------------------
    # 4. ATURAN REGEX 4: Menangani Reaksi Frustrasi / Bingung / Kata Kasar
    # --------------------------------------------------------------------------
    elif re.search(r'\b(aneh|bingung|ga\s*nyambung|gak\s*nyambung|gajelas|jelek|buruk|kecewa|lama|lemot|kontol|anjing|bangsat|tai|bego|goblok)\b', pesan, re.IGNORECASE):
        return ("[CS iTech]: Mohon maaf atas ketidaknyamanannya Kak! Kami siap membantu langsung. "
                "Kakak bisa pilih info: 1. Katalog HP, 2. Cek Harga, 3. Simulasi Cicilan, atau 4. Lacak Nota Servis.")

    # --------------------------------------------------------------------------
    # 5. ATURAN REGEX 5: Sapaan Pelanggan (Word Boundary & Case Insensitive)
    # --------------------------------------------------------------------------
    elif re.search(r'\b(halo|hai|hey|hei|pagi|siang|sore|malam|assalam|permisi|spada|ping|p\b|woy|min|admin|tes|test)\b', pesan, re.IGNORECASE):
        return "[CS iTech]: Halo Kak! Selamat datang di iTech Gadget Store. Ada yang bisa kami bantu seputar produk gadget, promo harga, cicilan, atau servis?"

    # --------------------------------------------------------------------------
    # 6. ATURAN REGEX 6: Menanyakan Spesifikasi & Fitur Perangkat
    # --------------------------------------------------------------------------
    elif re.search(r'\b(spek|spesifikasi|ram|kamera|layar|batre|baterai|chipset|processor|prosesor|fitur|performa)\b', pesan, re.IGNORECASE):
        return ("[CS iTech]: Spesifikasi gadget unggulan kami: "
                "• iPhone 15: Chip A16/A17 Pro, Kamera 48MP, Dynamic Island, USB-C. "
                "• Samsung S24 Ultra: Snapdragon 8 Gen 3, Kamera 200MP + AI Zoom, Layar Flat 120Hz. "
                "• MacBook Air M3: Chip M3 8-Core CPU/10-Core GPU, Baterai 18 Jam.")

    # --------------------------------------------------------------------------
    # 7. ATURAN REGEX 7: Menanyakan Harga, Promo, Diskon, & Cashback
    # --------------------------------------------------------------------------
    elif re.search(r'\b(harga|pricelist|biaya|tarif|berapaan|berapa|diskon|promo|cashback|murah|potongan|nego|ongkir|ongkos)\b', pesan, re.IGNORECASE):
        return (f"[CS iTech]: Daftar harga resmi gadget{info_storage}: "
                f"• iPhone 15 Series : Mulai dari Rp 13.999.000 | "
                f"• Samsung Galaxy S24 : Mulai dari Rp 12.499.000 | "
                f"• MacBook Air M2/M3 : Mulai dari Rp 16.299.000. "
                f"(Tersedia promo cashback hingga Rp 1.000.000 dan bebas ongkir seluruh Indonesia!)")

    # --------------------------------------------------------------------------
    # 8. ATURAN REGEX 8: Katalog, Beli HP, Rekomendasi, Ketersediaan Stok
    # --------------------------------------------------------------------------
    elif re.search(r'\b(beli|order|pesan|cari|rekomendasi|katalog|produk|barang|stok|ready|jual|hp|handphone|smartphone|gadget|android|ios|iphone|samsung|macbook|ipad|laptop|watch|airpods|tws)\b', pesan, re.IGNORECASE):
        return ("[CS iTech]: Pilihan produk best seller 100% Original bergaransi resmi: "
                "1. Flagship: iPhone 15 / 15 Pro, Samsung Galaxy S24 Ultra, Z Fold/Flip 6. "
                "2. Mid-Range: Samsung Galaxy A55 5G, iPhone 13 128GB. "
                "3. Laptop & Tablet: MacBook Air M3, iPad Gen 10. "
                "Kakak tertarik tipe yang mana?")

    # --------------------------------------------------------------------------
    # 9. ATURAN REGEX 9: Metode Pembayaran, Cicilan 0%, Kredit, Paylater
    # --------------------------------------------------------------------------
    elif re.search(r'\b(cicil|cicilan|kredit|kredivo|spaylater|paylater|akulaku|indodana|angsuran|kartu\s*kredit|qris|transfer|bca|mandiri|bni|cimb|cod|bayar)\b', pesan, re.IGNORECASE):
        return ("[CS iTech]: Metode pembayaran fleksibel: "
                "• Cicilan 0% Kartu Kredit BCA, Mandiri, BNI, CIMB (hingga 24 bulan). "
                "• Paylater tanpa kartu kredit: Kredivo, Shopee PayLater, Indodana, Akulaku. "
                "• Cashless: QRIS, Transfer Bank, Debit, dan COD di store.")

    # --------------------------------------------------------------------------
    # 10. ATURAN REGEX 10: Kebijakan Garansi Resmi (iBox & SEIN) serta Retur
    # --------------------------------------------------------------------------
    elif re.search(r'\b(garansi|retur|rusak|klaim|servis|service|benerin|mati|pecah|ibox|sein|ori|original|asli|resmi|cacat)\b', pesan, re.IGNORECASE):
        return ("[CS iTech]: Seluruh produk bergaransi resmi 1 tahun (Apple garansi iBox/Digimap, Samsung garansi SEIN). "
                "Kami memberikan garansi toko 7 hari ganti unit baru jika cacat pabrik. "
                "Untuk lacak status servis Anda, ketik format: 'Nota: [NomorNota]'.")

    # --------------------------------------------------------------------------
    # 11. ATURAN REGEX 11: Lokasi Store Offline, Alamat, Jam Operasional
    # --------------------------------------------------------------------------
    elif re.search(r'\b(alamat|lokasi|toko|cabang|buka|tutup|jam|offline|posisi|dimana|daerah|bandung|tempat)\b', pesan, re.IGNORECASE):
        return ("[CS iTech]: Outlet resmi iTech Gadget Store beralamat di: "
                "Jl. Soekarno-Hatta No. 456, Bandung. Buka setiap hari pukul 09.00 - 21.00 WIB.")

    # --------------------------------------------------------------------------
    # 12. ATURAN REGEX 12: Kontak WhatsApp & CS Manusia
    # --------------------------------------------------------------------------
    elif re.search(r'\b(kontak|hubungi|whatsapp|wa|telepon|telp|call|nomor|cs|manusia|orang\s*asli)\b', pesan, re.IGNORECASE):
        return "[CS iTech]: Hubungi CS officer kami langsung via WhatsApp: 0812-3456-7890 (Aktif 09.00 - 21.00 WIB)."

    # --------------------------------------------------------------------------
    # 13. ATURAN REGEX 13: Format Panduan Lacak Nota
    # --------------------------------------------------------------------------
    elif re.search(r'\b(nota|lacak|resi|posisi paket|status barang)\b', pesan, re.IGNORECASE):
        return "[CS iTech]: Untuk melacak perbaikan servis atau pesanan, gunakan format: 'Nota: [NomorNota]' (Contoh: Nota: 889214)."

    # --------------------------------------------------------------------------
    # 14. ATURAN DEFAULT (FALLBACK)
    # --------------------------------------------------------------------------
    else:
        return ("[CS iTech]: Maaf Kak, pertanyaan belum dipahami oleh sistem kami. "
                "Silakan ketik kata kunci seperti: 'mau beli hp', 'harga iphone 15', 'cicilan', "
                "'garansi', 'lokasi toko', atau format 'Nota: 889214'.")


# ==============================================================================
# SIMULASI PENGUJIAN LENGKAP SEMUA SKENARIO (SYARAT TUGAS MANDIRI 5)
# ==============================================================================
if __name__ == "__main__":
    print("=" * 80)
    print("       SIMULASI PENGUJIAN CHATBOT REGEX TOKO GADGET (SEMUA SKENARIO)")
    print("=" * 80)

    skenario_pengujian = [
        "Halo admin, selamat pagi!",
        "Saya mau beli hp baru nih",
        "Berapa harga iPhone 15 yang 128 GB?",
        "Spesifikasi Samsung S24 Ultra layarnya berapa hz?",
        "Bisa bayar pakai cicilan kredivo atau kartu kredit?",
        "Tolong lacak status servis saya dengan Nota: 88 92 14",
        "Apakah produknya garansi resmi iBox?",
        "Alamat toko offline di Bandung sebelah mana?",
        "Makasih infonya min",
        "Cuaca hari ini apakah hujan?"  # Menguji fallback (else)
    ]

    for idx, teks in enumerate(skenario_pengujian, 1):
        print(f"\n[Uji {idx:02d}] Pelanggan : \"{teks}\"")
        print(f"         Jawaban   : {chatbot_gadget(teks)}")

    print("\n" + "=" * 80)
    print(">> Semua skenario pengujian berhasil dieksekusi dengan tepat tanpa error!")
    print("=" * 80)
