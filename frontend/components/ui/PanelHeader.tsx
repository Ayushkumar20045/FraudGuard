type PanelHeaderProps = {
  number: string;
  title: string;
  meta: string;
};

export default function PanelHeader({
  number,
  title,
  meta,
}: PanelHeaderProps) {
  return (
    <div className="panel-header">

      <div>

        <span className="section-number">
          {number}
        </span>

        <span className="section-name">
          {title}
        </span>

      </div>

      <span className="panel-meta">
        {meta}
      </span>

    </div>
  );
}