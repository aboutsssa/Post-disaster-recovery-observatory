// Nepal Gorkha 2015 earthquake NDVI/EVI workflow template.
// Source: NASA LP DAAC MODIS MOD13Q1 v061 vegetation indices.
// Output target: annual or seasonal zonal statistics CSV, not raw rasters.
// Status: documented template; values remain manual_required until run/reviewed.

var caseId = 'nepal-gorkha-2015';
var disasterYear = 2015;

// TODO: Replace with a documented affected-area boundary asset.
// Example: var boundary = ee.FeatureCollection('users/YOUR_ACCOUNT/nepal_gorkha_affected_boundary');
var boundary = ee.FeatureCollection([]);

function maskSummaryQA(image) {
  // MOD13Q1 SummaryQA: 0 = good data, 1 = marginal data.
  var qa = image.select('SummaryQA');
  return image.updateMask(qa.lte(1));
}

function scaleVI(image) {
  return image
    .select(['NDVI', 'EVI'])
    .multiply(0.0001)
    .copyProperties(image, ['system:time_start']);
}

var collection = ee.ImageCollection('MODIS/061/MOD13Q1')
  .filterDate('2001-01-01', '2023-12-31')
  .filterBounds(boundary)
  .map(maskSummaryQA)
  .map(scaleVI);

var years = ee.List.sequence(2001, 2023);

var annual = ee.FeatureCollection(years.map(function(year) {
  year = ee.Number(year);
  var start = ee.Date.fromYMD(year, 1, 1);
  var end = start.advance(1, 'year');
  var annualMean = collection.filterDate(start, end).mean();
  var stats = annualMean.reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: boundary.geometry(),
    scale: 250,
    maxPixels: 1e13
  });
  return ee.Feature(null, {
    case_id: caseId,
    year: year,
    disaster_year: disasterYear,
    ndvi: stats.get('NDVI'),
    evi: stats.get('EVI'),
    source: 'NASA LP DAAC MODIS MOD13Q1 v061',
    unit: 'index',
    processing_method: 'MOD13Q1 SummaryQA <= 1, scaled by 0.0001, annual mean over affected boundary',
    data_quality: 'manual_review_required'
  });
}));

// Export.table.toDrive({
//   collection: annual,
//   description: 'nepal_gorkha_ndvi_evi_annual',
//   fileFormat: 'CSV'
// });
