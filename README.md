# Post-disaster Recovery Observatory / 灾后恢复长期监测台

**ReSpace Lab: Recovery · Resilience · Reimagine**

Post-disaster Recovery Observatory is a reusable geospatial dashboard and research template for comparative long-term recovery analysis after major disaster events.

The project starts from a simple premise: recovery is not only the repair of damaged buildings. It is a long-term spatial, ecological, socioeconomic, demographic, social, and policy process that unfolds unevenly across regions and communities.

## Core Questions

- How do different disaster regions recover over years and decades?
- Which places show ecological recovery, economic rebound, population return, relocation, or long-term decline?
- How do reconstruction policies shape spatial outcomes?
- How can satellite data, statistics, settlement data, policy records, and social sensing be compared within one research structure?
- What can cross-case comparison reveal that single-event disaster pages cannot?

## First Case Studies

| Case | Country | Event date | Research role |
| --- | --- | --- | --- |
| Wenchuan 5·12 Earthquake / 中国汶川 5·12 地震 | China | 2008-05-12 | Mountain-region reconstruction, ecological disturbance, relocation, and policy-led rebuilding |
| Japan 3·11 Triple Disaster / 日本 3·11 复合灾害 | Japan | 2011-03-11 | Compound earthquake-tsunami-nuclear recovery, evacuation, coastal rebuilding, and governance |
| Nepal 2015 Gorkha Earthquake / 尼泊尔 2015 戈尔卡地震 | Nepal | 2015-04-25 | Himalayan settlement reconstruction, accessibility, livelihoods, and aid governance |

## Indicator System

Every case follows six analytical modules: Disaster Impact, Ecological Recovery, Economic Recovery, Population & Settlement, Social Sensing, and Policy & Reconstruction. The shared schema lives in `public/data/indicators.json`.

## Data Pipeline

The project does not fabricate values. Values are shown only when obtained from reliable public APIs or documented open datasets. Missing or unprocessed indicators are marked as `manual_required` or `not_available`.

```text
data_sources.yml
scripts/
├── fetch_usgs.py
├── fetch_reliefweb.py
├── fetch_worldbank.py
├── process_all.py
├── process_remote_sensing_ndvi.py
└── process_remote_sensing_lulc_ntl_settlement.py
public/data/
├── processed/
├── provenance/
├── indicators.json
└── cases/
```

## Nepal Pilot

The first data-driven pilot is `nepal-gorkha-2015`.

- USGS FDSN Event Web Service provides earthquake metadata.
- World Bank WDI API provides national socioeconomic context.
- ReliefWeb Reports API is integrated; if API access returns `403 Forbidden`, the pipeline records `not_available_api_forbidden` and does not fabricate report counts.
- Remote-sensing layers for NDVI/EVI, land cover, night-time lights, and settlement exposure are documented as `manual_required` until reproducible raster processing is completed.

Run the pipeline locally:

```bash
python scripts/fetch_usgs.py
python scripts/fetch_reliefweb.py
python scripts/fetch_worldbank.py
python scripts/process_all.py
```

The manual GitHub Actions workflow **Update data** runs the same scripts and commits only `public/data/processed/` and `public/data/provenance/`.

## Development

```bash
npm install
npm run dev
npm run build
```

## Deployment

GitHub Pages is configured for:

```text
https://aboutsssa.github.io/Post-disaster-recovery-observatory/
```

The deployment workflow is `.github/workflows/deploy.yml`.
