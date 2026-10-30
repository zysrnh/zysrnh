# ==============================================================================
# SISTEM SILSILAH KELUARGA LENGKAP STATUS PERNIKAHAN & LOGIKA FOL (TERMINAL)
# ==============================================================================
from kanren.facts import Relation, facts
from kanren.core import var, run, conde

# ------------------------------------------------------------------------------
# 1. ATURAN LOGIKA ORDE PERTAMA (FOL RULES)
# ------------------------------------------------------------------------------
parent = Relation()

def tidak_sama(x, y):
    type_var = type(var())
    def tidak_sama_goal(state):
        val_x = state.subsumes(x) if hasattr(state, 'subsumes') else state.get(x, x)
        val_y = state.subsumes(y) if hasattr(state, 'subsumes') else state.get(y, y)
        if type(val_x) == type_var or type(val_y) == type_var:
            yield state
        elif val_x != val_y:
            yield state
    return tidak_sama_goal

def grandfather(x, y):
    z = var()
    return conde((parent(x, z), parent(z, y)))

def sibling(x, y):
    z = var()
    return conde((parent(z, x), parent(z, y), tidak_sama(x, y)))

def uncle(x, y):
    z = var()
    return conde((parent(z, y), sibling(x, z)))


# ------------------------------------------------------------------------------
# 2. INPUT INTERAKTIF STEP-BY-STEP (TANYA NIKAH & ANAK)
# ------------------------------------------------------------------------------
print("=" * 70)
print("     PROGRAM SILSILAH KELUARGA & PENELUSURAN LOGIKA INTERAKTIF     ")
print("=" * 70)
print("Pilih Mode:")
print("1. Bikin Silsilah Sendiri (Tanya Kakek, Pasangan, Anak, & Cucu)")
print("2. Gunakan Data Preset Modul (Keluarga Slamet & Pasangan)")

pilihan_mode = input("\nPilihan Anda [1/2] (Default 1): ").strip()

fakta_list = []
pasangan_map = {} # Mencatat siapa menikah dengan siapa
mertua_map = {}   # Mencatat mertua
branches = []

if pilihan_mode == "2":
    # Data Default Modul
    kakek = "Slamet"
    nenek = "Siti"
    pasangan_map[kakek] = nenek
    pasangan_map[nenek] = kakek
    
    branches = [
        {"anak": "Amin", "pasangan": "Rina", "cucu": ["Badu", "Budi"]},
        {"anak": "Anang", "pasangan": "Dewi", "cucu": ["Didi", "Dadi"]}
    ]
    
    for b in branches:
        pasangan_map[b["anak"]] = b["pasangan"]
        pasangan_map[b["pasangan"]] = b["anak"]
        mertua_map[b["pasangan"]] = f"{kakek} & {nenek}"
        fakta_list.append((kakek, b["anak"]))
        fakta_list.append((nenek, b["anak"]))
        for c in b["cucu"]:
            fakta_list.append((b["anak"], c))
            fakta_list.append((b["pasangan"], c))
            
    print("\n>> Berhasil memuat data silsilah Keluarga Slamet & Pasangan!")
else:
    # --- INPUT STEP-BY-STEP DI TERMINAL ---
    print("\n--- [LANGKAH 1: KAKEK & NENEK (GENERASI PERTAMA)] ---")
    kakek = input("1. Masukkan nama Kakek / Kepala Keluarga : ").strip().capitalize()
    while not kakek:
        kakek = input("   Nama tidak boleh kosong, masukkan nama : ").strip().capitalize()
        
    nenek = input(f"2. {kakek} menikah dengan siapa? (Nama Nenek) : ").strip().capitalize()
    while not nenek:
        nenek = input("   Nama Nenek tidak boleh kosong           : ").strip().capitalize()
        
    pasangan_map[kakek] = nenek
    pasangan_map[nenek] = kakek

    while True:
        try:
            jml_anak = int(input(f"\n3. Berapa jumlah anak dari {kakek} & {nenek}? : "))
            if jml_anak > 0:
                break
            print("   Jumlah anak minimal 1!")
        except ValueError:
            print("   Masukkan angka yang valid!")

    print(f"\n--- [LANGKAH 2: DATA ANAK & PASANGANNYA] ---")
    for i in range(1, jml_anak + 1):
        print(f"\n>> Data Anak ke-{i}:")
        nama_anak = input(f"   Nama anak ke-{i} : ").strip().capitalize()
        fakta_list.append((kakek, nama_anak))
        fakta_list.append((nenek, nama_anak))
        
        tanya_nikah = input(f"   Apakah {nama_anak} sudah menikah? (y/n) : ").strip().lower()
        nama_pasangan = ""
        cucu_list = []
        
        if tanya_nikah == 'y':
            nama_pasangan = input(f"   {nama_anak} menikah dengan siapa? (Nama Menantu) : ").strip().capitalize()
            pasangan_map[nama_anak] = nama_pasangan
            pasangan_map[nama_pasangan] = nama_anak
            mertua_map[nama_pasangan] = f"{kakek} & {nenek}"
            
            tanya_anak = input(f"   Apakah {nama_anak} & {nama_pasangan} sudah punya anak? (y/n) : ").strip().lower()
            if tanya_anak == 'y':
                while True:
                    try:
                        jml_cucu = int(input(f"   Berapa jumlah anak mereka? : "))
                        if jml_cucu >= 0:
                            break
                    except ValueError:
                        print("   Masukkan angka yang valid!")
                        
                for j in range(1, jml_cucu + 1):
                    nama_cucu = input(f"     Nama anak ke-{j} (Cucu) : ").strip().capitalize()
                    cucu_list.append(nama_cucu)
                    fakta_list.append((nama_anak, nama_cucu))
                    fakta_list.append((nama_pasangan, nama_cucu))
                    
        branches.append({"anak": nama_anak, "pasangan": nama_pasangan, "cucu": cucu_list})

