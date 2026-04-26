"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import ProgressBar from "@/app/components/dashboard-prodi/ProgressBar";
import StatusDot from "@/app/components/dashboard-prodi/StatusDot";
import GaugeMeter from "@/app/components/dashboard-prodi/GaugeMeter";
import {
  CriteriaRow,
  DashboardData,
} from "@/app/components/dashboard-prodi/types";
import { apiFetch } from "@/app/services/api";
import { useAuth } from "@/app/hooks/useAuth";
import { useClickOutside } from "@/app/hooks/useClickOutside";

const canEdit = (role: string) =>
  ["admin", "koordinator", "tim_prodi"].includes(role);

export default function DashboardProdiPage() {
  const [tahun, setTahun] = useState<string | null>(null);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isDownloadingLKPS, setIsDownloadingLKPS] = useState(false);
  const [isDownloadingLED, setIsDownloadingLED] = useState(false);
  const [isImportingLKPS, setIsImportingLKPS] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const importFileRef = useRef<HTMLInputElement>(null);

  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const searchParams = useSearchParams();
  const prodiIdFromUrl = searchParams.get("id");

  // Tutup dropdown saat klik di luar
  useClickOutside(dropdownRef, () => setDropdownOpen(false));

  // Fetch dashboard data — re-fetch saat tahun berubah
  useEffect(() => {
    const prodiId = prodiIdFromUrl || user?.program_studi_id;

    if (!prodiId) {
      if (!authLoading) setLoading(false);
      return;
    }

    async function fetchDashboard() {
      setLoading(true);
      setError(null);
      try {
        const url = tahun
          ? `/api/v1/prodi/${prodiId}/dashboard?tahun=${tahun}`
          : `/api/v1/prodi/${prodiId}/dashboard`;

        const res = await apiFetch(url);
        if (!res.ok) {
          throw new Error("Gagal mengambil data dashboard");
        }
        const json: DashboardData = await res.json();
        setData(json);
      } catch (err: any) {
        setError(err.message || "Terjadi kesalahan");
      } finally {
        setLoading(false);
      }
    }

    fetchDashboard();
  }, [tahun, user?.program_studi_id, prodiIdFromUrl, authLoading]);

  if (authLoading || loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg font-medium text-slate-500">Memuat data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen flex-col items-center justify-center space-y-4">
        <div className="text-lg font-medium text-red-500">{error}</div>
        <button
          onClick={() => window.location.reload()}
          className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Coba Lagi
        </button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg font-medium text-slate-500">
          Data tidak ditemukan.
        </div>
      </div>
    );
  }

  const role = user?.role || "tim_prodi";
  const onUnduhLKPS = async () => {
    if (!data?.lkps_submission_id) {
      alert("Belum ada submission LKPS untuk siklus ini.");
      return;
    }
    if (isDownloadingLKPS) return;

    setIsDownloadingLKPS(true);
    console.log("[LKPS Download] Starting download for submission ID:", data.lkps_submission_id);
    try {
      const { downloadLkpsWorkbook } = await import("@/lib/api/lkps");
      console.log("[LKPS Download] Calling API...");
      const blob = await downloadLkpsWorkbook(data.lkps_submission_id);
      console.log("[LKPS Download] Received blob:", blob, "Size:", blob.size, "Type:", blob.type);

      const url = window.URL.createObjectURL(blob);
      console.log("[LKPS Download] Created Object URL:", url);

      const a = document.createElement("a");
      a.href = url;
      const prodiName = data?.program_studi_profile?.name || "Prodi";
      const fileName = `LKPS_${prodiName.replace(/\\s+/g, "_")}.xlsx`;
      a.download = fileName;
      console.log("[LKPS Download] Appending anchor element with filename:", fileName);

      document.body.appendChild(a);
      a.click();
      console.log("[LKPS Download] Download triggered.");

      window.URL.revokeObjectURL(url);
      a.remove();
      console.log("[LKPS Download] Cleanup finished.");
    } catch (err) {
      console.error("[LKPS Download] Error encountered:", err);
      if (err instanceof TypeError) {
        console.error("[LKPS Download] This might be a network or CORS error. Check backend server and network tab.");
      }
      alert("Gagal mengunduh LKPS: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setIsDownloadingLKPS(false);
    }
  };

  const onUnduhLED = async () => {
    if (!data?.target_akreditasi_id) {
      alert("Belum ada target akreditasi untuk siklus ini.");
      return;
    }
    if (isDownloadingLED) return;

    setIsDownloadingLED(true);
    try {
      const { apiFetch, API_URL } = await import("@/app/services/api");
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const res = await fetch(`${API_URL}/api/v1/led/export/${data.target_akreditasi_id}`, {
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });
      if (!res.ok) {
        let msg = res.statusText;
        try {
          const body = await res.json();
          msg = body.detail ?? msg;
        } catch { /* ignore */ }
        throw new Error(msg || `Request failed with status ${res.status}`);
      }
      const blob = await res.blob();

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const prodiName = data?.program_studi_profile?.name || "Prodi";
      a.download = `LED_${prodiName.replace(/\s+/g, "_")}.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (err) {
      alert("Gagal mengunduh LED: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setIsDownloadingLED(false);
    }
  };

  const onImportLKPS = async () => {
    const file = importFileRef.current?.files?.[0];
    if (!file) {
      setImportError("Pilih file terlebih dahulu.");
      return;
    }
    if (!data?.lkps_submission_id) {
      setImportError("Belum ada submission LKPS untuk siklus ini.");
      return;
    }
    setIsImportingLKPS(true);
    setImportError(null);
    try {
      const { uploadLkps } = await import("@/lib/api/lkps");
      await uploadLkps(data.lkps_submission_id, file);
      if (importFileRef.current) importFileRef.current.value = "";
    } catch (err) {
      setImportError(err instanceof Error ? err.message : "Gagal mengimpor LKPS.");
    } finally {
      setIsImportingLKPS(false);
    }
  };

  const editAllowed = canEdit(role);

  return (
    <main className="min-h-screen bg-slate-50 p-6 md:p-8">
      <div className="mx-auto max-w-7xl space-y-8">
        {/* Header Section */}
        <header className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 md:text-3xl">
              Dashboard Akreditasi
            </h1>
            <p className="mt-1 text-sm text-slate-500 md:text-base">
              {data.program_studi_profile.name} •{" "}
              {data.program_studi_profile.degree}
            </p>
          </div>

          <div className="flex flex-col items-end gap-2">
            <div className="flex items-center gap-3">
              <button
                onClick={onUnduhLKPS}
                disabled={isDownloadingLKPS}
                className={`inline-flex items-center justify-center rounded-lg px-4 py-2.5 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${isDownloadingLKPS ? 'bg-[#00509d] opacity-70 cursor-not-allowed' : 'bg-[#00509d] hover:bg-[#003f7d]'}`}
              >
                {isDownloadingLKPS ? "Mengunduh..." : "Unduh LKPS"}
              </button>
              <button
                onClick={onUnduhLED}
                disabled={isDownloadingLED}
                className={`inline-flex items-center justify-center rounded-lg px-4 py-2.5 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 ${isDownloadingLED ? 'bg-green-700 opacity-70 cursor-not-allowed' : 'bg-green-700 hover:bg-green-800'}`}
              >
                {isDownloadingLED ? "Mengunduh..." : "Unduh LED"}
              </button>
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="inline-flex w-40 items-center justify-between rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Tahun {tahun || data.current_year}
                  <svg
                    className={`ml-2 h-5 w-5 transition-transform ${dropdownOpen ? "rotate-180" : ""}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-40 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
                    <div className="py-1">
                      {data.available_years.map((y) => (
                        <button
                          key={y}
                          onClick={() => { setTahun(y.toString()); setDropdownOpen(false); }}
                          className="block w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-100"
                        >
                          {y}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
            {/* Import LKPS */}
            <div className="flex items-center gap-2">
              <input
                ref={importFileRef}
                type="file"
                accept=".xls,.xlsx"
                className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-500 file:mr-3 file:rounded-md file:border-0 file:bg-blue-50 file:px-3 file:py-1 file:text-xs file:font-medium file:text-blue-700 hover:file:bg-blue-100"
              />
              <button
                onClick={onImportLKPS}
                disabled={isImportingLKPS}
                className={`inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${isImportingLKPS ? 'bg-[#00509d] opacity-70 cursor-not-allowed' : 'bg-[#00509d] hover:bg-[#003f7d]'}`}
              >
                {isImportingLKPS ? "Mengimpor..." : "Import LKPS"}
              </button>
            </div>
            {importError && (
              <p className="text-xs text-red-600">{importError}</p>
            )}
          </div>
        </header>

        {/* Warnings & Recommendations */}
        {(data.early_warnings.length > 0 ||
          data.recommendation_messages.length > 0) && (
            <div className="space-y-4">
              {data.early_warnings.map((msg, i) => (
                <div
                  key={i}
                  className="rounded-lg border-l-4 border-red-500 bg-red-50 p-4 shadow-sm"
                >
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg
                        className="h-5 w-5 text-red-400"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-red-800">{msg}</p>
                    </div>
                  </div>
                </div>
              ))}
              {data.recommendation_messages.map((msg, i) => (
                <div
                  key={i}
                  className="rounded-lg border-l-4 border-blue-500 bg-blue-50 p-4 shadow-sm"
                >
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg
                        className="h-5 w-5 text-blue-400"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-blue-800">{msg}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

        {/* Overview Cards */}
        <section className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-sm font-medium text-slate-500">
              Progress LKPS
            </h3>
            <div className="mt-4">
              <ProgressBar progress={data.lkps_percent} />
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {data.lkps_percent}%
              </p>
            </div>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-sm font-medium text-slate-500">Progress LED</h3>
            <div className="mt-4">
              <ProgressBar progress={data.led_percent} />
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {data.led_percent}%
              </p>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col items-center justify-center">
            <GaugeMeter
              score={data.score_value}
              target={data.target_score}
            />
          </div>
        </section>

        {/* Criteria List */}
        <section className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="border-b border-slate-200 bg-slate-50 px-6 py-4">
            <h2 className="text-lg font-semibold text-slate-800">
              Detail Kriteria
            </h2>
          </div>
          <div className="divide-y divide-slate-200">
            {data.criteria_list.map((kriteria: CriteriaRow) => (
              <div
                key={kriteria.id}
                className="p-6 transition-colors hover:bg-slate-50"
              >
                <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                  <div className="flex items-center space-x-4">
                    <StatusDot
                      status={kriteria.status}
                      label={kriteria.status_label} />
                    <div>
                      <h4 className="font-semibold text-slate-900">
                        {kriteria.name}
                      </h4>
                      <p className="text-sm text-slate-500">
                        Status: {kriteria.status_label}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-1 items-center justify-end">
                    <div className="hidden md:flex flex-col gap-1.5 w-48">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-slate-400 w-8 shrink-0">LKPS</span>
                        <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-2 bg-[#00509d] rounded-full transition-all duration-500"
                            style={{ width: `${kriteria.lkps_progress ?? 0}%` }}
                          />
                        </div>
                        <span className="text-[10px] font-semibold text-gray-600 w-7 text-right">
                          {kriteria.lkps_progress ?? 0}%
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-slate-400 w-8 shrink-0">LED</span>
                        <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-2 bg-green-600 rounded-full transition-all duration-500"
                            style={{ width: `${kriteria.led_progress ?? 0}%` }}
                          />
                        </div>
                        <span className="text-[10px] font-semibold text-gray-600 w-7 text-right">
                          {kriteria.led_progress ?? 0}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {editAllowed && (
                    <div className="mt-4 flex gap-2 md:mt-0">
                      <button
                        onClick={() =>
                          router.push(
                            `/akreditasi/lkps/${data.lkps_submission_id}?kriteria=${kriteria.id}&target_akreditasi_id=${data.target_akreditasi_id}&tahun=${data.current_year}&id=${prodiIdFromUrl || ""}`,
                          )
                        }
                        className="rounded-md bg-blue-50 px-3 py-1.5 text-sm font-medium text-blue-700 hover:bg-blue-100"
                      >
                        Isi LKPS
                      </button>
                      <button
                        onClick={() =>
                          router.push(
                            `/prodi/led?kriteria_kode=${kriteria.id}&target_akreditasi_id=${data.target_akreditasi_id}&tahun=${data.current_year}&id=${prodiIdFromUrl || ""}&lkps_submission_id=${data.lkps_submission_id}`,
                          )
                        }
                        className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                      >
                        Isi LED
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
