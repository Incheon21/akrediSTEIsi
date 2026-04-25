"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ProdiSummary } from "./types";

interface Props {
    prodiList: ProdiSummary[];
    currentYear?: number;
    onToggle?: (prodiId: string, tahun: number, isAktif: boolean) => void;
    isTogglingId?: string | null;
}

const READINESS_CONFIG = {
    green: {
        dot: "bg-green-500",
        badge: "bg-green-100 text-green-700",
        border: "border-green-200",
        label: "Siap",
    },
    yellow: {
        dot: "bg-yellow-400",
        badge: "bg-yellow-100 text-yellow-700",
        border: "border-yellow-200",
        label: "Perlu perhatian",
    },
    red: {
        dot: "bg-red-500",
        badge: "bg-red-100 text-red-700",
        border: "border-red-200",
        label: "Kritis",
    },
};

function MiniProgressRow({ label, value }: { label: string; value: number }) {
    return (
        <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400 w-8 shrink-0">{label}</span>
            <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                    className="h-1.5 bg-[#00509d] rounded-full transition-all duration-500"
                    style={{ width: `${value}%` }}
                />
            </div>
            <span className="text-xs text-gray-500 w-7 text-right">{value}%</span>
        </div>
    );
}

export default function ProdiCard({ prodiList, currentYear, onToggle, isTogglingId }: Props) {
    const router = useRouter();
    const [confirmingId, setConfirmingId] = useState<string | null>(null);

    return (
        <>
            {/* Backdrop transparan untuk menutup popup saat klik di luar */}
            {confirmingId && (
                <div
                    className="fixed inset-0 z-10"
                    onClick={() => setConfirmingId(null)}
                />
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {prodiList.map((prodi) => {
                    const cfg = READINESS_CONFIG[prodi.readiness_status];
                    const isToggling = isTogglingId === prodi.id;

                    return (
                        <div
                            key={prodi.id}
                            // Kode lama (status operasional):
                            // className={`relative bg-white rounded-2xl border ${prodi.prodi_status === "aktif" ? cfg.border : "border-gray-200"} shadow-sm p-4 ${prodi.prodi_status === "aktif" ? "cursor-pointer hover:shadow-md hover:-translate-y-0.5" : "opacity-80"} transition-all duration-200 flex flex-col gap-3`}

                            // Kode baru: navigasi dipindah ke span "Lihat detail" supaya tidak konflik dengan popup
                            className={`relative bg-white rounded-2xl border ${prodi.is_active ? cfg.border : "border-gray-200"} shadow-sm p-4 ${prodi.is_active ? "" : "opacity-80"} transition-all duration-200 flex flex-col gap-3`}
                        >
                            {/* Header — nama & status */}
                            <div className="flex items-start justify-between gap-2">
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-bold text-[#132040] leading-snug line-clamp-2">
                                        {prodi.name}
                                    </p>
                                    <p className="text-xs text-gray-400 mt-0.5">{prodi.degree}</p>
                                </div>
                                {/* Kode lama: {prodi.prodi_status === "aktif" && ( */}
                                {prodi.is_active && (
                                    <span
                                        className={`shrink-0 inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full ${cfg.badge}`}
                                    >
                                        <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
                                        {cfg.label}
                                    </span>
                                )}
                            </div>

                            {/* Akreditasi resmi */}
                            <div className="bg-gray-50 rounded-xl px-3 py-2">
                                <p className="text-[10px] text-gray-400 mb-0.5">Akreditasi terakhir</p>
                                <p className="text-sm font-semibold text-gray-700">
                                    {prodi.accreditation_status}
                                    <span className="text-gray-400 font-normal ml-1 text-xs">
                                        ({prodi.accreditation_year})
                                    </span>
                                </p>
                            </div>

                            {/* Kode lama: {prodi.prodi_status === "aktif" && ( */}
                            {prodi.is_active ? (
                                <>
                                    {/* Progress LKPS & LED */}
                                    <div className="flex flex-col gap-1.5">
                                        <MiniProgressRow label="LKPS" value={prodi.lkps_percent} />
                                        <MiniProgressRow label="LED" value={prodi.led_percent} />
                                    </div>

                                    {/* Skor simulasi */}
                                    <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                                        <span className="text-xs text-gray-400">Skor simulasi</span>
                                        <div className="text-right">
                                            <span className="text-base font-bold text-[#00509d]">
                                                {prodi.simulation_score}
                                            </span>
                                            <span className="text-xs text-gray-400 ml-1">
                                                / {prodi.target_score}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Tombol lihat detail + trigger popup nonaktifkan */}
                                    <div className="flex items-center justify-between">
                                        <span 
                                            onClick={() => {
                                                if (prodi.is_active && !confirmingId) {
                                                    router.push(`/prodi/dashboard-prodi?id=${prodi.id}`);
                                                }
                                            }}
                                            className="text-xs text-[#00509d] font-semibold hover:underline cursor-pointer"
                                        >
                                            Lihat detail →
                                        </span>
                                        {onToggle && currentYear && (
                                            <button
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    e.stopPropagation();
                                                    setConfirmingId(prodi.id);
                                                }}
                                                disabled={isToggling}
                                                className="text-[10px] text-gray-400 hover:text-red-500 transition-colors disabled:opacity-50"
                                                title="Nonaktifkan siklus akreditasi"
                                            >
                                                Nonaktifkan
                                            </button>
                                        )}
                                    </div>

                                    {/* Floating popup konfirmasi */}
                                    {confirmingId === prodi.id && onToggle && currentYear && (
                                        <div
                                            className="absolute bottom-12 right-3 z-50 bg-white border border-red-100 rounded-xl shadow-2xl p-3 w-52"
                                            onClick={(e) => {
                                                e.preventDefault();
                                                e.stopPropagation();
                                            }}
                                        >
                                            <p className="text-xs font-semibold text-gray-800 mb-1">
                                                Nonaktifkan siklus {currentYear}?
                                            </p>
                                            <p className="text-[10px] text-gray-400 mb-3 leading-relaxed">
                                                Prodi tidak akan tampil sebagai aktif. Data tetap tersimpan.
                                            </p>
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={(e) => {
                                                        e.preventDefault();
                                                        e.stopPropagation();
                                                        setConfirmingId(null);
                                                        onToggle(prodi.id, currentYear, false);
                                                    }}
                                                    disabled={isToggling}
                                                    className="flex-1 text-[11px] font-semibold text-white bg-red-500 hover:bg-red-600 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                                                >
                                                    {isToggling ? "..." : "Ya, nonaktif"}
                                                </button>
                                                <button
                                                    onClick={(e) => {
                                                        e.preventDefault();
                                                        e.stopPropagation();
                                                        setConfirmingId(null);
                                                    }}
                                                    className="flex-1 text-[11px] font-semibold text-gray-500 hover:text-gray-700 py-1.5 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
                                                >
                                                    Batal
                                                </button>
                                            </div>
                                        </div>
                                    )}

                                </>
                            ) : (
                                /* Tombol Aktifkan Siklus — hanya untuk prodi tidak aktif */
                                onToggle && currentYear && (
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onToggle(prodi.id, currentYear, true);
                                        }}
                                        disabled={isToggling}
                                        className="mt-auto w-full flex items-center justify-center gap-1.5 text-xs font-semibold text-[#00509d] border border-[#00509d] rounded-lg py-1.5 hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {isToggling ? (
                                            <span className="animate-spin h-3 w-3 border-2 border-[#00509d] border-t-transparent rounded-full" />
                                        ) : (
                                            <>
                                                <span>＋</span>
                                                <span>Aktifkan Siklus {currentYear}</span>
                                            </>
                                        )}
                                    </button>
                                )
                            )}
                        </div>
                    );
                })}
            </div>
        </>
    );
}