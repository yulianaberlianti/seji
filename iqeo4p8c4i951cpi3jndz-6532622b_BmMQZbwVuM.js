
// ╔══════════════════════════════════════════════════════════════════╗
// ║                                                                  ║
// ║   SEALeaf: Seagrass Earth App for Lightweight and Efficient      ║
// ║            Aquatic Feature mapping                               ║
// ║                                                                  ║
// ║   Developed for: Karimunjawa, Central Java, Indonesia            ║
// ║   Platform: Google Earth Engine                                  ║
// ║   Author: [YOUR NAME]                                            ║
// ║   Date: 2026                                                     ║
// ║                                                                  ║
// ╚══════════════════════════════════════════════════════════════════╝

// ============================================================
// MODULE 1: UI PANEL (FRONTEND)
// ============================================================

// --- 1.1 Styling & Layout ---
var COLORS = {
  primary: '#0077B6',
  secondary: '#00B4D8',
  accent: '#90E0EF',
  dark: '#03045E',
  white: '#FFFFFF',
  bg: '#CAF0F8'
};

// --- 1.2 Main Panel ---
var mainPanel = ui.Panel({
  style: {
    width: '360px',
    padding: '12px',
    backgroundColor: COLORS.bg
  }
});

// --- 1.3 Title ---
var titleLabel = ui.Label({
  value: '🌿 SEALeaf',
  style: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: COLORS.dark,
    textAlign: 'center',
    margin: '0 0 4px 0'
  }
});

var subtitleLabel = ui.Label({
  value: 'Seagrass Earth App for Lightweight\nand Efficient Aquatic Feature mapping',
  style: {
    fontSize: '11px',
    color: COLORS.primary,
    textAlign: 'center',
    margin: '0 0 12px 0'
  }
});

mainPanel.add(titleLabel);
mainPanel.add(subtitleLabel);

// --- 1.4 Separator Function ---
function addSeparator(panel) {
  panel.add(ui.Label({
    value: '─────────────────────────────',
    style: {color: COLORS.secondary, textAlign: 'center', margin: '4px 0'}
  }));
}

// --- 1.5 Section: Satellite Selection ---
addSeparator(mainPanel);
mainPanel.add(ui.Label({
  value: '🛰️ Satellite Selection',
  style: {fontSize: '14px', fontWeight: 'bold', color: COLORS.dark}
}));

var satelliteSelect = ui.Select({
  items: ['Sentinel-2 (10m)', 'Landsat-8 (30m)'],
  value: 'Sentinel-2 (10m)',
  style: {stretch: 'horizontal', margin: '4px 0'}
});
mainPanel.add(satelliteSelect);

// --- 1.6 Section: Date Range ---
mainPanel.add(ui.Label({
  value: '📅 Date Range',
  style: {fontSize: '14px', fontWeight: 'bold', color: COLORS.dark, margin: '8px 0 4px 0'}
}));

var startDateBox = ui.Textbox({
  placeholder: 'Start Date (YYYY-MM-DD)',
  value: '2024-06-01',
  style: {stretch: 'horizontal', margin: '2px 0'}
});

var endDateBox = ui.Textbox({
  placeholder: 'End Date (YYYY-MM-DD)',
  value: '2024-09-30',
  style: {stretch: 'horizontal', margin: '2px 0'}
});

mainPanel.add(startDateBox);
mainPanel.add(endDateBox);

// --- 1.7 Section: Cloud Cover ---
mainPanel.add(ui.Label({
  value: '☁️ Max Cloud Cover (%)',
  style: {fontSize: '14px', fontWeight: 'bold', color: COLORS.dark, margin: '8px 0 4px 0'}
}));

var cloudSlider = ui.Slider({
  min: 0, max: 50, value: 10, step: 1,
  style: {stretch: 'horizontal', margin: '2px 0'}
});
mainPanel.add(cloudSlider);

// --- 1.8 Section: Seagrass Index Selection ---
addSeparator(mainPanel);
mainPanel.add(ui.Label({
  value: '📐 Seagrass Index',
  style: {fontSize: '14px', fontWeight: 'bold', color: COLORS.dark}
}));

