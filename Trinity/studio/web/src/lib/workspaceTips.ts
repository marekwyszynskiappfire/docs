import type { WorkspaceSummary } from "../api";

export type WorkspaceTip = {
  id: string;
  version: number;
  text: string;
};

const STORAGE_KEY = "trinity.workspace.tips";

const TIPS: { tip: WorkspaceTip; applies: (w: WorkspaceSummary) => boolean }[] = [
  {
    tip: {
      id: "workspace-intro",
      version: 1,
      text: "This page covers the whole process. The card at the top always shows the one thing to do next.",
    },
    applies: () => true,
  },
  {
    tip: {
      id: "coverage-depth",
      version: 1,
      text: "Coverage depth sets how broad the Creator prompt is. Smoke stays on the critical happy paths. Edge adds evidence-backed corner cases.",
    },
    applies: (w) => w.epics.some((e) => e.stage === "draft" || e.stage === "review"),
  },
  {
    tip: {
      id: "cursor-handoff",
      version: 1,
      text: "After you paste the prompt into Cursor you can stay here. Studio checks for the suite file every few seconds and imports it.",
    },
    applies: (w) => w.epics.some((e) => e.creator_handoff?.status === "awaiting_cursor"),
  },
  {
    tip: {
      id: "first-tests",
      version: 1,
      text: "Open a test to read its steps. Only approved tests can be sent to Xray.",
    },
    applies: (w) => w.epics.some((e) => e.tests.total > 0),
  },
  {
    tip: {
      id: "import-plan",
      version: 1,
      text: "The Importer never writes to Xray without a dry-run plan and your confirmation.",
    },
    applies: (w) => w.next_action.current_stage === "import",
  },
];

type Dismissed = Record<string, { version: number; dismissed_at: string }>;

function readDismissed(): Dismissed {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Dismissed) : {};
  } catch {
    return {};
  }
}

export function activeTip(workspace: WorkspaceSummary): WorkspaceTip | null {
  const dismissed = readDismissed();
  for (const { tip, applies } of TIPS) {
    const seen = dismissed[tip.id];
    if (seen && seen.version >= tip.version) continue;
    if (applies(workspace)) return tip;
  }
  return null;
}

export function dismissTip(tip: WorkspaceTip): void {
  const dismissed = readDismissed();
  dismissed[tip.id] = { version: tip.version, dismissed_at: new Date().toISOString() };
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(dismissed));
}

export function resetTips(): void {
  window.localStorage.removeItem(STORAGE_KEY);
}
