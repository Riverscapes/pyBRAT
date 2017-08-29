---
title: Input Data
---

### 1. Input Data

 The ungulate utilization model requires:

- A drainage network layer 
- A water body and springs layer
- Digital Elevation Model (DEM)
- Vegetation type (by species) raster data

Existing, readily and freely available GIS datasets from GIS data clearinghouses can be used as model inputs. For the pilot study ungulate utilization model, we used:

* [NHD+](http://www.horizon-systems.com/nhdplus/) for a *drainage network layer & hydrography data*
  * National Hydrography Dataset (NHD) Plus
  * Both stream and water body data
* [Landfire](http://www.landfire.gov/) for *Vegetation Type raster data*
  * Us_110evt (existing vegetation type) 
* [USGS Digital Elevation (DEM) data](http://ned.usgs.gov/)*for Digital Elevation Model (DEM)*
* USGS NED  10 m DEM data

These data were processed to generate the following raster datasets:

1. Euclidean distance to Water (NHD streams and water bodies), 
2. Forage preference (LANDFIRE landcover data), 
3. Percent slope map (based on USGS 10-m DEM)

Ahead to [2. Vegetation Input Derivation]({{ site.baseurl}}/Documentation/Ungulate/2-VegetationInput) →