# Daftarkan fakta ke Kanren
facts(parent, *fakta_list)

# Kumpulkan semua nama unik untuk daftar pilihan bernomor
semua_anggota = []
for p_name, c_name in fakta_list:
    if p_name not in semua_anggota: semua_anggota.append(p_name)
    if c_name not in semua_anggota: semua_anggota.append(c_name)


# ------------------------------------------------------------------------------
# 3. BAGAN POHON KELUARGA (TERMINAL TREE - JELAS & TIDAK KEPOTONG)
# ------------------------------------------------------------------------------
print("\n" + "=" * 75)
print("                     BAGAN POHON SILSILAH KELUARGA                     ")
print("=" * 75)
print(f"   [Kakek] {kakek}  <=== Menikah dengan ===>  [Nenek] {nenek}")
print("      |")
for i, b in enumerate(branches):
    is_last = (i == len(branches) - 1)
    conn = "      \\-- " if is_last else "      |-- "
    p_info = f" <=== Menikah dengan ===> [Menantu] {b['pasangan']}" if b['pasangan'] else " (Belum Menikah)"
    print(f"{conn}[Anak] {b['anak']}{p_info}")
    
    sub_prefix = "          " if is_last else "      |   "
    for j, c in enumerate(b["cucu"]):
        c_conn = "\\-- " if j == len(b["cucu"]) - 1 else "|-- "
        print(f"{sub_prefix}{c_conn}[Cucu] {c}")
print("=" * 75)


# ------------------------------------------------------------------------------
# 4. FUNGSI PEMILIHAN NAMA & PENJELASAN POSISI
# ------------------------------------------------------------------------------
def pilih_orang(prompt_text):
    print("\nDaftar Anggota Keluarga Terdaftar:")
    for idx, nama in enumerate(semua_anggota, 1):
        pas_str = f" (💍 {pasangan_map[nama]})" if nama in pasangan_map else ""
        print(f"  [{idx}] {nama}{pas_str}")
    while True:
        masukan = input(prompt_text).strip()
        if masukan.isdigit():
            i = int(masukan) - 1
            if 0 <= i < len(semua_anggota):
                return semua_anggota[i]
        for nama in semua_anggota:
            if nama.lower() == masukan.lower():
                return nama
        print("Ketik nomor yang ada di daftar di atas!")

q = var()

