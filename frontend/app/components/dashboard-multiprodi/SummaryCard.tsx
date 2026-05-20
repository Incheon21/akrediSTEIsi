import { FakultasSummary } from "./types";

interface Props {
    summary: FakultasSummary;
}

const statItems = (summary: FakultasSummary) => [
    {
        label: "Total Prodi",
        value: summary.total_prodi,
        sub: "program studi aktif",
        color: "bg-blue-50 text-[#00509d]",
    },
    {
        label: "Siap",
        value: summary.prodi_green,
        sub: "prodi sudah baik",
        color: "bg-green-50 text-green-700",
    },
    {
        label: "Perlu Perhatian",
        value: summary.prodi_yellow,
        sub: "prodi perlu tindakan",
        color: "bg-yellow-50 text-yellow-700",
    },
    {
        label: "Kritis",
        value: summary.prodi_red,
        sub: "prodi di bawah target",
        color: "bg-red-50 text-red-700",
    },
];

export default function SummaryCards({ summary }: Props) {
    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
            {statItems(summary).map(({ label, value, sub, color }) => (
                <div
                    key={label}
                    className="bg-white rounded-xl border border-gray-100 shadow-sm p-4"
                >
                    <p className="text-xs text-gray-400 mb-1">{label}</p>
                    <p className={`text-3xl font-bold mb-1 ${color.split(" ")[1]}`}>
                        {value}
                    </p>
                    <p className="text-xs text-gray-500">{sub}</p>
                    <div className={`mt-2 h-1 rounded-full ${color.split(" ")[0]}`} />
                </div>
            ))}
        </div>
    );
}