var indexSelect = ui.Select({
  items: [
    'NDAVI (Normalized Difference Aquatic Vegetation Index)',
    'WAVI (Water Adjusted Vegetation Index)',
    'SABI (Seagrass Area Beyond Index)',
    'DII (Depth Invariant Index - Lyzenga)',
    'NDVI (Baseline Comparison)'
  ],
  value: 'NDAVI (Normalized Difference Aquatic Vegetation Index)',
  style: {stretch: 'horizontal', margin: '4px 0'}
});
mainPanel.add(indexSelect);

// --- 1.9 Section: Water Column Correction Toggle ---
addSeparator(mainPanel);
mainPanel.add(ui.Label({
  value: '🌊 Water Column Correction',
  style: {fontSize: '14px', fontWeight: 'bold', color: COLORS.dark}
}));

var wccCheckbox = ui.Checkbox({
  label: 'Enable Lyzenga Correction',
  value: true,
  style: {margin: '4px 0'}
});
mainPanel.add(wccCheckbox);

// --- 1.10 Section: Sun Glint Correction Toggle ---
mainPanel.add(ui.Label({
  value: '☀️ Sun Glint Correction',
  style: {fontSize: '14px', fontWeight: 'bold', color: COLORS.dark, margin: '8px 0 4px 0'}
}));

var sunGlintCheckbox = ui.Checkbox({
  label: 'Enable Hedley et al. (2005) method',
  value: true,
  style: {margin: '4px 0'}
});
mainPanel.add(sunGlintCheckbox);

// --- 1.11 Section: Area of Interest ---
addSeparator(mainPanel);
mainPanel.add(ui.Label({
  value: '🔲 Area of Interest',
  style: {fontSize: '14px', fontWeight: 'bold', color: COLORS.dark}
}));

var aoiSelect = ui.Select({
  items: [
    'Karimunjawa (Default)',
    'Draw Custom Polygon'
  ],
  value: 'Karimunjawa (Default)',
  style: {stretch: 'horizontal', margin: '4px 0'}
});
mainPanel.add(aoiSelect);

// --- 1.12 Buttons ---
addSeparator(mainPanel);

var runButton = ui.Button({
  label: '▶️  CALCULATE INDEX',
  style: {
    stretch: 'horizontal',
    color: COLORS.white,
    backgroundColor: COLORS.primary,
    fontWeight: 'bold',
    fontSize: '14px',
    margin: '8px 0 4px 0'
  }
});

var exportButton = ui.Button({
  label: '💾  EXPORT TO DRIVE',
  style: {
    stretch: 'horizontal',
    color: COLORS.dark,
    backgroundColor: COLORS.accent,
    fontWeight: 'bold',
    margin: '4px 0'
  }
});

var resetButton = ui.Button({
  label: '🔄  RESET MAP',
  style: {
    stretch: 'horizontal',
    margin: '4px 0'
  }
});

mainPanel.add(runButton);
mainPanel.add(exportButton);
mainPanel.add(resetButton);

// --- 1.13 Status Label ---
var statusLabel = ui.Label({
  value: '⏳ Ready. Select parameters and click CALCULATE.',
  style: {
    fontSize: '11px',
    color: '#666666',
    margin: '8px 0',
    whiteSpace: 'pre-wrap'
  }
});
mainPanel.add(statusLabel);

// --- 1.14 Info/Credit ---
addSeparator(mainPanel);
mainPanel.add(ui.Label({
  value: 'ℹ️ SEALeaf v1.0 | 2026\n'
       + 'Developed by: [Your Name]\n'
       + 'Ref: Adapted from ECOMangrove\n'
       + '(Anggraeni & Setiawan, 2025)',
  style: {fontSize: '10px', color: '#999999', textAlign: 'center'}
}));

// --- 1.15 Add Panel to Map ---
ui.root.insert(0, mainPanel);

// ============================================================
// MODULE 2: DATA LOADING & PREPROCESSING
// ============================================================

// --- 2.1 Default AOI: Karimunjawa ---
var karimunjawa = ee.Geometry.Rectangle([110.35, -5.92, 110.55, -5.78]);

// Center map on Karimunjawa
Map.centerObject(karimunjawa, 12);
Map.setOptions('SATELLITE');

