export type StatusColor = "green" | "yellow" | "red" | "orange";

export interface KriteriaRow {
  id: string;
  nama: string;       // e.g. "Visi & Misi (C1)"
  status: StatusColor;
  statusLabel: string; // e.g. "Baik"
  progres: number;    // 0–100
  hasLKPS: boolean;
  hasLED: boolean;
  hasEvidence: boolean;
}

export interface DashboardProdiProps {
  tahunOptions: string[];             // e.g. ["2023", "2024", "2025"]
  defaultTahun?: string;
  lkpsPercent: number;                // 0–100
  ledPercent: number;                 // 0–100
  dokumenPendukungPercent: number;    // 0–100
  kriteriaList: KriteriaRow[];
  pesanRekomendasi: string[];
  // Gauge
  skorNilai: number;                  // e.g. 3.2
  skorTarget: number;                 // e.g. 3.5 (affects needle)
  // Early Warning
  deadline: string;                   // e.g. "24 Maret 2026"
  sisaHari: number;
  earlyWarnings: string[];            // list of warning messages
  // Handlers (optional – wire up later)
  onUnduhLKPS?: () => void;
  onUnduhLED?: () => void;
  onEditLKPS?: (id: string) => void;
  onEditLED?: (id: string) => void;
  onEditEvidence?: (id: string) => void;
  onAturDeadline?: () => void;
}
