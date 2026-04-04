"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
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

const DashboardProdiPage = () => {
  const [tahun, setTahun] = useState<string | null>(null);
  const router = useRouter();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const [dashboardData, setDashboardData] = useState<DashboardData | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { user, loading: authLoading } = useAuth();

  // Tutup dropdown saat klik di luar
  useClickOutside(dropdownRef, () => setDropdownOpen(false));

  // Fetch dashboard data — re-fetch saat tahun berubah
  useEffect(() => {
    const prodiId = user?.program_studi_id;
    console.log("prodiId", prodiId);

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
        if (!res.ok) throw new Error("Gagal mengambil data dashboard");
        const data: DashboardData = await res.json();
        setDashboardData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Terjadi kesalahan");
      } finally {
        setLoading(false);
      }
    }

    fetchDashboard();
  }, [user, tahun]); // ← tahun sebagai dependency

  // TODO: ganti alert dengan toast notification
  const onUnduhLKPS = async () => {
    if (!dashboardData?.lkps_submission_id) {
      alert("Belum ada submission LKPS untuk siklus ini.");
      return;
    }
    try {
      const { downloadLkpsWorkbook } = await import("@/lib/api/lkps");
      await downloadLkpsWorkbook(dashboardData.lkps_submission_id);
    } catch (err) {
      alert(
        "Gagal mengunduh LKPS: " +
          (err instanceof Error ? err.message : String(err)),
      );
    }
  };
  const onUnduhLED = () => alert("Unduh LED coming soon...");
  const onInputLKPS = (id: string) => {
    if (!dashboardData?.lkps_submission_id) {
      alert(
        "Submission LKPS belum dibuat untuk siklus ini. Silakan buat di halaman LKPS terlebih dahulu.",
      );
      router.push("/akreditasi/lkps");
      return;
    }
    router.push(`/akreditasi/lkps/${dashboardData.lkps_submission_id}`);
  };
  const onInputLED = (id: string) => {
    // Note: Requires target_akreditasi_id to be returned in dashboardData
    // If dashboardData doesn't have target_akreditasi_id, backend endpoint needs to be updated
    if (!dashboardData?.target_akreditasi_id) {
      alert("Target akreditasi tidak ditemukan. Silakan segarkan halaman.");
      return;
    }

    const tahunAktif = tahun ? Number(tahun) : current_year;

    router.push(
      `/prodi/led?target_akreditasi_id=${dashboardData.target_akreditasi_id}&kriteria_kode=${id}&tahun=${tahunAktif}`,
    );
  };
  const onAturDeadline = () => alert("Atur Deadline coming soon...");

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#f4f6f8]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#00509d]" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#f4f6f8] p-5">
        <div className="bg-white max-w-md w-full rounded-xl shadow-sm border border-red-100 p-8 text-center text-[#132040]">
          <span className="text-5xl block mb-4">⚠️</span>
          <h2 className="text-lg font-bold mb-2">Terjadi Kesalahan</h2>
          <p className="text-sm text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-[#00509d] text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-[#003f7d] transition-colors"
          >
            Muat Ulang
          </button>
        </div>
      </div>
    );
  }

  if (!user) return null;
  if (!user.program_studi_id) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#f4f6f8] p-5">
        <div className="bg-white max-w-md w-full rounded-xl shadow-sm border border-orange-100 p-8 text-center text-[#132040]">
          <span className="text-5xl block mb-4">👤</span>
          <h2 className="text-lg font-bold mb-2">Profil Tidak Lengkap</h2>
          <p className="text-sm text-gray-600 mb-6">
            Akun Anda tidak terhubung dengan Program Studi manapun. Silakan
            hubungi admin.
          </p>
        </div>
      </div>
    );
  }

  if (!dashboardData) return null;

  const {
    program_studi_profile: profilProdi,
    current_year,
    available_years,
    criteria_list: criteriaList,
    recommendation_messages: pesanRekomendasi,
    early_warnings: earlyWarnings,
    score_value: scoreValue,
    target_score: targetScore,
    deadline,
    days_remaining: sisaHari,
    lkps_percent: lkpsPercent,
    led_percent: ledPercent,
    evidence_percent: evidencePercent,
  } = dashboardData;

  const editable = canEdit(user.role);

  return (
    <div className="p-6 px-10 bg-[#f4f6f8] min-h-screen">
      {!profilProdi.is_active_accreditation && (
        <div className="mb-5 bg-gray-100 border border-gray-300 rounded-xl px-5 py-3 flex items-center gap-3 text-sm text-gray-600">
          <span className="text-2xl">🔒</span>
          <div>
            <p className="font-bold text-gray-700">
              Prodi tidak aktif dalam siklus akreditasi tahun ini
            </p>
            <p>
              Hubungi admin untuk mengaktifkan prodi pada siklus akreditasi ini.
            </p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 mb-5">
        <div className="flex items-center gap-3 mb-4">
          <span className="w-1 h-6 bg-[#00509d] rounded-full inline-block" />
          <h2 className="text-base font-bold text-[#132040]">
            Profil Program Studi
          </h2>
          <span className="ml-auto text-xs bg-[#00509d]/10 text-[#00509d] font-semibold px-2.5 py-1 rounded-full capitalize">
            {user.role.replace("_", " ")}
          </span>
        </div>
        <div className="flex flex-wrap gap-6 text-sm">
          <div>
            <p className="text-xs text-gray-400 mb-0.5">Program Studi</p>
            <p className="font-semibold text-gray-800">{profilProdi.name}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-0.5">Jenjang</p>
            <p className="font-semibold text-gray-800">{profilProdi.degree}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-0.5">Akreditasi Terakhir</p>
            <p className="font-semibold text-gray-800">
              {profilProdi.last_accreditation_status}
              <span className="text-gray-400 font-normal ml-1">
                ({profilProdi.last_accreditation_year})
              </span>
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-0.5">Status Siklus Ini</p>
            <span
              className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                profilProdi.is_active_accreditation
                  ? "bg-green-100 text-green-700"
                  : "bg-gray-200 text-gray-500"
              }`}
            >
              {profilProdi.is_active_accreditation ? "Aktif" : "Tidak aktif"}
            </span>
          </div>
        </div>
      </div>

      <div className="flex gap-6 flex-wrap">
        <div className="flex-1 min-w-[320px] flex flex-col gap-4">
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-3">
                <span className="w-1 h-6 bg-[#00509d] rounded-full inline-block" />
                <h1 className="text-xl font-bold text-[#132040]">
                  Progres Akreditasi
                </h1>
              </div>

              {/* Dropdown dengan click-outside */}
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setDropdownOpen((prev) => !prev)}
                  className="flex items-center gap-2 border border-[#00509d] rounded-lg px-3 py-1.5 text-sm text-[#00509d] font-semibold hover:bg-blue-50 transition-colors"
                >
                  {tahun || current_year}
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
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
                  <ul className="absolute right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-[100px] overflow-hidden max-h-48 overflow-y-auto">
                    {available_years.map((t) => (
                      <li key={t}>
                        <button
                          className="w-full text-left px-4 py-2 text-sm hover:bg-blue-50 hover:text-[#00509d] transition-colors"
                          onClick={() => {
                            setTahun(t.toString());
                            setDropdownOpen(false);
                          }}
                        >
                          {t}
                        </button>
                      </li>
                    ))}
                    {available_years.length === 0 && (
                      <li className="px-4 py-2 text-sm text-gray-500 italic">
                        Data kosong
                      </li>
                    )}
                  </ul>
                )}
              </div>
            </div>

            <div className="space-y-3 mb-5">
              {[
                { label: "LKPS", value: lkpsPercent },
                { label: "LED", value: ledPercent },
                { label: "Evidence", value: evidencePercent },
              ].map(({ label, value }) => (
                <div key={label} className="flex items-center gap-3">
                  <span className="text-sm text-gray-600 font-medium w-36 shrink-0">
                    {label}
                  </span>
                  <ProgressBar value={value} />
                </div>
              ))}
            </div>

            <div className="flex gap-2 flex-wrap">
              <button
                onClick={onUnduhLKPS}
                className="flex items-center gap-1.5 text-xs bg-[#00509d] text-white rounded-lg px-4 py-2 hover:bg-[#003f7d] transition-colors font-medium shadow-sm"
              >
                📊 Unduh LKPS
              </button>
              <button
                onClick={onUnduhLED}
                className="flex items-center gap-1.5 text-xs border border-[#00509d] text-[#00509d] rounded-lg px-4 py-2 hover:bg-blue-50 transition-colors font-medium"
              >
                📝 Unduh LED
              </button>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="max-h-[300px] overflow-y-auto">
              <table className="w-full text-sm relative">
                <thead className="sticky top-0 z-10">
                  <tr className="bg-[#00509d] text-white">
                    <th className="px-4 py-3 text-left font-semibold">
                      Kriteria
                    </th>
                    <th className="px-4 py-3 font-semibold">Status</th>
                    <th className="px-4 py-3 font-semibold">Progres</th>
                    {editable && (
                      <th className="px-4 py-3 font-semibold">
                        Isi / Input Dokumen
                      </th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {criteriaList.map((row: CriteriaRow, i: number) => (
                    <tr
                      key={row.id}
                      className={i % 2 === 0 ? "bg-white" : "bg-[#f8fafc]"}
                    >
                      <td className="px-4 py-2.5 text-gray-800 font-medium whitespace-nowrap">
                        {row.name}
                      </td>
                      <td className="px-4 py-2.5">
                        <StatusDot
                          color={row.status}
                          label={row.status_label}
                        />
                      </td>
                      <td className="px-4 py-2.5 text-center font-semibold text-gray-700">
                        {row.progress}%
                      </td>
                      {editable && (
                        <td className="px-4 py-2.5">
                          <div className="flex gap-1.5 flex-wrap">
                            {row.has_lkps && (
                              <button
                                onClick={() => onInputLKPS(row.id)}
                                className={`text-xs rounded-md px-2.5 py-1 transition-colors font-medium border ${
                                  row.lkps_available
                                    ? "border-[#00509d] text-[#00509d] hover:bg-blue-50"
                                    : "border-orange-400 text-orange-600 hover:bg-orange-50"
                                }`}
                              >
                                📊{" "}
                                {row.lkps_available ? "Edit LKPS" : "Isi LKPS"}
                              </button>
                            )}
                            {row.has_led && (
                              <button
                                onClick={() => onInputLED(row.id)}
                                className={`text-xs rounded-md px-2.5 py-1 transition-colors font-medium border ${
                                  row.led_available
                                    ? "border-[#00509d] text-[#00509d] hover:bg-blue-50"
                                    : "border-orange-400 text-orange-600 hover:bg-orange-50"
                                }`}
                              >
                                ✏️ {row.led_available ? "Edit LED" : "Isi LED"}
                              </button>
                            )}
                            {row.has_evidence && (
                              <span className="text-xs text-gray-400 italic py-1">
                                📎 Ada dokumen eviden
                              </span>
                            )}
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {!editable && (
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-1 h-5 bg-[#00509d] rounded-full inline-block" />
                <p className="text-sm font-bold text-[#132040]">
                  Komentar Pimpinan
                </p>
              </div>
              <textarea
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 resize-none focus:outline-none focus:ring-2 focus:ring-[#00509d]/30"
                rows={3}
                placeholder="Tuliskan komentar atau catatan untuk tim prodi..."
              />
              <button className="mt-2 text-xs bg-[#00509d] text-white rounded-lg px-4 py-2 hover:bg-[#003f7d] transition-colors font-medium">
                Kirim Komentar
              </button>
            </div>
          )}

          <div className="bg-blue-50 border-l-4 border-[#00509d] rounded-r-xl p-4">
            <p className="text-sm font-bold text-[#132040] mb-2">
              💡 Pesan Rekomendasi
            </p>
            <ul className="list-disc list-inside space-y-1.5">
              {pesanRekomendasi.map((msg: string, i: number) => (
                <li key={i} className="text-xs text-gray-700 leading-relaxed">
                  {msg}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="flex flex-col gap-4 w-64 shrink-0">
          <GaugeMeter score={scoreValue} target={targetScore} />

          <div className="bg-white border border-red-200 rounded-xl shadow-sm p-4">
            <p className="text-sm font-bold text-[#132040] mb-3 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500 inline-block animate-pulse" />
              Early Warning
            </p>
            <div className="space-y-2 text-xs text-gray-700">
              <div className="flex items-start gap-2 bg-red-50 rounded-lg px-3 py-2">
                <span>⏰</span>
                <p>
                  Deadline: <strong className="text-red-600">{deadline}</strong>
                </p>
              </div>
              <div className="flex items-start gap-2 bg-red-50 rounded-lg px-3 py-2">
                <span>⌛</span>
                <p>
                  Sisa <strong className="text-red-600">{sisaHari}</strong> hari
                  lagi
                </p>
              </div>
              {earlyWarnings.map((w: string, i: number) => (
                <div
                  key={i}
                  className="flex items-start gap-2 bg-orange-50 rounded-lg px-3 py-2"
                >
                  <span>⚠️</span>
                  <p className="text-orange-700">{w}</p>
                </div>
              ))}
            </div>
          </div>

          {editable && (
            <button
              onClick={onAturDeadline}
              className="w-full bg-[#f39c12] text-white rounded-xl px-4 py-2.5 text-sm font-semibold hover:bg-[#e08e0b] transition-colors shadow-sm"
            >
              ⚙️ Atur Deadline
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardProdiPage;
