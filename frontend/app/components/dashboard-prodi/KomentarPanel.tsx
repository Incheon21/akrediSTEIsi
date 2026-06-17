"use client";

import { useState, useEffect, useRef } from "react";
import {
  fetchKomentar,
  createKomentar,
  deleteKomentar,
  KomentarResponse,
} from "@/app/services/api";

interface Props {
  targetAkreditasiId: string;
  currentUserRole: string;
  currentUserId: string;
}

function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return "Baru saja";
  if (diffMins < 60) return `${diffMins} menit lalu`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours} jam lalu`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays} hari lalu`;
  return date.toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" });
}

const ROLE_BADGE: Record<string, { label: string; cls: string }> = {
  pimpinan:  { label: "Pimpinan",  cls: "bg-indigo-100 text-indigo-700" },
  admin:     { label: "Admin/Koordinator", cls: "bg-slate-100 text-slate-600" },
  tim_prodi: { label: "Tim Prodi", cls: "bg-emerald-100 text-emerald-700" },
};

const canComment = (role: string) =>
  ["pimpinan", "admin"].includes(role);

function getInitials(nama: string) {
  return nama
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}

export default function KomentarPanel({
  targetAkreditasiId,
  currentUserRole,
  currentUserId,
}: Props) {
  const [komentar, setKomentar] = useState<KomentarResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [inputText, setInputText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const loadKomentar = async () => {
    try {
      const data = await fetchKomentar(targetAkreditasiId);
      setKomentar(data);
    } catch {
      // silent fail
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (targetAkreditasiId) loadKomentar();
  }, [targetAkreditasiId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    setError(null);
    setSubmitting(true);
    try {
      const newKomentar = await createKomentar(targetAkreditasiId, inputText.trim());
      setKomentar((prev) => [...prev, newKomentar]);
      setInputText("");
      textareaRef.current?.blur();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal mengirim komentar.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (komentarId: string) => {
    setDeletingId(komentarId);
    try {
      await deleteKomentar(targetAkreditasiId, komentarId);
      setKomentar((prev) => prev.filter((k) => k.id !== komentarId));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Gagal menghapus komentar.");
    } finally {
      setDeletingId(null);
    }
  };

  const canDeleteComment = (k: KomentarResponse) =>
    currentUserRole === "admin" || k.user_id === currentUserId;

  return (
    <section className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
      {/* Header */}
      <div className="border-b border-slate-200 bg-slate-50 px-6 py-4 flex items-center gap-2">
        <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
        <h2 className="text-base font-semibold text-slate-800">Komentar</h2>
        {komentar.length > 0 && (
          <span className="ml-1 text-xs bg-slate-200 text-slate-600 rounded-full px-2 py-0.5 font-medium">
            {komentar.length}
          </span>
        )}
      </div>

      {/* Input Form — hanya untuk pimpinan dan admin */}
      {canComment(currentUserRole) && (
        <div className="px-6 pt-5 pb-4 border-b border-slate-100">
          {error && (
            <p className="text-xs text-red-600 mb-3 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </p>
          )}
          <form onSubmit={handleSubmit}>
            <textarea
              ref={textareaRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (!submitting && inputText.trim()) handleSubmit(e as any);
                }
              }}
              rows={3}
              placeholder="Tulis komentar atau catatan untuk tim prodi… (Enter untuk kirim, Shift+Enter untuk baris baru)"
              className="w-full resize-none rounded-lg border border-slate-300 px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#00509d] focus:border-transparent transition"
            />
            <div className="flex justify-end mt-2">
              <button
                type="submit"
                disabled={submitting || !inputText.trim()}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#00509d] text-white text-sm font-medium hover:bg-[#003f7d] transition disabled:opacity-40 disabled:cursor-not-allowed shadow-sm"
              >
                {submitting ? (
                  <>
                    <span className="animate-spin w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full" />
                    Mengirim...
                  </>
                ) : (
                  <>
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                    </svg>
                    Kirim Komentar
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Comment List */}
      <div className="divide-y divide-slate-100">
        {loading ? (
          <div className="px-6 py-8 text-center">
            <p className="text-sm text-slate-400">Memuat komentar...</p>
          </div>
        ) : komentar.length === 0 ? (
          <div className="px-6 py-10 text-center">
            <p className="text-2xl mb-2">💬</p>
            <p className="text-sm text-slate-400">Belum ada komentar.</p>
          </div>
        ) : (
          komentar.map((k) => {
            const roleBadge =
              ROLE_BADGE[k.user?.role ?? ""] ??
              { label: k.user?.role ?? "Pengguna", cls: "bg-slate-100 text-slate-600" };
            const nama = k.user?.nama ?? "Pengguna";

            return (
              <div key={k.id} className="px-6 py-4 flex gap-4 group hover:bg-slate-50 transition-colors">
                {/* Avatar */}
                <div className="shrink-0 w-9 h-9 rounded-full bg-[#00509d]/10 flex items-center justify-center mt-0.5">
                  <span className="text-xs font-bold text-[#00509d]">
                    {getInitials(nama)}
                  </span>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  {/* Header row */}
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className="text-sm font-semibold text-slate-800">{nama}</span>
                    <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${roleBadge.cls}`}>
                      {roleBadge.label}
                    </span>
                    <span className="text-xs text-slate-400 ml-auto">
                      {formatRelativeTime(k.created_at)}
                    </span>
                  </div>

                  {/* Comment text */}
                  <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap break-words">
                    {k.isi_komentar}
                  </p>

                  {/* Delete */}
                  {canDeleteComment(k) && (
                    <div className="mt-2">
                      <button
                        onClick={() => handleDelete(k.id)}
                        disabled={deletingId === k.id}
                        className="text-xs text-red-400 hover:text-red-600 transition-colors disabled:opacity-50"
                      >
                        {deletingId === k.id ? "Menghapus..." : "Hapus"}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}
