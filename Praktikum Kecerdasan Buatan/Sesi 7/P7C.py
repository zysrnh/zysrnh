# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 7 (POST-TEST CHALLENGE)
# STUDI KASUS : SISTEM PAKAR SELEKSI BEASISWA KELAYAKAN MAHASISWA IDE LPKIA
# CARA PAKAI  : Buka langsung di Google Colab via GitHub (P7C.ipynb) atau
#               copy-paste ke Sel Colab -> RUN!
#               Otomatis terhubung ke Google Spreadsheet + Visualisasi Interaktif.
# ==============================================================================

import csv
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CSV_FILENAME = (
    os.path.join(os.path.dirname(__file__), "dataset_beasiswa_lpkia.csv")
    if "__file__" in globals()
    else "dataset_beasiswa_lpkia.csv"
)

SPREADSHEET_NAME = "Dataset_Beasiswa_LPKIA"
WORKSHEET_NAME = "Data_Mahasiswa"
SPREADSHEET_URL = ""  # Opsional: isi link Google Sheet tertentu jika sudah ada
GITHUB_CSV_100_URL = "https://raw.githubusercontent.com/zysrnh/Mini_Csv/main/dataset_beasiswa_lpkia_100.csv"

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

_GSHEET_WS = None


# ==============================================================================
# 0. UTILITAS PARSING, VALIDASI IPK (IF-ELIF-ELSE) & GOOGLE SPREADSHEET
# ==============================================================================
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
    - < 0.00 atau > 4.00 : Tidak valid (otomatis gagal, tidak di-clamp ke 4.00)
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
    """Mengambil nominal integer dari angka maupun teks format 'Rp 2.400.000'."""
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


def _profil_ke_baris_tabel(profil_list):
    rows = [HEADER_KOLOM]
    for m in profil_list:
        rows.append([
            m["nim"],
            m["nama"],
            m.get("prodi", "Teknik Informatika"),
            f"{m['ipk']:.2f}",
            str(m["penghasilan_ortu"]),
            "Ya" if m["prestasi_akademik"] else "Tidak",
            "Ya" if m["organisasi_aktif"] else "Tidak",
        ])
    return rows


def _simpan_csv_lokal(profil_list):
    with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(_profil_ke_baris_tabel(profil_list))


def simpan_dataset(profil_list):
    """Simpan ke CSV lokal dan sinkron otomatis ke Google Spreadsheet jika terhubung."""
    _simpan_csv_lokal(profil_list)
    if _GSHEET_WS is not None:
        try:
            _GSHEET_WS.clear()
            _GSHEET_WS.append_rows(
                _profil_ke_baris_tabel(profil_list),
                value_input_option="USER_ENTERED",
            )
        except Exception as err:
            print(f"[PERINGATAN] Gagal sinkron ke Google Spreadsheet: {err}")


def konek_google_spreadsheet():
    """Menghubungkan Colab otomatis ke Google Spreadsheet (baca & tulis 2 arah)."""
    global _GSHEET_WS
    if "google.colab" not in sys.modules:
        return None
    try:
        import gspread
        from google.auth import default
        from google.colab import auth

        auth.authenticate_user()
        creds, _ = default()
        gc = gspread.authorize(creds)

        if SPREADSHEET_URL.strip():
            sh = gc.open_by_url(SPREADSHEET_URL.strip())
        else:
            try:
                sh = gc.open(SPREADSHEET_NAME)
            except gspread.SpreadsheetNotFound:
                sh = gc.create(SPREADSHEET_NAME)

        try:
            ws = sh.worksheet(WORKSHEET_NAME)
        except gspread.WorksheetNotFound:
            ws = sh.sheet1
            if ws.title != WORKSHEET_NAME and len(ws.get_all_values()) <= 1:
                ws.update_title(WORKSHEET_NAME)

        baris = ws.get_all_values()
        if len(baris) <= 1:
            ws.clear()
            ws.append_rows(DEFAULT_CSV_DATA, value_input_option="USER_ENTERED")
            records = [dict(zip(HEADER_KOLOM, r)) for r in DEFAULT_CSV_DATA[1:]]
        else:
            header = [h.strip().lower() for h in baris[0]]
            records = [
                dict(zip(header, r + [""] * (len(header) - len(r))))
                for r in baris[1:]
                if any(str(c).strip() for c in r)
            ]

        _GSHEET_WS = ws
        profil_list = [_normalisasi_profil(r, idx) for idx, r in enumerate(records, 1)]
        _simpan_csv_lokal(profil_list)
        print(f"[GOOGLE SPREADSHEET] Terhubung otomatis ke '{sh.title}' -> {sh.url}")
        return profil_list
    except Exception as err:
        print(f"[INFO] Google Spreadsheet dilewati ({err}), memakai dataset CSV lokal.")
        return None


def siapkan_dataset():
    """Ambil dataset dari Google Spreadsheet (Colab) atau fallback ke CSV lokal."""
    profil_sheet = konek_google_spreadsheet()
    if profil_sheet:
        return profil_sheet

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


def siapkan_dataset_csv():
    """Alias kompatibilitas untuk memuat dataset."""
    return siapkan_dataset()


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

        # R1: IF IPK >= 3.5 AND OrangTua_KurangMampu THEN Layak_Ekonomi
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

        # R2: IF IPK >= 3.5 AND (Prestasi_Akademik OR Organisasi_Aktif) THEN Layak_Prestasi
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

        # R3: IF Layak_Ekonomi OR Layak_Prestasi THEN BEASISWA_DISETUJUI
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
    semua_profil = siapkan_dataset()
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
    return semua_profil


