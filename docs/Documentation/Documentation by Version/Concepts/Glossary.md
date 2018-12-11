---
title: Glossary
---
# Glossary

Because field names in ArcGIS are limited to ten characters, there is a limit to how descriptive those names can be. This page is meant to be a reference for what each field in the stream network produced by BRAT is meant to represent.

## Current pyBRAT Values
These are values that are presently generated and used by the latest version of pyBRAT (3.0.20 at the time of writing). They are sorted by what stage they are created in, not alphabetically.

*For values for other versions of pyBRAT by version please refer to the lookup tables in the [pyBRAT Outputs](http://brat.riverscapes.xyz/Documentation/Outputs/) under the particular version #*

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

**IsMultiCh -** An integer value. If the reach is part of a multi-branch system, the value will be 1. Otherwise, it will be 0.
- Field Type: "LONG"
- Generation Method: BRAT Table Tool

**IsMainCh -** An integer value. If the reach is the primary branch of a multi-branch system, the value will be 1. Otherwise, it will be 0. Defaults to a value of 1 for non-multibranch reaches, a value of 0 for multi-branch reaches. Must be manually edited to indicate main channels in order to properly use the optional Braid Handler tool.
- Field Type: "LONG"
- Generation Method: BRAT Table Tool

**ClusterID -** If the reach is not part of a multi-branch system, this wil have a value of -1. Otherwise, every reach in a cluster of multi-branch reaches will share a ClusterID value. This value will be used for fixing multi-branch drainage area values in the optional Braid Handler tool. If the technician wants to, they can manually edit these values.
- Field Type: "LONG"
- Generation Method: BRAT Table Tool or the Braid Handler tool

**iHyd_QLow -** The value for low stream flow (CFS) in the reach.

- Field Type: "DOUBLE"
- Generation Method: iHyd tool

**iHyd_Q2 -** The value for high stream flow (CFS) in the reach.

- Field Type: "DOUBLE"
- Generation Method: iHyd tool

**iHyd_SPLow-** The stream power in watts of the reach for the low stream flow.

- Field Type: "DOUBLE"
- Generation Method: iHyd tool

**iHyd_SP2-** The stream power in watts of the reach for the high stream flow.

- Field Type: "DOUBLE"
- Generation Method: iHyd tool

**oVC_PT-** Output of beaver dam density based on potential vegetation based on the FIS classifications that the user input for the "VEG_CODE" field in the historic vegetation raster.

- Field Type: "DOUBLE"
- Generation Method: Vegetation Dam Capacity Model tool

**oVC_EX-** Output of beaver dam density based on existing vegetation based on the FIS classifications that the user input for the "VEG_CODE" field in the existing vegetation raster.

- Field Type: "DOUBLE"
- Generation Method: Vegetation Dam Capacity Model tool

**oCC_PT-**  Final capacity output of historic beaver dam dam density based on the combined inputs of the reach.

- Field Type: "DOUBLE"
- Generation Method: Combined Dam Capacity tool

**mCC_PT_CT-** Final capacity output of historic beaver dam dam count based on the combined inputs of the reach.

- Field Type: "Long"
- Generation Method: Combined Dam Capacity tool

**oCC_EX-** Final capacity output of existing beaver dam dam density based on the combined inputs of the 

- Field Type: "DOUBLE"
- Generation Method: Combined Dam Capacity tool

**mCC_EX_CT-** Final capacity output of existing beaver dam dam count based on the combined inputs of the reach.

- Field Type: "Long"
- Generation Method: Combined Dam Capacity tool

**mCC_HisDep-**  The departure between the Historic dam count ("mCC_PT_CT") and the Existing dam count  ("mCC_EX_CT")

- Field Type: "Long"
- Generation Method: Combined Dam Capacity tool

**oPBRC_UI-**  Management output that outlines the unsuitable or limited beaver dam opportunities. Identifies the limiting factor that is limiting the reach from optimal beaver dam construction.

- Field Type: "String"
- Generation Method: Conservation and Restoration tool

**oPBRC_UD-**  Management output that outlines the areas beavers can build dams, but due to anthropogenic proximity could pose potential risk to the beavers. 

- Field Type: "String"
- Generation Method: Conservation and Restoration tool

**oPBRC_CR-** Possible beaver dam conservation/restoration opportunities that can be used for concentration of efforts made by management. This is subset into those reaches that are defined as a "oPBC_UI" score of "Negligible Risk" and "Minor Risk" in order to further aid in possible reaches for management to focus their efforts on in order to get the most bang for their buck.

- Field Type: "String"
- Generation Method: Conservation and Restoration tool

## Depreciated pyBRAT Values
These are values that were once used by pyBRAT, but were discontinued for one reason or another.

**SegID -** Was renamed to ReachID. Served the same purpose.
**SegLength - ** Was renamed to ReachLen. Served the same purpose.
**IsBraided -** Was renamed to "IsMultiThr" for accuracy reasons. Served the same purpose.
**IsMainstem -** Was renamed to "IsMainCh" for clarity reasons. Served the same purpose.















