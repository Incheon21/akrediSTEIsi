import { StatusColor } from "./types";

const STATUS_COLORS: Record<StatusColor, string> = {
  green: "bg-green-500",
  yellow: "bg-yellow-400",
  red: "bg-red-500",
  orange: "bg-orange-400",
};

const StatusDot = ({ status, label }: { status: StatusColor; label: string }) => (
  <div className="flex items-center gap-2">
    <span className={`w-4 h-4 rounded-full inline-block ${STATUS_COLORS[status]}`} />
    <span className="text-sm text-gray-600">{label}</span>
  </div>
);

export default StatusDot;
