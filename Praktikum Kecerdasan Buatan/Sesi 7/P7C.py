# ==============================================================================
# PRAKTIKUM KECERDASAN BUATAN - SESI 7 (POST-TEST CHALLENGE)
# STUDI KASUS : SISTEM PAKAR SELEKSI BEASISWA KELAYAKAN MAHASISWA IDE LPKIA
# CARA PAKAI  : Cukup Copy-Paste kode ini ke 1 Sel di Google Colab lalu RUN!
#               (TIDAK PERLU upload file CSV/HTML manual, otomatis ter-generate)
# ==============================================================================

import csv
import os
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

DEFAULT_CSV_DATA = [
    ["nim", "nama", "prodi", "ipk", "penghasilan_ortu", "prestasi_akademik", "organisasi_aktif"],
    ["250414001", "Rizky Pratama", "Teknik Informatika", "3.78", "2400000", "Tidak", "Tidak"],
    ["250414002", "Nadia Maharani", "Sistem Informasi", "3.65", "5500000", "Ya", "Ya"],
    ["250414003", "Dimas Anggara", "Teknik Informatika", "3.25", "2200000", "Tidak", "Ya"],
    ["250414004", "Siti Nurhaliza", "Sistem Informasi", "3.85", "2800000", "Ya", "Ya"],
]


