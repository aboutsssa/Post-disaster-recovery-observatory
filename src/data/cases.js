export const caseStudies = [
  {
    id: "wenchuan-2008",
    name: "Wenchuan 5.12 Earthquake",
    nameZh: "中国汶川 5.12 地震",
    year: "2008",
    country: "China",
    eventDate: "May 12, 2008",
    hazards: ["Earthquake", "landslides", "mountain settlement disruption"],
    researchFocus: "Mountain-region reconstruction, ecological disturbance, relocation, and policy-led rebuilding.",
    folder: "public/data/cases/wenchuan-2008/",
    boundaryStatus: "Pilot affected-area boundary for the Longmenshan recovery corridor. Replace with official GIS layers before quantitative analysis.",
    adminScale: "County and city reference units",
    event: {
      title: "M 7.9 - 58 km W of Tianpeng, China",
      magnitude: 7.9,
      magnitudeType: "mwc",
      depthKm: 19,
      latitude: 31.002,
      longitude: 103.322,
      source: "USGS Earthquake Hazards Program",
      sourceUrl: "https://earthquake.usgs.gov/earthquakes/eventpage/usp000g650"
    },
    affectedBoundary: [[32.35, 102.55], [32.2, 104.35], [31.45, 105.05], [30.55, 104.35], [30.45, 103.25], [31.15, 102.35], [32.35, 102.55]],
    adminUnits: [
      { name: "Wenchuan County", boundary: [[31.75, 102.75], [31.75, 103.55], [31.18, 103.62], [31.08, 102.85], [31.75, 102.75]] },
      { name: "Beichuan County", boundary: [[32.05, 104.05], [32.02, 104.85], [31.45, 104.92], [31.42, 104.18], [32.05, 104.05]] },
      { name: "Dujiangyan and Chengdu edge", boundary: [[31.12, 103.35], [31.12, 104.15], [30.55, 104.18], [30.52, 103.45], [31.12, 103.35]] }
    ]
  },
  {
    id: "japan-311-2011",
    name: "Japan 3.11 Triple Disaster",
    nameZh: "日本 3.11 复合灾害",
    year: "2011",
    country: "Japan",
    eventDate: "March 11, 2011",
    hazards: ["Earthquake", "tsunami", "nuclear accident"],
    researchFocus: "Coastal recovery, evacuation zones, demographic change, economic disruption, and multi-hazard governance.",
    folder: "public/data/cases/japan-311-2011/",
    boundaryStatus: "Pilot coastal affected-area boundary for the Tohoku recovery corridor. Replace with official inundation and evacuation-zone GIS layers.",
    adminScale: "Prefecture reference units",
    event: {
      title: "M 9.1 - 2011 Great Tohoku Earthquake, Japan",
      magnitude: 9.1,
      magnitudeType: "mww",
      depthKm: 29,
      latitude: 38.297,
      longitude: 142.373,
      source: "USGS Earthquake Hazards Program",
      sourceUrl: "https://earthquake.usgs.gov/earthquakes/eventpage/official20110311054624120_30"
    },
    affectedBoundary: [[40.3, 141.1], [40.25, 142.15], [39.1, 142.45], [37.25, 141.85], [36.65, 140.95], [37.35, 140.25], [39.2, 140.75], [40.3, 141.1]],
    adminUnits: [
      { name: "Iwate Prefecture coast", boundary: [[40.35, 141.2], [40.1, 142.0], [39.1, 142.15], [39.05, 141.15], [40.35, 141.2]] },
      { name: "Miyagi Prefecture coast", boundary: [[39.05, 141.1], [38.95, 142.0], [37.85, 141.75], [37.8, 140.75], [39.05, 141.1]] },
      { name: "Fukushima Prefecture coast", boundary: [[37.85, 140.7], [37.8, 141.55], [36.9, 141.25], [36.85, 140.35], [37.85, 140.7]] }
    ]
  },
  {
    id: "nepal-gorkha-2015",
    name: "Nepal 2015 Gorkha Earthquake",
    nameZh: "尼泊尔 2015 戈尔卡地震",
    year: "2015",
    country: "Nepal",
    eventDate: "April 25, 2015",
    hazards: ["Earthquake", "landslides", "rural housing damage"],
    researchFocus: "Himalayan settlement reconstruction, accessibility, livelihood recovery, and aid governance.",
    folder: "public/data/cases/nepal-gorkha-2015/",
    boundaryStatus: "Pilot affected Himalayan districts boundary. Replace with verified district polygons and landslide/housing-damage layers.",
    adminScale: "District and valley reference units",
    event: {
      title: "M 7.8 - 67 km NNE of Bharatpur, Nepal",
      magnitude: 7.8,
      magnitudeType: "mww",
      depthKm: 8.22,
      latitude: 28.2305,
      longitude: 84.7314,
      source: "USGS Earthquake Hazards Program",
      sourceUrl: "https://earthquake.usgs.gov/earthquakes/eventpage/us20002926"
    },
    affectedBoundary: [[29.05, 83.35], [29.15, 86.1], [28.55, 86.45], [27.45, 85.65], [27.2, 84.0], [27.85, 83.25], [29.05, 83.35]],
    adminUnits: [
      { name: "Gorkha District", boundary: [[28.55, 84.35], [28.65, 85.05], [28.0, 85.15], [27.85, 84.45], [28.55, 84.35]] },
      { name: "Dhading and Nuwakot", boundary: [[28.25, 84.85], [28.35, 85.65], [27.75, 85.7], [27.55, 84.95], [28.25, 84.85]] },
      { name: "Kathmandu Valley", boundary: [[27.95, 85.15], [27.98, 85.65], [27.48, 85.7], [27.45, 85.18], [27.95, 85.15]] }
    ]
  }
];

export const observatoryPrinciples = [
  "Affected-area first: charts and maps should be aggregated by disaster boundary, affected administrative unit, or recovery zone.",
  "National values are excluded from the public dashboard unless they are explicitly labeled as background context in a separate research appendix.",
  "Every case keeps the same module structure so new disasters can be added without redesigning the site."
];
