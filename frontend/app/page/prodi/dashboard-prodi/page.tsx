"use client";

import { useState } from "react";
import ProgressBar from "@/app/components/dashboard-prodi/ProgressBar";
import StatusDot from "@/app/components/dashboard-prodi/StatusDot";
import GaugeMeter from "@/app/components/dashboard-prodi/GaugeMeter";
import { KriteriaRow } from "@/app/components/dashboard-prodi/types";

// Data dummy
const kriteriaList: KriteriaRow[] = [
  { id: "c1", nama: "Visi & Misi (C1)", status: "green", statusLabel: "Baik", progres: 90, hasLKPS: false, hasLED: true, hasEvidence: false },
  { id: "c2", nama: "Tata Pamong (C2)", status: "yellow", statusLabel: "Cukup", progres: 60, hasLKPS: false, hasLED: true, hasEvidence: true },
  { id: "c3", nama: "Mahasiswa (C3)", status: "green", statusLabel: "Baik", progres: 80, hasLKPS: true, hasLED: true, hasEvidence: false },
  { id: "c4", nama: "SDM (C4)", status: "orange", statusLabel: "Kurang", progres: 45, hasLKPS: true, hasLED: true, hasEvidence: true },
  { id: "c5", nama: "Keuangan (C5)", status: "red", statusLabel: "Buruk", progres: 20, hasLKPS: true, hasLED: false, hasEvidence: false },
  { id: "c6", nama: "Pendidikan (C6)", status: "green", statusLabel: "Baik", progres: 85, hasLKPS: true, hasLED: true, hasEvidence: true },
  { id: "c7", nama: "Penelitian (C7)", status: "yellow", statusLabel: "Cukup", progres: 55, hasLKPS: true, hasLED: true, hasEvidence: false },
  { id: "c8", nama: "PKM (C8)", status: "yellow", statusLabel: "Cukup", progres: 50, hasLKPS: true, hasLED: true, hasEvidence: true },
  { id: "c9", nama: "Luaran (C9)", status: "red", statusLabel: "Buruk", progres: 30, hasLKPS: true, hasLED: true, hasEvidence: false },
];

const pesanRekomendasi = [
  "Lengkapi data keuangan pada kriteria C5 (progres hanya 20%)",
  "Upload evidence pendukung untuk kriteria C4 & C9",
  "Narasi LED kriteria C2 belum lengkap",
];

const earlyWarnings = [
  "Skor C5 di bawah target minimal (2.0)",
  "Deadline pengumpulan dokumen C9 dalam 30 hari",
];

// ─── Main Page 

