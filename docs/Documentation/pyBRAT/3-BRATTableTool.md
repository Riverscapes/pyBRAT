---
Title
---

[![BRAT_Banner_Web]({{ site.baseurl }}/assets/Images/BRAT_Banner_Web.png)]({{ site.url }})

### 3- BRAT Table Tool

The first step in using the BRAT toolbox is to generate the input table associated with the segmented stream network.

![table_tool]({{ site.baseurl }}/assets/Images/table_tool.PNG)

*The BRAT Table tool interface*

There are two versions of the BRAT table tool.  One is for use if you are only concerned with the BRAT capacity model.  The other is used if you also want to include the "Conflict" and "Conservation and Restoration" inference systems.

Inputs:

- **Input Segmented Network**: select the segmented (300m) network you created in the preprocessing steps
- **Input DEM**: select the DEM that you downloaded and created
- **Input Drainage Area Raster**: if you want, you can derive a drainage area raster from the DEM beforehand.  If you do so, select it here.  If you do not do so, the BRAT Table tool will automatically derive one, which will make the running time take longer
- **Input Coded Existing Vegetation Layer**: select the landfire EVT layer, making sure that the "VEG_CODE" field has been added and populated
- **Input Coded Historic Vegetation Layer**: select the landfire BPS layer, making sure that the "VEG_CODE" field has been added and populated.
- **Output Network**: select a location and name for the output line network which will include the necessary "iGeo", "iVeg", and (optionally) "iPC" attributes to run the model.
- **Set Scratch Workspace**: choose a file geodatabase where temporary files will be dumped.  The default is Arc's default GDB

**The following inputs are only applicable when running the full BRAT Table tool**

- **Input Valley Bottom Polygon**: select a valley bottom polygon that is associated with the input stream network
- **Input Road Layer Feature Class**: select a feature class representing all roads within the study area
- **Input Railroad Feature Class**: select a feature class representing all railroads within the study area
- **Input Canal Feature Class**: select a feature class representing all canals within the study area

Click OK to run the tool.

[Continue to Step 4]({{ site.baseurl }}/Documenation/pyBRAT/4-iHydAttributes) ->