import { NavLink, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import RunPage from "./pages/RunPage";
import UnitReviewPage from "./pages/UnitReviewPage";
import CreatorPage from "./pages/CreatorPage";
import CreatorRunPage from "./pages/CreatorRunPage";
import ImporterPage from "./pages/ImporterPage";
import TestEditPage from "./pages/TestEditPage";
import PersonasPage from "./pages/PersonasPage";
import ReviewerConfigsPage from "./pages/ReviewerConfigsPage";
import ThemeToggle from "./components/ThemeToggle";

export default function App() {
  return (
    <div className="layout">
      <header className="app-header">
        <h1>Trinity Studio</h1>
        <nav>
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
            Dashboard
          </NavLink>
          <NavLink to="/creator" className={({ isActive }) => (isActive ? "active" : "")}>
            Creator
          </NavLink>
          <NavLink to="/importer" className={({ isActive }) => (isActive ? "active" : "")}>
            Importer
          </NavLink>
          <NavLink to="/personas" className={({ isActive }) => (isActive ? "active" : "")}>
            Personas
          </NavLink>
          <NavLink to="/reviewer-configs" className={({ isActive }) => (isActive ? "active" : "")}>
            Reviewer configs
          </NavLink>
        </nav>
        <ThemeToggle />
      </header>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/runs/:runId" element={<RunPage />} />
        <Route path="/units/:unitId" element={<UnitReviewPage />} />
        <Route path="/personas" element={<PersonasPage />} />
        <Route path="/reviewer-configs" element={<ReviewerConfigsPage />} />
        <Route path="/creator" element={<CreatorPage />} />
        <Route path="/creator/:runId" element={<CreatorRunPage />} />
        <Route path="/importer" element={<ImporterPage />} />
        <Route path="/tests/:testId" element={<TestEditPage />} />
      </Routes>
    </div>
  );
}