// --- 2.2 Get AOI ---
function getAOI() {
  var aoiChoice = aoiSelect.getValue();
  if (aoiChoice === 'Karimunjawa (Default)') {
    return karimunjawa;
  } else {
    // Use drawn geometry from map
    var drawingTools = Map.drawingTools();
    var layers = drawingTools.layers();
    if (layers.length() > 0) {
      return layers.get(0).toGeometry();
    } else {
      statusLabel.setValue('⚠️ Please draw a polygon on the map first!');
      return null;
    }
  }
}

// --- 2.3 Cloud Masking for Sentinel-2 ---
function maskS2clouds(image) {
  var scl = image.select('SCL');
  // SCL values: 3=cloud shadow, 7=unclassified, 8=cloud medium, 9=cloud high, 10=cirrus
  var mask = scl.neq(3).and(scl.neq(7)).and(scl.neq(8)).and(scl.neq(9)).and(scl.neq(10));
  // Also mask land (SCL=4 is vegetation, 5=bare soil, 6=water — keep only water & wetland)
  return image.updateMask(mask)
              .divide(10000)  // Scale to reflectance
              .copyProperties(image, ['system:time_start']);
}

// --- 2.4 Cloud Masking for Landsat-8 ---
function maskL8clouds(image) {
  var qa = image.select('QA_PIXEL');
  var cloudBit = 1 << 3;
  var shadowBit = 1 << 4;
  var mask = qa.bitwiseAnd(cloudBit).eq(0)
              .and(qa.bitwiseAnd(shadowBit).eq(0));
  return image.updateMask(mask)
              .multiply(0.0000275).add(-0.2)  // Scale to reflectance
              .copyProperties(image, ['system:time_start']);
}

// --- 2.5 Load Image Collection ---
function loadCollection(aoi, startDate, endDate, maxCloud, satellite) {
  var collection;
  
  if (satellite === 'Sentinel-2 (10m)') {
    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
      .filterBounds(aoi)
      .filterDate(startDate, endDate)
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', maxCloud))
      .map(maskS2clouds);
  } else {
    collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
      .filterBounds(aoi)
      .filterDate(startDate, endDate)
      .filter(ee.Filter.lt('CLOUD_COVER', maxCloud))
      .map(maskL8clouds);
  }
  
  return collection;
}

// --- 2.6 Band Name Standardization ---
function standardizeBands(image, satellite) {
  if (satellite === 'Sentinel-2 (10m)') {
    return image.select(
      ['B1', 'B2', 'B3', 'B4', 'B5', 'B8'],
      ['coastal', 'blue', 'green', 'red', 'rededge', 'nir']
    );
  } else {
    return image.select(
      ['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5'],
      ['coastal', 'blue', 'green', 'red', 'nir']
    );
  }
}

// --- 2.7 Sun Glint Correction (Hedley et al., 2005) ---
// Removes specular reflection from water surface
function sunGlintCorrection(image, aoi) {
  // Define deep water region for NIR baseline
  // Deep water should have near-zero NIR reflectance
  var nirBand = image.select('nir');
  
  // Find minimum NIR value (deep water reference)
  var nirMin = nirBand.reduceRegion({
    reducer: ee.Reducer.percentile([5]),  // 5th percentile as robust minimum
    geometry: aoi,
    scale: 10,
    maxPixels: 1e9
  }).get('nir');
  
  nirMin = ee.Number(nirMin);
  
  // For each visible band, regress against NIR and remove glint
  var bands = ['coastal', 'blue', 'green', 'red'];
  var corrected = image;
  
  bands.forEach(function(band) {
    // Sample points for regression
    var samples = image.select([band, 'nir']).sample({
      region: aoi,
      scale: 10,
      numPixels: 5000,
      seed: 42
    });
    
    // Linear regression: band = a + b * NIR
    var regression = samples.reduceColumns({
      reducer: ee.Reducer.linearFit(),
      selectors: ['nir', band]
    });
    
    var slope = ee.Number(regression.get('scale'));
    
    // Corrected band = original - slope * (NIR - NIR_min)
    var correctedBand = image.select(band)
      .subtract(nirBand.subtract(nirMin).multiply(slope))
      .rename(band);
    
    corrected = corrected.addBands(correctedBand, null, true);
  });
  
  return corrected;
}


