### 1. Input Data Capture

### The dam-building beaver capacity model requires:

- A drainage network layer
- Hydrography data tied to that layer
- Vegetation type raster data
- Digital Elevation Model (DEM)
- Baseflow information throughout drainage network
- Highflow information throughout drainage network

 Existing, readily and freely available GIS datasets from GIS data clearinghouses can be used as model inputs. For the Utah statewide run, we used:

 [NHD](http://nhd.usgs.gov/) for a *drainage network layer & hydrography data*

 * National Hydrography Dataset (NHD)

 * Download both stream,  water body, area data


![NHD]({{site.baseurl }}/docs/assets/Images/NHD.png)

* [Landfire](http://www.landfire.gov/) for *Vegetation Type raster data
  * Download both Us_120evt (existing vegetation type) and us_120bps (potential vegetation type)

Note: The potential vegetation layer (biophysical settings (BpS)) represents the vegetation that may have been dominant on the landscape prior to Euro-American settlement and is based on both the current biophysical environment and an approximation of the historical disturbance regime. 

[USGS Digital Elevation (DEM) data](http://ned.usgs.gov/)* for Digital Elevation Model (DEM)*
* Download USGS NED  10 m DEM data[USGS StreamStats](http://streamstats.usgs.gov/) or [USGS National Streamflow Statistics](http://water.usgs.gov/osw/programs/nss/pubs.html) for:
  * Baseflow regional regression equations (e.g. PQ80 for month with lowest flows)
  * Highflow regional regression equations (e.g. Q2 - 2 year recurrence interval peak flow)

  ​


The potential conflict inference system requires the following layers:

- Roads 
- Railroads 
- Culverts
- Stream Crossings (User generated point file of road/stream intersections) 
- Canals
- Land use
- Landownership 



For the Utah statewide run, we obtained all of the above data from the [Utah AGRC Mapping Portal](http://gis.utah.gov/).

Note: These data or similar data must be captured before proceeding on to Step 2.

### Matlab and FIS Files

The matlab and FIS files for the beaver dam capacity, conflict potential and conservation and restoration models are provided at the following link: 

[Matlab_FIS.zip.](http://etal.usu.edu/BRAT/Website/Matlab_FIS.zip)

 This zipfile also contains an input .csv table (Matlab_Input_Formatted_Empty_CSV.csv) to be used when running the models.

Source Code available on [BitBucket](https://wheatonetal@bitbucket.org/etal_brat/brat_matlab.git)

[Advance to Step 2 ](http://brat.joewheaton.org/home/documentation/manual-implementation/beaver-dam-capacity-model/2-perennial-water-sources)->