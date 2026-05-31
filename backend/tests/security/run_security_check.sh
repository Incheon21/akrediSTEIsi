#!/usr/bin/env bash
# =============================================================================
# run_security_check.sh — Bandit Security Static Analysis
# =============================================================================
# Cara menjalankan (dari folder backend/):
#   bash tests/security/run_security_check.sh
#
# Atau dari root proyek:
#   docker compose exec backend bash tests/security/run_security_check.sh
# =============================================================================

set -euo pipefail

REPORT_DIR="tests/security/reports"
REPORT_TXT="${REPORT_DIR}/bandit_report.txt"
REPORT_JSON="${REPORT_DIR}/bandit_report.json"

mkdir -p "$REPORT_DIR"

echo "============================================="
echo " STEI Accreditation — Bandit Security Scan"
echo "============================================="
echo ""
echo "Target  : app/"
echo "Output  : ${REPORT_TXT}"
echo ""

# Jalankan Bandit dan simpan hasilnya ke file teks dan JSON
uv run bandit \
    -r app/ \
    --exclude ".venv,venv,tests,alembic,scripts" \
    --skip "B101,B311" \
    -l \
    --format txt \
    -o "$REPORT_TXT" || true

uv run bandit \
    -r app/ \
    --exclude ".venv,venv,tests,alembic,scripts" \
    --skip "B101,B311" \
    -l \
    --format json \
    -o "$REPORT_JSON" || true

echo ""
echo "=============================="
echo "         HASIL RINGKAS        "
echo "=============================="
cat "$REPORT_TXT"
echo ""
echo "Laporan lengkap (JSON) tersimpan di: ${REPORT_JSON}"
