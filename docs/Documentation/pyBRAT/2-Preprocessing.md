---
title: 2- Preprocessing
---

Some preprocessing is necessary before running the tools in the BRAT toolbox.

1. Subset the NHD network to the desired streams (e.g. only the perennial network, or perennial and intermittent) and segment the network into 300 m lengths.  Attached at the bottom is a document explaining one simple method of segmentation.


2. Classify the vegetation rasters according to suitability of dam building material.

![veg_code]({{ site.baseurl }}/assets/Images/veg_code.png)

- Add a field (type short int) to the landfire EVT raster and call it "VEG_CODE"
- Begin editing the EVT raster, and give each field a "VEG_CODE" value from 0 to 4 according to the chart above.  Save the edits and stop editing.  
- Repeat this process for the landfire BPS raster.
- Note: the coarseness of landfire data means that it is subject to significant error.  If you wish to refine your capacity model further, you can investigate where each of the the classes in the landfire rasters occur, and edit the "VEG_CODE" values accordingly.

3. Classify the land use raster (if no accurate land use layer exists for your study area you can use the landfire EVT raster again).  

- Add a field (type short int) to the raster and call it "CODE"

- Begin editing the raster and assign each field a land use value under the "CODE" field.  Values are as follows.

- - 3 - urban land uses
  - 2 - agricultural land uses
  - 1 - no land use or natural 

[Continue to Step 3]({{ site.baseurl }}/Documentation/pyBRAT/3-BratTableTool) ->