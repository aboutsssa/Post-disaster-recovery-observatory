// Nepal Gorkha 2015 land-cover workflow template.
// Candidate sources: ESA WorldCover or ESA CCI Land Cover.
// Output target: class-area transition table, not raw rasters.
// Status: documented template; values remain manual_required until run/reviewed.

var caseId = 'nepal-gorkha-2015';
var disasterYear = 2015;
var boundary = ee.FeatureCollection([]); // TODO: documented affected boundary asset.

// ESA WorldCover is available for limited epochs. For longer time series,
// use ESA CCI Land Cover and document the class crosswalk.
var worldCover = ee.ImageCollection('ESA/WorldCover/v200');

function classAreaTable(image) {
  var year = ee.Date(image.get('system:time_start')).get('year');
  var areaImage = ee.Image.pixelArea().divide(1e6).addBands(image.select('Map'));
  var grouped = areaImage.reduceRegion({
    reducer: ee.Reducer.sum().group({groupField: 1, groupName: 'lulc_class'}),
    geometry: boundary.geometry(),
    scale: 10,
    maxPixels: 1e13
  });
  var groups = ee.List(grouped.get('groups'));
  return ee.FeatureCollection(groups.map(function(item) {
    item = ee.Dictionary(item);
    return ee.Feature(null, {
      case_id: caseId,
      year: year,
      disaster_year: disasterYear,
      lulc_class: item.get('lulc_class'),
      area_km2: item.get('sum'),
      source: 'ESA WorldCover',
      unit: 'km2',
      processing_method: 'Pixel area summed by land-cover class inside affected boundary',
      data_quality: 'manual_review_required'
    });
  }));
}

var tables = worldCover.map(classAreaTable).flatten();

// Export.table.toDrive({
//   collection: tables,
//   description: 'nepal_gorkha_lulc_class_area',
//   fileFormat: 'CSV'
// });