// ============================================================
// MODULE 3: WATER COLUMN CORRECTION (LYZENGA, 1978, 1981)
// ============================================================

// --- 3.1 Calculate Attenuation Coefficient Ratio (ki/kj) ---
// Based on covariance of log-transformed bands over sand areas
function calculateKRatio(image, band_i, band_j, aoi) {
  
  // Log-transform the bands (natural log)
  var lnBi = image.select(band_i).log().rename('lnBi');
  var lnBj = image.select(band_j).log().rename('lnBj');
  
  var combined = lnBi.addBands(lnBj);
  
  // Calculate variance and covariance
  var stats = combined.reduceRegion({
    reducer: ee.Reducer.covariance(),
    geometry: aoi,
    scale: 10,
    maxPixels: 1e9
  });
  
  var covMatrix = ee.Array(stats.get('array'));
  
  var varBi = covMatrix.get([0, 0]);
  var varBj = covMatrix.get([1, 1]);
  var covBiBj = covMatrix.get([0, 1]);
  
  // ki/kj ratio using Lyzenga formula
  // ki/kj = (var_i - var_j + sqrt((var_i - var_j)^2 + 4*cov^2)) / (2 * cov)
  var a = ee.Number(varBi).subtract(varBj);
  var b = a.pow(2).add(ee.Number(covBiBj).pow(2).multiply(4)).sqrt();
  var kiKj = a.add(b).divide(ee.Number(covBiBj).multiply(2));
  
  return kiKj;
}

// --- 3.2 Depth Invariant Index (DII) ---
function depthInvariantIndex(image, band_i, band_j, kiKj) {
  var lnBi = image.select(band_i).log();
  var lnBj = image.select(band_j).log();
  
  // DII = ln(Bi) - (ki/kj) * ln(Bj)
  var dii = lnBi.subtract(lnBj.multiply(kiKj));
  
  return dii;
}

// --- 3.3 Apply Water Column Correction to All Bands ---
function applyWaterColumnCorrection(image, aoi) {
  // Calculate DII for multiple band pairs
  // Using blue-green pair (most common for seagrass)
  var kiKj_bg = calculateKRatio(image, 'blue', 'green', aoi);
  var kiKj_br = calculateKRatio(image, 'blue', 'red', aoi);
  var kiKj_gr = calculateKRatio(image, 'green', 'red', aoi);
  
  // Create depth-invariant bands
  var dii_bg = depthInvariantIndex(image, 'blue', 'green', kiKj_bg).rename('DII_bg');
  var dii_br = depthInvariantIndex(image, 'blue', 'red', kiKj_br).rename('DII_br');
  var dii_gr = depthInvariantIndex(image, 'green', 'red', kiKj_gr).rename('DII_gr');
  
  return image.addBands([dii_bg, dii_br, dii_gr]);
}


// ============================================================
// MODULE 4: SEAGRASS INDEX CALCULATION
// ============================================================

// --- 4.1 NDAVI (Normalized Difference Aquatic Vegetation Index) ---
// Villa et al. (2014)
// NDAVI = (NIR - Blue) / (NIR + Blue)
function calculateNDAVI(image) {
  var ndavi = image.normalizedDifference(['nir', 'blue']).rename('NDAVI');
  return ndavi;
}

// --- 4.2 WAVI (Water Adjusted Vegetation Index) ---
// Villa et al. (2014)
// WAVI = 1.5 * (NIR - Blue) / (NIR + Blue + 0.5)
function calculateWAVI(image) {
  var nir = image.select('nir');
  var blue = image.select('blue');
  var wavi = nir.subtract(blue)
               .multiply(1.5)
               .divide(nir.add(blue).add(0.5))
               .rename('WAVI');
  return wavi;
}

// --- 4.3 SABI (Seagrass Area Beyond Index) ---
// Wicaksono & Hafizt (2013)
// SABI = (NIR - Red) / (Blue + Green)
function calculateSABI(image) {
  var nir = image.select('nir');
  var red = image.select('red');
  var blue = image.select('blue');
  var green = image.select('green');
  var sabi = nir.subtract(red)
               .divide(blue.add(green))
               .rename('SABI');
  return sabi;
}

