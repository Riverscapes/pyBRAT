---
title: 1 - Input Data
---

### The dam-building beaver capacity model requires:

- A drainage network layer
- Hydrography data tied to that layer
- Vegetation type raster data
- Digital Elevation Model (DEM)
- Baseflow information throughout drainage network
- Highflow information throughout drainage network

Existing, readily and freely available GIS datasets from GIS data clearinghouses can be used as model inputs. For the Utah statewide run, we used:

* [NHD](http://nhd.usgs.gov/) for a *drainage network layer & hydrography data*
  * [National Hydrography Dataset](https://viewer.nationalmap.gov/basic/) (NHD) 

![national_map]({{ site.baseurl }}/assets/Images/national_map.PNG)

- [Landfire](http://www.landfire.gov/) for *Vegetation Type raster data*

- - Download both Us_140evt (existing vegetation type) and us_140bps (potential vegetation type)
  - us_130 can be used if 140 is not yet available for your study area

![landfire]({{ site.baseurl }}/assets/Images/landfire.PNG)

Note: The potential vegetation layer (biophysical settings (BpS)) represents the vegetation that may have been dominant on the landscape prior to Euro-American settlement and is based on both the current biophysical environment and an approximation of the historical disturbance regime. 

[USGS Digital Elevation (DEM) data](https://viewer.nationalmap.gov/basic/) for *Digital Elevation Model (DEM)*Download USGS NED  10 m DEM data

![national_map_dem]({{ site.baseurl }}/assets/Images/national_map_dem.PNG)

* [USGS StreamStats](http://streamstats.usgs.gov/) or [USGS National Streamflow Statistics](http://water.usgs.gov/osw/programs/nss/pubs.html) for: 
  * *Baseflow regional regression equations (e.g. PQ80 for month with lowest flows)*
  * *Highflow regional regression equations (e.g. Q2 - 2 year recurrence interval peak flow)* 

The **potential conflict inference system** requires the following layers:Roads Railroads Canals (can be extracted from NHD Flowline layer using FCODEs 33600, 33601, and 33603)Land use raster (can use landfire EVT layer for this)

For the Utah statewide run, we obtained some of this data from the [Utah AGRC Mapping Portal](http://gis.utah.gov/).

Note: These data or similar data must be captured before proceeding on to Step 2.

[Continue to Step 2]({{ site.baseurl }}/Documentation/pyBRAT/2-Preprocessing) ->