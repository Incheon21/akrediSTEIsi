/** Semicircle gauge SVG */
const GaugeMeter = ({ score, target }: { score: number; target: number }) => {
  // Map score 1.0–4.0 → angle -90° to +90°
  const clamp = (v: number, min: number, max: number) =>
    Math.min(max, Math.max(min, v));
  const scoreAngleDeg = ((clamp(score, 1, 4) - 1) / 3) * 180 - 90;
  const targetAngleDeg = ((clamp(target, 1, 4) - 1) / 3) * 180 - 90;

  const toRad = (d: number) => (d * Math.PI) / 180;
  const cx = 100;
  const cy = 100;
  const r = 70;

  const needleX = cx + r * 0.85 * Math.cos(toRad(scoreAngleDeg));
  const needleY = cy + r * 0.85 * Math.sin(toRad(scoreAngleDeg));

  const targetX = cx + (r + 14) * Math.cos(toRad(targetAngleDeg));
  const targetY = cy + (r + 14) * Math.sin(toRad(targetAngleDeg));

  return (
    <div className="flex flex-col items-center">
      <p className="text-sm font-semibold text-gray-700 mb-1">Hasil Skor</p>
      <svg viewBox="0 0 200 110" className="w-52">
        {/* Gradient arcs */}
        {[
          { start: -90, end: -30, color: "#ef4444" },   // 1.0–2.0 red
          { start: -30, end: 30,  color: "#eab308" },   // 2.0–3.0 yellow
          { start: 30,  end: 60,  color: "#a3e635" },   // 3.0–3.5 light green
          { start: 60,  end: 90,  color: "#22c55e" },   // 3.5–4.0 green
        ].map(({ start, end, color }, i) => {
          const x1 = cx + r * Math.cos(toRad(start));
          const y1 = cy + r * Math.sin(toRad(start));
          const x2 = cx + r * Math.cos(toRad(end));
          const y2 = cy + r * Math.sin(toRad(end));
          const large = end - start > 180 ? 1 : 0;
          return (
            <path
              key={i}
              d={`M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`}
              fill="none"
              stroke={color}
              strokeWidth="16"
              strokeLinecap="butt"
            />
          );
        })}

        {/* Range labels */}
        <text x="18" y="105" fontSize="7" fill="#6b7280">1,0 - 2,0</text>
        <text x="70" y="30" fontSize="7" fill="#6b7280" textAnchor="middle">2,01 - 3,5</text>
        <text x="148" y="60" fontSize="7" fill="#6b7280" textAnchor="middle">3,51 - 4,0</text>

        {/* Target marker */}
        <circle cx={targetX} cy={targetY} r="4" fill="#1d4ed8" />
        <text
          x={targetX + 4}
          y={targetY - 4}
          fontSize="7"
          fill="#1d4ed8"
          fontWeight="bold"
        >
          Target
        </text>

        {/* Needle */}
        <line
          x1={cx}
          y1={cy}
          x2={needleX}
          y2={needleY}
          stroke="#111"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <circle cx={cx} cy={cy} r="4" fill="#111" />

        {/* Skor label */}
        <text x={cx} y={cy + 18} fontSize="8" fill="#374151" textAnchor="middle">
          Skor
        </text>
      </svg>
    </div>
  );
};

export default GaugeMeter;
