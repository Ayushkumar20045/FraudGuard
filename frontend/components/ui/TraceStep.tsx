type TraceStepProps = {
  number: string;
  title: string;
  value: string;
  final?: boolean;
};

export default function TraceStep({
  number,
  title,
  value,
  final = false,
}: TraceStepProps) {
  return (
    <div
      className={`trace-step ${
        final ? "trace-final" : ""
      }`}
    >

      <div className="trace-number">
        {number}
      </div>

      <div>

        <strong>
          {title}
        </strong>

        <span>
          {value}
        </span>

      </div>

    </div>
  );
}