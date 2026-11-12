# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 7 (POST-TEST CHALLENGE)
# STUDI KASUS : SISTEM PAKAR SELEKSI BEASISWA KELAYAKAN MAHASISWA IDE LPKIA
# ==============================================================================

import csv
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CSV_FILENAME = (
    os.path.join(os.path.dirname(__file__), "dataset_beasiswa_lpkia_100.csv")
    if "__file__" in globals()
    else "dataset_beasiswa_lpkia_100.csv"
)

HEADER_KOLOM = [
    "nim",
    "nama",
    "prodi",
    "ipk",
    "penghasilan_ortu",
    "prestasi_akademik",
    "organisasi_aktif",
]

DEFAULT_CSV_DATA = [
    HEADER_KOLOM,
    ["250414001", "Rizky Pratama", "Teknik Informatika", "3.78", "2400000", "Tidak", "Tidak"],
    ["250414002", "Nadia Maharani", "Sistem Informasi", "3.65", "5500000", "Ya", "Ya"],
    ["250414003", "Dimas Anggara", "Teknik Informatika", "3.25", "2200000", "Tidak", "Ya"],
    ["250414004", "Siti Nurhaliza", "Sistem Informasi", "3.85", "2800000", "Ya", "Ya"],
]


def parse_ipk(nilai):
    """Parsing nilai IPK (mendukung format titik maupun koma)."""
    if isinstance(nilai, (int, float)):
        return float(nilai)
    teks = str(nilai or "").strip().replace(",", ".")
    if not teks:
        return -1.0
    try:
        return float(teks)
    except ValueError:
        return -1.0


def evaluasi_ipk(ipk):
    """
    Validasi dan klasifikasi IPK memakai percabangan if-elif-else:
    - < 0.00 atau > 4.00 : Tidak valid (otomatis gagal)
    - 3.50 <= ipk <= 4.00 : Memenuhi syarat IPK (>= 3.5)
    - 0.00 <= ipk < 3.50  : Tidak memenuhi syarat IPK
    """
    if ipk < 0.0 or ipk > 4.0:
        return False, "TIDAK VALID"
    elif ipk >= 3.5:
        return True, "MEMENUHI"
    else:
        return False, "GAGAL"


def _parse_rupiah_int(nilai):
    if isinstance(nilai, (int, float)):
        return max(0, int(nilai))
    digit = re.sub(r"\D", "", str(nilai or ""))
    return int(digit) if digit else 0


def _parse_bool_ya(nilai):
    if isinstance(nilai, bool):
        return nilai
    return str(nilai or "").strip().lower() in ("ya", "true", "1", "yes")


def _normalisasi_profil(row, idx=1):
    nim_default = f"250414{idx:03d}"
    return {
        "nim": str(row.get("nim") or nim_default).strip(),
        "nama": str(row.get("nama") or f"Mahasiswa {idx}").strip(),
        "prodi": str(row.get("prodi") or "Teknik Informatika").strip(),
        "ipk": parse_ipk(row.get("ipk", 0)),
        "penghasilan_ortu": _parse_rupiah_int(
            row.get("penghasilan_ortu", row.get("ortu", 0))
        ),
        "prestasi_akademik": _parse_bool_ya(
            row.get("prestasi_akademik", row.get("prestasi", False))
        ),
        "organisasi_aktif": _parse_bool_ya(
            row.get("organisasi_aktif", row.get("org", False))
        ),
    }


