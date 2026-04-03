"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/app/hooks/useAuth";
import { useClickOutside } from "@/app/hooks/useClickOutside";
import { apiFetch } from "@/app/services/api";
import { DashboardMultiProdiData } from "@/app/components/dashboard-multiprodi/types";
import SummaryCard from "@/app/components/dashboard-multiprodi/SummaryCard";
import SimulasiChart from "@/app/components/dashboard-multiprodi/SimulasiChart";
import ProdiCard from "@/app/components/dashboard-multiprodi/ProdiCard";

export default function DashboardMultiProdiPage() {
    const [tahun, setTahun] = useState<string | null>(null);
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const [dashboardData, setDashboardData] =
        useState<DashboardMultiProdiData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const { user, loading: authLoading } = useAuth();

    useClickOutside(dropdownRef, () => setDropdownOpen(false));

    useEffect(() => {
        if (!user) return;

        async function fetchDashboard() {
            setLoading(true);
            setError(null);
            try {
                const url = tahun
                    ? `/api/v1/multiprodi/dashboard?tahun=${tahun}`
                    : `/api/v1/multiprodi/dashboard`;

                const res = await apiFetch(url);
                if (!res.ok) throw new Error("Gagal mengambil data dashboard institusi");
                const serverData = await res.json();

                const prodiList = serverData.prodi_list ?? [];
                const fakultasSummary = serverData.fakultas_summary ?? {
                    total_prodi: 0,
                    prodi_green: 0,
                    prodi_yellow: 0,
                    prodi_red: 0,
                    avg_lkps_percent: 0,
                    avg_led_percent: 0,
                    avg_simulation_score: 0,
                };
                const availableYears = serverData.available_years ?? [];
                const currentYear = serverData.current_year ?? (availableYears.length ? availableYears[0] : new Date().getFullYear());

                setDashboardData({
                    fakultas_summary: fakultasSummary,
                    prodi_list: prodiList,
                    current_year: currentYear,
                    available_years: availableYears,
                });
            } catch (err) {
                setError(err instanceof Error ? err.message : "Terjadi kesalahan");
            } finally {
                setLoading(false);
            }
        }

        fetchDashboard();
    }, [user, tahun]);

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

    if (!dashboardData) return null;

    const {
        fakultas_summary,
        prodi_list,
        current_year,
        available_years,
    } = dashboardData;

    return (
        <div className="p-6 px-10 bg-[#f4f6f8] min-h-screen">

            {/* Header */}
            <div className="flex items-center justify-between mb-5">
                <div>
                    <h1 className="text-xl font-bold text-[#132040]">
                        Dashboard Multiprodi
                    </h1>
                    <p className="text-sm text-gray-500 mt-0.5">
                        Ringkasan akreditasi seluruh program studi STEI ITB
                    </p>
                </div>

                {/* Dropdown tahun */}
                <div className="relative" ref={dropdownRef}>
                    <button
                        onClick={() => setDropdownOpen((prev) => !prev)}
                        className="flex items-center gap-2 border border-[#00509d] rounded-lg px-3 py-1.5 text-sm text-[#00509d] font-semibold hover:bg-blue-50 transition-colors"
                    >
                        {tahun ?? current_year}
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
                        </ul>
                    )}
                </div>
            </div>


            {/* Summary cards */}
            <SummaryCard summary={fakultas_summary} />

            {/* Tabel prodi + chart — dua kolom di layar besar */}
            <div className="flex gap-6 flex-wrap">

                {/* Tabel prodi — kiri, lebih lebar */}
                <div className="flex-1 min-w-[320px] flex flex-col gap-4">
                    <div className="flex items-center gap-3">
                        <span className="w-1 h-6 bg-[#00509d] rounded-full inline-block" />
                        <h2 className="text-base font-bold text-[#132040]">
                            Daftar Program Studi
                        </h2>
                        <span className="ml-auto text-xs text-gray-400">
                            Klik baris untuk lihat detail
                        </span>
                    </div>
                    <ProdiCard prodiList={prodi_list} />
                </div>

                {/* Chart simulasi — kanan */}
                <div className="w-80 shrink-0 flex flex-col gap-4">
                    <SimulasiChart prodiList={prodi_list} />

                    {/* Rata-rata institusi */}
                    <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
                        <div className="flex items-center gap-2 mb-3">
                            <span className="w-1 h-5 bg-[#00509d] rounded-full inline-block" />
                            <p className="text-sm font-bold text-[#132040]">
                                Rata-rata prodi
                            </p>
                        </div>
                        <div className="space-y-2.5">
                            {[
                                { label: "LKPS", value: fakultas_summary.avg_lkps_percent },
                                { label: "LED", value: fakultas_summary.avg_led_percent },
                            ].map(({ label, value }) => (
                                <div key={label} className="flex items-center gap-3">
                                    <span className="text-xs text-gray-500 w-10">{label}</span>
                                    <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                                        <div
                                            className="h-2 bg-[#00509d] rounded-full"
                                            style={{ width: `${value}%` }}
                                        />
                                    </div>
                                    <span className="text-xs font-semibold text-gray-700 w-8 text-right">
                                        {value}%
                                    </span>
                                </div>
                            ))}
                            <div className="pt-1 border-t border-gray-100 flex justify-between items-center">
                                <span className="text-xs text-gray-500">
                                    Rata-rata skor simulasi
                                </span>
                                <span className="text-sm font-bold text-[#00509d]">
                                    {fakultas_summary.avg_simulation_score}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}