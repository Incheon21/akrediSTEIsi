export type StatusColor = "green" | "yellow" | "red" | "orange";

export type UserRole = "admin" | "pimpinan" | "koordinator" | "tim_prodi";

export interface ProgramStudiProfile {
  name: string;
  degree: string;
  last_accreditation_status: string;
  last_accreditation_year: number;
  is_active_accreditation: boolean;
}

export interface CriteriaRow {
  id: string;
  name: string;
  status: StatusColor;
  status_label: string;
  progress: number;
  has_lkps: boolean;
  lkps_available: boolean;
  has_led: boolean;
  led_available: boolean;
  has_evidence: boolean;
}


export interface DashboardData {
  program_studi_profile: ProgramStudiProfile;
  target_akreditasi_id: string;
  lkps_submission_id?: string;
  current_year: number;
  available_years: number[];
  criteria_list: CriteriaRow[];
  recommendation_messages: string[];
  early_warnings: string[];
  score_value: number;
  target_score: number;
  deadline: string;
  days_remaining: number;
  lkps_percent: number;
  led_percent: number;
  evidence_percent: number;
}
