import { NavLink, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import RunPage from "./pages/RunPage";
import UnitReviewPage from "./pages/UnitReviewPage";
import CreatorPage from "./pages/CreatorPage";
import CreatorRunPage from "./pages/CreatorRunPage";
import TestEditPage from "./pages/TestEditPage";
import PersonasPage from "./pages/PersonasPage";
import ReviewerConfigsPage from "./pages/ReviewerConfigsPage";

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
          <NavLink to="/personas" className={({ isActive }) => (isActive ? "active" : "")}>
            Personas
          </NavLink>
          <NavLink to="/reviewer-configs" className={({ isActive }) => (isActive ? "active" : "")}>
            Reviewer configs
          </NavLink>
        </nav>
      </header>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/runs/:runId" element={<RunPage />} />
        <Route path="/units/:unitId" element={<UnitReviewPage />} />
        <Route path="/personas" element={<PersonasPage />} />
        <Route path="/reviewer-configs" element={<ReviewerConfigsPage />} />
        <Route path="/creator" element={<CreatorPage />} />
        <Route path="/creator/:runId" element={<CreatorRunPage />} />
        <Route path="/tests/:testId" element={<TestEditPage />} />
      </Routes>
    </div>
  );
}
