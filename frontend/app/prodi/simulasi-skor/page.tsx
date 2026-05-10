"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { DashboardData } from "@/app/components/dashboard-prodi/types";
import { useAuth } from "@/app/hooks/useAuth";
import { apiFetch } from "@/app/services/api";

const MIN_PASS_SCORE = 200;

interface AutomaticIndicator {
  kode_indikator: string;
  nama_indikator: string;
  komponen: string;
  nilai_input: number;
  skor_mentah: number;
  kontribusi: number;
  kontribusi_maks: number;
  sumber_data: string;
}

interface MatrixIndicator {
  kode_indikator: string;
  nama_indikator: string;
  komponen: string;
  mode: "AUTO_LKPS" | "MANUAL";
  kontribusi_maks: number;
  skor_manual: number | null;
  kontribusi_manual: number;
}

interface AutomaticSimulation {
  program_studi: string;
  tahun_ts: number;
  submission_id: string;
  nilai_otomatis: number;
  nilai_manual: number;
  nilai_total: number;
  nilai_maksimum_total: number;
  nilai_maksimum_otomatis: number;
  jumlah_indikator_otomatis: number;
  jumlah_indikator_manual_terisi: number;
  breakdown_skor: Record<string, number>;
  indikator: AutomaticIndicator[];
  semua_indikator: MatrixIndicator[];
  catatan: string;
}

