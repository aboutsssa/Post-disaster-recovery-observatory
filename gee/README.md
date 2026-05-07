# Google Earth Engine Processing Scripts

These scripts document reproducible remote-sensing workflows for the Nepal 2015 Gorkha earthquake pilot. They are intended to be copied into the Google Earth Engine Code Editor or adapted for the Earth Engine Python API.

They do **not** fabricate outputs and they do **not** belong in `public/data/processed/` until:

1. An affected-area boundary is selected and cited.
2. Cloud/quality masks and scale factors are applied.
3. Zonal statistics are reviewed.
4. Exported CSV tables include source, unit, processing method, and data quality.

Do not commit raw raster exports. Commit only small chart-ready CSV/JSON summaries and provenance notes.
