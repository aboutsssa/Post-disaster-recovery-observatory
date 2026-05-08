export const caseStudies = [
  {
    id: "wenchuan-2008",
    name: "Wenchuan 5.12 Earthquake",
    year: "2008",
    country: "China",
    eventDate: "May 12, 2008",
    hazards: ["Earthquake", "landslides", "mountain settlement disruption"],
    researchFocus: "County-level long-term recovery panel for economy, ecology, population, settlement, public finance, and reconstruction investment.",
    folder: "public/data/cases/wenchuan-2008/",
    href: "/cases/wenchuan-2008/",
    status: "Panel data integrated",
    marker: { x: 43, y: 48 },
    event: {
      title: "M 7.9 - Wenchuan earthquake",
      magnitude: 7.9,
      magnitudeType: "Mw",
      depthKm: 19,
      latitude: 31.002,
      longitude: 103.322,
      source: "USGS Earthquake Hazards Program",
      sourceUrl: "https://earthquake.usgs.gov/earthquakes/eventpage/usp000g650"
    }
  },
  {
    id: "japan-311-2011",
    name: "Japan 3.11 Triple Disaster",
    year: "2011",
    country: "Japan",
    eventDate: "March 11, 2011",
    hazards: ["Earthquake", "tsunami", "nuclear accident"],
    researchFocus: "Compound-disaster recovery case for coastal rebuilding, evacuation, demographic change, and governance.",
    folder: "public/data/cases/japan-311-2011/",
    href: "/cases/japan-311-2011/",
    status: "Template scaffold",
    marker: { x: 69, y: 38 },
    event: {
      title: "M 9.1 - Great Tohoku earthquake",
      magnitude: 9.1,
      magnitudeType: "Mw",
      depthKm: 29,
      latitude: 38.297,
      longitude: 142.373,
      source: "USGS Earthquake Hazards Program",
      sourceUrl: "https://earthquake.usgs.gov/earthquakes/eventpage/official20110311054624120_30"
    }
  },
  {
    id: "nepal-gorkha-2015",
    name: "Nepal 2015 Gorkha Earthquake",
    year: "2015",
    country: "Nepal",
    eventDate: "April 25, 2015",
    hazards: ["Earthquake", "landslides", "rural housing damage"],
    researchFocus: "Himalayan recovery case for settlement reconstruction, accessibility, livelihoods, and aid governance.",
    folder: "public/data/cases/nepal-gorkha-2015/",
    href: "/cases/nepal-gorkha-2015/",
    status: "Template scaffold",
    marker: { x: 52, y: 53 },
    event: {
      title: "M 7.8 - Gorkha earthquake",
      magnitude: 7.8,
      magnitudeType: "Mw",
      depthKm: 8.22,
      latitude: 28.2305,
      longitude: 84.7314,
      source: "USGS Earthquake Hazards Program",
      sourceUrl: "https://earthquake.usgs.gov/earthquakes/eventpage/us20002926"
    }
  }
];

export const observatoryPrinciples = [
  "Each case gets its own long-form observatory page.",
  "The atlas is an entry point; analytical maps belong inside case pages.",
  "Modules are displayed as charts, notes, and evidence gaps rather than as six static boxes."
];
