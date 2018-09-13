---
title: Glossary
---
# Glossary

Because field names in ArcGIS are limited to ten characters, there is a limit to how descriptive those names can be. This page is meant to be a reference for what each field in the stream network produced by BRAT is meant to represent.

## Current pyBRAT Values
These are values that are presently generated and used by the latest version of pyBRAT (3.0.18 at the time of writing). They are sorted by what stage they are created in, not alphabetically.

**FID -** This attribute is automatically assigned to every segment in a stream network. Each segment should have a unique FID value.
- Field Type: "FID"
- Generation Method: Automatic

**Shape -** The type of vector that this element is. This attribute is automatically generated. In a stream network, this value should be *Polyline*.
- Field Type: "GEOMETRY"
- Generation Method: Automatic

**ReachID -** This attribute is generated based on the FID. By creating our own attribute, we give ourselves more flexibility in how we capture data values. For a technician running BRAT, it is effectively identical to FID. 
- Field Type: "LONG"
- Generation Method: SegmentNetwork.py script or the BRAT Table tool

**ReachLen -** The length of the polyline. 
- Field Type: "DOUBLE"
- Generation Method: SegmentNetwork.py script

**StreamName -** The name of the stream (for example, "Grouse Creek" or "Snake River"). Some datasets come with this value automatically. 
- Field Type: "STRING"
- Generation Method: Pre-existing in some datasets

**StreamID -** Generated based on the StreamName when running SegmentNetwork.py or AddAttributes.py. Every reach with the same StreamName value is given the same StreamID value, counting up from 1. Used primarily in the Drainage Area Check tool.
- Field Type: "LONG"
- Generation Method: SegmentNetwork.py script

**StreamLen -** The length the streams, identified using StreamID. 
- Field Type: "DOUBLE"
- Generation Method: SegmentNetwork.py script

**ReachDist -** How far a reach is from the headwaters of the stream. Calculated based off of StreamID.
- Field Type: "DOUBLE"
- Generation Method: SegmentNetwork.py script

**iGeo_ElMax -** The maximum elevation found within a buffer around the reach. Used in calculating slope. Extracted from the DEM given.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iGeo_ElMin -** The minimum elevation found within a buffer around the reach. Used in calculating slope. Extracted from the DEM given.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iGeo_Len -** The length of the reach. Redundant with ReachLen, but removal is currently low priority.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iGeo_Slope -** The average slope of the reach. Calculated using iGeo_ElMax, iGeo_ElMin, and iGeo_Len.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iGeo_DA -** The maximum drainage area value found in a buffer around the stream. Extracted from the drainage area raster given, or from a DA raster derived from the DEM (if no DA raster was given).
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iVeg_100EX -** The average VEG_CODE value on the existing vegetation raster within a 100m buffer of the reach.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iVeg_30EX -** The average VEG_CODE value on the existing vegetation raster within a 30m buffer of the reach.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iVeg_100PT -** The average VEG_CODE value on the historic vegetation raster within a 100m buffer of the reach.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iVeg_30PT -** The average VEG_CODE value on the historic vegetation raster within a 30m buffer of the reach.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iPC_RoadX -** The distance of the reach to the nearest point where a road crosses the stream.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iPC_Road -** The distance of the reach to the closest road.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iPC_RoadVB -** The distance of the reach to the closest road in the valley bottom.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iPC_Rail -** The distance of the reach to the closest railroad.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iPC_RailVB -** The distance of the reach to the closest road in the valley bottom.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**oPC_Dist -** The smallest value found in "iPC_RoadX", "iPC_Road", "iPC_RoadVB", "iPC_Rail", and "iPC_RailVB". 
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iPC_LU -** The average land use value in a 100m buffer around the reach.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iPC_VLowLU -** The percentage of cells in the buffer classified as having a low land use value.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iPC_LowLU -** The percentage of cells in the buffer classified as having a low land use value.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iPC_ModLU -** The percentage of cells in the buffer classified as having a low land use value.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool

**iPC_HighLU -** The percentage of cells in the buffer classified as having a low land use value.
- Field Type: "DOUBLE"
- Generation Method: BRAT Table Tool


## Depreciated pyBRAT Values
These are values that were once used by pyBRAT, but were discontinued for one reason or another.

**SegID -** Was renamed to ReachID. Served the same purpose.
**SegLength - ** Was renamed to ReachLen. Served the same purpose.
**IsBraided -** Was renamed to "IsMultiThr" for accuracy reasons. Served the same purpose.
**IsMainstem -** Was renamed to "IsMainCh" for clarity reasons. Served the same purpose.















