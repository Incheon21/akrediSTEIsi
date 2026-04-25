import { apiRequest } from "./client";
import type {
  LkpsSubmission,
  LkpsTemplateInfo,
  SectionProgress,
  SectionRecord,
} from "@/types/lkps";

export interface ProgramStudiOption {
  id: string;
  kode: string;
  nama: string;
  jenjang: string;
  fakultas: string | null;
  perguruan_tinggi: string | null;
  akreditasi: string | null;
  status: string;
}

export async function fetchProgramStudiList(): Promise<ProgramStudiOption[]> {
  return apiRequest("/api/v1/program-studi");
}

const BASE_PATH = "/api/v1/lkps";

export async function fetchLkpsSubmissions(): Promise<LkpsSubmission[]> {
  return apiRequest(`${BASE_PATH}/submissions`);
}

export async function fetchLkpsSubmission(id: string): Promise<LkpsSubmission> {
  return apiRequest(`${BASE_PATH}/submissions/${id}`);
}

export async function createLkpsSubmission(payload: {
  program_studi_id: string;
  tahun_ts: number;
  nama_pengusul?: string;
}): Promise<LkpsSubmission> {
  return apiRequest(`${BASE_PATH}/submissions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateLkpsSubmission(
  id: string,
  payload: Partial<Pick<LkpsSubmission, "status" | "nama_pengusul" | "tanggal_pengajuan">>,
): Promise<LkpsSubmission> {
  return apiRequest(`${BASE_PATH}/submissions/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function listTemplates(): Promise<LkpsTemplateInfo[]> {
  return apiRequest(`${BASE_PATH}/templates`);
}

export async function uploadTemplate(version: string, file: File): Promise<{ id: string; version: string }> {
  const form = new FormData();
  form.append("version", version);
  form.append("file", file);
  return apiRequest(`${BASE_PATH}/templates`, {
    method: "POST",
    body: form,
  });
}

export async function fetchSectionProgress(submissionId: string): Promise<SectionProgress[]> {
  return apiRequest(`${BASE_PATH}/submissions/${submissionId}/progress`);
}

export async function updateSectionProgress(
  submissionId: string,
  sectionCode: string,
  payload: Partial<Pick<SectionProgress, "status" | "completion_pct" | "notes">>,
): Promise<{ section_code: string; status: string; completion_pct: number }> {
  return apiRequest(`${BASE_PATH}/submissions/${submissionId}/progress/${sectionCode}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function fetchSectionRecords(
  submissionId: string,
  sectionCode: string,
): Promise<SectionRecord[]> {
  return apiRequest(`${BASE_PATH}/submissions/${submissionId}/sections/${sectionCode}/records`);
}

export async function createSectionRecord(
  submissionId: string,
  sectionCode: string,
  payload: SectionRecord,
): Promise<SectionRecord> {
  return apiRequest(`${BASE_PATH}/submissions/${submissionId}/sections/${sectionCode}/records`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateSectionRecord(
  submissionId: string,
  sectionCode: string,
  recordId: string,
  payload: SectionRecord,
): Promise<SectionRecord> {
  return apiRequest(`${BASE_PATH}/submissions/${submissionId}/sections/${sectionCode}/records/${recordId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteSectionRecord(
  submissionId: string,
  sectionCode: string,
  recordId: string,
): Promise<void> {
  await apiRequest(`${BASE_PATH}/submissions/${submissionId}/sections/${sectionCode}/records/${recordId}`, {
    method: "DELETE",
  });
}

export async function downloadLkpsWorkbook(submissionId: string): Promise<Blob> {
  return apiRequest(`${BASE_PATH}/submissions/${submissionId}/export`, {
    responseType: "blob",
  });
}
export async function uploadLkps(submissionId: string, file: File):
    Promise<{message: string; submission_id: string;}> {
  const form = new FormData();
  form.append("file", file);
  return apiRequest(`${BASE_PATH}/import/${submissionId}`, {
    method: "POST",
    body: form,
  });
}