# ==============================================================================
# 5. VISUALISASI INTERAKTIF NEUBRUTALISM (OTOMATIS MUNCUL DI GOOGLE COLAB)
# ==============================================================================
HTML_NEUBRUTALISM = r"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    .nb-wrap {
      display: flex; flex-direction: column; gap: 22px; width: 100%; max-width: 1080px;
      background: #ffffff; border: 4px solid #000000; border-radius: 6px;
      padding: 24px; box-shadow: 6px 6px 0px #000000; color: #000000;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      margin: 14px 0;
    }
    .nb-top-split { display: flex; flex-direction: row; gap: 24px; }
    .nb-left { flex: 1.05; display: flex; flex-direction: column; gap: 16px; min-width: 0; }
    .nb-right { flex: 0.95; display: flex; flex-direction: column; gap: 16px; border-left: 3px solid #000000; padding-left: 24px; min-width: 0; }
    .nb-header { border-bottom: 3px solid #000000; padding-bottom: 16px; display: flex; justify-content: space-between; align-items: center; gap: 16px; }
    .nb-title { font-size: 19px; font-weight: 900; text-transform: uppercase; letter-spacing: -0.4px; }
    .nb-pill { font-size: 12px; font-weight: 900; padding: 8px 14px; border: 3px solid #000000; box-shadow: 3px 3px 0px #000000; text-transform: uppercase; white-space: nowrap; }
    .nb-ok { background: #22c55e; color: #000000; }
    .nb-no { background: #ef4444; color: #ffffff; }
    .nb-seg { display: flex; background: #ffffff; border: 3px solid #000000; box-shadow: 3px 3px 0px #000000; }
    .nb-btn { flex: 1; background: #ffffff; color: #000000; border: none; border-right: 3px solid #000000; padding: 10px 8px; font-size: 11px; font-weight: 900; cursor: pointer; text-transform: uppercase; }
    .nb-btn:last-child { border-right: none; }
    .nb-btn.active-mode { background: #38bdf8; color: #000000; }
    .nb-id-grid { display: grid; grid-template-columns: 1.3fr 0.7fr; gap: 14px; }
    .nb-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .nb-card { background: #f8fafc; border: 3px solid #000000; padding: 12px 14px; box-shadow: 3px 3px 0px #000000; display: flex; flex-direction: column; gap: 8px; }
    .nb-ctop { display: flex; justify-content: space-between; align-items: center; font-size: 11px; font-weight: 900; text-transform: uppercase; gap: 8px; }
    .nb-badge { font-size: 10px; font-weight: 900; padding: 3px 8px; border: 2px solid #000000; white-space: nowrap; }
    .nb-b-on { background: #22c55e; color: #000000; }
    .nb-b-off { background: #e2e8f0; color: #475569; }
    .nb-b-err { background: #ef4444; color: #ffffff; }
    .nb-input { width: 100%; padding: 8px 10px; font-size: 13px; font-weight: 900; border: 2px solid #000000; background: #ffffff; color: #000000; outline: none; }
    .nb-input:focus { background: #fefce8; }
    .nb-input.invalid { border-color: #ef4444; background: #fef2f2; }
    .nb-trow { display: flex; border: 2px solid #000000; }
    .nb-tbtn { flex: 1; padding: 7px 0; font-size: 11px; font-weight: 900; border: none; border-right: 2px solid #000000; background: #ffffff; color: #000000; cursor: pointer; }
    .nb-tbtn:last-child { border-right: none; }
    .nb-tbtn.on { background: #22c55e; color: #000000; }
    .nb-tbtn.off { background: #000000; color: #ffffff; }
    .nb-actbar { display: grid; grid-template-columns: 1.35fr 0.8fr 0.85fr 1fr; gap: 10px; }
    .nb-actbtn { padding: 11px 8px; font-size: 11px; font-weight: 900; border: 3px solid #000000; box-shadow: 3px 3px 0px #000000; cursor: pointer; text-transform: uppercase; text-align: center; }
    .nb-actbtn:active { transform: translate(2px, 2px); box-shadow: 0px 0px 0px #000000; }
    .btn-save { background: #fde047; color: #000000; }
    .btn-new { background: #ffffff; color: #000000; }
    .btn-csv { background: #38bdf8; color: #000000; }
    .btn-load100 { background: #22c55e; color: #000000; }
    .nb-rules { display: flex; flex-direction: column; gap: 12px; }
    .nb-rule { border: 3px solid #000000; padding: 12px 14px; background: #f8fafc; box-shadow: 3px 3px 0px #000000; display: flex; justify-content: space-between; align-items: center; gap: 14px; }
    .nb-rule.fired { background: #fde047; }
    .nb-rcode { font-size: 11.5px; font-weight: 900; line-height: 1.45; }
    .nb-rtag { font-size: 10px; font-weight: 900; padding: 4px 10px; border: 2px solid #000000; background: #ffffff; text-transform: uppercase; white-space: nowrap; }
    .nb-rule.fired .nb-rtag { background: #000000; color: #fde047; }
    .nb-box { background: #f8fafc; border: 3px solid #000000; padding: 14px 16px; box-shadow: 3px 3px 0px #000000; }
    .nb-phead { font-size: 11px; font-weight: 900; text-transform: uppercase; border-bottom: 2px solid #000000; padding-bottom: 8px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; gap: 8px; }
    .nb-fwrap { display: flex; flex-wrap: wrap; gap: 8px; }
    .nb-chip { font-size: 11px; font-weight: 900; padding: 5px 10px; border: 2px solid #000000; background: #38bdf8; color: #000000; }
    .nb-chip.goal { background: #22c55e; }
    .nb-trace { font-family: Consolas, "Courier New", monospace; font-size: 11.5px; font-weight: 700; line-height: 1.55; background: #ffffff; border: 2px solid #000000; padding: 12px 14px; height: 270px; overflow-y: auto; white-space: pre-wrap; }
    .nb-filterbar { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; background: #f8fafc; border: 3px solid #000000; padding: 12px 14px; box-shadow: 3px 3px 0px #000000; }
    .nb-finput { flex: 1.5; min-width: 190px; padding: 8px 10px; font-size: 12px; font-weight: 800; border: 2px solid #000000; background: #ffffff; color: #000000; outline: none; }
    .nb-finput:focus { background: #fefce8; }
    .nb-fsel { flex: 1; min-width: 150px; padding: 8px 10px; font-size: 11.5px; font-weight: 900; border: 2px solid #000000; background: #ffffff; color: #000000; cursor: pointer; outline: none; }
    .nb-fcount { font-size: 11px; font-weight: 900; padding: 7px 11px; border: 2px solid #000000; background: #fde047; color: #000000; white-space: nowrap; }
    .nb-freset { padding: 7px 12px; font-size: 11px; font-weight: 900; border: 2px solid #000000; background: #ffffff; color: #000000; cursor: pointer; text-transform: uppercase; }
    .nb-table-wrap { overflow-x: auto; overflow-y: auto; max-height: 430px; border: 3px solid #000000; box-shadow: 4px 4px 0px #000000; background: #ffffff; }
    table.nb-tbl { width: 100%; border-collapse: collapse; font-size: 11.5px; }
    .nb-tbl th { position: sticky; top: 0; z-index: 2; background: #000000; color: #ffffff; padding: 11px 12px; text-align: left; font-weight: 900; text-transform: uppercase; border-right: 2px solid #334155; white-space: nowrap; }
    .nb-tbl td { padding: 10px 12px; border-bottom: 2px solid #000000; border-right: 2px solid #000000; font-weight: 800; cursor: pointer; color: #000000; white-space: nowrap; }
    .nb-tbl tr.active-row td { background: #fef08a; }
    .nb-tbl tr:hover td { background: #fef9c3; }
    .nb-cell-split { display: inline-flex; align-items: center; gap: 8px; }
    .chk-yes { background: #dcfce7; color: #14532d; padding: 3px 7px; border: 2px solid #000000; font-size: 10px; font-weight: 900; display: inline-block; }
    .chk-no { background: #f1f5f9; color: #64748b; padding: 3px 7px; border: 2px solid #000000; font-size: 10px; font-weight: 900; display: inline-block; }
    .st-ok { background: #22c55e; color: #000000; padding: 4px 9px; border: 2px solid #000000; font-size: 10px; font-weight: 900; display: inline-block; }
    .st-no { background: #ef4444; color: #ffffff; padding: 4px 9px; border: 2px solid #000000; font-size: 10px; font-weight: 900; display: inline-block; }
    .del-btn { background: #ef4444; color: #ffffff; border: 2px solid #000000; font-size: 10px; font-weight: 900; padding: 4px 9px; cursor: pointer; }
    @media (max-width: 860px) {
      .nb-top-split { flex-direction: column; }
      .nb-actbar { grid-template-columns: 1fr 1fr; }
      .nb-right { border-left: none; border-top: 3px solid #000000; padding-left: 0; padding-top: 18px; }
    }
  </style>
</head>
<body>
<div class="nb-wrap">
  <div class="nb-header">
    <div class="nb-title">SISTEM PAKAR SELEKSI BEASISWA IDE LPKIA</div>
    <div id="nb-pill" class="nb-pill nb-ok">BEASISWA DISETUJUI</div>
  </div>
  <div class="nb-top-split">
    <div class="nb-left">
      <div class="nb-seg">
        <button class="nb-btn active-mode" id="nb-fc" onclick="nbMode('forward')">Forward Chaining</button>
        <button class="nb-btn" id="nb-bc" onclick="nbMode('backward')">Backward Chaining</button>
      </div>
      <div class="nb-id-grid">
        <div class="nb-card">
          <div class="nb-ctop"><span>Nama Mahasiswa</span></div>
          <input type="text" id="nb-nama" class="nb-input" value="Rizky Pratama" oninput="nbCustom()">
        </div>
        <div class="nb-card">
          <div class="nb-ctop"><span>NIM</span></div>
          <input type="text" id="nb-nim" class="nb-input" value="250414001" oninput="nbCustom()">
        </div>
      </div>
      <div class="nb-grid">
        <div class="nb-card">
          <div class="nb-ctop"><span>IPK (&gt;= 3.5)</span><span id="nb-bipk" class="nb-badge nb-b-on">MEMENUHI</span></div>
          <input type="text" inputmode="decimal" id="nb-ipk" class="nb-input" value="3.78" placeholder="0.00 - 4.00" oninput="nbCustom()">
        </div>
        <div class="nb-card">
          <div class="nb-ctop"><span>Ortu (&lt; 3.000.000)</span><span id="nb-bortu" class="nb-badge nb-b-on">MEMENUHI</span></div>
          <input type="text" inputmode="numeric" id="nb-ortu" class="nb-input" value="Rp 2.400.000" placeholder="Rp 0" onkeydown="nbOrtuKeyDown(event)" oninput="nbOrtuInput(this)">
        </div>
        <div class="nb-card">
          <div class="nb-ctop"><span>Prestasi Akademik</span><span id="nb-bpres" class="nb-badge nb-b-off">TIDAK</span></div>
          <div class="nb-trow">
            <button type="button" id="nb-pya" class="nb-tbtn" onclick="nbTog('prestasi', true)">YA</button>
            <button type="button" id="nb-pno" class="nb-tbtn off" onclick="nbTog('prestasi', false)">TIDAK</button>
          </div>
        </div>
        <div class="nb-card">
          <div class="nb-ctop"><span>Organisasi Aktif</span><span id="nb-borg" class="nb-badge nb-b-off">TIDAK</span></div>
          <div class="nb-trow">
            <button type="button" id="nb-oya" class="nb-tbtn" onclick="nbTog('org', true)">YA</button>
            <button type="button" id="nb-ono" class="nb-tbtn off" onclick="nbTog('org', false)">TIDAK</button>
          </div>
        </div>
      </div>
      <div class="nb-actbar">
        <button type="button" class="nb-actbtn btn-save" onclick="nbSave()">+ Simpan / Update</button>
        <button type="button" class="nb-actbtn btn-new" onclick="nbNew()">Input Baru</button>
        <label class="nb-actbtn btn-csv">Upload CSV<input type="file" accept=".csv" style="display:none" onchange="nbImport(event)"></label>
        <button type="button" class="nb-actbtn btn-load100" onclick="nbImport100()">Import 100 Data</button>
      </div>
      <div class="nb-rules">
        <div class="nb-rule" id="nb-cr1"><div class="nb-rcode">R1: IF IPK >= 3.5 AND OrangTua_KurangMampu THEN Layak_Ekonomi</div><div class="nb-rtag" id="nb-tr1">AKTIF</div></div>
        <div class="nb-rule" id="nb-cr2"><div class="nb-rcode">R2: IF IPK >= 3.5 AND (Prestasi_Akademik OR Organisasi_Aktif) THEN Layak_Prestasi</div><div class="nb-rtag" id="nb-tr2">LEWAT</div></div>
        <div class="nb-rule" id="nb-cr3"><div class="nb-rcode">R3: IF Layak_Ekonomi OR Layak_Prestasi THEN BEASISWA_DISETUJUI</div><div class="nb-rtag" id="nb-tr3">AKTIF</div></div>
      </div>
    </div>
    <div class="nb-right">
      <div class="nb-box">
        <div class="nb-phead"><span>Working Memory (Fakta Terbentuk)</span><span id="nb-fcount">4 Fakta</span></div>
        <div class="nb-fwrap" id="nb-fwrap"></div>
      </div>
      <div class="nb-box" style="flex:1;">
        <div class="nb-phead"><span id="nb-ttitle">Jejak Inferensi (Forward Chaining)</span></div>
        <div class="nb-trace" id="nb-trace"></div>
      </div>
    </div>
  </div>
  <div class="nb-filterbar">
    <input type="text" id="nb-fq" class="nb-finput" placeholder="Cari NIM / Nama..." oninput="nbFilter()">
    <select id="nb-fst" class="nb-fsel" onchange="nbFilter()">
      <option value="all">Semua Status</option>
      <option value="disetujui">DISETUJUI</option>
      <option value="ditolak">DITOLAK</option>
    </select>
    <select id="nb-frule" class="nb-fsel" onchange="nbFilter()">
      <option value="all">Semua Rule / Syarat</option>
      <option value="r1">R1 (Layak Ekonomi)</option>
      <option value="r2">R2 (Layak Prestasi)</option>
      <option value="r1r2">R1 &amp; R2 Aktif</option>
      <option value="ipk_ok">IPK &gt;= 3.5</option>
      <option value="ipk_no">IPK &lt; 3.5 / Invalid</option>
    </select>
    <span id="nb-tcount" class="nb-fcount">4 / 4 Data</span>
    <button type="button" class="nb-freset" onclick="nbResetFilter()">Reset</button>
  </div>
  <div class="nb-table-wrap">
    <table class="nb-tbl">
      <thead>
        <tr>
          <th>No</th><th>NIM &amp; Nama</th><th>IPK (&gt;=3.5)</th><th>Ortu (&lt;3 Jt)</th>
          <th>Pres</th><th>Org</th><th>R1</th><th>R2</th><th>Keputusan</th><th>Hapus</th>
        </tr>
      </thead>
      <tbody id="nb-tbody"></tbody>
    </table>
  </div>
</div>

<script>
(function() {
  let profs = __PROFILES_JSON__;
  let selIdx = 0;
  let mode = "forward";
  let st = { ...profs[0] };

  function syncToColabSheet() {
    try {
      if (window.google && google.colab && google.colab.kernel && typeof google.colab.kernel.invokeFunction === "function") {
        google.colab.kernel.invokeFunction("sync_beasiswa_sheet", [profs], {});
      }
    } catch (e) {}
  }

  function parseIPK(val) {
    if (typeof val === "number") return Number.isFinite(val) ? val : NaN;
    const raw = String(val ?? "").trim().replace(",", ".");
    if (!raw || !/^-?(\d+(\.\d*)?|\.\d+)$/.test(raw)) return NaN;
    return Number(raw);
  }

  function evalIPK(val) {
    const num = parseIPK(val);
    if (isNaN(num) || num < 0 || num > 4) {
      return { num: num, ok: false, invalid: true, badge: "TIDAK VALID", cls: "nb-b-err", tag: "INV" };
    } else if (num >= 3.5) {
      return { num: num, ok: true, invalid: false, badge: "MEMENUHI", cls: "nb-b-on", tag: "YA" };
    } else {
      return { num: num, ok: false, invalid: false, badge: "GAGAL", cls: "nb-b-off", tag: "TDK" };
    }
  }

  function formatRupiah(num) {
    const n = Math.max(0, Math.round(Number(num) || 0));
    return "Rp " + n.toLocaleString("id-ID");
  }

  function parseRupiah(val) {
    const d = String(val || "").replace(/\D/g, "");
    return d ? parseInt(d, 10) : 0;
  }

  function applyFormattedOrtu(el, digits, targetDigits) {
    if (!digits) {
      el.value = "";
      st.ortu = 0;
      render();
      return;
    }
    const num = parseInt(digits, 10) || 0;
    const formatted = formatRupiah(num);
    el.value = formatted;

    let newPos = formatted.length;
    if (targetDigits === 0) {
      newPos = 3;
    } else {
      let count = 0;
      for (let i = 0; i < formatted.length; i++) {
        if (/\d/.test(formatted[i])) {
          count++;
          if (count === targetDigits) { newPos = i + 1; break; }
        }
      }
    }
    try { el.setSelectionRange(newPos, newPos); } catch (err) {}
    st.ortu = num;
    render();
  }

  window.nbOrtuKeyDown = function(e) {
    const el = e.target;
    if (e.key === "Backspace" && el.selectionStart === el.selectionEnd) {
      if (el.selectionStart <= 3 && el.value.startsWith("Rp ")) {
        e.preventDefault();
        return;
      }
      if (el.value[el.selectionStart - 1] === ".") {
        e.preventDefault();
        const rawBefore = el.value.slice(0, el.selectionStart - 1).replace(/\D/g, "");
        const rawAfter = el.value.slice(el.selectionStart).replace(/\D/g, "");
        const newDigits = rawBefore.slice(0, -1) + rawAfter;
        const targetDigits = Math.max(0, rawBefore.length - 1);
        applyFormattedOrtu(el, newDigits, targetDigits);
      }
    }
  };

  window.nbOrtuInput = function(el) {
    const sel = el.selectionStart ?? el.value.length;
    const targetDigits = el.value.slice(0, sel).replace(/\D/g, "").length;
    const digits = el.value.replace(/\D/g, "");
    applyFormattedOrtu(el, digits, targetDigits);
  };

  function getFacts(s) {
    const f = [];
    const ipkRes = evalIPK(s.ipk);
    if (ipkRes.ok) f.push("IPK >= 3.5");
    if (s.ortu < 3000000) f.push("OrangTua_KurangMampu");
    if (s.prestasi) f.push("Prestasi_Akademik");
    if (s.org) f.push("Organisasi_Aktif");
    return f;
  }

  function evalFC(init, label) {
    const k = new Set(init);
    const tr = [`[MAHASISWA] ${label}`, `[FAKTA AWAL] ${JSON.stringify(Array.from(k))}`];
    const fired = { R1: false, R2: false, R3: false };
    let step = 1, chg = true;
    while (chg) {
      chg = false;
      tr.push(`\n--- ITERASI ${step} ---`);
      if (k.has("IPK >= 3.5") && k.has("OrangTua_KurangMampu") && !k.has("Layak_Ekonomi")) {
        k.add("Layak_Ekonomi"); fired.R1 = true; chg = true;
        tr.push("[R1 AKTIF] IF IPK >= 3.5 AND OrangTua_KurangMampu -> +Layak_Ekonomi");
        step++; continue;
      } else {
        tr.push(`[R1 LEWAT] ${k.has("Layak_Ekonomi") ? "Sudah diketahui" : "Syarat belum terpenuhi"}`);
      }
      if (k.has("IPK >= 3.5") && (k.has("Prestasi_Akademik") || k.has("Organisasi_Aktif")) && !k.has("Layak_Prestasi")) {
        k.add("Layak_Prestasi"); fired.R2 = true; chg = true;
        tr.push("[R2 AKTIF] IF IPK >= 3.5 AND (Prestasi/Organisasi) -> +Layak_Prestasi");
        step++; continue;
      } else {
        tr.push(`[R2 LEWAT] ${k.has("Layak_Prestasi") ? "Sudah diketahui" : "Syarat belum terpenuhi"}`);
      }
      if ((k.has("Layak_Ekonomi") || k.has("Layak_Prestasi")) && !k.has("BEASISWA_DISETUJUI")) {
        k.add("BEASISWA_DISETUJUI"); fired.R3 = true; chg = true;
        tr.push("[R3 AKTIF] IF Layak_Ekonomi OR Layak_Prestasi -> +BEASISWA_DISETUJUI");
        step++; continue;
      } else {
        tr.push(`[R3 LEWAT] ${k.has("BEASISWA_DISETUJUI") ? "Sudah diketahui" : "Syarat belum terpenuhi"}`);
      }
    }
    const ok = k.has("BEASISWA_DISETUJUI");
    tr.push(`\n[KEPUTUSAN] ${ok ? "BEASISWA_DISETUJUI (LOLOS)" : "BEASISWA_DITOLAK (TIDAK LOLOS)"}`);
    return { known: Array.from(k), trace: tr.join("\n"), fired, ok };
  }

  function evalBC(init, label) {
    const k = new Set(init);
    const tr = [`[MAHASISWA] ${label}`, `[HIPOTESIS] Membuktikan Goal: 'BEASISWA_DISETUJUI'\n`];
    const fired = { R1: false, R2: false, R3: false };
    const rmap = {
      "BEASISWA_DISETUJUI": [
        { id: "R3 (Jalur Ekonomi)", req: ["Layak_Ekonomi"], c: "R3" },
        { id: "R3 (Jalur Prestasi)", req: ["Layak_Prestasi"], c: "R3" }
      ],
      "Layak_Ekonomi": [{ id: "R1", req: ["IPK >= 3.5", "OrangTua_KurangMampu"], c: "R1" }],
      "Layak_Prestasi": [
        { id: "R2 (Prestasi)", req: ["IPK >= 3.5", "Prestasi_Akademik"], c: "R2" },
        { id: "R2 (Organisasi)", req: ["IPK >= 3.5", "Organisasi_Aktif"], c: "R2" }
      ]
    };
    function prove(g, d) {
      const pad = "  ".repeat(d);
      if (k.has(g)) { tr.push(`${pad}[FAKTA VALID] '${g}' ditemukan`); return true; }
      if (!rmap[g]) { tr.push(`${pad}[GAGAL] '${g}' tidak ditemukan`); return false; }
      for (const b of rmap[g]) {
        tr.push(`${pad}[CEK ${b.id}] Buktikan '${g}' <- ${JSON.stringify(b.req)}`);
        let m = true;
        for (const s of b.req) { if (!prove(s, d + 1)) { m = false; break; } }
        if (m) { k.add(g); fired[b.c] = true; tr.push(`${pad}[TERBUKTI] '${g}' VALID via ${b.id}`); return true; }
      }
      tr.push(`${pad}[TIDAK TERBUKTI] '${g}' gagal dibuktikan`);
      return false;
    }
    const ok = prove("BEASISWA_DISETUJUI", 0);
    tr.push(`\n[KESIMPULAN] Hipotesis BEASISWA_DISETUJUI = ${ok ? "TERBUKTI (DISETUJUI)" : "TIDAK TERBUKTI (DITOLAK)"}`);
    return { known: Array.from(k), trace: tr.join("\n"), fired, ok };
  }

  function escHtml(s) {
    return String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function rowMatchesFilter(p) {
    const q = (document.getElementById("nb-fq").value || "").trim().toLowerCase();
    const fst = document.getElementById("nb-fst").value;
    const frule = document.getElementById("nb-frule").value;
    const r = evalFC(getFacts(p), p.nama);
    const ipkCheck = evalIPK(p.ipk);

    if (q && !`${p.nim} ${p.nama}`.toLowerCase().includes(q)) return null;
    if (fst === "disetujui" && !r.ok) return null;
    else if (fst === "ditolak" && r.ok) return null;

    if (frule === "r1" && !r.fired.R1) return null;
    else if (frule === "r2" && !r.fired.R2) return null;
    else if (frule === "r1r2" && !(r.fired.R1 && r.fired.R2)) return null;
    else if (frule === "ipk_ok" && !ipkCheck.ok) return null;
    else if (frule === "ipk_no" && ipkCheck.ok) return null;

    return { r, ipkCheck };
  }

  function renderTable() {
    const tbody = document.getElementById("nb-tbody");
    const rowsHtml = [];
    profs.forEach((p, i) => {
      const match = rowMatchesFilter(p);
      if (!match) return;
      const { r, ipkCheck } = match;
      const ipkText = isNaN(ipkCheck.num) ? "-" : Number(ipkCheck.num).toFixed(2);
      const ipkCls = ipkCheck.ok ? "chk-yes" : (ipkCheck.invalid ? "st-no" : "chk-no");
      const ortuOk = p.ortu < 3000000;
      const rp = formatRupiah(p.ortu);
      rowsHtml.push(`<tr class="${i === selIdx ? 'active-row' : ''}" onclick="nbSelect(${i})">
        <td>${i + 1}</td>
        <td>${escHtml(p.nim)} - ${escHtml(p.nama)}</td>
        <td><span class="nb-cell-split"><span>${ipkText}</span><span class="${ipkCls}">${ipkCheck.tag}</span></span></td>
        <td><span class="nb-cell-split"><span>${rp}</span><span class="${ortuOk ? 'chk-yes' : 'chk-no'}">${ortuOk ? 'YA' : 'TDK'}</span></span></td>
        <td><span class="${p.prestasi ? 'chk-yes' : 'chk-no'}">${p.prestasi ? 'YA' : 'TDK'}</span></td>
        <td><span class="${p.org ? 'chk-yes' : 'chk-no'}">${p.org ? 'YA' : 'TDK'}</span></td>
        <td><span class="${r.fired.R1 ? 'chk-yes' : 'chk-no'}">${r.fired.R1 ? 'AKTIF' : '-'}</span></td>
        <td><span class="${r.fired.R2 ? 'chk-yes' : 'chk-no'}">${r.fired.R2 ? 'AKTIF' : '-'}</span></td>
        <td><span class="${r.ok ? 'st-ok' : 'st-no'}">${r.ok ? 'DISETUJUI' : 'DITOLAK'}</span></td>
        <td onclick="event.stopPropagation(); nbDel(${i})"><button class="del-btn">X</button></td>
      </tr>`);
    });
    document.getElementById("nb-tcount").textContent = `${rowsHtml.length} / ${profs.length} Data`;
    tbody.innerHTML = rowsHtml.length
      ? rowsHtml.join("")
      : `<tr><td colspan="10" style="text-align:center;padding:18px;cursor:default;">Tidak ada data mahasiswa sesuai filter.</td></tr>`;
  }

  function render() {
    const ipkRes = evalIPK(st.ipk);
    const ov = st.ortu < 3000000;
    document.getElementById("nb-ipk").classList.toggle("invalid", ipkRes.invalid);
    const bi = document.getElementById("nb-bipk"); bi.textContent = ipkRes.badge; bi.className = "nb-badge " + ipkRes.cls;
    const bo = document.getElementById("nb-bortu"); bo.textContent = ov ? "MEMENUHI" : "GAGAL"; bo.className = "nb-badge " + (ov ? "nb-b-on" : "nb-b-off");
    const bp = document.getElementById("nb-bpres"); bp.textContent = st.prestasi ? "YA" : "TIDAK"; bp.className = "nb-badge " + (st.prestasi ? "nb-b-on" : "nb-b-off");
    const bg = document.getElementById("nb-borg"); bg.textContent = st.org ? "YA" : "TIDAK"; bg.className = "nb-badge " + (st.org ? "nb-b-on" : "nb-b-off");

    document.getElementById("nb-pya").className = "nb-tbtn " + (st.prestasi ? "on" : "");
    document.getElementById("nb-pno").className = "nb-tbtn " + (!st.prestasi ? "off" : "");
    document.getElementById("nb-oya").className = "nb-tbtn " + (st.org ? "on" : "");
    document.getElementById("nb-ono").className = "nb-tbtn " + (!st.org ? "off" : "");

    const label = `${st.nama || "Mahasiswa"} (${st.nim || "-"})`;
    const f = getFacts(st);
    const res = mode === "forward" ? evalFC(f, label) : evalBC(f, label);

    const pill = document.getElementById("nb-pill");
    pill.textContent = res.ok ? "BEASISWA DISETUJUI" : "BEASISWA DITOLAK";
    pill.className = "nb-pill " + (res.ok ? "nb-ok" : "nb-no");

    ["R1", "R2", "R3"].forEach(r => {
      const c = document.getElementById("nb-c" + r.toLowerCase());
      const t = document.getElementById("nb-t" + r.toLowerCase());
      if (res.fired[r]) { c.classList.add("fired"); t.textContent = "TERPEMICU"; }
      else { c.classList.remove("fired"); t.textContent = "LEWAT"; }
    });

    document.getElementById("nb-fcount").textContent = `${res.known.length} Fakta`;
    document.getElementById("nb-fwrap").innerHTML = res.known.length
      ? res.known.map(x => `<span class="nb-chip ${x === 'BEASISWA_DISETUJUI' ? 'goal' : ''}">${x}</span>`).join("")
      : `<span class="nb-chip" style="background:#e2e8f0;">Tidak ada fakta memenuhi syarat</span>`;

    document.getElementById("nb-ttitle").textContent = `Jejak Inferensi (${mode === "forward" ? "Forward Chaining" : "Backward Chaining"})`;
    document.getElementById("nb-trace").textContent = res.trace;

    renderTable();
  }

  function syncInputsFromState() {
    document.getElementById("nb-nama").value = st.nama;
    document.getElementById("nb-nim").value = st.nim;
    const ipkNum = parseIPK(st.ipk);
    document.getElementById("nb-ipk").value = isNaN(ipkNum) ? "" : ipkNum.toFixed(2);
    document.getElementById("nb-ortu").value = formatRupiah(st.ortu);
  }

  function nextNim() {
    return "250414" + String(profs.length + 1).padStart(3, "0");
  }

  window.nbSelect = function(i) {
    if (i < 0 || i >= profs.length) return;
    selIdx = i;
    st = { ...profs[i] };
    syncInputsFromState();
    render();
  };
  window.nbMode = function(m) {
    mode = m;
    document.getElementById("nb-fc").classList.toggle("active-mode", m === "forward");
    document.getElementById("nb-bc").classList.toggle("active-mode", m === "backward");
    render();
  };
  window.nbTog = function(k, v) { st[k] = v; render(); };
  window.nbFilter = function() { renderTable(); };
  window.nbResetFilter = function() {
    document.getElementById("nb-fq").value = "";
    document.getElementById("nb-fst").value = "all";
    document.getElementById("nb-frule").value = "all";
    renderTable();
  };
  window.nbCustom = function() {
    st.nama = document.getElementById("nb-nama").value.trim() || "Mahasiswa Baru";
    st.nim = document.getElementById("nb-nim").value.trim() || "-";
    st.ipk = parseIPK(document.getElementById("nb-ipk").value);
    st.ortu = parseRupiah(document.getElementById("nb-ortu").value);
    render();
  };
  window.nbSave = function() {
    const ipkCheck = evalIPK(document.getElementById("nb-ipk").value);
    if (ipkCheck.invalid) {
      document.getElementById("nb-ipk").focus();
      alert("IPK tidak valid. Masukkan nilai IPK antara 0.00 sampai 4.00.");
      return;
    }
    const entry = {
      nim: document.getElementById("nb-nim").value.trim() || nextNim(),
      nama: document.getElementById("nb-nama").value.trim() || `Mahasiswa ${profs.length + 1}`,
      ipk: Number(ipkCheck.num.toFixed(2)),
      ortu: parseRupiah(document.getElementById("nb-ortu").value),
      prestasi: st.prestasi,
      org: st.org
    };
    if (selIdx >= 0 && selIdx < profs.length && profs[selIdx].nim === entry.nim) {
      profs[selIdx] = entry;
    } else {
      profs.push(entry);
      selIdx = profs.length - 1;
    }
    st = { ...entry };
    syncInputsFromState();
    syncToColabSheet();
    render();
  };
  window.nbNew = function() {
    selIdx = -1;
    st = { nim: nextNim(), nama: "", ipk: 3.60, ortu: 2500000, prestasi: false, org: false };
    syncInputsFromState();
    document.getElementById("nb-nama").focus();
    render();
  };
  window.nbDel = function(i) {
    if (profs.length <= 1) return;
    profs.splice(i, 1);
    if (selIdx >= profs.length) selIdx = profs.length - 1;
    if (selIdx < 0) selIdx = 0;
    st = { ...profs[selIdx] };
    syncInputsFromState();
    syncToColabSheet();
    render();
  };

  function loadCsvText(csvText) {
    const lines = String(csvText || "").split(/\r?\n/).filter(l => l.trim().length > 0);
    if (lines.length < 2) return false;
    const arr = [];
    for (let i = 1; i < lines.length; i++) {
      const c = lines[i].split(",").map(x => x.replace(/^"|"$/g, "").trim());
      if (c.length >= 6) {
        const hp = c.length >= 7;
        const ipkParsed = parseIPK(c[hp ? 3 : 2]);
        arr.push({
          nim: c[0],
          nama: c[1],
          ipk: isNaN(ipkParsed) ? 0 : ipkParsed,
          ortu: parseRupiah(c[hp ? 4 : 3]),
          prestasi: ["ya", "true", "1", "yes"].includes(c[hp ? 5 : 4].toLowerCase()),
          org: ["ya", "true", "1", "yes"].includes(c[hp ? 6 : 5].toLowerCase())
        });
      }
    }
    if (arr.length > 0) {
      profs = arr;
      nbResetFilter();
      syncToColabSheet();
      nbSelect(0);
      return true;
    }
    return false;
  }

  window.nbImport = function(ev) {
    const f = ev.target.files[0];
    if (!f) return;
    const r = new FileReader();
    r.onload = function(e) { loadCsvText(e.target.result); };
    r.readAsText(f);
    ev.target.value = "";
  };

  window.nbImport100 = async function() {
    const rawUrl = "__GITHUB_CSV_100_URL__";
    const isLocalHttp = location.protocol.startsWith("http") && !location.hostname.includes("colab") && !location.hostname.includes("googleusercontent");
    const candidates = isLocalHttp ? ["./dataset_beasiswa_lpkia_100.csv", rawUrl] : [rawUrl, "./dataset_beasiswa_lpkia_100.csv"];
    for (const url of candidates) {
      try {
        const resp = await fetch(url, { cache: "no-store" });
        if (resp.ok && loadCsvText(await resp.text())) return;
      } catch (err) {}
    }
    alert("Gagal mengambil CSV 100 data. Pastikan koneksi aktif atau gunakan Upload CSV.");
  };

  nbSelect(0);
})();
</script>
</body>
</html>"""


def _callback_sync_sheet(data_html):
    """Callback Colab JS -> Python untuk sinkronisasi otomatis HTML ke Google Spreadsheet."""
    if not isinstance(data_html, list) or not data_html:
        return
    profil_list = [_normalisasi_profil(row, idx) for idx, row in enumerate(data_html, 1)]
    simpan_dataset(profil_list)


def tampilkan_visualisasi_colab(profil_list=None):
    """Menampilkan UI HTML Neubrutalism + daftarkan sinkronisasi Google Spreadsheet di Colab."""
    try:
        from IPython.display import HTML, display
        if "google.colab" not in sys.modules and "ipykernel" not in sys.modules:
            return

        if "google.colab" in sys.modules:
            try:
                from google.colab import output
                output.register_callback("sync_beasiswa_sheet", _callback_sync_sheet)
            except Exception:
                pass

        profil_aktif = profil_list if profil_list is not None else siapkan_dataset()
        js_profiles = [
            {
                "nim": m["nim"],
                "nama": m["nama"],
                "ipk": m["ipk"],
                "ortu": m["penghasilan_ortu"],
                "prestasi": m["prestasi_akademik"],
                "org": m["organisasi_aktif"],
            }
            for m in profil_aktif
        ]
        html_render = HTML_NEUBRUTALISM.replace(
            "__PROFILES_JSON__", json.dumps(js_profiles, ensure_ascii=False)
        ).replace(
            "__GITHUB_CSV_100_URL__", GITHUB_CSV_100_URL
        )
        display(HTML(html_render))
    except Exception:
        pass


if __name__ == "__main__":
    daftar_profil = jalankan_pengujian_3_profil()
    tampilkan_visualisasi_colab(daftar_profil)
