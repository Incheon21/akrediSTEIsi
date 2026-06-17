"use client";

import { use, useCallback, useEffect, useMemo, useRef, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useAuth } from "@/app/hooks/useAuth";

import {
  createSectionRecord,
  deleteSectionRecord,
  fetchLkpsSubmission,
  fetchProgramStudiList,
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

type PersistedRecord = SectionRecord & { id: string };
type SectionRecordsState = Record<string, PersistedRecord[]>;

// Minimum pixel width for each column type
const COL_WIDTH: Record<string, number> = {
  textarea: 220,
  text: 160,
  integer: 90,
  decimal: 90,
  number: 90,
  date: 130,
  select: 140,
  boolean: 80,
};

function LkpsWorkspaceDetailInner({ params }: WorkspaceParams) {
  const { submissionId } = use(params);
  const searchParams = useSearchParams();
  const router = useRouter();
  const kriteriaFilter = searchParams.get("kriteria");
  const targetId = searchParams.get("target_akreditasi_id");
  const tahun = searchParams.get("tahun");
  const prodiId = searchParams.get("id");

  const { user } = useAuth();
  const canEdit = user?.role === "admin" || user?.role === "tim_prodi";

  const [jenjang, setJenjang] = useState<string | null>(null);

  useEffect(() => {
    async function loadJenjang() {
      try {
        const [submission, prodiList] = await Promise.all([
          fetchLkpsSubmission(submissionId),
          fetchProgramStudiList(),
        ]);
        const prodi = prodiList.find((p) => p.id === submission.program_studi_id);
        if (prodi) setJenjang(prodi.jenjang);
      } catch {
        // jenjang stays null → all sections shown (safe fallback)
      }
    }
    loadJenjang();
  }, [submissionId]);

  const applicableSections = useMemo(() => {
    if (!jenjang) return LKPS_SECTIONS;
    return LKPS_SECTIONS.filter(
      (s) => !s.applicableFor || s.applicableFor.includes(jenjang),
    );
  }, [jenjang]);

  const sectionLookup = useMemo(
    () => Object.fromEntries(applicableSections.map((s) => [s.code, s])),
    [applicableSections],
  );

  const groupedSections = useMemo(() => {
    const groups = new Map<string, SectionDefinition[]>();
    applicableSections.forEach((s) => {
      if (kriteriaFilter) {
        const filterNumber = kriteriaFilter.replace(/\D/g, "");
        if (!s.group.includes(`Kriteria ${filterNumber}`)) return;
      }
      const list = groups.get(s.group) ?? [];
      list.push(s);
      groups.set(s.group, list);
    });
    return Array.from(groups.entries());
  }, [applicableSections, kriteriaFilter]);

  const firstEditable = useMemo(() => {
    if (groupedSections.length > 0 && groupedSections[0][1].length > 0) {
      return (
        groupedSections[0][1].find((s) => s.mode === "records") ??
        groupedSections[0][1][0]
      );
    }
    return applicableSections.find((s) => s.mode === "records") ?? applicableSections[0];
  }, [groupedSections, applicableSections]);

  const [activeSectionCode, setActiveSectionCode] = useState<string>(
    firstEditable.code,
  );

  useEffect(() => {
    setActiveSectionCode(firstEditable.code);
  }, [firstEditable.code]);

  const [recordsBySection, setRecordsBySection] = useState<SectionRecordsState>({});

  const [loadingSection, setLoadingSection] = useState<string | null>(null);
  const [addingRow, setAddingRow] = useState(false);
  const [deletingIndex, setDeletingIndex] = useState<number | null>(null);
  const [sectionError, setSectionError] = useState<string | null>(null);

  const activeSection = sectionLookup[activeSectionCode] ?? applicableSections[0];
  const activeRecords = recordsBySection[activeSection.code] ?? [];

  const loadSection = useCallback(
    async (code: string) => {
      const section = sectionLookup[code];
      if (!section || section.mode !== "records") return;

      setLoadingSection(code);
      setSectionError(null);
      try {
        const rows = await fetchSectionRecords(submissionId, code);

        if (section.templateRows && section.labelKey) {
          // Fixed-row section: merge DB values into template row order
          const lk = section.labelKey;
          const dbByKey = new Map(
            (rows as PersistedRecord[]).map((r) => [String(r[lk] ?? ""), r]),
          );
          const merged = section.templateRows.map((tpl) => {
            const key = String(tpl[lk] ?? "");
            const db = dbByKey.get(key);
            return db ? { ...tpl, ...db } : ({ ...tpl } as unknown as PersistedRecord);
          });
          setRecordsBySection((prev) => ({ ...prev, [code]: merged }));
        } else {
          setRecordsBySection((prev) => ({ ...prev, [code]: rows as PersistedRecord[] }));
        }
      } catch (err) {
        setSectionError(err instanceof Error ? err.message : "Gagal memuat data seksi.");
      } finally {
        setLoadingSection(null);
      }
    },
    [submissionId, sectionLookup],
  );

  // Eagerly fetch all applicable sections so sidebar counts are immediately correct
  useEffect(() => {
    const recordSections = applicableSections.filter((s) => s.mode === "records");
    Promise.all(recordSections.map((s) => loadSection(s.code)));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [submissionId, applicableSections]);

  const handleAddRecord = useCallback(
    async (section: SectionDefinition) => {
      if (section.mode !== "records") return;
      setSectionError(null);
      setAddingRow(true);
      const newRecord = createEmptyRecord(section);
      const hasNo = section.fields.some((f) => f.key === "no");
      if (hasNo) {
        // Read current count synchronously from state snapshot via ref trick
        newRecord.no = (recordsBySection[section.code]?.length ?? 0) + 1;
      }
      try {
        await createSectionRecord(submissionId, section.code, newRecord);
        // Reload from backend to get authoritative order
        await loadSection(section.code);
      } catch (err) {
        setSectionError(err instanceof Error ? err.message : "Gagal menambah baris.");
      } finally {
        setAddingRow(false);
      }
    },
    [submissionId, recordsBySection, loadSection],
  );

  const saveTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

  const handleFieldChange = useCallback(
    (sectionCode: string, recordIndex: number, fieldKey: string, value: unknown) => {
      setRecordsBySection((prev) => {
        const sectionRecords = prev[sectionCode] ?? [];
        const updatedRecord = { ...sectionRecords[recordIndex], [fieldKey]: value };
        const nextRecords = [...sectionRecords];
        nextRecords[recordIndex] = updatedRecord as PersistedRecord;
        return { ...prev, [sectionCode]: nextRecords };
      });

      const timerKey = `${sectionCode}-${recordIndex}`;
      clearTimeout(saveTimers.current[timerKey]);
      saveTimers.current[timerKey] = setTimeout(async () => {
        setRecordsBySection((prev) => {
          const record = prev[sectionCode]?.[recordIndex];
          if (!record) return prev;
          if (record.id) {
            updateSectionRecord(submissionId, sectionCode, record.id, record).catch((err) => {
              setSectionError(err instanceof Error ? err.message : "Gagal menyimpan perubahan.");
            });
          } else {
            // Fixed-row record with no DB entry yet — create it
            createSectionRecord(submissionId, sectionCode, record).then((saved) => {
              setRecordsBySection((s) => {
                const next = [...(s[sectionCode] ?? [])];
                next[recordIndex] = { ...next[recordIndex], ...saved, id: (saved as PersistedRecord).id } as PersistedRecord;
                return { ...s, [sectionCode]: next };
              });
            }).catch((err) => {
              setSectionError(err instanceof Error ? err.message : "Gagal menyimpan perubahan.");
            });
          }
          return prev;
        });
      }, 600);
    },
    [submissionId],
  );

  const handleRemoveRecord = useCallback(
    async (sectionCode: string, recordIndex: number) => {
      const record = recordsBySection[sectionCode]?.[recordIndex];
      if (!record) return;
      setSectionError(null);
      setDeletingIndex(recordIndex);
      try {
        if (record.id) {
          await deleteSectionRecord(submissionId, sectionCode, record.id);
        }
        // Reload from backend so remaining rows reflect correct order/no values
        await loadSection(sectionCode);
      } catch (err) {
        setSectionError(err instanceof Error ? err.message : "Gagal menghapus baris.");
      } finally {
        setDeletingIndex(null);
      }
    },
    [submissionId, recordsBySection, loadSection],
  );


  const totalRows = applicableSections
    .filter((s) => s.mode === "records" && !s.templateRows)
    .reduce((acc, s) => acc + (recordsBySection[s.code]?.length ?? 0), 0);


  return (
    <main className="min-h-screen bg-[#f4f6f8] px-4 py-8 text-(--accent-ink) md:px-8">
      {kriteriaFilter && targetId && (
        <div className="mx-auto max-w-full mb-6">
          <div className="flex justify-between items-end border-b border-gray-300 pb-4">
            <div>
              <button
                onClick={() => router.push(`/prodi/dashboard-prodi${prodiId ? `?id=${prodiId}` : ""}`)}
                className="text-sm font-semibold text-[#00509d] hover:text-[#003f7d] transition-colors mb-4 block"
              >
                ← Kembali ke Dashboard Prodi
              </button>
              <div className="flex gap-6 mt-2">
                <button className="pb-2 text-sm font-semibold text-[#00509d] border-b-2 border-[#00509d] relative top-px">
                  Data LKPS
                </button>
                <button
                  onClick={() => router.push(
                    `/prodi/led?target_akreditasi_id=${targetId}&kriteria_kode=${kriteriaFilter}&tahun=${tahun || ""}&lkps_submission_id=${submissionId}${prodiId ? `&id=${prodiId}` : ""}`,
                  )}
                  className="pb-2 text-sm font-semibold text-gray-500 hover:text-[#00509d] transition-colors relative"
                >
                  Narasi LED
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="mx-auto flex max-w-full flex-col gap-6 lg:flex-row">
        {/* Sidebar */}
        <aside className="lg:w-64 shrink-0">
          <div className="sticky top-6 rounded-2xl border border-(--border-soft) bg-white p-4 shadow-sm">
            <p className="text-[10px] uppercase tracking-widest text-[#00509d] font-semibold">Submission</p>
            <h2 className="mt-1 truncate text-xs font-mono text-gray-500">{submissionId}</h2>

            <div className="mt-3 flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 text-xs font-semibold text-gray-700 border border-gray-100">
              <span>Total baris</span>
              <span>{totalRows}</span>
            </div>

            <div className="mt-4 space-y-4">
              {groupedSections.map(([groupName, sections]) => (
                <div key={groupName}>
                  <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">
                    {groupName}
                  </p>
                  <div className="space-y-0.5">
                    {sections.map((section) => {
                      const isActive = section.code === activeSectionCode;
                      const recordCount = recordsBySection[section.code]?.length ?? 0;
                      return (
                        <button
                          key={section.code}
                          type="button"
                          onClick={() => setActiveSectionCode(section.code)}
                          className={`flex w-full items-center justify-between rounded-lg px-3 py-1.5 text-left text-xs transition ${
                            isActive
                              ? "bg-[#00509d] text-white font-semibold"
                              : "text-gray-600 hover:bg-gray-100"
                          }`}
                        >
                          <span className="pr-1 leading-snug">{section.title}</span>
                          {section.mode === "records" && !section.templateRows && (
                            <span className={`shrink-0 rounded-full px-1.5 py-0.5 text-[10px] font-bold ${
                              isActive ? "bg-white/20 text-white" : "bg-gray-100 text-gray-500"
                            }`}>
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

        {/* Main panel */}
        <section className="flex-1 min-w-0 rounded-2xl border border-(--border-soft) bg-white shadow-sm overflow-hidden">
          {/* Section header */}
          <div className="border-b border-gray-200 bg-gray-50 px-6 py-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-widest text-[#00509d]">
                  {activeSection.sheetLabel}
                </p>
                <h1 className="mt-0.5 text-xl font-bold text-gray-900">{activeSection.title}</h1>
                {activeSection.purpose && (
                  <p className="mt-1 text-xs text-gray-500 max-w-2xl">{activeSection.purpose}</p>
                )}
              </div>
              {activeSection.mode === "records" && !activeSection.templateRows && canEdit && (
                <button
                  type="button"
                  onClick={() => handleAddRecord(activeSection)}
                  disabled={addingRow}
                  className="shrink-0 flex items-center gap-1.5 rounded-lg bg-[#00509d] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#003f7d] disabled:opacity-50"
                >
                  {addingRow ? (
                    <>
                      <span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                      Menyimpan...
                    </>
                  ) : (
                    <>
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                      </svg>
                      Tambah Baris
                    </>
                  )}
                </button>
              )}
            </div>

            {sectionError && (
              <div className="mt-3 rounded-lg border border-red-200 bg-red-50 px-4 py-2.5 text-sm text-red-700">
                {sectionError}
              </div>
            )}
          </div>

          {/* Content */}
          {activeSection.mode === "static" ? (
            <div className="px-6 py-10 text-sm text-gray-500">
              <p>{activeSection.note ?? "Seksi ini bersifat statis dan mengikuti master data."}</p>
            </div>
          ) : loadingSection === activeSectionCode ? (
            <div className="flex items-center justify-center py-20 text-sm text-gray-400">
              <span className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-gray-200 border-t-[#00509d] mr-2" />
              Memuat data...
            </div>
          ) : (
            <SectionTable
              section={activeSection}
              records={activeRecords}
              deletingIndex={deletingIndex}
              isFixed={Boolean(activeSection.templateRows)}
              onFieldChange={(recordIndex, fieldKey, value) =>
                handleFieldChange(activeSection.code, recordIndex, fieldKey, value)
              }
              onRemove={(recordIndex) => handleRemoveRecord(activeSection.code, recordIndex)}
              onAddRow={() => handleAddRecord(activeSection)}
              addingRow={addingRow}
              canEdit={canEdit}
            />
          )}
        </section>
      </div>
    </main>
  );
}

// ---------------------------------------------------------------------------
// SectionTable — spreadsheet-style table for one LKPS section
// ---------------------------------------------------------------------------

function SectionTable({
  section,
  records,
  deletingIndex,
  isFixed,
  onFieldChange,
  onRemove,
  onAddRow,
  addingRow,
  canEdit,
}: {
  section: SectionDefinition;
  records: PersistedRecord[];
  deletingIndex: number | null;
  isFixed: boolean;
  onFieldChange: (recordIndex: number, fieldKey: string, value: unknown) => void;
  onRemove: (recordIndex: number) => void;
  onAddRow: () => void;
  addingRow: boolean;
  canEdit: boolean;
}) {
  // Hide: labelKey for fixed sections, pinnedValues fields, and "no" (auto-filled from row index).
  const visibleFields = section.fields.filter((f) => {
    if (f.key === "no") return false;
    if (isFixed && f.key === section.labelKey) return false;
    if (!isFixed && section.pinnedValues && f.key in section.pinnedValues) return false;
    return true;
  });

  if (records.length === 0 && !isFixed) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="mb-3 rounded-full bg-gray-100 p-4">
          <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 0v10m0-10a2 2 0 012 2h2a2 2 0 012-2" />
          </svg>
        </div>
        <p className="text-sm font-medium text-gray-500 mb-1">Belum ada data</p>
        {canEdit && (
          <>
            <p className="text-xs text-gray-400 mb-5">Klik tombol di bawah untuk menambah baris pertama</p>
            <button
              onClick={onAddRow}
              disabled={addingRow}
              className="flex items-center gap-1.5 rounded-lg bg-[#00509d] px-4 py-2 text-sm font-semibold text-white hover:bg-[#003f7d] disabled:opacity-50"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              Tambah Baris Pertama
            </button>
          </>
        )}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm" style={{ minWidth: 600 }}>
        <thead>
          <tr className="bg-[#f0f5fb] border-b-2 border-[#00509d]/20">
            <th className="sticky left-0 z-10 bg-[#f0f5fb] w-10 px-2 py-3 text-center text-xs font-bold text-gray-500 border-r border-gray-200">
              No
            </th>
            {isFixed && (
              <th className="px-3 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wide border-r border-gray-100 whitespace-nowrap" style={{ minWidth: 260 }}>
                {section.fields.find((f) => f.key === section.labelKey)?.label ?? "Jenis"}
              </th>
            )}
            {visibleFields.map((field) => (
              <th
                key={field.key}
                style={{ minWidth: COL_WIDTH[field.type] ?? 140 }}
                className="px-3 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wide border-r border-gray-100 last:border-r-0 whitespace-nowrap"
              >
                {field.label}
              </th>
            ))}
            {!isFixed && canEdit && (
              <th className="w-14 px-2 py-3 text-center text-xs font-bold text-gray-400 uppercase tracking-wide">
                Hapus
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {records.map((record, rowIndex) => {
            const isDeleting = deletingIndex === rowIndex;
            return (
              <tr
                key={record.id ?? `row-${rowIndex}`}
                className={`border-b border-gray-100 transition-colors ${
                  isDeleting ? "opacity-40 pointer-events-none" : "hover:bg-blue-50/30"
                } ${rowIndex % 2 === 0 ? "bg-white" : "bg-gray-50/50"}`}
              >
                <td className="sticky left-0 z-10 bg-inherit w-10 px-2 py-1.5 text-center text-xs font-semibold text-gray-400 border-r border-gray-200">
                  {rowIndex + 1}
                </td>
                {isFixed && (
                  <td className="px-3 py-2 border-r border-gray-100 align-middle text-sm font-medium text-gray-700 bg-gray-50/70" style={{ minWidth: 260 }}>
                    {String(record["kode_label"] ?? record[section.labelKey ?? ""] ?? "")}
                  </td>
                )}
                {visibleFields.map((field) => (
                  <td key={field.key} className="px-1.5 py-1.5 border-r border-gray-100 last:border-r-0 align-top">
                    <TableCellInput
                      field={field}
                      value={record[field.key]}
                      onChange={(value) => canEdit && onFieldChange(rowIndex, field.key, value)}
                      readOnly={!canEdit}
                    />
                  </td>
                ))}
                {!isFixed && canEdit && (
                  <td className="w-14 px-2 py-1.5 text-center">
                    <button
                      type="button"
                      onClick={() => onRemove(rowIndex)}
                      disabled={isDeleting}
                      title="Hapus baris"
                      className="rounded p-1 text-red-400 hover:bg-red-50 hover:text-red-600 transition-colors disabled:opacity-40"
                    >
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </td>
                )}
              </tr>
            );
          })}
        </tbody>
        {!isFixed && canEdit && (
          <tfoot>
            <tr>
              <td
                colSpan={visibleFields.length + 2}
                className="px-4 py-2 border-t border-gray-200 bg-gray-50"
              >
                <button
                  type="button"
                  onClick={onAddRow}
                  disabled={addingRow}
                  className="flex items-center gap-1.5 text-xs font-semibold text-[#00509d] hover:text-[#003f7d] disabled:opacity-50 transition-colors py-1"
                >
                  {addingRow ? (
                    <>
                      <span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-[#00509d]/20 border-t-[#00509d]" />
                      Menyimpan baris baru...
                    </>
                  ) : (
                    <>
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                      </svg>
                      + Tambah baris
                    </>
                  )}
                </button>
              </td>
            </tr>
          </tfoot>
        )}
      </table>
    </div>
  );
}

// ---------------------------------------------------------------------------
// TableCellInput — compact inline input for use inside a table cell
// ---------------------------------------------------------------------------

function TableCellInput({
  field,
  value,
  onChange,
  readOnly = false,
}: {
  field: FieldDefinition;
  value: unknown;
  onChange: (value: unknown) => void;
  readOnly?: boolean;
}) {
  const [error, setError] = useState<string | null>(null);

  const base =
    "w-full bg-transparent border rounded px-1.5 py-1 text-sm text-gray-800 focus:bg-white focus:outline-none transition-colors";
  const normalBorder = "border-transparent hover:border-gray-300 focus:border-[#00509d]";
  const errorBorder = "border-red-400 focus:border-red-500";
  const readOnlyCls = "cursor-default select-text";

  if (field.type === "textarea") {
    return (
      <textarea
        rows={2}
        value={(value as string | undefined) ?? ""}
        onChange={(e) => !readOnly && onChange(e.target.value)}
        readOnly={readOnly}
        placeholder={readOnly ? "—" : (field.placeholder ?? "—")}
        className={`${base} ${normalBorder} resize-none leading-snug ${readOnly ? readOnlyCls : ""}`}
        style={{ minWidth: COL_WIDTH.textarea, minHeight: 52 }}
      />
    );
  }

  if (field.type === "select" && field.options) {
    return (
      <select
        value={(value as string | undefined) ?? ""}
        onChange={(e) => !readOnly && onChange(e.target.value)}
        disabled={readOnly}
        className={`${base} ${normalBorder} cursor-pointer`}
        style={{ minWidth: COL_WIDTH.select }}
      >
        <option value="">— pilih —</option>
        {field.options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    );
  }

  if (field.type === "boolean") {
    return (
      <div className="flex items-center justify-center">
        <input
          type="checkbox"
          checked={Boolean(value)}
          onChange={(e) => !readOnly && onChange(e.target.checked)}
          disabled={readOnly}
          className="h-4 w-4 rounded border-gray-300 text-[#00509d] cursor-pointer focus:ring-[#00509d] disabled:cursor-default"
        />
      </div>
    );
  }

  const isNumber = field.type === "integer" || field.type === "decimal" || field.type === "number";
  const inputType = field.type === "date" ? "date" : isNumber ? "number" : "text";
  const step = field.step ?? (field.type === "integer" ? 1 : field.type === "decimal" ? 0.01 : undefined);
  const minValue = field.min ?? (isNumber ? 0 : undefined);

  const validate = (raw: string): string | null => {
    if (raw === "") return null;
    if (isNumber) {
      const n = Number(raw);
      if (Number.isNaN(n)) return "Harus berupa angka";
      if (n < 0) return "Tidak boleh negatif";
      if (field.max !== undefined && n > field.max) return `Maks ${field.max}`;
    }
    return null;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    const err = validate(raw);
    setError(err);
    if (err) return; // don't propagate invalid values
    if (field.type === "integer") {
      onChange(raw === "" ? "" : Number.parseInt(raw, 10));
    } else if (field.type === "decimal" || field.type === "number") {
      onChange(raw === "" ? "" : Number(raw));
    } else {
      onChange(raw);
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setError(validate(e.target.value));
  };

  return (
    <div>
      <input
        type={inputType}
        value={value === undefined || value === null ? "" : typeof value === "number" ? value : (value as string)}
        onChange={handleChange}
        onBlur={handleBlur}
        readOnly={readOnly}
        placeholder={readOnly ? "—" : (field.placeholder ?? (isNumber ? "0" : "—"))}
        min={minValue}
        max={field.max}
        step={step}
        className={`${base} ${error ? errorBorder : normalBorder} ${readOnly ? readOnlyCls : ""}`}
        style={{ minWidth: COL_WIDTH[field.type] ?? 140 }}
      />
      {error && (
        <p className="mt-0.5 text-[10px] text-red-500 leading-tight">{error}</p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function createEmptyRecord(section: SectionDefinition): SectionRecord {
  const record: SectionRecord = {};
  section.fields.forEach((field) => { record[field.key] = defaultValueForField(field); });
  if (section.pinnedValues) Object.assign(record, section.pinnedValues);
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

export default function LkpsWorkspaceDetail({ params }: WorkspaceParams) {
  return (
    <Suspense fallback={null}>
      <LkpsWorkspaceDetailInner params={params} />
    </Suspense>
  )
}
