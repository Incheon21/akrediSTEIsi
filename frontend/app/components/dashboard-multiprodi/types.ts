export interface ProdiSummary {
    id: string;
    name: string;
    degree: string;
    accreditation_status: string;
    accreditation_year: number;
    lkps_percent: number;
    led_percent: number;
    evidence_percent: number;
    simulation_score: number;
    target_score: number;
    readiness_status: "green" | "yellow" | "red";
    is_active: boolean;
    days_remaining: number | null;
}

export interface FakultasSummary {
    total_prodi: number;
    prodi_green: number;
    prodi_yellow: number;
    prodi_red: number;
    avg_lkps_percent: number;
    avg_led_percent: number;
    avg_simulation_score: number;
}

export interface DashboardMultiProdiData {
    fakultas_summary: FakultasSummary;
    prodi_list: ProdiSummary[];
    current_year: number;
    available_years: number[];
}