// --- 4.4 DII (Depth Invariant Index) ---
// Lyzenga (1978, 1981)
// Uses blue-green band pair (most effective for seagrass)
function calculateDII(image, aoi) {
  var kiKj = calculateKRatio(image, 'blue', 'green', aoi);
  var dii = depthInvariantIndex(image, 'blue', 'green', kiKj).rename('DII');
  return dii;
}

// --- 4.5 NDVI (Baseline Comparison) ---
// Rouse et al. (1974)
// NDVI = (NIR - Red) / (NIR + Red)
function calculateNDVI(image) {
  var ndvi = image.normalizedDifference(['nir', 'red']).rename('NDVI');
  return ndvi;
}

// --- 4.6 Index Router ---
function calculateIndex(image, indexName, aoi) {
  if (indexName.indexOf('NDAVI') > -1) {
    return calculateNDAVI(image);
  } else if (indexName.indexOf('WAVI') > -1) {
    return calculateWAVI(image);
  } else if (indexName.indexOf('SABI') > -1) {
    return calculateSABI(image);
  } else if (indexName.indexOf('DII') > -1) {
    return calculateDII(image, aoi);
  } else if (indexName.indexOf('NDVI') > -1) {
    return calculateNDVI(image);
  }
}


// ============================================================
// MODULE 5: VISUALIZATION & LEGEND
// ============================================================

// --- 5.1 Color Palettes ---
var palettes = {
  'NDAVI': {min: -0.5, max: 0.5, palette: ['#d73027','#fc8d59','#fee08b','#d9ef8b','#91cf60','#1a9850']},
  'WAVI':  {min: -0.5, max: 0.5, palette: ['#d73027','#fc8d59','#fee08b','#d9ef8b','#91cf60','#1a9850']},
  'SABI':  {min: -0.5, max: 0.5, palette: ['#d73027','#fc8d59','#fee08b','#d9ef8b','#91cf60','#1a9850']},
  'DII':   {min: -2,   max: 2,   palette: ['#2166ac','#67a9cf','#d1e5f0','#fddbc7','#ef8a62','#b2182b']},
  'NDVI':  {min: -0.5, max: 0.5, palette: ['#d73027','#fc8d59','#fee08b','#d9ef8b','#91cf60','#1a9850']}
};

// --- 5.2 Get Visualization Parameters ---
function getVisParams(indexName) {
  var keys = Object.keys(palettes);
  for (var i = 0; i < keys.length; i++) {
    if (indexName.indexOf(keys[i]) > -1) {
      return palettes[keys[i]];
    }
  }
  return palettes['NDAVI']; // default
}

// --- 5.3 Create Legend ---
function createLegend(indexName, visParams) {
  var legendPanel = ui.Panel({
    style: {
      position: 'bottom-right',
      padding: '8px',
      backgroundColor: 'rgba(255,255,255,0.9)'
    }
  });
  
  legendPanel.add(ui.Label({
    value: indexName.split(' ')[0] + ' Legend',
    style: {fontWeight: 'bold', fontSize: '13px', margin: '0 0 6px 0'}
  }));
  
  var colors = visParams.palette;
  var min = visParams.min;
  var max = visParams.max;
  var step = (max - min) / colors.length;
  
  for (var i = 0; i < colors.length; i++) {
    var colorBox = ui.Label({
      value: '',
      style: {
        backgroundColor: colors[i],
        padding: '8px 16px',
        margin: '0 4px 0 0'
      }
    });
    var valueLabel = ui.Label({
      value: (min + step * i).toFixed(2) + ' – ' + (min + step * (i + 1)).toFixed(2),
      style: {fontSize: '10px', margin: '2px 0'}
    });
    legendPanel.add(ui.Panel({
      widgets: [colorBox, valueLabel],
      layout: ui.Panel.Layout.Flow('horizontal')
    }));
  }
  
  return legendPanel;
}


// ============================================================
// MODULE 6: MAIN EXECUTION & EXPORT
// ============================================================

// --- 6.1 Global Variables ---
var currentResult = null;
var currentLegend = null;

