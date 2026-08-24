type SnapshotRowProps = {
  label: string;
  value: string;
  status?: boolean;
};

export default function SnapshotRow({
  label,
  value,
  status = false,
}: SnapshotRowProps) {
  return (
    <div className="snapshot-row">

      <span className="data-label">
        {label}
      </span>

      <span className={status ? "status-value" : ""}>
        {value}
      </span>

    </div>
  );
}