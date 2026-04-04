"use client";

import { use, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

import {
  createSectionRecord,
  deleteSectionRecord,
  downloadLkpsWorkbook,
  fetchSectionRecords,
  updateSectionRecord,
} from "@/lib/api/lkps";
import { LKPS_SECTIONS } from "@/constants/lkps-sections";
import type {
  FieldDefinition,
  SectionDefinition,
  SectionRecord,
} from "@/types/lkps";

interface WorkspaceParams {
  params: Promise<{ submissionId: string }>;
}

// Records persisted to backend include an `id` field returned by the server
type PersistedRecord = SectionRecord & { id: string };
type SectionRecordsState = Record<string, PersistedRecord[]>;

const spanClassMap: Record<number, string> = {
  1: "md:col-span-1",
  2: "md:col-span-2",
  3: "md:col-span-3",
  4: "md:col-span-4",
  5: "md:col-span-5",
  6: "md:col-span-6",
};

export default function LkpsWorkspaceDetail({ params }: WorkspaceParams) {
  const { submissionId } = use(params);
  const searchParams = useSearchParams();
  const router = useRouter();
  const kriteriaFilter = searchParams.get("kriteria");
  const targetId = searchParams.get("target_akreditasi_id");
  const tahun = searchParams.get("tahun");

  const sectionLookup = useMemo(() => {
    return Object.fromEntries(LKPS_SECTIONS.map((s) => [s.code, s]));
  }, []);

  const groupedSections = useMemo(() => {
    const groups = new Map<string, SectionDefinition[]>();
    LKPS_SECTIONS.forEach((s) => {
      if (kriteriaFilter) {
        const filterNumber = kriteriaFilter.replace(/\D/g, "");
        if (!s.group.includes(`Kriteria ${filterNumber}`)) return;
      }
      const list = groups.get(s.group) ?? [];
      list.push(s);
      groups.set(s.group, list);
    });
    return Array.from(groups.entries());
  }, [kriteriaFilter]);

  const firstEditable = useMemo(() => {
    if (groupedSections.length > 0 && groupedSections[0][1].length > 0) {
      return (
        groupedSections[0][1].find((s) => s.mode === "records") ??
        groupedSections[0][1][0]
      );
    }
    return LKPS_SECTIONS.find((s) => s.mode === "records") ?? LKPS_SECTIONS[0];
  }, [groupedSections]);

  const [activeSectionCode, setActiveSectionCode] = useState<string>(
    firstEditable.code,
  );

  useEffect(() => {
    setActiveSectionCode(firstEditable.code);
  }, [firstEditable.code]);
  const [recordsBySection, setRecordsBySection] = useState<SectionRecordsState>(
    () => {
      const initial: SectionRecordsState = {};
      LKPS_SECTIONS.forEach((s) => {
        initial[s.code] = [];
      });
      return initial;
    },
  );

  // Loading / saving / error state
  const [loadingSection, setLoadingSection] = useState<string | null>(null);
  const [savingIndex, setSavingIndex] = useState<number | null>(null);
  const [sectionError, setSectionError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  // Track which sections have already been fetched so we don't re-fetch on every tab switch
  const fetchedSections = useRef<Set<string>>(new Set());

  const activeSection = sectionLookup[activeSectionCode] ?? LKPS_SECTIONS[0];
  const activeRecords = recordsBySection[activeSection.code] ?? [];

  // -----------------------------------------------------------------------
  // Load records for the active section when user switches to it
  // -----------------------------------------------------------------------
  const loadSection = useCallback(
    async (code: string) => {
      const section = sectionLookup[code];
      if (!section || section.mode !== "records") return;
      if (fetchedSections.current.has(code)) return;

      setLoadingSection(code);
      setSectionError(null);
      try {
        const rows = await fetchSectionRecords(submissionId, code);
        fetchedSections.current.add(code);
        setRecordsBySection((prev) => ({
          ...prev,
          [code]: rows as PersistedRecord[],
        }));
      } catch (err) {
        setSectionError(
          err instanceof Error ? err.message : "Gagal memuat data seksi.",
        );
      } finally {
        setLoadingSection(null);
      }
    },
    [submissionId, sectionLookup],
  );

  // Load on mount and on section change
  useEffect(() => {
    loadSection(activeSectionCode);
  }, [activeSectionCode, loadSection]);

  // -----------------------------------------------------------------------
  // Add a new row (POST to backend, then update local state)
  // -----------------------------------------------------------------------
  const handleAddRecord = useCallback(
    async (section: SectionDefinition) => {
      if (section.mode !== "records") return;
      setSectionError(null);
      const newRecord = createEmptyRecord(section);
      setSavingIndex(-1); // -1 = new row being saved
      try {
        const saved = await createSectionRecord(
          submissionId,
          section.code,
          newRecord,
        );
        setRecordsBySection((prev) => ({
          ...prev,
          [section.code]: [...prev[section.code], saved as PersistedRecord],
        }));
      } catch (err) {
        setSectionError(
          err instanceof Error ? err.message : "Gagal menambah baris.",
        );
      } finally {
        setSavingIndex(null);
      }
    },
    [submissionId],
  );

  // -----------------------------------------------------------------------
  // Field change: debounced PATCH to backend
  // -----------------------------------------------------------------------
  const saveTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

  const handleFieldChange = useCallback(
    (
      sectionCode: string,
      recordIndex: number,
      fieldKey: string,
      value: unknown,
    ) => {
      // Optimistic local update first
      setRecordsBySection((prev) => {
        const sectionRecords = prev[sectionCode] ?? [];
        const updatedRecord = {
          ...sectionRecords[recordIndex],
          [fieldKey]: value,
        };
        const nextRecords = [...sectionRecords];
        nextRecords[recordIndex] = updatedRecord as PersistedRecord;
        return { ...prev, [sectionCode]: nextRecords };
      });

      // Debounce PATCH – 600 ms
      const timerKey = `${sectionCode}-${recordIndex}`;
      clearTimeout(saveTimers.current[timerKey]);
      saveTimers.current[timerKey] = setTimeout(async () => {
        setRecordsBySection((prev) => {
          const record = prev[sectionCode]?.[recordIndex];
          if (!record?.id) return prev;
          updateSectionRecord(
            submissionId,
            sectionCode,
            record.id,
            record,
          ).catch((err) => {
            setSectionError(
              err instanceof Error ? err.message : "Gagal menyimpan perubahan.",
            );
          });
          return prev;
        });
      }, 600);
    },
    [submissionId],
  );

  // -----------------------------------------------------------------------
  // Remove a row (DELETE from backend)
  // -----------------------------------------------------------------------
  const handleRemoveRecord = useCallback(
    async (sectionCode: string, recordIndex: number) => {
      const record = recordsBySection[sectionCode]?.[recordIndex];
      if (!record) return;
      setSectionError(null);
      setSavingIndex(recordIndex);
      try {
        if (record.id) {
          await deleteSectionRecord(submissionId, sectionCode, record.id);
        }
        setRecordsBySection((prev) => {
          const nextRecords = (prev[sectionCode] ?? []).filter(
            (_, idx) => idx !== recordIndex,
          );
          return { ...prev, [sectionCode]: nextRecords };
        });
      } catch (err) {
        setSectionError(
          err instanceof Error ? err.message : "Gagal menghapus baris.",
        );
      } finally {
        setSavingIndex(null);
      }
    },
    [submissionId, recordsBySection],
  );

  // -----------------------------------------------------------------------
  // Export workbook
  // -----------------------------------------------------------------------
  const handleExport = useCallback(async () => {
    setExporting(true);
    setSectionError(null);
    try {
      const blob = await downloadLkpsWorkbook(submissionId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `LKPS-${submissionId}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setSectionError(
        err instanceof Error ? err.message : "Gagal mengekspor workbook.",
      );
    } finally {
      setExporting(false);
    }
  }, [submissionId]);

  const totalRows = Object.values(recordsBySection).reduce(
    (acc, rows) => acc + rows.length,
    0,
  );

  return (
    <main className="min-h-screen bg-[#f4f6f8] px-4 py-8 text-[var(--accent-ink)] md:px-8">
      {kriteriaFilter && targetId && (
        <div className="mx-auto max-w-7xl mb-6">
          <div className="flex justify-between items-end border-b border-gray-300 pb-4">
            <div>
              <button
                onClick={() => router.push("/prodi/dashboard-prodi")}
                className="text-sm font-semibold text-[#00509d] hover:text-[#003f7d] transition-colors mb-4 block"
              >
                ← Kembali ke Dashboard Prodi
              </button>
              <div className="flex gap-6 mt-2">
                <button className="pb-2 text-sm font-semibold text-[#00509d] border-b-2 border-[#00509d] relative top-[1px]">
                  Data LKPS
                </button>
                <button
                  onClick={() => {
                    router.push(
                      `/prodi/led?target_akreditasi_id=${targetId}&kriteria_kode=${kriteriaFilter}&tahun=${tahun || ""}&lkps_submission_id=${submissionId}`,
                    );
                  }}
                  className="pb-2 text-sm font-semibold text-gray-500 hover:text-[#00509d] transition-colors relative"
                >
                  Narasi LED
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="mx-auto flex max-w-7xl flex-col gap-6 lg:flex-row">
        {/* ----------------------------------------------------------------
            Sidebar
        ---------------------------------------------------------------- */}
        <aside className="lg:w-72">
          <div className="sticky top-6 rounded-3xl border border-[var(--border-soft)] bg-[var(--surface-primary)] p-5 shadow-[var(--shadow-soft)]">
            <p className="text-xs uppercase tracking-[0.3em] text-[#00509d]">
              Submission
            </p>
            <h2 className="mt-2 truncate text-lg font-semibold text-[var(--accent-ink)]">
              {submissionId}
            </h2>

            <div className="mt-4 flex items-center justify-between rounded-2xl bg-[var(--surface-muted)]/70 px-3 py-2 text-xs font-semibold text-[var(--accent-ink)]">
              <span>Total baris tersimpan</span>
              <span>{totalRows}</span>
            </div>

            <button
              type="button"
              onClick={handleExport}
              disabled={exporting}
              className="mt-3 w-full rounded-2xl bg-[#00509d] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#003f7d] disabled:opacity-50"
            >
              {exporting ? "Mengekspor..." : "Ekspor ke Excel (.xlsx)"}
            </button>

            <div className="mt-6 space-y-5">
              {groupedSections.map(([groupName, sections]) => (
                <div key={groupName}>
                  <p className="text-xs font-semibold uppercase tracking-wide text-[var(--accent-ink)]/60">
                    {groupName}
                  </p>
                  <div className="mt-2 space-y-1.5">
                    {sections.map((section) => {
                      const isActive = section.code === activeSectionCode;
                      const recordCount =
                        recordsBySection[section.code]?.length ?? 0;
                      return (
                        <button
                          key={section.code}
                          type="button"
                          onClick={() => setActiveSectionCode(section.code)}
                          className={`flex w-full items-center justify-between rounded-2xl border px-3 py-2 text-left text-sm transition ${
                            isActive
                              ? "border-[#00509d] bg-[#eef4fb] text-[var(--accent-ink)]"
                              : "border-transparent bg-transparent text-[var(--accent-ink)]/70 hover:bg-white/40"
                          }`}
                        >
                          <span className="pr-2 font-medium">
                            {section.title}
                          </span>
                          {section.mode === "records" && (
                            <span className="rounded-full bg-[var(--surface-muted)] px-2 py-0.5 text-xs font-semibold text-[var(--accent-ink)]/80">
                              {recordCount}
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* ----------------------------------------------------------------
            Main panel
        ---------------------------------------------------------------- */}
        <section className="flex-1 rounded-[32px] border border-[var(--border-soft)] bg-[var(--surface-primary)] p-6 shadow-[var(--shadow-soft)] md:p-8">
          <header className="flex flex-col gap-4 border-b border-[var(--border-soft)] pb-6 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.4em] text-[#00509d]">
                {activeSection.sheetLabel}
              </p>
              <h1 className="mt-2 text-3xl font-semibold text-[var(--accent-ink)]">
                {activeSection.title}
              </h1>
              {activeSection.purpose && (
                <p className="mt-2 max-w-2xl text-sm text-[var(--accent-ink)]/80">
                  {activeSection.purpose}
                </p>
              )}
            </div>
            {activeSection.mode === "records" && (
              <div className="flex flex-wrap gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => handleAddRecord(activeSection)}
                  disabled={savingIndex === -1}
                  className="rounded-full bg-[#00509d] px-4 py-2 font-semibold text-white transition hover:bg-[#003f7d] disabled:opacity-50"
                >
                  {savingIndex === -1 ? "Menyimpan..." : "Tambah baris"}
                </button>
              </div>
            )}
          </header>

          {/* Error banner */}
          {sectionError && (
            <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
              {sectionError}
            </div>
          )}

          {activeSection.mode === "static" ? (
            <div className="mt-6 rounded-3xl border border-dashed border-[var(--border-soft)] bg-white/70 p-6 text-sm text-[var(--accent-ink)]/80">
              <p>
                {activeSection.note ??
                  "Seksi ini bersifat statis dan mengikuti master data."}
              </p>
            </div>
          ) : (
            <div className="mt-6 space-y-6">
              {activeSection.note && (
                <div className="rounded-2xl border border-[var(--border-soft)] bg-[var(--surface-muted)]/70 px-4 py-3 text-sm text-[var(--accent-ink)]/80">
                  {activeSection.note}
                </div>
              )}

              {activeSection.pinnedValues && (
                <div className="flex flex-wrap gap-2 text-xs text-[var(--accent-ink)]">
                  {Object.entries(activeSection.pinnedValues).map(
                    ([key, value]) => (
                      <span
                        key={key}
                        className="rounded-full bg-[var(--surface-muted)] px-3 py-1 font-semibold"
                      >
                        {key}: {String(value)}
                      </span>
                    ),
                  )}
                </div>
              )}

              {loadingSection === activeSectionCode ? (
                <p className="py-10 text-center text-sm text-[var(--accent-ink)]/60">
                  Memuat data seksi...
                </p>
              ) : activeRecords.length === 0 ? (
                <p className="rounded-3xl border border-dashed border-[var(--border-soft)] bg-white/60 px-4 py-10 text-center text-sm text-[var(--accent-ink)]/70">
                  Belum ada baris data. Klik &quot;Tambah baris&quot; untuk
                  mulai mengisi tabel LKPS.
                </p>
              ) : (
                <div className="space-y-5">
                  {activeRecords.map((record, index) => (
                    <RecordCard
                      key={record.id ?? `${activeSection.code}-${index}`}
                      index={index}
                      section={activeSection}
                      record={record}
                      saving={savingIndex === index}
                      onFieldChange={(fieldKey, value) =>
                        handleFieldChange(
                          activeSection.code,
                          index,
                          fieldKey,
                          value,
                        )
                      }
                      onRemove={() =>
                        handleRemoveRecord(activeSection.code, index)
                      }
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

// ---------------------------------------------------------------------------
// RecordCard
// ---------------------------------------------------------------------------

function RecordCard({
  index,
  section,
  record,
  saving,
  onFieldChange,
  onRemove,
}: {
  index: number;
  section: SectionDefinition;
  record: SectionRecord;
  saving: boolean;
  onFieldChange: (fieldKey: string, value: unknown) => void;
  onRemove: () => void;
}) {
  return (
    <div className="rounded-3xl border border-[var(--border-soft)] bg-white/85 p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between text-sm font-semibold text-[var(--accent-ink)]">
        <p>Baris #{index + 1}</p>
        <button
          type="button"
          onClick={onRemove}
          disabled={saving}
          className="text-xs text-red-500 hover:underline disabled:opacity-40"
        >
          {saving ? "Menghapus..." : "Hapus baris"}
        </button>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {section.fields.map((field) => {
          const disabled = Boolean(
            section.pinnedValues && field.key in section.pinnedValues,
          );
          return (
            <FieldInput
              key={field.key}
              field={field}
              value={record[field.key]}
              disabled={disabled}
              onChange={(value) => onFieldChange(field.key, value)}
            />
          );
        })}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// FieldInput
// ---------------------------------------------------------------------------

function FieldInput({
  field,
  value,
  disabled,
  onChange,
}: {
  field: FieldDefinition;
  value: unknown;
  disabled?: boolean;
  onChange: (value: unknown) => void;
}) {
  const spanClass = spanClassMap[field.span ?? 1] ?? "md:col-span-2";
  const baseLabel =
    "mb-1 block text-xs font-semibold uppercase tracking-wide text-[var(--accent-ink)]/60";
  const baseInput =
    "w-full rounded-2xl border border-[var(--border-soft)] bg-white px-3 py-2 text-sm text-[var(--accent-ink)] focus:border-[#00509d] focus:outline-none disabled:opacity-60";

  if (field.type === "textarea") {
    return (
      <div className={spanClass}>
        <label className={baseLabel}>{field.label}</label>
        <textarea
          rows={field.span && field.span > 1 ? 4 : 3}
          value={(value as string | undefined) ?? ""}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          placeholder={field.placeholder}
          className={`${baseInput} min-h-[120px]`}
        />
      </div>
    );
  }

  if (field.type === "select" && field.options) {
    return (
      <div className={spanClass}>
        <label className={baseLabel}>{field.label}</label>
        <select
          value={(value as string | undefined) ?? ""}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          className={baseInput}
        >
          <option value="">Pilih opsi</option>
          {field.options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    );
  }

  if (field.type === "boolean") {
    return (
      <div className={spanClass}>
        <label className={baseLabel}>{field.label}</label>
        <div className="flex items-center gap-2 rounded-2xl border border-[var(--border-soft)] bg-white px-3 py-2">
          <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={(e) => onChange(e.target.checked)}
            disabled={disabled}
            className="h-4 w-4"
          />
          <span className="text-sm text-[var(--accent-ink)]">
            {Boolean(value) ? "Ya" : "Tidak"}
          </span>
        </div>
      </div>
    );
  }

  const isNumberField =
    field.type === "integer" ||
    field.type === "decimal" ||
    field.type === "number";
  const inputType =
    field.type === "date" ? "date" : isNumberField ? "number" : "text";
  const step =
    field.step ??
    (field.type === "integer"
      ? 1
      : field.type === "decimal"
        ? 0.01
        : undefined);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (field.type === "integer") {
      onChange(
        e.target.value === "" ? "" : Number.parseInt(e.target.value, 10),
      );
    } else if (field.type === "decimal" || field.type === "number") {
      onChange(e.target.value === "" ? "" : Number(e.target.value));
    } else {
      onChange(e.target.value);
    }
  };

  return (
    <div className={spanClass}>
      <label className={baseLabel}>{field.label}</label>
      <input
        type={inputType}
        value={
          value === undefined || value === null
            ? ""
            : typeof value === "number"
              ? value
              : (value as string)
        }
        onChange={handleChange}
        disabled={disabled}
        placeholder={field.placeholder}
        min={field.min}
        max={field.max}
        step={step}
        className={baseInput}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function createEmptyRecord(section: SectionDefinition): SectionRecord {
  const record: SectionRecord = {};
  section.fields.forEach((field) => {
    record[field.key] = defaultValueForField(field);
  });
  if (section.pinnedValues) {
    Object.assign(record, section.pinnedValues);
  }
  return record;
}

function defaultValueForField(field: FieldDefinition): unknown {
  switch (field.type) {
    case "integer":
    case "decimal":
    case "number":
      return 0;
    case "boolean":
      return false;
    case "select":
      return field.options?.[0]?.value ?? "";
    default:
      return "";
  }
}
