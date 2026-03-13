const ProgressBar = ({ value }: { value: number }) => (
  <div className="flex items-center gap-3 flex-1">
    <div className="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
      <div
        className="h-full bg-blue-500 rounded-full transition-all duration-500"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
    <span className="text-sm font-semibold text-gray-700 w-10 text-right">
      {value}%
    </span>
  </div>
);

export default ProgressBar;