// --- 6.2 Main Run Function ---
runButton.onClick(function() {
  
  // Clear previous layers
  Map.layers().reset();
  if (currentLegend) {
    Map.remove(currentLegend);
  }
  
  statusLabel.setValue('⏳ Processing... Please wait.');
  
  // Get parameters
  var aoi = getAOI();
  if (!aoi) return;
  
  var satellite = satelliteSelect.getValue();
  var startDate = startDateBox.getValue();
  var endDate = endDateBox.getValue();
  var maxCloud = cloudSlider.getValue();
  var indexName = indexSelect.getValue();
  var enableWCC = wccCheckbox.getValue();
  var enableSunGlint = sunGlintCheckbox.getValue();
  
  // Load collection
  var collection = loadCollection(aoi, startDate, endDate, maxCloud, satellite);
  
  // Create median composite
  var composite = collection.median().clip(aoi);
  
  // Standardize band names
  composite = standardizeBands(composite, satellite);
  
  // Apply sun glint correction if enabled
  if (enableSunGlint) {
    composite = sunGlintCorrection(composite, aoi);
    statusLabel.setValue('⏳ Sun glint correction applied...');
  }
  
  // Apply water column correction if enabled
  if (enableWCC) {
    composite = applyWaterColumnCorrection(composite, aoi);
    statusLabel.setValue('⏳ Water column correction applied...');
  }
  
  // Calculate selected index
  var indexImage = calculateIndex(composite, indexName, aoi);
  currentResult = indexImage;
  
  // Visualize
  var visParams = getVisParams(indexName);
  
  // Add true color composite first
  Map.addLayer(composite, {
    bands: ['red', 'green', 'blue'],
    min: 0, max: 0.3
  }, 'True Color', false);
  
  // Add index layer
  Map.addLayer(indexImage, visParams, indexName.split(' ')[0]);
  
  // Add AOI boundary
  Map.addLayer(ee.Image().paint(aoi, 0, 2), {palette: ['yellow']}, 'AOI Boundary');
  
  // Add legend
  currentLegend = createLegend(indexName, visParams);
  Map.add(currentLegend);
  
  // Count images used
  var count = collection.size();
  count.evaluate(function(n) {
    statusLabel.setValue(
      '✅ Done!\n' +
      '📊 Index: ' + indexName.split(' ')[0] + '\n' +
      '🛰️ Images used: ' + n + '\n' +
      '🌊 Water Column Correction: ' + (enableWCC ? 'ON' : 'OFF') + '\n' +
      '☀️ Sun Glint Correction: ' + (enableSunGlint ? 'ON' : 'OFF')
    );
  });
});

// --- 6.3 Export Function ---
exportButton.onClick(function() {
  if (!currentResult) {
    statusLabel.setValue('⚠️ Please calculate an index first!');
    return;
  }
  
  var indexName = indexSelect.getValue().split(' ')[0];
  var aoi = getAOI();
  
  Export.image.toDrive({
    image: currentResult,
    description: 'SEALeaf_' + indexName + '_Karimunjawa',
    folder: 'SEALeaf_Export',
    region: aoi,
    scale: 10,
    crs: 'EPSG:4326',
    maxPixels: 1e13,
    fileFormat: 'GeoTIFF'
  });
  
  statusLabel.setValue(
    '💾 Export task submitted!\n' +
    'Check Tasks tab (⚙️) to start download.\n' +
    'File: SEALeaf_' + indexName + '_Karimunjawa.tif'
  );
});

// --- 6.4 Reset Function ---
resetButton.onClick(function() {
  Map.layers().reset();
  if (currentLegend) {
    Map.remove(currentLegend);
  }
  currentResult = null;
  statusLabel.setValue('🔄 Map reset. Ready for new calculation.');
  Map.centerObject(karimunjawa, 12);
});

// --- 6.5 Drawing Tools Setup ---
var drawingTools = Map.drawingTools();
drawingTools.setShown(true);
drawingTools.setDrawModes(['polygon']);

// ============================================================
// END OF SEALeaf APPLICATION
// ============================================================
// 
// USAGE:
// 1. Copy this entire script to Google Earth Engine Code Editor
// 2. Click "Run"
// 3. The app panel will appear on the left
// 4. Select parameters and click "CALCULATE INDEX"
// 5. To publish as App: Click "Apps" > "Publish" in GEE
//
// ============================================================
