---
title: Step 2 - Preprocessing Input Data
weight: 2
---

Some preprocessing of the following inputs is necessary before running the tools in the BRAT toolbox.

## NHD Network

- Subset the NHD network to the desired streams (e.g. only the perennial network, or perennial and intermittent).  The NHD network builder tool (NBT) was designed for this process.  It is part of the [Riparian Condition Assessment Tools (RCAT) Toolbox](https://github.com/Riverscapes/RCAT).  Documenation on the NHD NBT can be found [here](https://bitbucket.org/jtgilbert/riparian-condition-assessment-tools/wiki/Tool_Documentation/Version_1.0/NHD_Network_Builder).
- Segment the network into 300 m lengths.  This can either be carried out manually or by running the 'segmentNetwork.py' script which can found in the pyBRAT 'SupportingTools' folder.

## Vegetation Input Rasters

- Classify the vegetation rasters according to suitability of dam building material.  Add a "VEG_CODE" field to the raster attribute table and assign a value from 0 to 4 according to the chart below:

![veg_code]({{ site.baseurl }}/assets/images/veg_code.png)
Figure 1. Diagram showing Landfire land cover data classification for the beaver dam capacity model.

- If you use Landifre data, you can follow these steps:
  1. Make a copy of your vegetation type layer (e.g.  US_120evt) as a new raster (we suggest using *.img or *.tif; e.g. LANDFIRE_EVT.img) in the same coordinate system as your drainage network layer.
  2. Load your vegetation type raster and add a field called “VEG_CODE” representing dam-building material preferences (0-4) (Figure 1).  
  3. Begin editing the EVT raster.  Classify the VEG_CODE field according to its suitability as a dam building material.  Example classifications are shown in Table 1.  
  4. Repeat this process for the landfire BPS raster.

Table 1. Suitability of LANDFIRE Land Cover as Dam-building Material 

| Suitability | Description                  | Landifre Land Cover Classes              |
| ----------- | ---------------------------- | ---------------------------------------- |
| 0           | Unsuitable Material          | Agriculture, roads, barren, non-vegetated, or sparsely vegetated |
| 1           | Barely Suitable Material     | Herbaceous wetland/riparian or shrubland, transitional herbaceous, or grasslands |
| 2           | Moderately Suitable Material | Introduced woody riparian, woodland/conifer, or sagebrush |
| 3           | Suitable Material            | Deciduous upland trees, or aspen/conifer |
| 4           | Preferred Material           | Aspen, cottonwood, willow, or other native woody riparian |

**Notes:** 
- The coarseness of Landfire data means that it is subject to significant error.  If you wish to refine your capacity model further, you can investigate where each of the the classes in the landfire rasters occur, and edit the "VEG_CODE" values accordingly.
- We suggest you consider the classification carefully for those vegetation types that end up in your riparian areas, but remember that the majority of categories occur well outside the riparian corridor and are not critical in this analysis.

## Land Use Raster

**Optional and only necessary if running the conflict and management models** 

If using the Landfire existing vegetation type raster (e.g., 'us_140evt) to represent land use this pre-processing step can either be carried out manually or by running the 'LANDFIRE_LUCode.py' script which can found in the pyBRAT 'SupportingTools' folder

Classify the land use raster according to land use categories to characterize differing land use intensities:

- Add a new field (type double) to the raster attribute table and name it "LU_CODE"
- Add a new field (type text) to the raster attribute table and name it "LUI_CLASS"
- Begin editing the raster.  Assign each row a value in the  "LU_CODE" and "LUI_CLASS"  fields using Table 2.

Table 2. Land Use Code and Class Descriptions 

| LU_CODE | LUI_CLASS | Description | Example land use categories          |
| ---- | ---- | --------------------- | ---------------------------------|
| 0    | 'VeryLow' | Natural Setting, No Land Use | Riparian, Open Water  |
| 0.33  | 'Low' | Lower Intensity Agricultural | Idle Cropland, Pasture, Hayland |
| 0.66  | 'High' | Higher Intensity Agricultural | Row Crop, Orchard, Vineyard |
| 1    | 'VeryHigh' | Urban or Developed                 | Developed, Quarries          |



<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/1-InputData"><i class="fa fa-arrow-circle-left"></i> Back to Step 1 </a>
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/3-BRATTableTool"><i class="fa fa-arrow-circle-right"></i> Continue to Step 3 </a>
</div>	

------
<div align="center">

	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>