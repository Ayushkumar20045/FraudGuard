type VerdictStatProps = {
  label: string;
  value: string;
};

export default function VerdictStat({
  label,
  value,
}: VerdictStatProps) {
  return (
    <div className="verdict-stat">

      <span className="data-label">
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}