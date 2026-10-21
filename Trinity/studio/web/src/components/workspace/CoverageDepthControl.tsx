import type { CoverageProfile, CoverageProfileId } from "../../api";

type Props = {
  profiles: CoverageProfile[];
  value: CoverageProfileId;
  overrideCount: number;
  disabled: boolean;
  onChange: (profile: CoverageProfileId) => void;
};

export default function CoverageDepthControl({
  profiles,
  value,
  overrideCount,
  disabled,
  onChange,
}: Props) {
  const selected = profiles.find((profile) => profile.id === value) ?? profiles[2];
  if (!selected) return null;
  const position = String(selected.position);

  return (
    <section className="panel ws-depth" aria-labelledby="ws-depth-heading">
      <div className="ws-depth-head">
        <h3 id="ws-depth-heading">Coverage depth</h3>
        <p className="muted">
          {selected.summary} Target {selected.test_count_min}–{selected.test_count_max} journey tests.
        </p>
      </div>
      <input
        className="ws-depth-slider"
        type="range"
        min={0}
        max={Math.max(profiles.length - 1, 0)}
        step={1}
        value={position}
        disabled={disabled}
        aria-label="Coverage depth"
        aria-valuemin={0}
        aria-valuemax={profiles.length - 1}
        aria-valuenow={selected.position}
        aria-valuetext={`${selected.label}. ${selected.summary} ${selected.test_count_min} to ${selected.test_count_max} journey tests.`}
        onChange={(event) => {
          const next = profiles.find((profile) => profile.position === Number(event.target.value));
          if (next && next.id !== value) onChange(next.id);
        }}
      />
      <div className="ws-depth-scale">
        <span>Smoke tests</span>
        <span>Corner cases</span>
      </div>
      <div className="ws-depth-stops">
        {profiles.map((profile) => (
          <button
            key={profile.id}
            type="button"
            className={profile.id === value ? "ws-depth-stop is-active" : "ws-depth-stop"}
            disabled={disabled}
            onClick={() => {
              if (profile.id !== value) onChange(profile.id);
            }}
          >
            {profile.label}
            <span className="ws-depth-range">
              {profile.test_count_min}–{profile.test_count_max}
            </span>
          </button>
        ))}
      </div>
      {overrideCount > 0 && (
        <p className="muted">
          {overrideCount} {overrideCount === 1 ? "Epic uses" : "Epics use"} a different depth.
        </p>
      )}
    </section>
  );
}
