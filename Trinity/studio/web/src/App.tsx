import { lazy, Suspense, useRef } from "react";
import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import HomePage from "./pages/HomePage";
import RunPage from "./pages/RunPage";
import UnitReviewPage from "./pages/UnitReviewPage";
import CreatorPage from "./pages/CreatorPage";
import CreatorRunPage from "./pages/CreatorRunPage";
import ImporterPage from "./pages/ImporterPage";
import TestEditPage from "./pages/TestEditPage";
const PersonasPage = lazy(() => import("./pages/PersonasPage"));
import ReviewerConfigsPage from "./pages/ReviewerConfigsPage";
import StatisticsPage from "./pages/StatisticsPage";
import WorkspacePage from "./pages/WorkspacePage";
import ThemeToggle from "./components/ThemeToggle";

function navClass(isActive: boolean) {
  return isActive ? "active" : "";
}

function AppNav() {
  const { pathname } = useLocation();
  const moreRef = useRef<HTMLDetailsElement>(null);
  const onWorkspace = pathname === "/" || pathname.startsWith("/workspace/");
  const onEarlierPage =
    pathname.startsWith("/creator") ||
    pathname.startsWith("/importer") ||
    pathname.startsWith("/reviewer-configs") ||
    pathname.startsWith("/runs/") ||
    pathname.startsWith("/units/") ||
    pathname.startsWith("/tests/");
  const closeMore = () => {
    if (moreRef.current) moreRef.current.open = false;
  };

  return (
    <nav className="app-nav" aria-label="Primary">
      <Link
        to="/"
        className={navClass(onWorkspace)}
        aria-current={onWorkspace ? "page" : undefined}
      >
        Workspace
      </Link>
      <NavLink to="/personas" className={({ isActive }) => navClass(isActive)}>
        Personas
      </NavLink>
      <NavLink to="/statistics" className={({ isActive }) => navClass(isActive)}>
        Statistics
      </NavLink>
      <details className="nav-more" ref={moreRef}>
        <summary className={navClass(onEarlierPage)}>More</summary>
        <div className="nav-more-menu" role="group" aria-label="Earlier Studio pages">
          <NavLink to="/" end onClick={closeMore}>
            Dashboard
          </NavLink>
          <NavLink to="/creator" onClick={closeMore}>
            Creator
          </NavLink>
          <NavLink to="/importer" onClick={closeMore}>
            Importer
          </NavLink>
          <NavLink to="/reviewer-configs" onClick={closeMore}>
            Reviewer configs
          </NavLink>
        </div>
      </details>
    </nav>
  );
}

export default function App() {
  return (
    <div className="layout">
      <header className="app-header">
        <div className="brand">
          <h1>Trinity Studio</h1>
          <p className="brand-tagline">Reviewer → Creator → Importer</p>
        </div>
        <AppNav />
        <ThemeToggle />
      </header>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/statistics" element={<StatisticsPage />} />
        <Route path="/workspace/:runId" element={<WorkspacePage />} />
        <Route path="/runs/:runId" element={<RunPage />} />
        <Route path="/units/:unitId" element={<UnitReviewPage />} />
        <Route
          path="/personas"
          element={
            <Suspense fallback={<p className="page-lead">Loading personas…</p>}>
              <PersonasPage />
            </Suspense>
          }
        />
        <Route path="/reviewer-configs" element={<ReviewerConfigsPage />} />
        <Route path="/creator" element={<CreatorPage />} />
        <Route path="/creator/:runId" element={<CreatorRunPage />} />
        <Route path="/importer" element={<ImporterPage />} />
        <Route path="/tests/:testId" element={<TestEditPage />} />
      </Routes>
    </div>
  );
}
