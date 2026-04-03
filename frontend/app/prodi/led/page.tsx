"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  fetchIndikatorsByKriteria,
  fetchLedNarasi,
  saveLedNarasi,
  type IndicatorResponse,
} from "@/app/services/api";
import { useAuth } from "@/app/hooks/useAuth";

export default function ProdiLedPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, loading: authLoading } = useAuth();

  const targetId = searchParams.get("target_akreditasi_id") ?? "";
  const kriteriaKode = searchParams.get("kriteria_kode") ?? "";

  const [indikators, setIndikators] = useState<IndicatorResponse[]>([]);
  const [narasis, setNarasis] = useState<Record<string, string>>({});
  const [originalNarasis, setOriginalNarasis] = useState<
    Record<string, string>
  >({});
  const [existingLedIds, setExistingLedIds] = useState<
    Record<string, string | null>
  >({});

  const [loadingPage, setLoadingPage] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Determine if user can edit
  const canEdit = useMemo(() => {
    if (!user) return false;
    return ["admin", "tim_prodi", "koordinator"].includes(user.role);
  }, [user]);

  const isReadOnly = !canEdit;

  // Track unsaved changes
  const hasUnsavedChanges = useMemo(() => {
    for (const ind of indikators) {
      const current = (narasis[ind.id] || "").trim();
      const original = (originalNarasis[ind.id] || "").trim();
      if (current !== original) {
        return true;
      }
    }
    return false;
  }, [narasis, originalNarasis, indikators]);

  const groupedIndikators = useMemo(() => {
    const groupMap: Record<string, typeof indikators> = {};
    indikators.forEach((ind) => {
      const parts = ind.kode_indikator.split(".");
      const parent =
        parts.length > 2 ? parts.slice(0, 2).join(".") : ind.kode_indikator;
      if (!groupMap[parent]) groupMap[parent] = [];
      groupMap[parent].push(ind);
    });

    const result: { title: string; items: typeof indikators }[] = [];
    const seen = new Set<string>();
    indikators.forEach((ind) => {
      const parts = ind.kode_indikator.split(".");
      const parent =
        parts.length > 2 ? parts.slice(0, 2).join(".") : ind.kode_indikator;
      if (!seen.has(parent)) {
        seen.add(parent);
        result.push({ title: parent, items: groupMap[parent] });
      }
    });
    return result;
  }, [indikators]);

  const isFormReady = useMemo(
    () => Boolean(targetId && kriteriaKode && indikators.length > 0),
    [targetId, kriteriaKode, indikators],
  );

  useEffect(() => {
    async function initPage() {
      setLoadingPage(true);
      setError(null);
      setSuccess(null);

      try {
        if (!targetId || !kriteriaKode) {
          setError(
            "Parameter halaman tidak lengkap. Pastikan target_akreditasi_id dan kriteria_kode tersedia.",
          );
          return;
        }

        // 1) Load indikator metadata for the specific kriteria
        const indikatorData = await fetchIndikatorsByKriteria(kriteriaKode);
        if (indikatorData.length === 0) {
          setError("Tidak ada indikator ditemukan untuk kriteria ini.");
          return;
        }

        // Sort by kode_indikator
        indikatorData.sort((a, b) =>
          a.kode_indikator.localeCompare(b.kode_indikator),
        );
        setIndikators(indikatorData);

        // 2) Try load existing LED narasi for all indicators
        const newNarasis: Record<string, string> = {};
        const newOriginalNarasis: Record<string, string> = {};
        const newExistingIds: Record<string, string | null> = {};

        await Promise.all(
          indikatorData.map(async (ind) => {
            const existingNarasi = await fetchLedNarasi(targetId, ind.id);
            if (existingNarasi) {
              newExistingIds[ind.id] = existingNarasi.id;
              newNarasis[ind.id] = existingNarasi.narasi ?? "";
              newOriginalNarasis[ind.id] = existingNarasi.narasi ?? "";
            } else {
              newExistingIds[ind.id] = null;
              newNarasis[ind.id] = "";
              newOriginalNarasis[ind.id] = "";
            }
          }),
        );

        setNarasis(newNarasis);
        setOriginalNarasis(newOriginalNarasis);
        setExistingLedIds(newExistingIds);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Terjadi kesalahan.");
      } finally {
        setLoadingPage(false);
      }
    }

    if (!authLoading) {
      initPage();
    }
  }, [authLoading, targetId, kriteriaKode]);

  // Warn before leaving if unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = "";
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [hasUnsavedChanges]);

  const handleNarasiChange = (id: string, value: string) => {
    setNarasis((prev) => ({ ...prev, [id]: value }));
  };

  async function handleSave() {
    setSuccess(null);
    setError(null);

    // Validate empty narasis if changed
    for (const ind of indikators) {
      const current = (narasis[ind.id] || "").trim();
      const original = (originalNarasis[ind.id] || "").trim();
      if (current !== original && !current) {
        setError(
          `Narasi LED untuk indikator ${ind.kode_indikator} tidak boleh kosong jika diubah.`,
        );
        return;
      }
    }

    try {
      setSaving(true);

      const promises = indikators.map(async (ind) => {
        const current = (narasis[ind.id] || "").trim();
        const original = (originalNarasis[ind.id] || "").trim();

        if (current !== original) {
          await saveLedNarasi({
            target_akreditasi_id: targetId,
            indikator_id: ind.id,
            narasi: current,
          });
        }
      });

      await Promise.all(promises);

      const updatedOriginals = { ...originalNarasis };
      indikators.forEach((ind) => {
        updatedOriginals[ind.id] = (narasis[ind.id] || "").trim();
      });
      setOriginalNarasis(updatedOriginals);

      setSuccess("Semua Narasi LED berhasil disimpan.");
      // Auto dismiss success after 3s
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Terjadi kesalahan.");
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveAndBack() {
    setSuccess(null);
    setError(null);

    // Validate empty narasis if changed
    for (const ind of indikators) {
      const current = (narasis[ind.id] || "").trim();
      const original = (originalNarasis[ind.id] || "").trim();
      if (current !== original && !current) {
        setError(
          `Narasi LED untuk indikator ${ind.kode_indikator} tidak boleh kosong jika diubah.`,
        );
        return;
      }
    }

    try {
      setSaving(true);

      const promises = indikators.map(async (ind) => {
        const current = (narasis[ind.id] || "").trim();
        const original = (originalNarasis[ind.id] || "").trim();

        if (current !== original) {
          await saveLedNarasi({
            target_akreditasi_id: targetId,
            indikator_id: ind.id,
            narasi: current,
          });
        }
      });

      await Promise.all(promises);

      // Navigate back immediately after save
      router.push("/prodi/dashboard-prodi");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Gagal menyimpan narasi LED.",
      );
      setSaving(false);
    }
  }

  function goBack() {
    if (hasUnsavedChanges) {
      const confirmed = window.confirm(
        "Anda memiliki perubahan yang belum disimpan. Yakin ingin keluar?",
      );
      if (!confirmed) return;
    }
    router.push("/prodi/dashboard-prodi");
  }

  if (authLoading || loadingPage) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#f4f6f8]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#00509d]" />
      </div>
    );
  }

  if (!user) return null;

  if (!["admin", "koordinator", "tim_prodi", "pimpinan"].includes(user.role)) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#f4f6f8] p-5">
        <div className="bg-white max-w-md w-full rounded-xl shadow-sm border border-orange-100 p-8 text-center text-[#132040]">
          <span className="text-5xl block mb-4">⛔</span>
          <h2 className="text-lg font-bold mb-2">Akses Ditolak</h2>
          <p className="text-sm text-gray-600 mb-6">
            Anda tidak memiliki izin untuk membuka halaman input LED.
          </p>
          <button
            onClick={goBack}
            className="bg-[#00509d] text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-[#003f7d] transition-colors"
          >
            Kembali ke Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 px-10 bg-[#f4f6f8] min-h-screen">
      <div className="mb-5">
        <button
          onClick={goBack}
          className="text-sm font-semibold text-[#00509d] hover:text-[#003f7d] transition-colors"
        >
          ← Kembali ke Dashboard Prodi
        </button>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 mb-5">
        <div className="flex items-center gap-3 mb-4">
          <span className="w-1 h-6 bg-[#00509d] rounded-full inline-block" />
          <h1 className="text-xl font-bold text-[#132040]">
            {isReadOnly
              ? "Lihat Narasi LED Kriteria"
              : "Input Narasi LED Kriteria"}{" "}
            {kriteriaKode.toUpperCase()}
          </h1>
          <span className="ml-auto text-xs bg-[#00509d]/10 text-[#00509d] font-semibold px-2.5 py-1 rounded-full capitalize">
            {user.role.replace("_", " ")}
          </span>
          {isReadOnly && (
            <span className="text-xs bg-gray-200 text-gray-700 font-semibold px-2.5 py-1 rounded-full">
              Baca Saja
            </span>
          )}
        </div>

        {!isFormReady ? (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
            {error ||
              "Parameter halaman tidak valid atau data indikator tidak dapat dimuat."}
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="bg-[#f8fafc] border border-gray-200 rounded-lg p-3">
                <p className="text-xs text-gray-500 mb-1">
                  Target Akreditasi ID
                </p>
                <p className="font-mono text-xs text-gray-800 break-all">
                  {targetId}
                </p>
              </div>
              <div className="bg-[#f8fafc] border border-gray-200 rounded-lg p-3">
                <p className="text-xs text-gray-500 mb-1">Kriteria</p>
                <p className="font-semibold text-gray-800 uppercase">
                  {kriteriaKode}
                  {indikators.length > 0 &&
                  (indikators[0] as any).kriteria?.nama
                    ? ` - ${(indikators[0] as any).kriteria.nama}`
                    : ""}
                </p>
              </div>
            </div>

            {groupedIndikators.map((group) => {
              const isGroup = group.items.length > 1;

              return (
                <div
                  key={group.title}
                  className={
                    isGroup
                      ? "border border-gray-300 bg-gray-50 rounded-xl overflow-hidden p-4 space-y-4"
                      : ""
                  }
                >
                  {isGroup && (
                    <div className="flex items-center gap-2 mb-2 px-1">
                      <span className="w-1.5 h-5 bg-[#00509d] rounded-full inline-block" />
                      <h2 className="font-bold text-[#132040] text-base">
                        {group.title.endsWith(".3")
                          ? `Indikator Kinerja Utama (IKU) - ${group.title}`
                          : `Grup Indikator ${group.title}`}
                      </h2>
                    </div>
                  )}

                  {group.items.map((ind) => {
                    const isChanged =
                      (narasis[ind.id] || "").trim() !==
                      (originalNarasis[ind.id] || "").trim();

                    const dotCount = (ind.kode_indikator.match(/\./g) || [])
                      .length;
                    let indentClass = "";
                    if (dotCount === 3) indentClass = "ml-8 lg:ml-12";
                    else if (dotCount > 3) indentClass = "ml-16 lg:ml-24";

                    return (
                      <div
                        key={ind.id}
                        className={`border border-gray-200 bg-white rounded-xl overflow-hidden shadow-sm ${indentClass}`}
                      >
                        <div className="bg-[#f8fafc] border-b border-gray-200 p-3">
                          <div className="flex items-start justify-between gap-4">
                            <p className="font-bold text-[#132040] text-sm leading-relaxed">
                              <span className="text-[#00509d] mr-1">
                                {ind.kode_indikator}
                              </span>
                              {ind.deskripsi
                                .replace(
                                  new RegExp(
                                    ` untuk Kriteria ${kriteriaKode}`,
                                    "i",
                                  ),
                                  "",
                                )
                                .replace(/^IKU - /i, "")}
                            </p>
                            {isChanged && !isReadOnly && (
                              <span className="text-[10px] bg-orange-100 text-orange-700 font-bold px-2 py-1 rounded-md border border-orange-200 whitespace-nowrap mt-0.5">
                                Belum Disimpan
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="p-3">
                          <textarea
                            id={`narasi-${ind.id}`}
                            value={narasis[ind.id] || ""}
                            onChange={(e) =>
                              handleNarasiChange(ind.id, e.target.value)
                            }
                            disabled={isReadOnly || saving}
                            rows={5}
                            placeholder={
                              isReadOnly
                                ? "Anda tidak memiliki akses untuk mengedit."
                                : `Tuliskan narasi LED untuk indikator ${ind.kode_indikator}...`
                            }
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 resize-y focus:outline-none focus:ring-2 focus:ring-[#00509d]/30 disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed"
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              );
            })}

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 rounded-lg px-4 py-3 text-sm">
                {success}
              </div>
            )}

            {!isReadOnly && (
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={handleSave}
                  disabled={saving || !hasUnsavedChanges}
                  className="flex items-center gap-1.5 text-sm bg-[#00509d] text-white rounded-lg px-5 py-2 hover:bg-[#003f7d] transition-colors font-medium shadow-sm disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {saving ? "Menyimpan..." : "Simpan Perubahan"}
                </button>
                <button
                  onClick={handleSaveAndBack}
                  disabled={saving || !hasUnsavedChanges}
                  className="flex items-center gap-1.5 text-sm bg-green-600 text-white rounded-lg px-5 py-2 hover:bg-green-700 transition-colors font-medium shadow-sm disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {saving ? "Menyimpan..." : "Simpan & Kembali"}
                </button>
                <button
                  onClick={goBack}
                  disabled={saving}
                  className="text-sm border border-[#00509d] text-[#00509d] rounded-lg px-5 py-2 hover:bg-blue-50 transition-colors font-medium disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  Batal
                </button>
              </div>
            )}

            {isReadOnly && (
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={goBack}
                  className="text-sm border border-gray-300 text-gray-600 rounded-lg px-5 py-2 hover:bg-gray-50 transition-colors font-medium"
                >
                  Kembali
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
