export type StatusColor = "green" | "yellow" | "red" | "orange";

export interface KriteriaRow {
  id: string;
  nama: string;
  status: StatusColor;
  statusLabel: string;
  progres: number;
  hasLKPS: boolean;
  hasLED: boolean;
  hasEvidence: boolean;
}

export interface DashboardProdiProps {
  tahunOptions: string[];
  defaultTahun?: string;
  lkpsPercent: number;
  ledPercent: number;
  dokumenPendukungPercent: number;
  kriteriaList: KriteriaRow[];
  pesanRekomendasi: string[];
  // Gauge
  skorNilai: number;
  skorTarget: number;
  // Early Warning
  deadline: string;
  sisaHari: number;
  earlyWarnings: string[];
  onUnduhLKPS?: () => void;
  onUnduhLED?: () => void;
  onEditLKPS?: (id: string) => void;
  onEditLED?: (id: string) => void;
  onEditEvidence?: (id: string) => void;
  onAturDeadline?: () => void;
}
