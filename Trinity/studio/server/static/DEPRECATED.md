# Legacy static Studio UI (deprecated)

This folder served the pre-React Studio shell (`index.html`, `unit-review.js`).

**Default:** When `Trinity/studio/web/dist` exists, `app.py` serves the Vite build on port **8765**.

**Fallback:** Set `QA_STUDIO_LEGACY_STATIC=1` to force this folder, or omit `web/dist` after `npm run build`.

Development: `npm run dev` on **5173** with API proxy to **8765**.
