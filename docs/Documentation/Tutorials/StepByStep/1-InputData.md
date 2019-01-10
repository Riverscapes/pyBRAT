---
title: Step 1 - Input Data
weight: 1
---

## Capacity Model Inputs

The requisite inputs to the capacity model include:
- A drainage network layer and associated hydrography
- Vegetation type raster data
- Digital Elevation Model (DEM)
- Streamflow (baseflow and peak flow) information throughout drainage network

Existing, readily and freely available datasets from GIS data clearinghouses can be used as model inputs.  Just make sure all input data are projected in the same coordinate system prior to running the BRAT model.

### Drainage Network

We use the National Hydrograph Dataset [(NHD)](https://viewer.nationalmap.gov/basic/) for the drainage network and associated hydrography data.  The NHD layers required to run BRAT include the stream flowline, waterbody and area feature classes.

![national_map]({{ site.baseurl }}/assets/images/national_map.PNG)

### Vegetation Raster

You will need 2 separate vegetation rasters:
- Existing vegetation raster
- Historic vegetation raster

We typically use  [Landfire](http://www.landfire.gov/) for the vegetation raster inputs.  If using Landfire, download:
- 'us_140evt' (existing vegetation type) 
- 'us_140bps' (historic vegetation type)

Note: If 'us_140' is not yet available for your study area you can use 'us_130'.

Note: The historic vegetation layer (biophysical settings, bps) represents the vegetation that may have been dominant on the landscape prior to Euro-American settlement and is based on both the current biophysical environment and an approximation of the historical disturbance regime.

![landfire]({{ site.baseurl }}/assets/images/landfire.PNG)

### DEM

We typically use [USGS National Elevation Dataset (NED)](https://viewer.nationalmap.gov/basic/) 1/3 arc second (~ 10 m) DEM data.

![national_map_dem]({{ site.baseurl }}/assets/images/national_map_dem.PNG)

### Streamflow Information

If you need base and high flow estimations for your stream network, regional regression equations can be found at [USGS StreamStats](http://streamstats.usgs.gov/) or [USGS National Streamflow Statistics](http://water.usgs.gov/osw/programs/nss/pubs.html). 
- Baseflow regional regression equations (e.g. PQ80 for month with lowest flows)
- Highflow regional regression equations (e.g. Q2 - 2 year recurrence interval peak flow)

## Potential Conflict Model Inputs

The requisite inputs to the potential conflict model include:
- Approximation of the valley bottom
- Detailed roads layer
- Railroads layer
- Canals layer
- Landuse raster

### Valley Bottom Layer
The valley bottom is a polgon feature class. We use it to check if roads or railroads are in the valley bottom as they may have a higher probability of being flooded or impacted by nearby beaver dam building activity. The [Valley Bottom Extraction Tool (V-BET)](http://rcat.riverscapes.xyz/Documentation/Version_1.0/VBET.html) is what we typically use to derive this.

### Roads Layer

We use [TIGER](https://www.census.gov/cgi-bin/geo/shapefiles) roads shapefile for the roads layer input.  Use 'All Roads' shapefiles which are downloaded by county.

### Railroads Layer

The national railroads shapefile can by downloaded [here](https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2017&layergroup=Rails).

### Canals

Canals can be extracted from the NHD Flowline layer (our recommended drainage network dataset) using the ['FCODE'](https://nhd.usgs.gov/userGuide/Robohelpfiles/NHD_User_Guide/Feature_Catalog/Hydrography_Dataset/Complete_FCode_List.htm) attribute field.  Canals have 'FCODE' 33600, 33601, and 33603. 

### Land Use Raster

If no accurate land use layer exits for you study are you can use the Landfire existing vegetation type raster (e.g., 'us_140evt').



<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/2-Preprocessing"><i class="fa fa-arrow-circle-right"></i> Continue to Step 2 </a>
</div>	

------
<div align="center">

	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>
