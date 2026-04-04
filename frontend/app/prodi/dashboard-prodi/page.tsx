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
  const dropdownRef = useRef<HTMLDivElement>(null);

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

  const role = user?.role?.name || "tim_prodi";
  const onUnduhLKPS = async () => {
    if (!data?.lkps_submission_id) {
      alert("Belum ada submission LKPS untuk siklus ini.");
      return;
    }
    try {
      const { downloadLkpsWorkbook } = await import("@/lib/api/lkps");
      await downloadLkpsWorkbook(data.lkps_submission_id);
    } catch (err) {
      alert("Gagal mengunduh LKPS: " + (err instanceof Error ? err.message : String(err)));
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

          <div className="flex items-center gap-3">
          <button
            onClick={onUnduhLKPS}
            className="inline-flex h-full items-center justify-center rounded-lg bg-[#00509d] px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-[#003f7d] focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Unduh LKPS
          </button>
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="inline-flex w-40 items-center justify-between rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Tahun {tahun || data.current_year}
              <svg
                className={`ml-2 h-5 w-5 transition-transform ${
                  dropdownOpen ? "rotate-180" : ""
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-40 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
                <div className="py-1">
                  {data.available_years.map((y) => (
                    <button
                      key={y}
                      onClick={() => {
                        setTahun(y.toString());
                        setDropdownOpen(false);
                      }}
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
        <section className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
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
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-sm font-medium text-slate-500">
              Progress Dokumen Pendukung
            </h3>
            <div className="mt-4">
              <ProgressBar progress={data.evidence_percent} />
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {data.evidence_percent}%
              </p>
            </div>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col items-center justify-center">
            <GaugeMeter
              score={data.score_value}
              max={4.0}
              target={data.target_score}
              title="Simulasi Skor"
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
                    <StatusDot status={kriteria.status} />
                    <div>
                      <h4 className="font-semibold text-slate-900">
                        {kriteria.name}
                      </h4>
                      <p className="text-sm text-slate-500">
                        Status: {kriteria.status_label}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-1 items-center justify-end space-x-4">
                    <div className="w-32 hidden md:block">
                      <ProgressBar progress={kriteria.progress} />
                    </div>
                    <span className="text-sm font-medium text-slate-700">
                      {kriteria.progress}%
                    </span>
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
