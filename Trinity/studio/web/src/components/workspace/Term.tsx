import { useEffect, useId, useRef, useState } from "react";

export const TERMS: Record<string, string> = {
  testability:
    "Whether QA can design tests from what the Epic says today: testable now, testable with clarifications, or not testable yet.",
  handoff:
    "Work Studio asked Cursor to do. Studio saves the prompt and watches for the file Cursor writes.",
  blocker:
    "A High-priority open question. Its answer changes what the tests must check.",
  dryrun:
    "A preview of what the Importer would create in Xray. Nothing is written until you confirm.",
};

export default function Term({ id, children }: { id: keyof typeof TERMS; children: string }) {
  const [open, setOpen] = useState(false);
  const tipId = useId();
  const wrapper = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    const onPointer = (event: PointerEvent) => {
      if (!wrapper.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onPointer);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onPointer);
    };
  }, [open]);

  return (
    <span
      className="term"
      ref={wrapper}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        type="button"
        className="term-trigger"
        aria-describedby={open ? tipId : undefined}
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
      >
        {children}
      </button>
      {open && (
        <span role="tooltip" id={tipId} className="term-tooltip">
          {TERMS[id]}
        </span>
      )}
    </span>
  );
}
