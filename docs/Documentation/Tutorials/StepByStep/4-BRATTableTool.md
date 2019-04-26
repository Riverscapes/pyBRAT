---
title: Step 4 - BRAT Table Tool
weight: 4
---

The BRAT Table tool will generate the attributes needed to run the other tools in the toolbox.

![table_tool]({{ site.baseurl }}/assets/images/table_tool_new.PNG)

Figure 1. The BRAT Table tool interface

### Required Inputs:

- **Select Project Folder** - path to the BRAT project folder
- **Input Segmented Network** - select the segmented (300m) network you created in the preprocessing steps
- **Input DEM** - select the DEM that you downloaded and created
- **Input Coded Existing Vegetation Raster** - select the landfire EVT layer, making sure that the "VEG_CODE" field has been added and populated
- **Input Coded Historic Vegetation Raster** - select the landfire BPS layer, making sure that the "VEG_CODE" field has been added and populated.
- **Name BRAT Table Output Feature Class** - select a location and name for the output line network which will include the necessary "iGeo", "iVeg", and (optionally) "iPC" attributes to run the model.

### Optional Inputs:

- **Input Drainage Area Raster** - if you want, you can derive a drainage area raster from the DEM beforehand.  If you do so, select it here.  If you do not do so, the BRAT Table tool will automatically derive one, which will make the run time longer
- **Short Description for Run** - Write a short (less than 100 characters, including spaces) description for the BRAT run to be included in the project XML file. 

**The following inputs are optional but required to run the conflict potential and management models**

- **Input Valley Bottom Polygon** - select a valley bottom polygon that is associated with the input stream network
- **Input Road Layer Feature Class** - select a feature class representing all roads within the study area
- **Input Railroad Feature Class** - select a feature class representing all railroads within the study area
- **Input Canal Feature Class** - select a feature class representing all canals within the study area
- **Input Land Use Raster** - select the land use raster, making sure that the "LU_CODE" and "LUI_CLASS" fields have been added and populated.

In addition, there are checkboxes that change the behavior of the tool in minor ways.

- **Find Clusters** - This option will create a `ClusterID` field and populate it. This field is used in the Braid Handler to modify drainage area values. By creating them in the BRAT table, the technician can modify clusters to fit with what they want the tool to do. This is an advanced editing option, and not necessary for most users.
- **Segment Network by Roads** - This option divides reaches based on the roads input. This can be useful if the user wants to compare the results of the model to field data collected from upstream and downstream of bridges. This is not necessary for most users, but can be useful.
- **Run Verbose** - This option enables ArcMap to provide messages for each step conducted by the tool, letting the user track progress as the tool runs. 

Click OK to run the tool.

<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/3-BRATProjectBuilder"><i class="fa fa-arrow-circle-left"></i> Back to Step 3 </a>
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/4.1-DrainageAreaCheck"><i class="fa fa-arrow-circle-right"></i> Continue to Step 4.1 </a>
</div>	
------
<div align="center">

	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>