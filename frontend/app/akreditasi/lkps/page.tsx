"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import {
  createLkpsSubmission,
  fetchLkpsSubmissions,
  fetchProgramStudiList,
  listTemplates,
  uploadTemplate,
} from "@/lib/api/lkps";
import type { ProgramStudiOption } from "@/lib/api/lkps";
import type { LkpsSubmission, LkpsTemplateInfo } from "@/types/lkps";

const statusPalette: Record<string, { label: string; bg: string; text: string }> = {
  draft: { label: "Draft", bg: "bg-amber-100", text: "text-amber-900" },
  submitted: { label: "Submitted", bg: "bg-sky-100", text: "text-sky-900" },
  reviewed: { label: "Reviewed", bg: "bg-indigo-100", text: "text-indigo-900" },
  approved: { label: "Approved", bg: "bg-emerald-100", text: "text-emerald-900" },
};

const LOCAL_SUBMISSIONS_KEY = "lkps_offline_submissions";
const LOCAL_TEMPLATES_KEY = "lkps_offline_templates";

export default function LkpsHomePage() {
  const [submissions, setSubmissions] = useState<LkpsSubmission[]>([]);
  const [templates, setTemplates] = useState<LkpsTemplateInfo[]>([]);
  const [programStudiList, setProgramStudiList] = useState<ProgramStudiOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offlineMode, setOfflineMode] = useState(false);
  const [formState, setFormState] = useState({
    program_studi_id: "",
    tahun_ts: new Date().getFullYear(),
    nama_pengusul: "",
  });
  const [isCreating, setIsCreating] = useState(false);
  const [templateVersion, setTemplateVersion] = useState("2024-v1");
  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        setLoading(true);
        const [subs, tmpl, prodiList] = await Promise.all([
          fetchLkpsSubmissions(),
          listTemplates(),
          fetchProgramStudiList(),
        ]);
        setSubmissions(subs);
        setTemplates(tmpl);
        setProgramStudiList(prodiList);
      } catch (err) {
        setOfflineMode(true);
        const offlineSubs = loadOfflineList<LkpsSubmission>(LOCAL_SUBMISSIONS_KEY);
        const offlineTemplates = loadOfflineList<LkpsTemplateInfo>(LOCAL_TEMPLATES_KEY);
        setSubmissions(offlineSubs);
        setTemplates(offlineTemplates);
        setError(err instanceof Error ? err.message : null);
      } finally {
        setLoading(false);
      }
    };
    bootstrap();
  }, []);

  const stats = useMemo(() => {
    const total = submissions.length;
    const completed = submissions.filter((s) => s.status === "approved").length;
    const draft = submissions.filter((s) => s.status === "draft").length;
    return { total, completed, draft };
  }, [submissions]);

  const handleCreate = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsCreating(true);
    try {
      const payload = {
        program_studi_id: formState.program_studi_id.trim(),
        tahun_ts: Number(formState.tahun_ts),
        nama_pengusul: formState.nama_pengusul || undefined,
      };
      if (offlineMode) {
        const submission: LkpsSubmission = {
          id: crypto.randomUUID(),
          program_studi_id: payload.program_studi_id,
          template_id: null,
          tahun_ts: payload.tahun_ts,
          status: "draft",
          nama_pengusul: payload.nama_pengusul ?? null,
          created_at: new Date().toISOString(),
        };
        setSubmissions((prev) => {
          const next = [submission, ...prev];
          persistOfflineList(LOCAL_SUBMISSIONS_KEY, next);
          return next;
        });
        setFormState((prev) => ({ ...prev, program_studi_id: "", nama_pengusul: "" }));
        return;
      }
      const submission = await createLkpsSubmission(payload);
      setSubmissions((prev) => [submission, ...prev]);
      setFormState((prev) => ({ ...prev, program_studi_id: "", nama_pengusul: "" }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal membuat submission baru");
    } finally {
      setIsCreating(false);
    }
  };

  const handleTemplateUpload = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!templateFile) return;
    setUploading(true);
    setError(null);
    try {
      if (offlineMode) {
        const offlineTemplate: LkpsTemplateInfo = {
          id: crypto.randomUUID(),
          version: templateVersion,
          filename: templateFile.name,
          is_active: true,
          uploaded_at: new Date().toISOString(),
        };
        setTemplates((prev) => {
          const updated = [offlineTemplate, ...prev.map((tpl) => ({ ...tpl, is_active: false }))];
          persistOfflineList(LOCAL_TEMPLATES_KEY, updated);
          return updated;
        });
        setTemplateFile(null);
        return;
      }
      await uploadTemplate(templateVersion, templateFile);
      const freshTemplates = await listTemplates();
      setTemplates(freshTemplates);
      setTemplateFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal mengunggah template");
    } finally {
      setUploading(false);
    }
  };

  return (
    <main className="min-h-screen px-6 py-10 text-[var(--accent-ink)]">
      <div className="mx-auto flex max-w-6xl flex-col gap-10">
        <header className="rounded-3xl bg-[var(--surface-primary)]/95 p-8 shadow-[var(--shadow-soft)]">
          <p className="text-sm uppercase tracking-[0.4em] text-[var(--accent-emerald)]">LKPS Workspace</p>
          <h1 className="mt-3 text-4xl font-semibold text-[var(--accent-ink)]">
            Kelola data akreditasi dengan panel terintegrasi
          </h1>
          <p className="mt-4 max-w-3xl text-base text-[var(--accent-ink)]/80">
            Setiap submission LKPS membungkus 52 seksi data dan progress tracker. Mulai dari sini untuk mengunduh template terbaru,
            mengisi tabel, dan menutup gap sebelum unggah akhir.
          </p>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <StatCard title="Total Submission" value={stats.total.toString()} accent="bg-emerald-100 text-emerald-900" />
            <StatCard title="Selesai" value={stats.completed.toString()} accent="bg-slate-100 text-slate-900" />
            <StatCard title="Draft" value={stats.draft.toString()} accent="bg-amber-100 text-amber-900" />
          </div>
        </header>

        {offlineMode && (
          <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            Backend LKPS belum aktif. Workspace berjalan di mode sandbox dan semua data hanya tersimpan di browser.
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div>
        )}

        <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-3xl border border-[var(--border-soft)] bg-[var(--surface-primary)]/90 p-6 shadow-sm">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 className="text-2xl font-semibold text-[var(--accent-ink)]">Submission terbaru</h2>
                <p className="text-sm text-[var(--accent-ink)]/70">Pilih submission untuk membuka workspace per seksi.</p>
              </div>
              <form onSubmit={handleCreate} className="w-full rounded-2xl bg-white/70 p-4 shadow-inner sm:max-w-md">
                <p className="text-sm font-semibold text-[var(--accent-ink)]">Tambah submission</p>
                <div className="mt-3 space-y-3 text-sm">
                  <div>
                    <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-[var(--accent-ink)]/70">
                      Program Studi
                    </label>
                    <select
                      required
                      value={formState.program_studi_id}
                      onChange={(e) => setFormState((prev) => ({ ...prev, program_studi_id: e.target.value }))}
                      className="w-full rounded-xl border border-[var(--border-soft)] bg-white px-3 py-2 text-sm focus:border-[var(--accent-emerald)] focus:outline-none"
                    >
                      <option value="">Pilih program studi</option>
                      {programStudiList.map((ps) => (
                        <option key={ps.id} value={ps.id}>
                          {ps.nama} ({ps.jenjang})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div>
                      <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-[var(--accent-ink)]/70">
                        Tahun TS
                      </label>
                      <input
                        type="number"
                        min={2000}
                        value={formState.tahun_ts}
                        onChange={(e) => setFormState((prev) => ({ ...prev, tahun_ts: Number(e.target.value) }))}
                        className="w-full rounded-xl border border-[var(--border-soft)] bg-white px-3 py-2 text-sm focus:border-[var(--accent-emerald)] focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-[var(--accent-ink)]/70">
                        Nama Pengusul
                      </label>
                      <input
                        type="text"
                        value={formState.nama_pengusul}
                        onChange={(e) => setFormState((prev) => ({ ...prev, nama_pengusul: e.target.value }))}
                        className="w-full rounded-xl border border-[var(--border-soft)] bg-white px-3 py-2 text-sm focus:border-[var(--accent-emerald)] focus:outline-none"
                        placeholder="Nama reviewer internal"
                      />
                    </div>
                  </div>
                  <button
                    type="submit"
                    disabled={isCreating}
                    className="w-full rounded-xl bg-[var(--accent-emerald)] px-4 py-2 text-sm font-semibold text-white transition hover:brightness-110 disabled:opacity-50"
                  >
                    {isCreating ? "Menyimpan..." : "Buat submission"}
                  </button>
                </div>
              </form>
            </div>

            <div className="mt-6 space-y-4">
              {loading && <p className="text-sm text-[var(--accent-ink)]/70">Memuat submission...</p>}
              {!loading && submissions.length === 0 && (
                <p className="rounded-xl border border-dashed border-[var(--border-soft)] bg-white/60 px-4 py-6 text-center text-sm text-[var(--accent-ink)]/70">
                  Belum ada submission. Buat satu untuk mulai mengisi data LKPS.
                </p>
              )}
              {submissions.slice(0, 5).map((submission) => (
                <SubmissionCard key={submission.id} submission={submission} />
              ))}
              {submissions.length > 5 && (
                <p className="text-right text-sm text-[var(--accent-ink)]/70">Menampilkan 5 terbaru dari {submissions.length} submission.</p>
              )}
            </div>
          </div>

          <div className="rounded-3xl border border-[var(--border-soft)] bg-white/80 p-6 shadow-sm">
            <h2 className="text-2xl font-semibold text-[var(--accent-ink)]">Template LKPS</h2>
            <p className="text-sm text-[var(--accent-ink)]/70">Unggah template resmi terbaru agar ekspor mengikuti format yang disahkan.</p>

            <form onSubmit={handleTemplateUpload} className="mt-4 space-y-3 rounded-2xl border border-[var(--border-soft)] bg-[var(--surface-muted)]/70 p-4">
              <div className="flex flex-col gap-3 text-sm">
                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-[var(--accent-ink)]/70">Versi Template</label>
                  <input
                    type="text"
                    value={templateVersion}
                    onChange={(e) => setTemplateVersion(e.target.value)}
                    className="w-full rounded-xl border border-[var(--border-soft)] bg-white px-3 py-2 text-sm focus:border-[var(--accent-emerald)] focus:outline-none"
                    placeholder="2024-v1"
                    required
                  />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-[var(--accent-ink)]/70">File .xlsx</label>
                  <input
                    type="file"
                    accept=".xlsx"
                    onChange={(e) => setTemplateFile(e.target.files?.[0] ?? null)}
                    className="w-full rounded-xl border border-dashed border-[var(--border-soft)] bg-white px-3 py-2 text-sm"
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={!templateFile || uploading}
                  className="rounded-xl bg-[var(--accent-ink)] px-4 py-2 text-sm font-semibold text-white transition hover:brightness-125 disabled:opacity-50"
                >
                  {uploading ? "Mengunggah..." : "Simpan sebagai versi aktif"}
                </button>
              </div>
            </form>

            <div className="mt-5">
              <p className="text-sm font-semibold text-[var(--accent-ink)]">Riwayat versi</p>
              <ul className="mt-2 space-y-2">
                {templates.map((template) => (
                  <li
                    key={template.id}
                    className="flex items-center justify-between rounded-2xl border border-[var(--border-soft)] bg-white px-4 py-3 text-sm text-[var(--accent-ink)]"
                  >
                    <div>
                      <p className="font-semibold">{template.version}</p>
                      <p className="text-xs text-[var(--accent-ink)]/60">{new Date(template.uploaded_at).toLocaleString()}</p>
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        template.is_active ? "bg-emerald-100 text-emerald-900" : "bg-slate-100 text-slate-700"
                      }`}
                    >
                      {template.is_active ? "Aktif" : "Arsip"}
                    </span>
                  </li>
                ))}
                {templates.length === 0 && (
                  <li className="rounded-xl border border-dashed border-[var(--border-soft)] bg-white/60 px-4 py-4 text-sm text-[var(--accent-ink)]/70">
                    Belum ada template yang diunggah.
                  </li>
                )}
              </ul>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function StatCard({ title, value, accent }: { title: string; value: string; accent: string }) {
  return (
    <div className={`rounded-2xl px-4 py-5 text-center text-sm font-semibold ${accent}`}>
      <p className="text-xs uppercase tracking-wide text-[var(--accent-ink)]/60">{title}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
    </div>
  );
}

function SubmissionCard({ submission }: { submission: LkpsSubmission }) {
  const badge = statusPalette[submission.status] ?? statusPalette.draft;
  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-[var(--border-soft)] bg-white/80 p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-sm font-semibold text-[var(--accent-ink)]">TS {submission.tahun_ts}</p>
        <p className="text-xs text-[var(--accent-ink)]/70">ID: {submission.program_studi_id}</p>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <span className={`inline-flex items-center justify-center rounded-full px-3 py-1 text-xs font-semibold ${badge.bg} ${badge.text}`}>
          {badge.label}
        </span>
        <Link
          href={`/akreditasi/lkps/${submission.id}`}
          className="rounded-full border border-[var(--accent-emerald)] px-4 py-1.5 text-sm font-semibold text-[var(--accent-emerald)] transition hover:bg-[var(--accent-emerald)] hover:text-white"
        >
          Buka workspace
        </Link>
      </div>
    </div>
  );
}

function loadOfflineList<T>(key: string): T[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T[]) : [];
  } catch {
    return [];
  }
}

function persistOfflineList<T>(key: string, value: T[]): void {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore quota errors in sandbox mode
  }
}