export default function SimulasiSkorPage() {
  const { user, loading: authLoading } = useAuth();
  const searchParams = useSearchParams();
  const prodiIdFromUrl = searchParams.get("id");

  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [simulation, setSimulation] = useState<AutomaticSimulation | null>(null);
  const [manualScores, setManualScores] = useState<Record<string, string>>({});
  const [savingManual, setSavingManual] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const prodiId = prodiIdFromUrl || user?.program_studi_id;

    if (!prodiId) {
      if (!authLoading) setLoading(false);
      return;
    }

    async function fetchSimulation() {
      setLoading(true);
      setError(null);

      try {
        const [dashboardRes, simulationRes] = await Promise.all([
          apiFetch(`/api/v1/prodi/${prodiId}/dashboard`),
          apiFetch(`/api/v1/simulasi/otomatis/${prodiId}`),
        ]);

        if (!dashboardRes.ok) {
          throw new Error("Gagal mengambil data dashboard.");
        }
        if (!simulationRes.ok) {
          throw new Error("Gagal menghitung simulasi otomatis.");
        }

        const simulationData: AutomaticSimulation = await simulationRes.json();
        const savedManualScores = Object.fromEntries(
          simulationData.semua_indikator
            .filter((item) => item.mode === "MANUAL" && item.skor_manual !== null)
            .map((item) => [item.kode_indikator, String(item.skor_manual)]),
        );

        setDashboard(await dashboardRes.json());
        setSimulation(simulationData);
        setManualScores(savedManualScores);
        setSaveMessage(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Terjadi kesalahan saat memuat data.",
        );
      } finally {
        setLoading(false);
      }
    }

    fetchSimulation();
  }, [authLoading, prodiIdFromUrl, user?.program_studi_id]);

  if (authLoading || loading) {
    return (
      <div className="flex min-h-[calc(100vh-80px)] items-center justify-center">
        <p className="text-sm font-medium text-slate-500">Menghitung simulasi skor...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[calc(100vh-80px)] items-center justify-center px-6">
        <div className="rounded-xl border border-red-100 bg-white px-5 py-4 text-sm font-medium text-red-600 shadow-sm">
          {error}
        </div>
      </div>
    );
  }

  if (!dashboard || !simulation) {
    return (
      <div className="flex min-h-[calc(100vh-80px)] items-center justify-center px-6">
        <div className="rounded-xl border border-slate-200 bg-white px-5 py-4 text-sm font-medium text-slate-500 shadow-sm">
          Data simulasi tidak ditemukan.
        </div>
      </div>
    );
  }

  const maxScore = simulation.nilai_maksimum_total;
  const automaticByCode = new Map(
    simulation.indikator.map((item) => [item.kode_indikator, item]),
  );
  const manualScoreEntries = Object.entries(manualScores)
    .filter(([, value]) => value.trim() !== "")
    .map(([kode, value]) => [kode, Number(value)] as const)
    .filter(([, value]) => !Number.isNaN(value));
  const manualContribution = manualScoreEntries.reduce((total, [kode, value]) => {
    const indicator = simulation.semua_indikator.find(
      (item) => item.kode_indikator === kode,
    );
    if (!indicator) return total;
    return total + (Math.min(4, Math.max(0, value)) / 4) * indicator.kontribusi_maks;
  }, 0);
  const manualFilled = manualScoreEntries.length;
  const totalScore = simulation.nilai_otomatis + manualContribution;
  const scorePct = Math.min(
    100,
    Math.max(0, (totalScore / maxScore) * 100),
  );
  const passPct = (MIN_PASS_SCORE / maxScore) * 100;
  const automatedCoveragePct = Math.round(
    (simulation.nilai_maksimum_otomatis / maxScore) * 100,
  );
  const statusLabel = "Simulasi Parsial";
  const statusClass = "bg-blue-50 text-blue-700 border-blue-200";

  async function handleSaveManualScores() {
    setSavingManual(true);
    setSaveMessage(null);

    const scores = Object.fromEntries(
      manualScoreEntries.map(([kode, value]) => [
        kode,
        Math.min(4, Math.max(0, value)),
      ]),
    );

    try {
      const response = await apiFetch(
        `/api/v1/simulasi/manual/${simulation.submission_id}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ scores }),
        },
      );

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new Error(errorBody?.detail || "Gagal menyimpan skor manual.");
      }

      setSaveMessage("Skor manual tersimpan ke database.");
    } catch (err) {
      setSaveMessage(
        err instanceof Error ? err.message : "Gagal menyimpan skor manual.",
      );
    } finally {
      setSavingManual(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-80px)] bg-slate-50 px-6 py-6">
      <div className="mx-auto flex max-w-6xl flex-col gap-5">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Simulasi Skor
          </p>
          <h1 className="mt-1 text-2xl font-bold text-[#132040]">
            {simulation.program_studi}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            Tahun akreditasi {simulation.tahun_ts}
          </p>
        </div>

        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Skor Simulasi Sementara
              </p>
              <div className="mt-2 flex items-end gap-3">
                <span className="text-5xl font-bold text-[#00509d]">
                  {totalScore.toFixed(2)}
                </span>
                <span className="mb-1 text-sm font-semibold text-slate-400">
                  / {maxScore.toFixed(0)}
                </span>
              </div>
              <p className="mt-2 text-xs text-slate-500">
                Otomatis {simulation.nilai_otomatis.toFixed(2)} + manual{" "}
                {manualContribution.toFixed(2)}
              </p>
            </div>

            <div className={`rounded-full border px-3 py-1 text-xs font-bold ${statusClass}`}>
              {statusLabel}
            </div>
          </div>

          <div className="mt-6">
            <div className="relative h-5 overflow-hidden rounded-full bg-slate-100">
              <div
                className="absolute inset-y-0 left-0 bg-[#00509d] transition-all duration-700"
                style={{ width: `${scorePct}%` }}
              />
              <div
                className="absolute inset-y-0 w-0.5 bg-red-400"
                style={{ left: `${passPct}%` }}
              />
            </div>
            <div className="mt-2 flex justify-between text-[11px] font-medium text-slate-400">
              <span>0</span>
              <span>Ambang lulus {MIN_PASS_SCORE}</span>
              <span>{maxScore.toFixed(0)}</span>
            </div>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-4">
            <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Indikator Otomatis
              </p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {simulation.jumlah_indikator_otomatis}
              </p>
            </div>
            <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Cakupan Bobot
              </p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {automatedCoveragePct}%
              </p>
            </div>
            <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Progress LKPS
              </p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {dashboard.lkps_percent}%
              </p>
            </div>
            <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Target
              </p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {dashboard.target_score > 0 ? dashboard.target_score.toFixed(0) : "-"}
              </p>
            </div>
            <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Manual Terisi
              </p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                {manualFilled}
              </p>
            </div>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <span className="inline-block h-6 w-1 rounded-full bg-[#00509d]" />
            <h2 className="text-base font-bold text-[#132040]">
              Indikator yang Sudah Dihitung Otomatis
            </h2>
          </div>

          <div className="mt-4 overflow-hidden rounded-lg border border-slate-100">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
                <tr>
                  <th className="px-4 py-3">Kode</th>
                  <th className="px-4 py-3">Indikator</th>
                  <th className="px-4 py-3">Sumber Data</th>
                  <th className="px-4 py-3">Input</th>
                  <th className="px-4 py-3">Skor</th>
                  <th className="px-4 py-3">Kontribusi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {simulation.indikator.map((item) => (
                  <tr key={item.kode_indikator} className="bg-white">
                    <td className="px-4 py-3 font-semibold text-slate-600">
                      {item.kode_indikator}
                    </td>
                    <td className="px-4 py-3 text-slate-700">
                      <p className="font-medium">{item.nama_indikator}</p>
                      <p className="text-xs text-slate-400">{item.komponen}</p>
                    </td>
                    <td className="px-4 py-3 text-xs leading-relaxed text-slate-500">
                      {item.sumber_data}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {item.nilai_input.toLocaleString("id-ID")}
                    </td>
                    <td className="px-4 py-3 font-semibold text-slate-700">
                      {item.skor_mentah.toFixed(2)}
                    </td>
                    <td className="px-4 py-3 font-semibold text-[#00509d]">
                      {item.kontribusi.toFixed(2)} / {item.kontribusi_maks.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <span className="inline-block h-6 w-1 rounded-full bg-[#00509d]" />
            <h2 className="text-base font-bold text-[#132040]">
              Input Skor Manual
            </h2>
            <button
              type="button"
              onClick={handleSaveManualScores}
              disabled={savingManual}
              className="ml-auto rounded-lg bg-[#00509d] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#003f7d] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {savingManual ? "Menyimpan..." : "Simpan Skor Manual"}
            </button>
          </div>
          {saveMessage && (
            <p className="mt-3 text-sm font-medium text-slate-500">
              {saveMessage}
            </p>
          )}

          <div className="mt-4 overflow-hidden rounded-lg border border-slate-100">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
                <tr>
                  <th className="px-4 py-3">Kode</th>
                  <th className="px-4 py-3">Indikator</th>
                  <th className="px-4 py-3">Mode</th>
                  <th className="px-4 py-3">Skor Rubrik</th>
                  <th className="px-4 py-3">Poin</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {simulation.semua_indikator.map((item) => {
                  const automatic = automaticByCode.get(item.kode_indikator);
                  const manualValue = Number(manualScores[item.kode_indikator] || 0);
                  const manualPoint =
                    automatic?.kontribusi ??
                    (Math.min(4, Math.max(0, manualValue)) / 4) *
                      item.kontribusi_maks;

                  return (
                    <tr key={item.kode_indikator} className="bg-white">
                      <td className="px-4 py-3 font-semibold text-slate-600">
                        {item.kode_indikator}
                      </td>
                      <td className="px-4 py-3 text-slate-700">
                        <p className="font-medium">{item.nama_indikator}</p>
                        <p className="text-xs text-slate-400">{item.komponen}</p>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`rounded-full px-2 py-1 text-[11px] font-semibold ${
                            automatic
                              ? "bg-emerald-50 text-emerald-700"
                              : "bg-amber-50 text-amber-700"
                          }`}
                        >
                          {automatic ? "Otomatis" : "Manual"}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {automatic ? (
                          <span className="font-semibold text-slate-700">
                            {automatic.skor_mentah.toFixed(2)} / 4
                          </span>
                        ) : (
                          <input
                            type="number"
                            min="0"
                            max="4"
                            step="0.1"
                            value={manualScores[item.kode_indikator] ?? ""}
                            onChange={(event) => {
                              const { value } = event.target;
                              setManualScores((current) => {
                                const next = { ...current };
                                if (value === "") {
                                  delete next[item.kode_indikator];
                                } else {
                                  next[item.kode_indikator] = value;
                                }
                                return next;
                              });
                            }}
                            className="h-9 w-24 rounded-lg border border-slate-200 px-3 text-sm font-semibold text-slate-700 outline-none focus:border-[#00509d]"
                            placeholder="0-4"
                          />
                        )}
                      </td>
                      <td className="px-4 py-3 font-semibold text-[#00509d]">
                        {manualPoint.toFixed(2)} / {item.kontribusi_maks.toFixed(2)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <span className="inline-block h-6 w-1 rounded-full bg-[#00509d]" />
            <h2 className="text-base font-bold text-[#132040]">
              Breakdown Kontribusi
            </h2>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            {Object.entries(simulation.breakdown_skor).map(([name, value]) => (
              <div key={name} className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  {name}
                </p>
                <p className="mt-1 text-2xl font-bold text-slate-900">
                  {value.toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
