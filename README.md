# Post-disaster Recovery Observatory / 灾后恢复长期监测台

**ReSpace Lab: Recovery · Space · Resilience**

Post-disaster Recovery Observatory is a reusable geospatial dashboard and research template for comparative long-term recovery analysis after major disaster events. It is designed as a static Astro website for GitHub Pages under the repository name `recovery-observatory`.

The project starts from a simple premise: recovery is not only the repair of damaged buildings. It is a long-term spatial, ecological, socioeconomic, demographic, social, and policy process that unfolds unevenly across regions and communities.

## Core Questions

- How do different disaster regions recover over years and decades?
- Which places show ecological recovery, economic rebound, population return, relocation, or long-term decline?
- How do reconstruction policies shape spatial outcomes?
- How can satellite data, statistics, settlement data, policy records, and social sensing be compared within one research structure?
- What can cross-case comparison reveal that single-event disaster pages cannot?

## First Case Studies

The first version includes three reusable case templates:

| Case | Country | Event date | Research role |
| --- | --- | --- | --- |
| Wenchuan 5·12 Earthquake / 中国汶川 5·12 地震 | China | 2008-05-12 | Mountain-region reconstruction, ecological disturbance, relocation, and policy-led rebuilding |
| Japan 3·11 Triple Disaster / 日本 3·11 复合灾害 | Japan | 2011-03-11 | Compound earthquake-tsunami-nuclear recovery, evacuation, coastal rebuilding, and governance |
| Nepal 2015 Gorkha Earthquake / 尼泊尔 2015 戈尔卡地震 | Nepal | 2015-04-25 | Himalayan settlement reconstruction, accessibility, livelihoods, and aid governance |

## Indicator System

Every case follows the same six analytical modules:

1. **Disaster Impact / 灾害冲击**  
   Magnitude, affected area, building damage, population exposure, disaster boundary.

2. **Ecological Recovery / 生态恢复**  
   NDVI, EVI, NBR, LULC, ecosystem service value, land surface temperature.

3. **Economic Recovery / 经济恢复**  
   Night-time lights, GDP, industrial structure, investment, fiscal expenditure.

4. **Population & Settlement / 人口与居住**  
   Population change, urban-rural population, built-up area expansion, housing reconstruction, relocation, accessibility.

5. **Social Sensing / 社会感知**  
   Public emotions, topics, needs, risk perception, public attention, social media or textual data.

6. **Policy & Reconstruction / 政策与重建**  
   Reconstruction strategies, fiscal input, policy timeline, planning zones, governance mechanisms.

The shared schema lives in:

```text
public/data/indicators.json
```

## Data Structure

The MVP uses plain public files so the site can run without a backend, database, login system, or external API.

```text
public/data/
├── indicators.json
└── cases/
    ├── wenchuan-2008/
    │   ├── metadata.yml
    │   ├── disaster-impact.csv
    │   ├── ecological-recovery.csv
    │   ├── economic-recovery.csv
    │   ├── population-settlement.csv
    │   ├── social-sensing.csv
    │   └── policy-reconstruction.csv
    ├── japan-311-2011/
    │   └── same six-module structure
    └── nepal-gorkha-2015/
        └── same six-module structure
```

Each placeholder CSV uses this starting schema:

```csv
case_id,module,year,spatial_unit,indicator,value,unit,source,notes
```

Future datasets can add columns such as geometry IDs, administrative codes, confidence scores, URLs, processing methods, and temporal aggregation notes.

## Site Structure

- `src/pages/index.astro` - Home page and project framing
- `src/pages/cases.astro` - Three comparative case cards
- `src/pages/indicators.astro` - Six-module indicator system
- `src/pages/methods.astro` - Research workflow and analytical frame
- `src/pages/data.astro` - Data folder structure
- `src/pages/about.astro` - Project vision and ReSpace Lab framing

## Development

Install dependencies:

```bash
npm install
```

Start the local development server:

```bash
npm run dev
```

Build the static site:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## GitHub Pages Deployment

This project is configured for a GitHub Pages project site at:

```text
https://your-github-username.github.io/recovery-observatory/
```

Before publishing, update `site` in `astro.config.mjs`:

```js
site: "https://your-github-username.github.io",
base: "/recovery-observatory"
```

Then push the repository to GitHub and enable Pages with **GitHub Actions** as the source. The workflow in `.github/workflows/deploy.yml` will build Astro and publish the static output.

## Future Extensions

- Interactive maps for disaster boundaries, damage zones, relocation sites, and planning areas
- Time-series charts for recovery indicators
- GeoJSON and raster layer catalogues
- Client-side CSV and JSON loading
- Case-specific methods pages and source bibliographies
- Data provenance, uncertainty, and reproducibility notes

The first version is intentionally modest: a clean static-site MVP with a durable research structure. The observatory can now grow case by case, dataset by dataset.
