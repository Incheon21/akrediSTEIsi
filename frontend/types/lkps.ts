export type LkpsStatus = "draft" | "submitted" | "reviewed" | "approved";

export interface LkpsSubmission {
  id: string;
  program_studi_id: string;
  template_id: string | null;
  tahun_ts: number;
  status: LkpsStatus;
  nama_pengusul?: string | null;
  tanggal_pengajuan?: string | null;
  submitted_at?: string | null;
  created_at?: string;
}

export interface LkpsTemplateInfo {
  id: string;
  version: string;
  filename: string;
  is_active: boolean;
  uploaded_at: string;
}

export interface SectionProgress {
  section_code: string;
  status: "not_started" | "in_progress" | "completed";
  completion_pct: number;
  notes?: string | null;
  last_updated_at?: string | null;
}

export type FieldInputType =
  | "text"
  | "textarea"
  | "number"
  | "integer"
  | "decimal"
  | "date"
  | "select"
  | "boolean";

export interface FieldDefinition {
  key: string;
  label: string;
  type: FieldInputType;
  placeholder?: string;
  description?: string;
  options?: { label: string; value: string }[];
  span?: number;
  min?: number;
  max?: number;
  step?: number;
}

export type SectionMode = "records" | "static";

export interface SectionDefinition {
  code: string;
  title: string;
  sheetLabel: string;
  purpose: string;
  group: string;
  mode: SectionMode;
  pinnedValues?: Record<string, string | number | boolean>;
  fields: FieldDefinition[];
  note?: string;
  /** If set, only these jenjang codes may fill this section. Omit = universal. */
  applicableFor?: string[];
  /**
   * Fixed template rows. When present the section is rendered in "fixed" mode:
   * rows are pre-seeded from the template (merged with DB values), no add/delete.
   * Each object must contain the labelKey field used to match DB records.
   */
  templateRows?: Record<string, string | number>[];
  /** The field key that identifies a fixed row (e.g. "kode", "kode_sumber", "jenis_dokumen"). */
  labelKey?: string;
}

export type SectionRecord = Record<string, unknown>;
