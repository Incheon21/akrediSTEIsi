"use client";

import { ProdiSummary } from "./types";

interface Props {
    prodiList: ProdiSummary[];
}

const COLOR_MAP = {
    green: { bar: "bg-green-500", text: "text-green-700" },
    yellow: { bar: "bg-yellow-400", text: "text-yellow-700" },
    red: { bar: "bg-red-500", text: "text-red-600" },
};

export default function SimulasiChart({ prodiList }: Props) {
    const maxScore = 400; // skala nilai akhir LAM Teknik
    const clampPct = (value: number) =>
        Math.min(100, Math.max(0, Math.round((value / maxScore) * 100)));

    // Nama prodi disingkat agar muat di bar chart
    const shortened = (name: string) =>
        name.length > 20 ? name.slice(0, 18) + "…" : name;

    return (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-center gap-3 mb-5">
                <span className="w-1 h-6 bg-[#00509d] rounded-full inline-block" />
                <h2 className="text-base font-bold text-[#132040]">
                    Perbandingan Skor Simulasi
                </h2>
            </div>

            <div className="space-y-3">
                {[...prodiList]
                    .sort((a, b) => b.simulation_score - a.simulation_score)
                    .map((prodi) => {
                        const pct = clampPct(prodi.simulation_score);
                        const targetPct = clampPct(prodi.target_score);
                        const colors = COLOR_MAP[prodi.readiness_status];

                        return (
                            <div key={prodi.id}>
                                <div className="flex justify-between items-center mb-1">
                                    <span className="text-xs text-gray-700 font-medium w-48 shrink-0">
                                        {shortened(prodi.name)}
                                    </span>
                                    <span className={`text-xs font-semibold ${colors.text}`}>
                                        {prodi.simulation_score}
                                    </span>
                                </div>
                                <div className="relative h-4 bg-gray-100 rounded-full overflow-visible">
                                    {/* Bar skor simulasi */}
                                    <div
                                        className={`h-4 rounded-full transition-all duration-500 ${colors.bar}`}
                                        style={{ width: `${pct}%` }}
                                    />
                                    {/* Garis target */}
                                    <div
                                        className="absolute top-0 h-4 w-0.5 bg-[#132040] opacity-40"
                                        style={{ left: `${targetPct}%` }}
                                        title={`Target: ${prodi.target_score}`}
                                    />
                                </div>
                            </div>
                        );
                    })}
            </div>

            {/* Legenda */}
            <div className="flex gap-4 mt-4 text-xs text-gray-500 flex-wrap">
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-green-500 inline-block" />
                    Siap
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-yellow-400 inline-block" />
                    Perlu perhatian
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded-full bg-red-500 inline-block" />
                    Kritis
                </span>
                <span className="flex items-center gap-1.5">
                    <span className="w-0.5 h-3 bg-[#132040] opacity-40 inline-block" />
                    Garis target
                </span>
            </div>
        </div>
    );
}
