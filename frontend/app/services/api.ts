export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiFetch(path: string, options?: RequestInit) {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options?.headers,
  };

  const doFetch = () =>
    fetch(`${API_URL}${path}`, { cache: "no-store", ...options, headers });

  try {
    return await doFetch();
  } catch {
    // One retry after a short delay for transient connection errors (e.g. backend cold start)
    await new Promise((r) => setTimeout(r, 800));
    try {
      return await doFetch();
    } catch (error) {
      throw new Error(
        `Tidak dapat terhubung ke backend API di ${API_URL}. Pastikan backend berjalan dan NEXT_PUBLIC_API_URL sudah benar.`,
        { cause: error },
      );
    }
  }
}

function getErrorMessage(body: unknown, fallback: string): string {
  if (
    body &&
    typeof body === "object" &&
    "detail" in body &&
    typeof body.detail === "string"
  ) {
    return body.detail;
  }
  return fallback;
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

export async function fetchLedNarasiBatch(
  targetId: string,
  indikatorIds: string[],
): Promise<Record<string, LedNarasiResponse>> {
  if (indikatorIds.length === 0) return {};
  const params = new URLSearchParams({ target_akreditasi_id: targetId });
  indikatorIds.forEach((id) => params.append("indikator_ids", id));
  const res = await apiFetch(`/api/v1/led/narasi/batch?${params.toString()}`);
  if (!res.ok) {
    throw new Error("Gagal mengambil narasi LED.");
  }
  const json: { data: Record<string, LedNarasiResponse> } = await res.json();
  return json.data;
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
    throw new Error(getErrorMessage(body, "Gagal menyimpan narasi LED."));
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
    throw new Error(getErrorMessage(body, "Gagal menyimpan target skor."));
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
    throw new Error(getErrorMessage(body, "Gagal menyimpan deadline."));
  }
  return res.json();
}

// ── Komentar Pimpinan ──────────────────────────────────────────────────────

export interface UserKomentar {
  id: string;
  nama: string;
  role: string;
}

export interface KomentarResponse {
  id: string;
  target_akreditasi_id: string;
  user_id: string | null;
  isi_komentar: string;
  created_at: string;
  updated_at: string;
  user: UserKomentar | null;
}

export async function fetchKomentar(targetId: string): Promise<KomentarResponse[]> {
  const res = await apiFetch(`/api/v1/target/${targetId}/komentar/`);
  if (!res.ok) throw new Error("Gagal mengambil komentar.");
  return res.json();
}

export async function createKomentar(
  targetId: string,
  isiKomentar: string
): Promise<KomentarResponse> {
  const res = await apiFetch(`/api/v1/target/${targetId}/komentar/`, {
    method: "POST",
    body: JSON.stringify({ isi_komentar: isiKomentar }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = (body as Record<string, unknown>)?.detail;
    throw new Error(
      typeof detail === "string" ? detail : "Gagal mengirim komentar."
    );
  }
  return res.json();
}

export async function deleteKomentar(
  targetId: string,
  komentarId: string
): Promise<void> {
  const res = await apiFetch(`/api/v1/target/${targetId}/komentar/${komentarId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = (body as Record<string, unknown>)?.detail;
    throw new Error(
      typeof detail === "string" ? detail : "Gagal menghapus komentar."
    );
  }
}
