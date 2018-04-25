---
title: Step 3 - Preprocessing
---

Some preprocessing of the following inputs in necessary before running the tools in the BRAT toolbox.

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

Classify the land use raster according to water-related land use categories:

- Add a new field (type short int) to the raster attribute table and name it "CODE"
- Begin editing the raster.  Assign each row a value of 1, 2, or 3 in the  "CODE" field using Table 2.

Table 2. Suitability of LANDFIRE Land Cover as Dam-building Material 

| CODE | Description           | Example land use categories              |
| ---- | --------------------- | ---------------------------------------- |
| 1    | Conservation Emphasis | Riparian, No Landuse, Open Water         |
| 2    | Agricultural          | Agriculture, Irrigated, Non Irrigated, Naturally Irrigated |
| 3    | Urban                 | Urban, Developed                         |

[Continue to Step 4]({{ site.baseurl }}/Documentation/4-BRATTableTool)