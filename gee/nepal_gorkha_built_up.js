// Nepal Gorkha 2015 built-up area workflow template.
// Source: JRC Global Human Settlement Layer.
// Output target: built-up area by epoch inside affected boundary, not raw rasters.
// Status: documented template; values remain manual_required until run/reviewed.

var caseId = 'nepal-gorkha-2015';
var disasterYear = 2015;
var boundary = ee.FeatureCollection([]); // TODO: documented affected boundary asset.

// TODO: Select the GHSL collection/version available in your Earth Engine account.
// Example candidates may include JRC/GHSL/P2023A/GHS_BUILT_S.
var ghsl = ee.ImageCollection('JRC/GHSL/P2023A/GHS_BUILT_S');

var table = ghsl.map(function(image) {
  var year = ee.Number.parse(ee.String(image.get('system:index')).slice(0, 4));
  var built = image.gt(0);
  var area = built.multiply(ee.Image.pixelArea()).divide(1e6).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: boundary.geometry(),
    scale: 100,
    maxPixels: 1e13
  });
  return ee.Feature(null, {
    case_id: caseId,
    year: year,
    disaster_year: disasterYear,
    built_up_area_km2: area.values().get(0),
    source: 'JRC Global Human Settlement Layer',
    unit: 'km2',
    processing_method: 'Built-up mask area summed inside affected boundary by GHSL epoch',
    data_quality: 'manual_review_required'
  });
});

// Export.table.toDrive({
//   collection: table,
//   description: 'nepal_gorkha_built_up_area',
//   fileFormat: 'CSV'
// });
