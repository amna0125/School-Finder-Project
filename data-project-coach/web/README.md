
# Stockholm School Finder (website)

A React + TypeScript site that reads the project's dbt gold tables as Parquet files and
queries them **in the browser** with DuckDB-WASM. There is no backend: filtering and scoring
are SQL queries, and the "How this is calculated" panel shows the exact query that ran.

```
Skolverket APIs ──dlt / Prefect──▶ .state/schools.duckdb
                                        │  (attached read-only)
                                        ▼
                         dbt: bronze ▶ silver ▶ gold  (+ 40 data tests)
                                        │  gold = materialized: external, format: parquet
                                        ▼
                               web/public/data/*.parquet + lineage.json
                                        │
                                        ▼
                     browser: DuckDB-WASM ◀── SQL ── React (map, chart, pages)
```

## Run it locally

You need Node.js 20 or newer (https://nodejs.org) and the project's Python venv with dbt-duckdb.

1. Build the data (from the project root):

   ```
   cd dbt
   dbt build --profiles-dir .
   python scripts/export_lineage.py
   ```

   This writes the Parquet files and `lineage.json` into `web/public/data/`.

2. Start the site:

   ```
   cd web
   npm install
   npm run dev
   ```

   Open http://localhost:5173.

3. For a production build: `npm run build`, then `npm run preview`. The `dist/` folder is a
   static site that can be hosted anywhere (GitHub Pages, Netlify, Cloudflare Pages).

## Where things are

| Path | What it does |
|---|---|
| `src/lib/db.ts` | Starts DuckDB-WASM, registers the Parquet files as views, builds one record per school. |
| `src/lib/scoring.ts` | Turns the parent's answers into one SQL query (`buildScoreSQL`) and explains each verdict. |
| `src/lib/store.tsx` | App state (answers, home, compare list) and re-scoring when anything changes. |
| `src/components/MapPanel.tsx` | MapLibre with free OpenFreeMap tiles, school dots drawn on a canvas above it. |
| `src/components/ChartPanel.tsx` | Teachers vs national tests scatter. |
| `src/pages/` | Find, School, Compare and Data pipeline pages. |

## Notes

- Map tiles come from OpenFreeMap (OpenStreetMap data); they need an internet connection. Everything else works offline.
- A school's approach is what it says on its own website, not verified practice.
- Schools are compared with the county median, never ranked.
