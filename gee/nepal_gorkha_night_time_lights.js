// Nepal Gorkha 2015 night-time lights workflow template.
// Candidate source: NOAA VIIRS DNB monthly composites or NASA Black Marble.
// Output target: annual radiance statistics inside affected boundary, not raw rasters.
// Status: documented template; values remain manual_required until run/reviewed.

var caseId = 'nepal-gorkha-2015';
var disasterYear = 2015;
var boundary = ee.FeatureCollection([]); // TODO: documented affected boundary asset.

var viirs = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
  .filterDate('2012-01-01', '2023-12-31')
  .filterBounds(boundary)
  .select('avg_rad');

var years = ee.List.sequence(2012, 2023);

var annual = ee.FeatureCollection(years.map(function(year) {
  year = ee.Number(year);
  var start = ee.Date.fromYMD(year, 1, 1);
  var end = start.advance(1, 'year');
  var image = viirs.filterDate(start, end).mean();
  var stats = image.reduceRegion({
    reducer: ee.Reducer.mean().combine({
      reducer2: ee.Reducer.median(),
      sharedInputs: true
    }),
    geometry: boundary.geometry(),
    scale: 500,
    maxPixels: 1e13
  });
  return ee.Feature(null, {
    case_id: caseId,
    year: year,
    disaster_year: disasterYear,
    mean_radiance: stats.get('avg_rad_mean'),
    median_radiance: stats.get('avg_rad_median'),
    source: 'NOAA VIIRS DNB monthly VCMSLCFG',
    unit: 'nW/cm2/sr',
    processing_method: 'Monthly cloud-free avg_rad annual mean, zonal mean and median inside affected boundary',
    data_quality: 'manual_review_required'
  });
}));

// Export.table.toDrive({
//   collection: annual,
//   description: 'nepal_gorkha_viirs_night_lights',
//   fileFormat: 'CSV'
// });
