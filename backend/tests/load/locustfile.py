"""
Locust Load Testing - Sistem Akreditasi STEI ITB
=================================================
Cara menjalankan:
  locust -f tests/load/locustfile.py --host=http://localhost:8000

Lalu buka browser ke http://localhost:8089 untuk memulai pengujian via UI.

Atau jalankan headless (tanpa browser):
  locust -f tests/load/locustfile.py --host=http://localhost:8000 \
    --headless --users 50 --spawn-rate 5 --run-time 60s \
    --html tests/load/reports/load_test_report.html
"""

import random
import uuid

from locust import HttpUser, between, task


# ---------------------------------------------------------------------------
# Base user class — handles login & stores token
# ---------------------------------------------------------------------------

class BaseSTEIUser(HttpUser):
    """Abstract base: setiap subclass harus menyediakan `credentials`."""

    abstract = True
    wait_time = between(1, 3)

    credentials: dict = {}

    def on_start(self):
        """Login saat user mulai dan simpan Bearer token."""
        response = self.client.post(
            "/api/v1/auth/login",
            json=self.credentials,
            name="[auth] POST /login",
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token", "")
        else:
            self.token = ""
            response.failure(f"Login gagal: {response.status_code}")

    def auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}


# ---------------------------------------------------------------------------
# Admin User — akses dashboard multiprodi & manajemen pengguna
# ---------------------------------------------------------------------------

class AdminUser(BaseSTEIUser):
    """
    Mensimulasikan Admin yang mengakses dashboard multiprodi,
    melihat daftar pengguna, dan memeriksa profil sendiri.

    Weight 1: lebih sedikit admin dibanding tim_prodi.
    """

    weight = 1
    credentials = {"email": "admin@stei.itb.ac.id", "password": "admin123"}

    @task(3)
    def get_dashboard_multiprodi(self):
        self.client.get(
            "/api/v1/multiprodi/dashboard",
            headers=self.auth_headers(),
            name="[dashboard] GET /multiprodi/dashboard",
        )

    @task(2)
    def get_all_users(self):
        self.client.get(
            "/api/v1/user-management/users",
            headers=self.auth_headers(),
            name="[user-mgmt] GET /users",
        )

    @task(1)
    def get_my_profile(self):
        self.client.get(
            "/api/v1/auth/me",
            headers=self.auth_headers(),
            name="[auth] GET /me",
        )

    @task(2)
    def get_all_notifications(self):
        self.client.get(
            "/api/v1/notifikasi",
            headers=self.auth_headers(),
            name="[notifikasi] GET /notifikasi",
        )


# ---------------------------------------------------------------------------
# Tim Prodi User — akses dashboard prodi, LED, LKPS, dan evidence
# ---------------------------------------------------------------------------

class TimProdiUser(BaseSTEIUser):
    """
    Mensimulasikan Tim Prodi (IF) yang mengisi LED, mengakses
    dashboard prodi, melihat evidence, dan memantau simulasi skor.

    Weight 5: mayoritas pengguna aktif adalah tim prodi.
    """

    weight = 5
    credentials = {"email": "timprodiIF@stei.itb.ac.id", "password": "timprodiIF123"}

    # Cache prodi_id agar tidak query ulang setiap request
    _prodi_id: str = ""
    _target_id: str = ""

    def on_start(self):
        super().on_start()
        self._fetch_prodi_context()

    def _fetch_prodi_context(self):
        """Ambil prodi_id dari profil user yang login."""
        if not self.token:
            return
        r = self.client.get(
            "/api/v1/auth/me",
            headers=self.auth_headers(),
            name="[auth] GET /me (setup)",
        )
        if r.status_code == 200:
            data = r.json()
            prodi = data.get("program_studi") or {}
            self._prodi_id = prodi.get("id", "")

    @task(5)
    def get_dashboard_prodi(self):
        if not self._prodi_id:
            return
        self.client.get(
            f"/api/v1/prodi/{self._prodi_id}/dashboard",
            headers=self.auth_headers(),
            name="[dashboard] GET /prodi/{id}/dashboard",
        )

    @task(4)
    def get_evidence_list(self):
        self.client.get(
            "/api/v1/evidence/",
            headers=self.auth_headers(),
            name="[evidence] GET /evidence/",
        )

    @task(3)
    def get_simulasi_otomatis(self):
        if not self._prodi_id:
            return
        self.client.get(
            f"/api/v1/simulasi/otomatis/{self._prodi_id}",
            headers=self.auth_headers(),
            name="[simulasi] GET /simulasi/otomatis/{id}",
        )

    @task(3)
    def get_notifications(self):
        params = {}
        if self._prodi_id:
            params["program_studi_id"] = self._prodi_id
        self.client.get(
            "/api/v1/notifikasi",
            headers=self.auth_headers(),
            params=params,
            name="[notifikasi] GET /notifikasi",
        )

    @task(2)
    def get_my_profile(self):
        self.client.get(
            "/api/v1/auth/me",
            headers=self.auth_headers(),
            name="[auth] GET /me",
        )

    @task(1)
    def get_indikator_list(self):
        """Ambil daftar indikator untuk kriteria C1."""
        self.client.get(
            "/api/v1/indikator?kriteria_kode=C1",
            headers=self.auth_headers(),
            name="[indikator] GET /indikator?kriteria_kode=C1",
        )


# ---------------------------------------------------------------------------
# Pimpinan User — baca-saja dashboard multiprodi & notifikasi
# ---------------------------------------------------------------------------

class PimpinanUser(BaseSTEIUser):
    """
    Mensimulasikan Pimpinan yang hanya memantau dashboard dan notifikasi.

    Weight 2.
    """

    weight = 2
    credentials = {"email": "pimpinan@stei.itb.ac.id", "password": "pimpinan123"}

    @task(4)
    def get_dashboard_multiprodi(self):
        self.client.get(
            "/api/v1/multiprodi/dashboard",
            headers=self.auth_headers(),
            name="[dashboard] GET /multiprodi/dashboard",
        )

    @task(3)
    def get_notifications(self):
        self.client.get(
            "/api/v1/notifikasi",
            headers=self.auth_headers(),
            name="[notifikasi] GET /notifikasi",
        )

    @task(1)
    def get_my_profile(self):
        self.client.get(
            "/api/v1/auth/me",
            headers=self.auth_headers(),
            name="[auth] GET /me",
        )
