import { Link } from "react-router-dom";

type Props = {
  kind: "new" | "updated";
  title: string;
  detail: string;
  linkTo?: string;
  linkLabel?: string;
  onDismiss?: () => void;
};

export default function ImportFeedback({
  kind,
  title,
  detail,
  linkTo,
  linkLabel,
  onDismiss,
}: Props) {
  return (
    <div
      className={`import-feedback import-feedback--${kind}`}
      role="status"
      aria-live="polite"
    >
      <div className="import-feedback-body">
        <strong>{title}</strong>
        <p className="muted import-feedback-detail">{detail}</p>
        {linkTo && linkLabel && (
          <p>
            <Link to={linkTo}>{linkLabel}</Link>
          </p>
        )}
      </div>
      {onDismiss && (
        <button type="button" className="secondary import-feedback-dismiss" onClick={onDismiss}>
          Dismiss
        </button>
      )}
    </div>
  );
}