const DashboardProdiPage = () => {
  // Data dummy
  const tahunOptions = ["2023", "2024", "2025"];
  const [tahun, setTahun] = useState("2025");
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const lkpsPercent = 72;
  const ledPercent = 55;
  const dokumenPendukungPercent = 40;
  const skorNilai = 3.2;
  const skorTarget = 3.5;
  const deadline = "24 Maret 2026";
  const sisaHari = 376;

  // Handlers (kosong)
  const onUnduhLKPS = () => alert("Unduh LKPS...");
  const onUnduhLED = () => alert("Unduh LED...");
  const onEditLKPS = (id: string) => alert(`Edit LKPS ${id}`);
  const onEditLED = (id: string) => alert(`Edit LED ${id}`);
  const onEditEvidence = (id: string) => alert(`Edit Evidence ${id}`);
  const onAturDeadline = () => alert("Atur Deadline...");

  return (
    <div className="p-6 px-10 bg-background min-h-screen">
      <div className="flex gap-6 flex-wrap">

        <div className="flex-1 min-w-[320px]">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-bold underline text-gray-800">
              Akreditasi
            </h1>
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center gap-2 border border-gray-300 rounded-md px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
              >
                {tahun || "<tahun>"}
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {dropdownOpen && (
                <ul className="absolute right-0 mt-1 bg-white border border-gray-200 rounded-md shadow-md z-10 min-w-[100px]">
                  {tahunOptions.map((t) => (
                    <li key={t}>
                      <button
                        className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                        onClick={() => { setTahun(t); setDropdownOpen(false); }}
                      >
                        {t}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Progress Bars */}
          <div className="space-y-2 mb-4">
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-700 w-32 shrink-0">LKPS</span>
              <ProgressBar value={lkpsPercent} />
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-700 w-32 shrink-0">LED</span>
              <ProgressBar value={ledPercent} />
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-700 w-32 shrink-0 leading-tight">
                Dokumen Pendukung
              </span>
              <ProgressBar value={dokumenPendukungPercent} />
            </div>
          </div>

          {/* Download Buttons */}
          <div className="flex gap-2 mb-5">
            <button
              onClick={onUnduhLKPS}
              className="flex items-center gap-1.5 text-xs border border-gray-300 rounded-full px-3 py-1 hover:bg-gray-50"
            >
              📊 Unduh LKPS
            </button>
            <button
              onClick={onUnduhLED}
              className="flex items-center gap-1.5 text-xs border border-gray-300 rounded-full px-3 py-1 hover:bg-gray-50"
            >
              📝 Unduh LED
            </button>
          </div>

          {/* Kriteria Table */}
          <div className="border border-gray-300 rounded-md overflow-hidden mb-4">
            <div className="max-h-[260px] overflow-y-auto">
              <table className="w-full text-sm relative">
                <thead className="sticky top-0 z-10">
                  <tr className="bg-green-100 text-gray-700 shadow-sm">
                    <th className="px-3 py-2 text-left font-semibold">Kriteria</th>
                    <th className="px-3 py-2 font-semibold">Status</th>
                    <th className="px-3 py-2 font-semibold">Progres</th>
                    <th className="px-3 py-2 font-semibold">Edit LKPS/LED</th>
                  </tr>
                </thead>
                <tbody>
                  {kriteriaList.map((row, i) => (
                    <tr key={row.id} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                      <td className="px-3 py-2 text-gray-800 whitespace-nowrap">
                        {row.nama}
                      </td>
                      <td className="px-3 py-2">
                        <StatusDot color={row.status} label={row.statusLabel} />
                      </td>
                      <td className="px-3 py-2 text-center font-medium text-gray-700">
                        {row.progres}%
                      </td>
                      <td className="px-3 py-2">
                        <div className="flex gap-1 flex-wrap">
                          {row.hasLKPS && (
                            <button
                              onClick={() => onEditLKPS(row.id)}
                              className="text-xs border border-gray-300 rounded-full px-2 py-0.5 hover:bg-blue-50"
                            >
                              📊 LKPS
                            </button>
                          )}
                          {row.hasLED && (
                            <button
                              onClick={() => onEditLED(row.id)}
                              className="text-xs border border-gray-300 rounded-full px-2 py-0.5 hover:bg-blue-50"
                            >
                              ✏️ LED
                            </button>
                          )}
                          {row.hasEvidence && (
                            <button
                              onClick={() => onEditEvidence(row.id)}
                              className="text-xs border border-gray-300 rounded-full px-2 py-0.5 hover:bg-blue-50"
                            >
                              📎 Evidence
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pesan Rekomendasi */}
          <div>
            <p className="text-sm font-semibold text-gray-800 mb-1">
              Pesan Rekomendasi :
            </p>
            <ul className="list-disc list-inside space-y-1">
              {pesanRekomendasi.map((msg, i) => (
                <li key={i} className="text-xs text-gray-600">
                  {msg}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* ── RIGHT PANEL ── */}
        <div className="flex flex-col gap-4 w-64 shrink-0">
          {/* Gauge */}
          <GaugeMeter score={skorNilai} target={skorTarget} />

          {/* Early Warning */}
          <div className="border border-red-300 bg-red-50 rounded-md p-4">
            <p className="text-sm font-bold text-gray-800 mb-2">Early Warning</p>
            <div className="space-y-1.5 text-xs text-gray-700">
              <p>⏰ Deadline: {deadline}</p>
              <p>⌛ Sisa <strong>{sisaHari}</strong> hari lagi</p>
              {earlyWarnings.map((w, i) => (
                <p key={i}>⚠️ {w}</p>
              ))}
            </div>
          </div>

          {/* Atur Deadline */}
          <button
            onClick={onAturDeadline}
            className="w-full border border-gray-300 rounded-md px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Atur deadline
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardProdiPage;
