export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiFetch(path: string, options?: RequestInit) {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  const res = await fetch(`${API_URL}${path}`, {
    cache: "no-store",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });
  return res;
}

// LED Narasi API Types
export interface LedNarasiResponse {
  id: string;
  target_akreditasi_id: string;
  indikator_id: string;
  narasi: string;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface SaveLedNarasiRequest {
  target_akreditasi_id: string;
  indikator_id: string;
  narasi: string;
}

export interface SaveLedNarasiResponse {
  message: string;
  data: LedNarasiResponse;
}

export interface IndicatorResponse {
  id: string;
  kriteria_id: string;
  kode_indikator: string;
  deskripsi: string;
  tipe_input: string;
}

// LED Narasi API Functions
export async function fetchIndikatorsByKriteria(
  kriteriaKode: string,
): Promise<IndicatorResponse[]> {
  const res = await apiFetch(`/api/v1/indikator?kriteria_kode=${kriteriaKode}`);
  if (!res.ok) {
    throw new Error("Gagal mengambil daftar indikator.");
  }
  return res.json();
}

export async function fetchIndikator(
  indikatorId: string,
): Promise<IndicatorResponse> {
  const res = await apiFetch(`/api/v1/indikator/${indikatorId}`);
  if (!res.ok) {
    throw new Error("Gagal mengambil data indikator.");
  }
  return res.json();
}

export async function fetchLedNarasi(
  targetId: string,
  indikatorId: string,
): Promise<LedNarasiResponse | null> {
  const res = await apiFetch(
    `/api/v1/led/narasi?target_akreditasi_id=${targetId}&indikator_id=${indikatorId}`,
  );
  if (res.status === 404) {
    return null;
  }
  if (!res.ok) {
    throw new Error("Gagal mengambil narasi LED.");
  }
  return res.json();
}

export async function saveLedNarasi(
  request: SaveLedNarasiRequest,
): Promise<SaveLedNarasiResponse> {
  const res = await apiFetch("/api/v1/led/narasi", {
    method: "POST",
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      (body as Record<string, unknown>)?.detail ??
        "Gagal menyimpan narasi LED.",
    );
  }
  return res.json();
}

// ── Target Akreditasi ──────────────────────────────────────────────────────

export async function setTargetScore(data: {
  prodi_id: string;
  target_skor: number;
  tahun_akreditasi: number;
}) {
  const res = await apiFetch("/api/v1/target_akreditasi/score", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      (body as Record<string, unknown>)?.detail ?? "Gagal menyimpan target skor.",
    );
  }
  return res.json();
}

export async function setTargetDeadline(data: {
  prodi_id: string;
  deadline: string; // ISO date string: "YYYY-MM-DD"
  tahun_akreditasi: number;
}) {
  const res = await apiFetch("/api/v1/target_akreditasi/deadline", {
    method: "POST",
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(
      (body as Record<string, unknown>)?.detail ?? "Gagal menyimpan deadline.",
    );
  }
  return res.json();
}
