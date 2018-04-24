---
title: Step 4 - BRAT Table Tool
---

The first step in using the BRAT toolbox is to generate the input table associated with the segmented stream network.

![table_tool]({{ site.baseurl }}/assets/images/table_tool.PNG)

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

## Running the Braid Handler

Currently, there is no good way to find the drainage area values of segments where the river splits, braids, and eventually comes back together. The Flow Accumulation tool can only model a single river, and so gives segments either a much higher value than they should have, or a much lower value. Sometimes, the Flow Accumulation line doesn't accurately line up with the real world dominant stem. An example of this problem is depicted in the pictures below. 

##### Stream Network with Imagery
![FlowAccBasemap]({{ site.baseurl }}/assets/images/FlowAccBasemap.PNG)
##### Stream Network with Flow Accumulation Raster
![FlowAccExample]({{ site.baseurl }}/assets/images/FlowAccExample.PNG)

In an effort to more accurately model these sorts of stream networks, we have created an optional tool, called the Braid Handler, that identifies clusters of braided networks. It then assigns the sidechannels with a reasonable Drainage Area value and gives the dominant channel, if one exists, the highest Drainage Area value found in the cluster.

### Input Preparation
The Braid Handler requires the technician to go through and identify with imagery the mainstem of each cluster in the network. Because thiscan be a time intensive process, it is only recommended that the Braid Handler be run on watershed that contain large amounts of heavily braided streams. Outside of these watershed, the Braid Handler offers little benefit for the work put into running it.

The BRAT Table tool produces a stream network with the attributes "IsBraided" and "IsMainstem". In these fields, a value of 0 is "false", and a value of 1 is "true". If the stream is braided, they are automatically assigned a value of 0, "false", for the "IsMainstem" attribute. The most efficient way to identify areas that need editing is to select by attribute streams where "IsBraided"=1. Once this is done, every cluster of braided streams in the network will be hightlighted. Once that is done, visually identify what stream network is on the mainstem of the cluster, and set "IsMainstem" of each of those streams to 1.

Once the mainstems are identified, the user can run the Braid Handler. The Braid Handler will set the value of any stream where "IsMainstem" is 1 to the highest drainage area value found in the cluster, and will set the drainage area value of any other braided stream to 25 square kilometers. We chose 25 square kilometers because it is a small enough value that it will not preclude the possibility of beaver dams on that river. There is no good way to get an accurate value of the drainage area of these sidechannels, so 25 serves as a placeholder.

After the Braid handler is run, the user can run the rest of the tool as normal.



[Continue to Step 5]({{ site.baseurl }}/Documenation/5-BRATBraidHandler) ->
