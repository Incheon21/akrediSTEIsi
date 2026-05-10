"use client";

import { useState, useEffect } from "react";
import { setTargetScore, setTargetDeadline } from "@/app/services/api";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  prodiId: string;
  tahunAkreditasi: number;
  currentTargetScore: number;
  currentDeadlineLabel?: string;
}

export default function SetTargetModal({
  isOpen,
  onClose,
  onSuccess,
  prodiId,
  tahunAkreditasi,
  currentTargetScore,
  currentDeadlineLabel,
}: Props) {
  const initialSkor =
    currentTargetScore >= 200 && currentTargetScore <= 361
      ? currentTargetScore.toFixed(0)
      : "";

  const [targetSkor, setTargetSkor] = useState<string>(initialSkor);
  const [deadline, setDeadline] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form setiap modal dibuka
  useEffect(() => {
    if (isOpen) {
      setTargetSkor(
        currentTargetScore >= 200 && currentTargetScore <= 361
          ? currentTargetScore.toFixed(0)
          : ""
      );
      setDeadline("");
      setError(null);
    }
  }, [isOpen, currentTargetScore]);

  if (!isOpen) return null;

  const minDate = `${tahunAkreditasi}-01-01`;
  const maxDate = `${tahunAkreditasi}-12-31`;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const skorFilled = targetSkor.trim() !== "";
    const deadlineFilled = deadline.trim() !== "";

    if (!skorFilled && !deadlineFilled) {
      setError("Isi minimal satu field: target skor atau deadline.");
      return;
    }

    if (skorFilled) {
      const skor = parseFloat(targetSkor);
      if (isNaN(skor) || skor < 200 || skor > 361) {
        setError("Target skor harus berada di antara 200 dan 361.");
        return;
      }
    }

    setSaving(true);
    try {
      if (skorFilled) {
        await setTargetScore({
          prodi_id: prodiId,
          target_skor: parseFloat(targetSkor),
          tahun_akreditasi: tahunAkreditasi,
        });
      }
      if (deadlineFilled) {
        await setTargetDeadline({
          prodi_id: prodiId,
          deadline: deadline,
          tahun_akreditasi: tahunAkreditasi,
        });
      }
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Terjadi kesalahan.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm w-screen h-screen"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-[0_20px_60px_-15px_rgba(0,0,0,0.3)] border border-slate-200 w-full max-w-md mx-4 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="bg-[#00509d] px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-white font-bold text-base">
              Set Skor Target &amp; Deadline
            </h2>
            <p className="text-blue-200 text-xs mt-0.5">
              Siklus akreditasi tahun {tahunAkreditasi} — isi salah satu atau keduanya
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-blue-200 hover:text-white transition-colors text-xl leading-none"
            aria-label="Tutup"
          >
            ×
          </button>
        </div>


        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-5">

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">
              Target Skor Akreditasi
              <span className="text-slate-400 font-normal ml-1">(200 – 361, opsional)</span>
            </label>
            {/* Current value hint */}
            {currentTargetScore >= 200 && currentTargetScore <= 361 && (
              <p className="text-[11px] text-slate-400 mb-1.5">
                Nilai saat ini:{" "}
                <span className="font-semibold text-[#00509d]">
                  {currentTargetScore.toFixed(0)}
                </span>
              </p>
            )}
            <input
              type="number"
              min="200"
              max="361"
              step="1"
              value={targetSkor}
              onChange={(e) => setTargetSkor(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#00509d] focus:border-transparent placeholder:text-slate-300"
              placeholder="Kosongkan jika tidak ingin diubah"
            />
            <div className="mt-2 flex h-1.5 rounded-full overflow-hidden">
              <div className="flex-[1] bg-red-400" title="200–240" />
              <div className="flex-[1] bg-yellow-400" title="241–280" />
              <div className="flex-[1] bg-lime-400" title="281–320" />
              <div className="flex-[1] bg-green-500" title="321–361" />
            </div>
            <div className="flex justify-between text-[10px] text-slate-400 mt-0.5">
              <span>200</span>
              <span>240</span>
              <span>280</span>
              <span>320</span>
              <span>361</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex-1 h-px bg-slate-100" />
            <span className="text-[11px] text-slate-400 uppercase tracking-wide">atau</span>
            <div className="flex-1 h-px bg-slate-100" />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">
              Deadline Pengisian
              <span className="text-slate-400 font-normal ml-1">(opsional)</span>
            </label>
            {currentDeadlineLabel && currentDeadlineLabel !== "Belum Diatur" && (
              <p className="text-[11px] text-slate-400 mb-1.5">
                Deadline saat ini:{" "}
                <span className="font-semibold text-slate-600">
                  {currentDeadlineLabel}
                </span>
              </p>
            )}
            <input
              type="date"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              min={minDate}
              max={maxDate}
              className="w-full border border-slate-300 rounded-lg px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#00509d] focus:border-transparent"
            />
            <p className="text-[11px] text-slate-400 mt-1">
              Hanya tanggal dalam tahun {tahunAkreditasi} yang dapat dipilih.
            </p>
          </div>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              className="flex-1 py-2.5 rounded-lg border border-slate-300 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors disabled:opacity-50"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 py-2.5 rounded-lg bg-[#00509d] text-sm font-semibold text-white hover:bg-[#003f7d] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {saving ? (
                <>
                  <span className="animate-spin h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full" />
                  Menyimpan...
                </>
              ) : (
                "Simpan"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