def siapkan_dataset_csv():
    """Membaca dataset CSV mahasiswa (otomatis membuat contoh awal jika belum ada)."""
    if not os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(DEFAULT_CSV_DATA)

    profil_list = []
    with open(CSV_FILENAME, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            profil_list.append(_normalisasi_profil(row, idx))
    return profil_list


# ==============================================================================
# 1. EKSTRAKSI FAKTA GEJALA / ATRIBUT MAHASISWA
# ==============================================================================
def ekstrak_fakta_awal(mhs):
    """
    Fakta Gejala / Atribut sesuai soal:
    1. IPK >= 3.5 (valid di rentang 0.00 - 4.00)
    2. OrangTua_KurangMampu (Penghasilan Orang Tua < Rp 3.000.000)
    3. Prestasi_Akademik
    4. Organisasi_Aktif
    """
    fakta = []
    ipk_memenuhi, _ = evaluasi_ipk(mhs["ipk"])
    if ipk_memenuhi:
        fakta.append("IPK >= 3.5")

    if mhs["penghasilan_ortu"] < 3000000:
        fakta.append("OrangTua_KurangMampu")

    if mhs["prestasi_akademik"]:
        fakta.append("Prestasi_Akademik")

    if mhs["organisasi_aktif"]:
        fakta.append("Organisasi_Aktif")

    return fakta


# ==============================================================================
# 2. MESIN INFERENSI FORWARD CHAINING (DATA-DRIVEN)
# ==============================================================================
def forward_chaining_beasiswa(fakta_awal, cetak_log=True):
    """
    Evaluasi aturan produksi Forward Chaining:
    - R1: IF IPK >= 3.5 AND OrangTua_KurangMampu THEN Layak_Ekonomi
    - R2: IF IPK >= 3.5 AND (Prestasi_Akademik OR Organisasi_Aktif) THEN Layak_Prestasi
    - R3: IF Layak_Ekonomi OR Layak_Prestasi THEN BEASISWA_DISETUJUI
    """
    known_facts = set(fakta_awal)
    aturan_aktif = []
    iterasi = 1
    ada_fakta_baru = True

    if cetak_log:
        print(f"  [START] Fakta Awal : {sorted(list(known_facts))}")

    while ada_fakta_baru:
        ada_fakta_baru = False
        if cetak_log:
            print(f"  --- Iterasi ke-{iterasi} ---")

        syarat_r1 = ("IPK >= 3.5" in known_facts) and ("OrangTua_KurangMampu" in known_facts)
        if syarat_r1 and ("Layak_Ekonomi" not in known_facts):
            known_facts.add("Layak_Ekonomi")
            aturan_aktif.append("R1")
            if cetak_log:
                print("    [+] R1 Terpemicu: IF IPK >= 3.5 AND OrangTua_KurangMampu THEN Layak_Ekonomi")
            ada_fakta_baru = True
            iterasi += 1
            continue
        elif cetak_log:
            st_r1 = "Sudah diketahui" if "Layak_Ekonomi" in known_facts else "Syarat belum terpenuhi"
            print(f"    [-] R1 Dilewati ({st_r1})")

        syarat_r2 = ("IPK >= 3.5" in known_facts) and (
            ("Prestasi_Akademik" in known_facts) or ("Organisasi_Aktif" in known_facts)
        )
        if syarat_r2 and ("Layak_Prestasi" not in known_facts):
            known_facts.add("Layak_Prestasi")
            aturan_aktif.append("R2")
            if cetak_log:
                print("    [+] R2 Terpemicu: IF IPK >= 3.5 AND (Prestasi_Akademik OR Organisasi_Aktif) THEN Layak_Prestasi")
            ada_fakta_baru = True
            iterasi += 1
            continue
        elif cetak_log:
            st_r2 = "Sudah diketahui" if "Layak_Prestasi" in known_facts else "Syarat belum terpenuhi"
            print(f"    [-] R2 Dilewati ({st_r2})")

        syarat_r3 = ("Layak_Ekonomi" in known_facts) or ("Layak_Prestasi" in known_facts)
        if syarat_r3 and ("BEASISWA_DISETUJUI" not in known_facts):
            known_facts.add("BEASISWA_DISETUJUI")
            aturan_aktif.append("R3")
            if cetak_log:
                print("    [+] R3 Terpemicu: IF Layak_Ekonomi OR Layak_Prestasi THEN BEASISWA_DISETUJUI")
            ada_fakta_baru = True
            iterasi += 1
            continue
        elif cetak_log:
            st_r3 = "Sudah diketahui" if "BEASISWA_DISETUJUI" in known_facts else "Syarat belum terpenuhi"
            print(f"    [-] R3 Dilewati ({st_r3})")

    disetujui = "BEASISWA_DISETUJUI" in known_facts
    if cetak_log:
        print(f"  [FAKTA AKHIR]      : {sorted(list(known_facts))}")
        print(f"  [KEPUTUSAN FC]     : {'BEASISWA_DISETUJUI (LOLOS)' if disetujui else 'BEASISWA_DITOLAK (TIDAK LOLOS)'}")
    return disetujui, known_facts, aturan_aktif


# ==============================================================================
# 3. MESIN INFERENSI BACKWARD CHAINING (GOAL-DRIVEN)
# ==============================================================================
ATURAN_BACKWARD = {
    "BEASISWA_DISETUJUI": [
        ("R3 [Jalur Ekonomi]", ["Layak_Ekonomi"]),
        ("R3 [Jalur Prestasi]", ["Layak_Prestasi"]),
    ],
    "Layak_Ekonomi": [
        ("R1", ["IPK >= 3.5", "OrangTua_KurangMampu"]),
    ],
    "Layak_Prestasi": [
        ("R2 [Prestasi Akademik]", ["IPK >= 3.5", "Prestasi_Akademik"]),
        ("R2 [Organisasi Aktif]", ["IPK >= 3.5", "Organisasi_Aktif"]),
    ],
}


def backward_chaining_beasiswa(goal, known_facts, depth=0, cetak_log=True):
    """Membuktikan hipotesis 'BEASISWA_DISETUJUI' secara rekursif (Backward Chaining)."""
    indent = "    " + ("  " * depth)

    if goal in known_facts:
        if cetak_log:
            print(f"{indent}[VALID] Fakta '{goal}' ditemukan pada data mahasiswa.")
        return True

    if goal not in ATURAN_BACKWARD:
        if cetak_log:
            print(f"{indent}[GAGAL] Fakta '{goal}' TIDAK ditemukan pada data mahasiswa.")
        return False

    for nama_aturan, subgoals in ATURAN_BACKWARD[goal]:
        if cetak_log:
            print(f"{indent}[CEK {nama_aturan}] Membuktikan '{goal}' dengan syarat: {subgoals}")
        semua_terpenuhi = True
        for sg in subgoals:
            if not backward_chaining_beasiswa(sg, known_facts, depth + 1, cetak_log):
                semua_terpenuhi = False
                break

        if semua_terpenuhi:
            known_facts.add(goal)
            if cetak_log:
                print(f"{indent}[TERBUKTI] Sub-goal '{goal}' berhasil dibuktikan melalui {nama_aturan}!")
            return True

    if cetak_log:
        print(f"{indent}[TIDAK TERBUKTI] Goal '{goal}' gagal dibuktikan.")
    return False


# ==============================================================================
# 4. FILTERING & TABEL MATRIKS PENGECEKAN + PENGUJIAN 3 PROFIL
# ==============================================================================
def filter_mahasiswa(daftar_mhs, query="", status="all", rule="all"):
    """Filter daftar mahasiswa berdasarkan pencarian NIM/nama, status keputusan, atau rule."""
    hasil = []
    q = str(query or "").strip().lower()
    for m in daftar_mhs:
        if q and q not in f"{m['nim']} {m['nama']}".lower():
            continue
        fakta = ekstrak_fakta_awal(m)
        lolos, facts_akhir, _ = forward_chaining_beasiswa(fakta, cetak_log=False)
        ipk_ok, _ = evaluasi_ipk(m["ipk"])

        if status == "disetujui" and not lolos:
            continue
        elif status == "ditolak" and lolos:
            continue

        if rule == "r1" and "Layak_Ekonomi" not in facts_akhir:
            continue
        elif rule == "r2" and "Layak_Prestasi" not in facts_akhir:
            continue
        elif rule == "r1r2" and not (
            "Layak_Ekonomi" in facts_akhir and "Layak_Prestasi" in facts_akhir
        ):
            continue
        elif rule == "ipk_ok" and not ipk_ok:
            continue
        elif rule == "ipk_no" and ipk_ok:
            continue

        hasil.append(m)
    return hasil


def cetak_tabel_pengecekan(daftar_mhs):
    print("\nTABEL MATRIKS PENGECEKAN KELAYAKAN BEASISWA:")
    print("=" * 108)
    header = (
        f"{'No':<3} | {'NIM & Nama':<24} | {'IPK (>=3.5)':<13} | {'Ortu (<3Jt)':<15} | "
        f"{'Pres':<5} | {'Org':<5} | {'R1':<5} | {'R2':<5} | {'Keputusan Akhir'}"
    )
    print(header)
    print("-" * 108)

    for i, m in enumerate(daftar_mhs, 1):
        fakta = ekstrak_fakta_awal(m)
        lolos, facts_akhir, _ = forward_chaining_beasiswa(fakta, cetak_log=False)
        ipk_ok, ipk_status = evaluasi_ipk(m["ipk"])

        if ipk_status == "TIDAK VALID":
            tag_ipk = "INV"
        elif ipk_ok:
            tag_ipk = "YA"
        else:
            tag_ipk = "TDK"

        cek_ipk = f"{m['ipk']:.2f} [{tag_ipk}]"
        cek_ortu = f"Rp{m['penghasilan_ortu'] / 1000000:.2f}Jt [{'YA' if m['penghasilan_ortu'] < 3000000 else 'TDK'}]"
        cek_pres = "YA" if m["prestasi_akademik"] else "TDK"
        cek_org = "YA" if m["organisasi_aktif"] else "TDK"
        cek_r1 = "AKTIF" if "Layak_Ekonomi" in facts_akhir else "-"
        cek_r2 = "AKTIF" if "Layak_Prestasi" in facts_akhir else "-"
        keputusan = "BEASISWA_DISETUJUI" if lolos else "DITOLAK"
        identitas = f"{m['nim']} {m['nama']}"[:24]

        print(
            f"{i:<3} | {identitas:<24} | {cek_ipk:<13} | {cek_ortu:<15} | "
            f"{cek_pres:<5} | {cek_org:<5} | {cek_r1:<5} | {cek_r2:<5} | {keputusan}"
        )
    print("=" * 108)


def jalankan_pengujian_3_profil():
    semua_profil = siapkan_dataset_csv()
    tiga_profil_uji = semua_profil[:3]

    print("=" * 105)
    print("           SISTEM PAKAR SELEKSI BEASISWA KELAYAKAN MAHASISWA IDE LPKIA (SESI 7 - CHALLENGE)           ")
    print("=" * 105)

    for idx, mhs in enumerate(tiga_profil_uji, 1):
        fakta_awal = ekstrak_fakta_awal(mhs)
        rp_ortu = f"Rp {mhs['penghasilan_ortu']:,}".replace(",", ".")

        print(f"\nPROFIL UJI #{idx}: {mhs['nama']} (NIM: {mhs['nim']} - {mhs['prodi']})")
        print(
            f"  Atribut : IPK = {mhs['ipk']:.2f} | Penghasilan Ortu = {rp_ortu} | "
            f"Prestasi = {'Ya' if mhs['prestasi_akademik'] else 'Tidak'} | "
            f"Organisasi = {'Ya' if mhs['organisasi_aktif'] else 'Tidak'}"
        )
        print("-" * 105)

        print("  [A] EVALUASI FORWARD CHAINING:")
        forward_chaining_beasiswa(fakta_awal, cetak_log=True)

        print("\n  [B] EVALUASI BACKWARD CHAINING (Hipotesis: 'BEASISWA_DISETUJUI'):")
        lolos_bc = backward_chaining_beasiswa("BEASISWA_DISETUJUI", set(fakta_awal), cetak_log=True)
        print(
            f"  [KEPUTUSAN BC]     : Hipotesis BEASISWA_DISETUJUI -> "
            f"{'TERBUKTI (DISETUJUI)' if lolos_bc else 'TIDAK TERBUKTI (DITOLAK)'}"
        )
        print("=" * 105)

    cetak_tabel_pengecekan(semua_profil)


if __name__ == "__main__":
    jalankan_pengujian_3_profil()