def siapkan_dataset_csv():
    """Membuat otomatis dataset CSV jika belum ada (tidak perlu upload manual di Colab)."""
    if not os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(DEFAULT_CSV_DATA)

    profil_list = []
    with open(CSV_FILENAME, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            profil_list.append({
                "nim": row["nim"],
                "nama": row["nama"],
                "prodi": row["prodi"],
                "ipk": float(row["ipk"]),
                "penghasilan_ortu": int(row["penghasilan_ortu"]),
                "prestasi_akademik": row["prestasi_akademik"].strip().lower() == "ya",
                "organisasi_aktif": row["organisasi_aktif"].strip().lower() == "ya",
            })
    return profil_list


# ==============================================================================
# 1. EKSTRAKSI FAKTA GEJALA / ATRIBUT MAHASISWA
# ==============================================================================
def ekstrak_fakta_awal(mhs):
    """
    Fakta Gejala / Atribut sesuai soal:
    1. IPK >= 3.5
    2. OrangTua_KurangMampu (Penghasilan Orang Tua < Rp 3.000.000)
    3. Prestasi_Akademik
    4. Organisasi_Aktif
    """
    fakta = []
    if mhs["ipk"] >= 3.5:
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
# 4. PENGUJIAN 3 PROFIL + TABEL MATRIKS PENGECEKAN SYARAT & ATURAN
# ==============================================================================
def cetak_tabel_pengecekan(daftar_mhs):
    print("\nTABEL MATRIKS PENGECEKAN KELAYAKAN BEASISWA:")
    print("=" * 102)
    header = (
        f"{'No':<3} | {'NIM & Nama':<24} | {'IPK (>=3.5)':<12} | {'Ortu (<3Jt)':<11} | "
        f"{'Pres':<5} | {'Org':<5} | {'R1':<5} | {'R2':<5} | {'Keputusan Akhir'}"
    )
    print(header)
    print("-" * 102)

    for i, m in enumerate(daftar_mhs, 1):
        fakta = ekstrak_fakta_awal(m)
        lolos, facts_akhir, _ = forward_chaining_beasiswa(fakta, cetak_log=False)

        cek_ipk = f"{m['ipk']:.2f} [{'YA' if m['ipk'] >= 3.5 else 'TDK'}]"
        cek_ortu = f"{m['penghasilan_ortu'] // 1000000:.1f}Jt [{'YA' if m['penghasilan_ortu'] < 3000000 else 'TDK'}]"
        cek_pres = "YA" if m["prestasi_akademik"] else "TDK"
        cek_org = "YA" if m["organisasi_aktif"] else "TDK"
        cek_r1 = "AKTIF" if "Layak_Ekonomi" in facts_akhir else "-"
        cek_r2 = "AKTIF" if "Layak_Prestasi" in facts_akhir else "-"
        keputusan = "BEASISWA_DISETUJUI" if lolos else "DITOLAK"
        identitas = f"{m['nim']} {m['nama']}"[:24]

        print(
            f"{i:<3} | {identitas:<24} | {cek_ipk:<12} | {cek_ortu:<11} | "
            f"{cek_pres:<5} | {cek_org:<5} | {cek_r1:<5} | {cek_r2:<5} | {keputusan}"
        )
    print("=" * 102)


def jalankan_pengujian_3_profil():
    semua_profil = siapkan_dataset_csv()
    tiga_profil_uji = semua_profil[:3]

    print("=" * 102)
    print("         SISTEM PAKAR SELEKSI BEASISWA KELAYAKAN MAHASISWA IDE LPKIA (SESI 7 - CHALLENGE)         ")
    print("=" * 102)

    for idx, mhs in enumerate(tiga_profil_uji, 1):
        fakta_awal = ekstrak_fakta_awal(mhs)
        rp_ortu = f"Rp {mhs['penghasilan_ortu']:,}".replace(",", ".")

        print(f"\nPROFIL UJI #{idx}: {mhs['nama']} (NIM: {mhs['nim']} - {mhs['prodi']})")
        print(
            f"  Atribut : IPK = {mhs['ipk']} | Penghasilan Ortu = {rp_ortu} | "
            f"Prestasi = {'Ya' if mhs['prestasi_akademik'] else 'Tidak'} | "
            f"Organisasi = {'Ya' if mhs['organisasi_aktif'] else 'Tidak'}"
        )
        print("-" * 102)

        print("  [A] EVALUASI FORWARD CHAINING:")
        forward_chaining_beasiswa(fakta_awal, cetak_log=True)

        print("\n  [B] EVALUASI BACKWARD CHAINING (Hipotesis: 'BEASISWA_DISETUJUI'):")
        lolos_bc = backward_chaining_beasiswa("BEASISWA_DISETUJUI", set(fakta_awal), cetak_log=True)
        print(
            f"  [KEPUTUSAN BC]     : Hipotesis BEASISWA_DISETUJUI -> "
            f"{'TERBUKTI (DISETUJUI)' if lolos_bc else 'TIDAK TERBUKTI (DITOLAK)'}"
        )
        print("=" * 102)

    cetak_tabel_pengecekan(semua_profil)


# ==============================================================================
# 5. VISUALISASI INTERAKTIF NEUBRUTALISM (OTOMATIS MUNCUL DI GOOGLE COLAB)
# ==============================================================================
HTML_NEUBRUTALISM = """<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    .nb-wrap {
      display: flex; flex-direction: column; gap: 16px; width: 100%; max-width: 1000px;
      background: #ffffff; border: 4px solid #000000; border-radius: 6px;
      padding: 18px; box-shadow: 6px 6px 0px #000000; color: #000000;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
      margin: 12px 0;
    }
    .nb-top-split { display: flex; flex-direction: row; gap: 18px; }
    .nb-left { flex: 1.05; display: flex; flex-direction: column; gap: 11px; }
    .nb-right { flex: 0.95; display: flex; flex-direction: column; gap: 11px; border-left: 3px solid #000000; padding-left: 18px; }
    .nb-header { border-bottom: 3px solid #000000; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center; gap: 10px; }
    .nb-title { font-size: 18px; font-weight: 900; text-transform: uppercase; letter-spacing: -0.4px; }
    .nb-pill { font-size: 12px; font-weight: 900; padding: 6px 12px; border: 3px solid #000000; box-shadow: 2px 2px 0px #000000; text-transform: uppercase; white-space: nowrap; }
    .nb-ok { background: #22c55e; color: #000000; }
    .nb-no { background: #ef4444; color: #ffffff; }
    .nb-seg { display: flex; background: #ffffff; border: 3px solid #000000; box-shadow: 3px 3px 0px #000000; }
    .nb-btn { flex: 1; background: #ffffff; color: #000000; border: none; border-right: 3px solid #000000; padding: 8px 6px; font-size: 11px; font-weight: 900; cursor: pointer; text-transform: uppercase; }
    .nb-btn:last-child { border-right: none; }
    .nb-btn.active-mode { background: #38bdf8; color: #000000; }
    .nb-id-grid { display: grid; grid-template-columns: 1.3fr 0.7fr; gap: 10px; }
    .nb-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .nb-card { background: #f8fafc; border: 3px solid #000000; padding: 8px 10px; box-shadow: 3px 3px 0px #000000; display: flex; flex-direction: column; gap: 5px; }
    .nb-ctop { display: flex; justify-content: space-between; align-items: center; font-size: 11px; font-weight: 900; text-transform: uppercase; }
    .nb-badge { font-size: 10px; font-weight: 900; padding: 2px 6px; border: 2px solid #000000; }
    .nb-b-on { background: #22c55e; color: #000000; }
    .nb-b-off { background: #e2e8f0; color: #475569; }
    .nb-input { width: 100%; padding: 6px 8px; font-size: 13px; font-weight: 900; border: 2px solid #000000; background: #ffffff; color: #000000; outline: none; }
    .nb-input:focus { background: #fefce8; }
    .nb-trow { display: flex; border: 2px solid #000000; }
    .nb-tbtn { flex: 1; padding: 5px 0; font-size: 11px; font-weight: 900; border: none; border-right: 2px solid #000000; background: #ffffff; color: #000000; cursor: pointer; }
    .nb-tbtn:last-child { border-right: none; }
    .nb-tbtn.on { background: #22c55e; color: #000000; }
    .nb-tbtn.off { background: #000000; color: #ffffff; }
    .nb-actbar { display: grid; grid-template-columns: 1.3fr 0.85fr 0.85fr; gap: 8px; }
    .nb-actbtn { padding: 8px 6px; font-size: 11px; font-weight: 900; border: 3px solid #000000; box-shadow: 2px 2px 0px #000000; cursor: pointer; text-transform: uppercase; text-align: center; }
    .btn-save { background: #fde047; color: #000000; }
    .btn-new { background: #ffffff; color: #000000; }
    .btn-csv { background: #38bdf8; color: #000000; }
    .nb-rules { display: flex; flex-direction: column; gap: 7px; }
    .nb-rule { border: 3px solid #000000; padding: 8px 10px; background: #f8fafc; box-shadow: 3px 3px 0px #000000; display: flex; justify-content: space-between; align-items: center; gap: 8px; }
    .nb-rule.fired { background: #fde047; }
    .nb-rcode { font-size: 11.5px; font-weight: 900; line-height: 1.35; }
    .nb-rtag { font-size: 10px; font-weight: 900; padding: 3px 8px; border: 2px solid #000000; background: #ffffff; text-transform: uppercase; white-space: nowrap; }
    .nb-rule.fired .nb-rtag { background: #000000; color: #fde047; }
    .nb-box { background: #f8fafc; border: 3px solid #000000; padding: 11px; box-shadow: 3px 3px 0px #000000; }
    .nb-phead { font-size: 11px; font-weight: 900; text-transform: uppercase; border-bottom: 2px solid #000000; padding-bottom: 5px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
    .nb-fwrap { display: flex; flex-wrap: wrap; gap: 6px; }
    .nb-chip { font-size: 11px; font-weight: 900; padding: 4px 8px; border: 2px solid #000000; background: #38bdf8; color: #000000; }
    .nb-chip.goal { background: #22c55e; }
    .nb-trace { font-family: Consolas, monospace; font-size: 11.5px; font-weight: 700; line-height: 1.48; background: #ffffff; border: 2px solid #000000; padding: 10px; height: 245px; overflow-y: auto; white-space: pre-wrap; }
    .nb-table-wrap { overflow-x: auto; border: 3px solid #000000; box-shadow: 3px 3px 0px #000000; background: #ffffff; }
    table.nb-tbl { width: 100%; border-collapse: collapse; font-size: 11.5px; }
    .nb-tbl th { background: #000000; color: #ffffff; padding: 8px 7px; text-align: left; font-weight: 900; text-transform: uppercase; border-right: 2px solid #334155; }
    .nb-tbl td { padding: 7px; border-bottom: 2px solid #000000; border-right: 2px solid #000000; font-weight: 800; cursor: pointer; color: #000000; }
    .nb-tbl tr.active-row td { background: #fef08a; }
    .nb-tbl tr:hover td { background: #fef9c3; }
    .chk-yes { background: #dcfce7; color: #14532d; padding: 2px 6px; border: 2px solid #000000; font-size: 10px; font-weight: 900; display: inline-block; }
    .chk-no { background: #f1f5f9; color: #64748b; padding: 2px 6px; border: 2px solid #000000; font-size: 10px; font-weight: 900; display: inline-block; }
    .st-ok { background: #22c55e; color: #000000; padding: 3px 8px; border: 2px solid #000000; font-size: 10.5px; font-weight: 900; display: inline-block; }
    .st-no { background: #ef4444; color: #ffffff; padding: 3px 8px; border: 2px solid #000000; font-size: 10.5px; font-weight: 900; display: inline-block; }
    .del-btn { background: #ef4444; color: #ffffff; border: 2px solid #000000; font-size: 10px; font-weight: 900; padding: 2px 6px; cursor: pointer; }
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
          <div class="nb-ctop"><span>IPK (>= 3.5)</span><span id="nb-bipk" class="nb-badge nb-b-on">MEMENUHI</span></div>
          <input type="number" id="nb-ipk" class="nb-input" step="0.01" min="0" max="4" value="3.78" oninput="nbCustom()">
        </div>
        <div class="nb-card">
          <div class="nb-ctop"><span>Ortu (< 3.000.000)</span><span id="nb-bortu" class="nb-badge nb-b-on">MEMENUHI</span></div>
          <input type="number" id="nb-ortu" class="nb-input" step="100000" min="0" value="2400000" oninput="nbCustom()">
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
        <button type="button" class="nb-actbtn btn-save" onclick="nbSave()">+ Simpan / Update ke Tabel</button>
        <button type="button" class="nb-actbtn btn-new" onclick="nbNew()">Input Baru</button>
        <label class="nb-actbtn btn-csv">
          Upload CSV
          <input type="file" accept=".csv" style="display:none" onchange="nbImport(event)">
        </label>
      </div>
      <div class="nb-rules">
        <div class="nb-rule" id="nb-cr1">
          <div class="nb-rcode">R1: IF IPK >= 3.5 AND OrangTua_KurangMampu THEN Layak_Ekonomi</div>
          <div class="nb-rtag" id="nb-tr1">AKTIF</div>
        </div>
        <div class="nb-rule" id="nb-cr2">
          <div class="nb-rcode">R2: IF IPK >= 3.5 AND (Prestasi_Akademik OR Organisasi_Aktif) THEN Layak_Prestasi</div>
          <div class="nb-rtag" id="nb-tr2">LEWAT</div>
        </div>
        <div class="nb-rule" id="nb-cr3">
          <div class="nb-rcode">R3: IF Layak_Ekonomi OR Layak_Prestasi THEN BEASISWA_DISETUJUI</div>
          <div class="nb-rtag" id="nb-tr3">AKTIF</div>
        </div>
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
  <div class="nb-table-wrap">
    <table class="nb-tbl">
      <thead>
        <tr>
          <th>No</th>
          <th>NIM & Nama</th>
          <th>IPK (>=3.5)</th>
          <th>Ortu (<3 Jt)</th>
          <th>Prestasi</th>
          <th>Organisasi</th>
          <th>R1 (Ekonomi)</th>
          <th>R2 (Prestasi)</th>
          <th>R3 (Keputusan)</th>
          <th>Hapus</th>
        </tr>
      </thead>
      <tbody id="nb-tbody"></tbody>
    </table>
  </div>
</div>
<script>
(function() {
  let profs = [
    { nim: "250414001", nama: "Rizky Pratama", ipk: 3.78, ortu: 2400000, prestasi: false, org: false },
    { nim: "250414002", nama: "Nadia Maharani", ipk: 3.65, ortu: 5500000, prestasi: true, org: true },
    { nim: "250414003", nama: "Dimas Anggara", ipk: 3.25, ortu: 2200000, prestasi: false, org: true },
    { nim: "250414004", nama: "Siti Nurhaliza", ipk: 3.85, ortu: 2800000, prestasi: true, org: true }
  ];
  let selIdx = 0;
  let mode = "forward";
  let st = { ...profs[0] };

  function getFacts(s) {
    const f = [];
    if (s.ipk >= 3.5) f.push("IPK >= 3.5");
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
      tr.push(`\\n--- ITERASI ${step} ---`);
      if (k.has("IPK >= 3.5") && k.has("OrangTua_KurangMampu") && !k.has("Layak_Ekonomi")) {
        k.add("Layak_Ekonomi"); fired.R1 = true; chg = true;
        tr.push("[R1 AKTIF] IF IPK >= 3.5 AND OrangTua_KurangMampu -> +Layak_Ekonomi");
        step++; continue;
      } else tr.push(`[R1 LEWAT] ${k.has("Layak_Ekonomi") ? "Sudah diketahui" : "Syarat belum terpenuhi"}`);

      if (k.has("IPK >= 3.5") && (k.has("Prestasi_Akademik") || k.has("Organisasi_Aktif")) && !k.has("Layak_Prestasi")) {
        k.add("Layak_Prestasi"); fired.R2 = true; chg = true;
        tr.push("[R2 AKTIF] IF IPK >= 3.5 AND (Prestasi/Organisasi) -> +Layak_Prestasi");
        step++; continue;
      } else tr.push(`[R2 LEWAT] ${k.has("Layak_Prestasi") ? "Sudah diketahui" : "Syarat belum terpenuhi"}`);

      if ((k.has("Layak_Ekonomi") || k.has("Layak_Prestasi")) && !k.has("BEASISWA_DISETUJUI")) {
        k.add("BEASISWA_DISETUJUI"); fired.R3 = true; chg = true;
        tr.push("[R3 AKTIF] IF Layak_Ekonomi OR Layak_Prestasi -> +BEASISWA_DISETUJUI");
        step++; continue;
      } else tr.push(`[R3 LEWAT] ${k.has("BEASISWA_DISETUJUI") ? "Sudah diketahui" : "Syarat belum terpenuhi"}`);
    }
    const ok = k.has("BEASISWA_DISETUJUI");
    tr.push(`\\n[KEPUTUSAN] ${ok ? "BEASISWA_DISETUJUI (LOLOS)" : "BEASISWA_DITOLAK (TIDAK LOLOS)"}`);
    return { known: Array.from(k), trace: tr.join("\\n"), fired, ok };
  }

  function evalBC(init, label) {
    const k = new Set(init);
    const tr = [`[MAHASISWA] ${label}`, `[HIPOTESIS] Membuktikan Goal: 'BEASISWA_DISETUJUI'\\n`];
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
    tr.push(`\\n[KESIMPULAN] Hipotesis BEASISWA_DISETUJUI = ${ok ? "TERBUKTI (DISETUJUI)" : "TIDAK TERBUKTI (DITOLAK)"}`);
    return { known: Array.from(k), trace: tr.join("\\n"), fired, ok };
  }

  function render() {
    const iv = st.ipk >= 3.5, ov = st.ortu < 3000000;
    const bi = document.getElementById("nb-bipk"); bi.textContent = iv ? "MEMENUHI" : "GAGAL"; bi.className = "nb-badge " + (iv ? "nb-b-on" : "nb-b-off");
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

    document.getElementById("nb-tbody").innerHTML = profs.map((p, i) => {
      const r = evalFC(getFacts(p), p.nama);
      const ipkOk = p.ipk >= 3.5;
      const ortuOk = p.ortu < 3000000;
      const rp = "Rp " + Number(p.ortu).toLocaleString("id-ID");
      return `<tr class="${i === selIdx ? 'active-row' : ''}" onclick="nbSelect(${i})">
        <td>${i + 1}</td>
        <td>${p.nim} - ${p.nama}</td>
        <td>${Number(p.ipk).toFixed(2)} <span class="${ipkOk ? 'chk-yes' : 'chk-no'}">${ipkOk ? 'YA' : 'TIDAK'}</span></td>
        <td>${rp} <span class="${ortuOk ? 'chk-yes' : 'chk-no'}">${ortuOk ? 'YA' : 'TIDAK'}</span></td>
        <td><span class="${p.prestasi ? 'chk-yes' : 'chk-no'}">${p.prestasi ? 'YA' : 'TIDAK'}</span></td>
        <td><span class="${p.org ? 'chk-yes' : 'chk-no'}">${p.org ? 'YA' : 'TIDAK'}</span></td>
        <td><span class="${r.fired.R1 ? 'chk-yes' : 'chk-no'}">${r.fired.R1 ? 'AKTIF' : '-'}</span></td>
        <td><span class="${r.fired.R2 ? 'chk-yes' : 'chk-no'}">${r.fired.R2 ? 'AKTIF' : '-'}</span></td>
        <td><span class="${r.ok ? 'st-ok' : 'st-no'}">${r.ok ? 'DISETUJUI' : 'DITOLAK'}</span></td>
        <td onclick="event.stopPropagation(); nbDel(${i})"><button class="del-btn">X</button></td>
      </tr>`;
    }).join("");
  }

  window.nbSelect = function(i) {
    if (i < 0 || i >= profs.length) return;
    selIdx = i;
    st = { ...profs[i] };
    document.getElementById("nb-nama").value = st.nama;
    document.getElementById("nb-nim").value = st.nim;
    document.getElementById("nb-ipk").value = st.ipk;
    document.getElementById("nb-ortu").value = st.ortu;
    render();
  };
  window.nbMode = function(m) {
    mode = m;
    document.getElementById("nb-fc").classList.toggle("active-mode", m === "forward");
    document.getElementById("nb-bc").classList.toggle("active-mode", m === "backward");
    render();
  };
  window.nbTog = function(k, v) { st[k] = v; render(); };
  window.nbCustom = function() {
    st.nama = document.getElementById("nb-nama").value.trim() || "Mahasiswa Baru";
    st.nim = document.getElementById("nb-nim").value.trim() || "-";
    st.ipk = parseFloat(document.getElementById("nb-ipk").value) || 0;
    st.ortu = parseFloat(document.getElementById("nb-ortu").value) || 0;
    render();
  };
  window.nbSave = function() {
    const entry = {
      nim: document.getElementById("nb-nim").value.trim() || `25041400${profs.length + 1}`,
      nama: document.getElementById("nb-nama").value.trim() || `Mahasiswa ${profs.length + 1}`,
      ipk: parseFloat(document.getElementById("nb-ipk").value) || 0,
      ortu: parseFloat(document.getElementById("nb-ortu").value) || 0,
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
    render();
  };
  window.nbNew = function() {
    selIdx = -1;
    st = { nim: `25041400${profs.length + 1}`, nama: "", ipk: 3.60, ortu: 2500000, prestasi: false, org: false };
    document.getElementById("nb-nama").value = "";
    document.getElementById("nb-nim").value = st.nim;
    document.getElementById("nb-ipk").value = st.ipk;
    document.getElementById("nb-ortu").value = st.ortu;
    document.getElementById("nb-nama").focus();
    render();
  };
  window.nbDel = function(i) {
    if (profs.length <= 1) return;
    profs.splice(i, 1);
    if (selIdx >= profs.length) selIdx = profs.length - 1;
    st = { ...profs[Math.max(0, selIdx)] };
    render();
  };
  window.nbImport = function(ev) {
    const f = ev.target.files[0];
    if (!f) return;
    const r = new FileReader();
    r.onload = function(e) {
      const lines = e.target.result.split(/\\r?\\n/).filter(l => l.trim().length > 0);
      if (lines.length < 2) return;
      const arr = [];
      for (let i = 1; i < lines.length; i++) {
        const c = lines[i].split(",");
        if (c.length >= 6) {
          const hp = c.length >= 7;
          arr.push({
            nim: c[0].trim(),
            nama: c[1].trim(),
            ipk: parseFloat(c[hp ? 3 : 2]) || 0,
            ortu: parseFloat(c[hp ? 4 : 3]) || 0,
            prestasi: ["ya", "true", "1", "yes"].includes(c[hp ? 5 : 4].trim().toLowerCase()),
            org: ["ya", "true", "1", "yes"].includes(c[hp ? 6 : 5].trim().toLowerCase())
          });
        }
      }
      if (arr.length > 0) { profs = arr; nbSelect(0); }
    };
    r.readAsText(f);
  };
  render();
})();
</script>
</body>
</html>"""


def tampilkan_visualisasi_colab():
    """Menampilkan UI HTML Neubrutalism secara otomatis jika dijalankan di Google Colab."""
    try:
        from IPython.display import HTML, display
        if "google.colab" not in sys.modules and "ipykernel" not in sys.modules:
            return
        display(HTML(HTML_NEUBRUTALISM))
    except Exception:
        pass


if __name__ == "__main__":
    jalankan_pengujian_3_profil()
    tampilkan_visualisasi_colab()
