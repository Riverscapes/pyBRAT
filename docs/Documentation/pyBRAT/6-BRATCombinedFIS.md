---
<<<<<<< HEAD
Title
---

[![BRAT_Banner_Web]({{ site.baseurl }}/assets/Images/BRAT_Banner_Web.png)]({{ site.url }})

### 6- BRAT Combined FIS
=======
title: 6- BRAT Combined FIS
---
>>>>>>> bd658760559364a5a587a4629f372a3fb419fa24

After running the Vegetation FIS, you can run the "BRAT Combined FIS" tool.  This fuzzy inference system predicts the capacity of stream reaches to support dam building activity based on 4 inputs: 1) the output of the vegetation FIS 2) the low (base) flow stream power, 3) the high flow (Q2) stream power, and 4) the slope of the reach.  This tool like the vegetation FIS tool, must be run twice, once based on historic vegetation and once based on existing vegetation.

![comb_fis]({{ site.baseurl }}/assets/Images/comb_fis.PNG)

Inputs and Parameters:

- **Input BRAT Network**: select the BRAT network that you have been using up to this point
- **FIS Type**:  the first time you run this tool type: PT  the second time you run the tool type: EX
- **Maximum DA Threshold**: this is a drainage area value above which it is assumed that the stream is too large for beaver to build dams on.  This varies from region to region and should be adjusted according to the hydrologic characteristics of the study area.
- **Save Output Network**: the *second* time that you run the tool (ie when you type EX as the FIS Type) choose a location and name to save the output.  It should be something like "Location_BRAT_Capacity.shp"
- **Set Scratch Workspace**: select a file geodatabase to dump intermediate files. The default is the ArcMap default GDB.

"Location_BRAT_Capacity.shp") that will have the new fields "oCC_PT" and "oCC_EX."  When the tool finishes running the second time it should automatically add the output to the map and symbolize the "oCC_EX" field, which represents the existing capacity to support dam building activity.

[![output]({{ site.baseurl }}/assets/Images/output.PNG)]({{ site.baseurl }}/assets/Images/hr/output.PNG)

