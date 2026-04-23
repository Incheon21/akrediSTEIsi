"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/app/hooks/useAuth";
import { API_URL } from "@/app/services/api";

interface EvidenceItem {
  id: string;
  judul: string;
  deskripsi: string | null;
  is_global: boolean;
  url_file: string;
  tipe_file: string | null;
  uploaded_by: string | null;
  uploaded_at: string | null;
}

function getFileIcon(tipeFile: string | null): string {
  if (!tipeFile) return "📄";
  if (tipeFile.includes("pdf")) return "📕";
  if (tipeFile.includes("word") || tipeFile.includes("docx") || tipeFile.includes("doc")) return "📘";
  if (tipeFile.includes("image") || tipeFile.includes("jpeg") || tipeFile.includes("png")) return "🖼️";
  return "📄";
}

function formatDate(iso: string | null): string {
  if (!iso) return "-";
  return new Date(iso).toLocaleDateString("id-ID", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

async function apiFetchAuth(path: string, token: string | null, options: RequestInit = {}) {
  return fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
}

export default function EvidencePage() {
  const { user, loading: authLoading } = useAuth();

  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Upload form state
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [uploadJudul, setUploadJudul] = useState("");
  const [uploadDeskripsi, setUploadDeskripsi] = useState("");
  const [uploadIsGlobal, setUploadIsGlobal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Delete state
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  // Filter state
  const [filterType, setFilterType] = useState<"all" | "global" | "prodi">("all");
  const [searchQuery, setSearchQuery] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const canEdit = user && ["admin", "koordinator", "tim_prodi"].includes(user.role);

  async function fetchEvidence() {
    setLoadingList(true);
    setError(null);
    try {
      const res = await apiFetchAuth("/api/v1/evidence/", token);
      if (!res.ok) throw new Error("Gagal memuat daftar evidence.");
      const data: EvidenceItem[] = await res.json();
      setEvidenceList(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Terjadi kesalahan.");
    } finally {
      setLoadingList(false);
    }
  }

  useEffect(() => {
    if (!authLoading) fetchEvidence();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading]);

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!uploadFile) {
      setUploadError("Pilih file terlebih dahulu.");
      return;
    }
    if (!uploadJudul.trim()) {
      setUploadError("Judul tidak boleh kosong.");
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    const form = new FormData();
    form.append("file", uploadFile);
    form.append("judul", uploadJudul.trim());
    if (uploadDeskripsi.trim()) form.append("deskripsi", uploadDeskripsi.trim());
    form.append("is_global", uploadIsGlobal ? "true" : "false");

    try {
      const res = await apiFetchAuth("/api/v1/evidence/", token, {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error((body as Record<string, string>)?.detail ?? "Gagal mengunggah file.");
      }
      setUploadSuccess("Dokumen berhasil diunggah!");
      setUploadJudul("");
      setUploadDeskripsi("");
      setUploadIsGlobal(false);
      setUploadFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setShowUploadForm(false);
      await fetchEvidence();
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Terjadi kesalahan saat upload.");
    } finally {
      setUploading(false);
    }
  }

  async function handleDownload(item: EvidenceItem) {
    setDownloadingId(item.id);
    try {
      const res = await apiFetchAuth(`/api/v1/evidence/${item.id}/download`, token);
      if (!res.ok) throw new Error("Gagal mengunduh file.");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = item.judul;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (err) {
      alert("Gagal mengunduh: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setDownloadingId(null);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Yakin ingin menghapus dokumen ini? Tindakan ini tidak dapat dibatalkan.")) return;
    setDeletingId(id);
    try {
      const res = await apiFetchAuth(`/api/v1/evidence/${id}`, token, { method: "DELETE" });
      if (!res.ok && res.status !== 204) throw new Error("Gagal menghapus dokumen.");
      setEvidenceList((prev) => prev.filter((e) => e.id !== id));
    } catch (err) {
      alert("Gagal menghapus: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setDeletingId(null);
    }
  }

  const filteredList = evidenceList.filter((ev) => {
    const matchesSearch =
      ev.judul.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (ev.deskripsi?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);
    const matchesType =
      filterType === "all" ||
      (filterType === "global" && ev.is_global) ||
      (filterType === "prodi" && !ev.is_global);
    return matchesSearch && matchesType;
  });

  const globalCount = evidenceList.filter((e) => e.is_global).length;
  const prodiCount = evidenceList.filter((e) => !e.is_global).length;

  if (authLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 p-6 md:p-8">
      <div className="mx-auto max-w-6xl space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 md:text-3xl">
              Repositori Evidence
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Kelola dan akses dokumen pendukung akreditasi secara terpusat.
            </p>
          </div>
          {canEdit && (
            <button
              onClick={() => {
                setShowUploadForm((v) => !v);
                setUploadError(null);
                setUploadSuccess(null);
              }}
              className="inline-flex items-center gap-2 rounded-lg bg-[#00509d] px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-[#003f7d] focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {showUploadForm ? "✕ Batal" : "+ Unggah Dokumen"}
            </button>
          )}
        </div>

        {/* Upload Success Banner */}
        {uploadSuccess && (
          <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
            ✅ {uploadSuccess}
          </div>
        )}

        {/* Upload Form */}
        {showUploadForm && canEdit && (
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-base font-semibold text-slate-800">Unggah Dokumen Baru</h2>
            <form onSubmit={handleUpload} className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">
                    Judul Dokumen <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={uploadJudul}
                    onChange={(e) => setUploadJudul(e.target.value)}
                    placeholder="Contoh: SK Pengangkatan Dosen"
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">File</label>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                    onChange={(e) => setUploadFile(e.target.files?.[0] ?? null)}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-500 file:mr-3 file:rounded-md file:border-0 file:bg-blue-50 file:px-3 file:py-1 file:text-sm file:font-medium file:text-blue-700 hover:file:bg-blue-100"
                    required
                  />
                  <p className="mt-1 text-xs text-slate-400">PDF, DOC, DOCX, JPG, PNG (maks. tipe file yang didukung)</p>
                </div>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  Deskripsi (opsional)
                </label>
                <textarea
                  value={uploadDeskripsi}
                  onChange={(e) => setUploadDeskripsi(e.target.value)}
                  rows={2}
                  placeholder="Keterangan singkat dokumen..."
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-800 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3">
                <input
                  id="is-global-toggle"
                  type="checkbox"
                  checked={uploadIsGlobal}
                  onChange={(e) => setUploadIsGlobal(e.target.checked)}
                  className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="is-global-toggle" className="text-sm text-slate-700">
                  <span className="font-medium">Bagikan ke semua prodi (Global)</span>
                  <span className="ml-2 text-slate-400">
                    — Jika tidak dicentang, dokumen hanya terlihat oleh prodi Anda sendiri.
                  </span>
                </label>
              </div>

              {uploadError && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
                  ⚠️ {uploadError}
                </div>
              )}

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={uploading}
                  className="inline-flex items-center gap-2 rounded-lg bg-[#00509d] px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#003f7d] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {uploading ? "Mengunggah..." : "Unggah Sekarang"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowUploadForm(false)}
                  className="rounded-lg border border-slate-300 px-5 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
                >
                  Batal
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Stats Summary */}
        <div className="grid gap-4 sm:grid-cols-3">
          {[
            { label: "Total Dokumen", value: evidenceList.length, color: "text-slate-800" },
            { label: "Dokumen Global", value: globalCount, color: "text-blue-700" },
            { label: "Dokumen Prodi", value: prodiCount, color: "text-green-700" },
          ].map((stat) => (
            <div key={stat.label} className="rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
              <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{stat.label}</p>
              <p className={`mt-1 text-3xl font-bold ${stat.color}`}>{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Filter & Search Bar */}
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="flex gap-2">
            {(["all", "global", "prodi"] as const).map((type) => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${filterType === type
                    ? "bg-[#00509d] text-white"
                    : "border border-slate-300 bg-white text-slate-600 hover:bg-slate-50"
                  }`}
              >
                {type === "all" ? "Semua" : type === "global" ? "🌐 Global" : "🏫 Prodi"}
              </button>
            ))}
          </div>
          <input
            type="search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Cari judul atau deskripsi..."
            className="w-full rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 md:w-72"
          />
        </div>

        {/* Evidence List */}
        <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          {loadingList ? (
            <div className="flex items-center justify-center py-16">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
            </div>
          ) : error ? (
            <div className="p-8 text-center">
              <p className="text-sm text-red-500">{error}</p>
              <button
                onClick={fetchEvidence}
                className="mt-3 rounded-lg border border-slate-300 px-4 py-1.5 text-sm text-slate-600 hover:bg-slate-50"
              >
                Coba Lagi
              </button>
            </div>
          ) : filteredList.length === 0 ? (
            <div className="py-16 text-center">
              <p className="text-4xl">📂</p>
              <p className="mt-3 text-sm font-medium text-slate-500">
                {searchQuery || filterType !== "all"
                  ? "Tidak ada dokumen yang cocok dengan filter."
                  : "Belum ada dokumen evidence. Mulai unggah sekarang!"}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {filteredList.map((ev) => (
                <div
                  key={ev.id}
                  className="flex flex-col gap-3 p-4 transition-colors hover:bg-slate-50 md:flex-row md:items-center md:justify-between"
                >
                  {/* File Info */}
                  <div className="flex items-start gap-3 min-w-0">
                    <span className="mt-0.5 text-2xl flex-shrink-0">{getFileIcon(ev.tipe_file)}</span>
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-semibold text-slate-800 truncate">{ev.judul}</h3>
                        {ev.is_global ? (
                          <span className="inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-700">
                            Global
                          </span>
                        ) : (
                          <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-700">
                            Prodi
                          </span>
                        )}
                      </div>
                      {ev.deskripsi && (
                        <p className="mt-0.5 text-sm text-slate-500 line-clamp-1">{ev.deskripsi}</p>
                      )}
                      <p className="mt-1 text-xs text-slate-400">
                        Diunggah {formatDate(ev.uploaded_at)}
                        {ev.tipe_file && ` · ${ev.tipe_file.split("/").pop()?.toUpperCase()}`}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-shrink-0 gap-2 md:ml-4">
                    <button
                      onClick={() => handleDownload(ev)}
                      disabled={downloadingId === ev.id}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {downloadingId === ev.id ? "Mengunduh..." : "⬇ Unduh"}
                    </button>
                    {canEdit && (
                      <button
                        onClick={() => handleDelete(ev.id)}
                        disabled={deletingId === ev.id}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-sm font-medium text-red-600 shadow-sm hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        {deletingId === ev.id ? "Menghapus..." : "🗑 Hapus"}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
