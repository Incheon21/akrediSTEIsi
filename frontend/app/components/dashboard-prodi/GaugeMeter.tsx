const MAX_SCORE = 361;
const MIN_LULUS = 200;

const GaugeMeter = ({ score, target }: { score: number; target: number }) => {
  const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

  const hasScore = score > 0;
  const scoreVal = clamp(score, 0, MAX_SCORE);
  const targetVal = clamp(target, 0, MAX_SCORE);

  const pct = (v: number) => `${((v / MAX_SCORE) * 100).toFixed(2)}%`;

  const scoreColor = scoreVal >= MIN_LULUS ? "#22c55e" : "#ef4444";

  return (
    <div className="w-full flex flex-col">
      {/* Title */}
      <div className="flex items-center gap-2 mb-5">
        <span className="w-1 h-5 bg-[#00509d] rounded-full inline-block shrink-0" />
        <p className="text-sm font-bold text-[#132040]">Hasil Skor AkreditasiIIII</p>
      </div>

      {/* ── Bar area with top padding for the target marker ── */}
      <div className="relative w-full mt-6">

        {/* Target marker — segitiga + label di atas bar */}
        {targetVal > 0 && (
          <div
            className="absolute flex flex-col items-center"
            style={{
              left: pct(targetVal),
              transform: "translateX(-50%)",
              bottom: "calc(100% + 4px)",
            }}
          >
            <span className="text-[10px] font-bold text-[#00509d] whitespace-nowrap mb-1">
              Target: {targetVal}
            </span>
            <div
              className="w-0 h-0"
              style={{
                borderLeft: "5px solid transparent",
                borderRight: "5px solid transparent",
                borderTop: "8px solid #00509d",
              }}
            />
          </div>
        )}

        <div className="flex h-6 w-full rounded-full overflow-hidden">
          <div
            className="bg-red-100 shrink-0"
            style={{ width: pct(MIN_LULUS) }}
          />
          <div className="flex-1 bg-green-100" />
        </div>

        {hasScore && (
          <div
            className="absolute top-0 left-0 h-6 rounded-full transition-all duration-700"
            style={{ width: pct(scoreVal), backgroundColor: scoreColor, opacity: 0.65 }}
          />
        )}

        <div
          className="absolute top-0 h-6 w-0.5 bg-red-400"
          style={{ left: pct(MIN_LULUS) }}
        />
      </div>

      <div className="relative w-full mt-1.5 h-5">
        <span className="absolute left-0 text-[10px] text-slate-400">0</span>
        <span
          className="absolute text-[9px] text-red-400 font-medium whitespace-nowrap"
          style={{ left: pct(MIN_LULUS), transform: "translateX(-50%)" }}
        >
          {MIN_LULUS}
        </span>
        <span className="absolute right-0 text-[10px] text-slate-400">{MAX_SCORE}</span>
      </div>

      {/* ── Zone legend ── */}
      <div className="flex items-center justify-center gap-4 mt-2">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm bg-red-300 inline-block" />
          <span className="text-[10px] text-slate-500">Tidak Lulus (0–199)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm bg-green-400 inline-block" />
          <span className="text-[10px] text-slate-500">Lulus (200–361)</span>
        </div>
      </div>

      {/* ── Stats row ── */}
      <div className="flex mt-4 pt-3 border-t border-slate-100 divide-x divide-slate-100">
        <div className="flex-1 text-center">
          <p className="text-[10px] text-slate-400 uppercase tracking-wide">Skor</p>
          <p
            className={hasScore ? "text-xl font-bold mt-0.5" : "text-sm font-semibold mt-1"}
            style={{ color: hasScore ? scoreColor : "#94a3b8" }}
          >
            {hasScore ? scoreVal.toFixed(0) : "Belum dihitung"}
          </p>
        </div>
        <div className="flex-1 text-center">
          <p className="text-[10px] text-slate-400 uppercase tracking-wide">Target</p>
          <p className="text-xl font-bold text-[#00509d] mt-0.5">
            {targetVal > 0 ? targetVal.toFixed(0) : "—"}
          </p>
        </div>
        <div className="flex-1 text-center">
          <p className="text-[10px] text-slate-400 uppercase tracking-wide">Maks</p>
          <p className="text-xl font-bold text-slate-300 mt-0.5">{MAX_SCORE}</p>
        </div>
      </div>
    </div>
  );
};

export default GaugeMeter;
