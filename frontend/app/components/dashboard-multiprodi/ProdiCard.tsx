"use client";

import { useRouter } from "next/navigation";
import { ProdiSummary } from "./types";

interface Props {
    prodiList: ProdiSummary[];
}

const READINESS_CONFIG = {
    green: {
        dot: "bg-green-500",
        badge: "bg-green-100 text-green-700",
        border: "border-green-200",
        bar: "bg-green-500",
        label: "Siap",
    },
    yellow: {
        dot: "bg-yellow-400",
        badge: "bg-yellow-100 text-yellow-700",
        border: "border-yellow-200",
        bar: "bg-yellow-400",
        label: "Perlu perhatian",
    },
    red: {
        dot: "bg-red-500",
        badge: "bg-red-100 text-red-700",
        border: "border-red-200",
        bar: "bg-red-500",
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

export default function ProdiCard({ prodiList }: Props) {
    const router = useRouter();

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {prodiList.map((prodi) => {
                const cfg = READINESS_CONFIG[prodi.readiness_status];

                return (
                    <div
                        key={prodi.id}
                        onClick={() =>
                            router.push(`/prodi/dashboard-prodi?id=${prodi.id}`)
                        }
                        className={`bg-white rounded-2xl border ${cfg.border} shadow-sm p-4 cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 flex flex-col gap-3`}
                    >
                        {/* Header — nama & status */}
                        <div className="flex items-start justify-between gap-2">
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-bold text-[#132040] leading-snug line-clamp-2">
                                    {prodi.name}
                                </p>
                                <p className="text-xs text-gray-400 mt-0.5">{prodi.degree}</p>
                            </div>
                            <span
                                className={`shrink-0 inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full ${cfg.badge}`}
                            >
                                <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
                                {cfg.label}
                            </span>
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

                        {/* Tombol lihat detail */}
                        <div className="text-right">
                            <span className="text-xs text-[#00509d] font-semibold hover:underline">
                                Lihat detail →
                            </span>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}