while True:
    print("\n" + "=" * 55)
    print("      MENU PENGECEKAN LOGIKA SILSILAH KELUARGA      ")
    print("=" * 55)
    print("1. Penjelasan Posisi Lengkap ('Dia itu Siapa dari Siapa')")
    print("2. Tanya Relasi 2 Orang ('Si A itu Siapanya Si B?')")
    print("3. Cari Kakek dari seseorang")
    print("4. Cari Paman dari seseorang")
    print("5. Cari Saudara Kandung dari seseorang")
    print("6. Jalankan 4 Kueri Wajib Modul Praktikum")
    print("0. Selesai / Keluar")
    print("=" * 55)
    
    pilihan = input("Pilih menu [0-6]: ").strip()
    
    # --- FITUR 1: DIA ITU SIAPA DARI SIAPA ---
    if pilihan == "1":
        nama = pilih_orang(">> Pilih nomor orang yang ingin dijelaskan: ")
        ayah_ibu = run(0, q, parent(q, nama))
        kakek_list = run(0, q, grandfather(q, nama))
        saudara = run(0, q, sibling(q, nama))
        paman_list = run(0, q, uncle(q, nama))
        anak_list = run(0, q, parent(nama, q))
        pasangan = pasangan_map.get(nama)
        mertua = mertua_map.get(nama)
        
        print("\n" + "-" * 60)
        print(f"     PENJELASAN POSISI SILSILAH: {nama.upper()}     ")
        print("-" * 60)
        print(f"- Status Menikah  : {'Menikah dengan 💍 ' + pasangan if pasangan else 'Belum Menikah'}")
        if mertua:
            print(f"- Status Menantu  : Menantu dari {mertua}")
        if ayah_ibu:
            print(f"- Orang Tua / Ayah: {', '.join(ayah_ibu)}")
        else:
            print(f"- Generasi        : Generasi Pertama / Kakek-Nenek")
        if kakek_list:
            print(f"- Kakek           : {', '.join(kakek_list)}")
        if saudara:
            print(f"- Saudara Kandung : {', '.join(saudara)}")
        if paman_list:
            print(f"- Paman (Om)      : {', '.join(paman_list)}")
        if anak_list:
            print(f"- Anak-anak       : {', '.join(anak_list)}")
        print("-" * 60)

    # --- FITUR 2: TANYA RELASI 2 ORANG ---
    elif pilihan == "2":
        a = pilih_orang(">> Pilih Orang Pertama (A): ")
        b = pilih_orang(">> Pilih Orang Kedua   (B): ")
        
        if a == b:
            print(f"\n>> {a} dan {b} adalah orang yang sama.")
        elif pasangan_map.get(a) == b:
            print(f"\n>> HASIL: {a} dan {b} adalah PASANGAN SUAMI-ISTRI.")
        elif mertua_map.get(b) and a in mertua_map[b]:
            print(f"\n>> HASIL: {a} adalah MERTUA dari {b}.")
        elif mertua_map.get(a) and b in mertua_map[a]:
            print(f"\n>> HASIL: {a} adalah MENANTU dari {b}.")
        elif b in run(0, q, parent(a, q)):
            print(f"\n>> HASIL: {a} adalah ORANG TUA dari {b}.")
        elif a in run(0, q, parent(b, q)):
            print(f"\n>> HASIL: {a} adalah ANAK dari {b}.")
        elif b in run(0, q, grandfather(a, q)):
            print(f"\n>> HASIL: {a} adalah KAKEK dari {b}.")
        elif a in run(0, q, grandfather(b, q)):
            print(f"\n>> HASIL: {a} adalah CUCU dari {b}.")
        elif b in run(0, q, sibling(a, q)):
            print(f"\n>> HASIL: {a} dan {b} adalah SAUDARA KANDUNG.")
        elif b in run(0, q, uncle(a, q)):
            print(f"\n>> HASIL: {a} adalah PAMAN dari {b}.")
        else:
            print(f"\n>> HASIL: Hubungan keluarga ipar / jauh antara {a} dan {b}.")

    elif pilihan == "3":
        nama = pilih_orang(">> Cari Kakek dari siapa?: ")
        hasil = run(0, q, grandfather(q, nama))
        print(f"\n>> Hasil: Kakek dari {nama} adalah: {', '.join(hasil) if hasil else 'Tidak ditemukan'}")

    elif pilihan == "4":
        nama = pilih_orang(">> Cari Paman dari siapa?: ")
        hasil = run(0, q, uncle(q, nama))
        print(f"\n>> Hasil: Paman dari {nama} adalah: {', '.join(hasil) if hasil else 'Tidak ditemukan'}")

    elif pilihan == "5":
        nama = pilih_orang(">> Cari Saudara dari siapa?: ")
        hasil = run(0, q, sibling(q, nama))
        print(f"\n>> Hasil: Saudara kandung dari {nama} adalah: {', '.join(hasil) if hasil else 'Anak tunggal'}")

    elif pilihan == "6":
        print("\n" + "=" * 55)
        print("HASIL 4 KUERI PEMBUKTIAN KASUS MODUL PRAKTIKUM:")
        print("=" * 55)
        print("1. Kakek Badu   :", list(run(0, q, grandfather(q, "Badu"))) or "Tidak ada di data")
        print("2. Paman Didi   :", list(run(0, q, uncle(q, "Didi"))) or "Tidak ada di data")
        print("3. Saudara Budi :", list(run(0, q, sibling(q, "Budi"))) or "Tidak ada di data")
        print("4. Paman Badu   :", list(run(0, q, uncle(q, "Badu"))) or "Tidak ada di data")
        print("=" * 55)

    elif pilihan == "0":
        print("\nProgram selesai. Terima kasih!")
        break
