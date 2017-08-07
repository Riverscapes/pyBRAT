[![BRAT_Banner_Web]({{ site.baseurl }}/assets/Images/BRAT_Banner_Web.png)]({{ site.baseurl }})



### 4. Calculating Upstream Drainage Area

### Task 1: Deriving Upstream Drainage Area

- **Step 1:** Clip the DEM to the watershed or your area of interest 

- - Use the "Extract by Mask" command.  Note: make sure that the extent of the DEM when clipped covers the entire watershed or watersheds of the stream network that you are using to ensure accurate flow accumulation values.   


- **Step 2**: In the BRAT toolbox downloaded previously (see bottom of [Stream Network Geoprocessing](http://brat.joewheaton.org/home/documentation/manual-implementation/beaver-dam-capacity-model/2-perennial-water-sources) page), open the "DEM to Flow Accumulation" script tool.  


![fig4](C:\Users\A00805535\Documents\GitHub\pyBRAT\docs\assets\Images\fig4.PNG)

- **Step 3**: Run the tool using the two required inputs: 1. Set the workspace for the tool to run in.  A subfolder containing the DEM to be used is generally a good workspace.  2. The input DEM that has been clipped to the watersheds of interest.  The tool will produce a flow accumulation raster where the values of each cell have already been converted to square kilometers. The figure below shows the output, which looks like a standard flow accumulation, but with values in square kilometers.  The raster will be stored in the designated workspace and can be added to ArcMap after the tool has run.

![fig](C:\Users\A00805535\Documents\GitHub\pyBRAT\docs\assets\Images\fig.PNG)



- **Output**: 

- - `DrainArea_sqkm.img `


- **Step 4**: Calculate maximum flow accumulation within the 100 m buffer using Zonal Statistics. 

- - *Spatial Analyst Tools > Zonal Statistics*. 


- - The dialog box prompts you to input the 100 m stream buffer and the flow accumulation raster created in the last step. The output should be named something that designates the grid as the maximum zonal statistic of the flow accumulation raster. 

- **Output**: 

- - `(watershed_name)_100m_ZS_Max_FAC.img `

## Task 2: Capture Maximum Flow Accumulation Values on the Stream Network

In the pilot study we found that the stream network did not always precisely overlay the maximum flow accumulation value due to the coarseness of the input data.  To resolve this issue in the statewide run we used a segmented 100 m buffer, and zonal statistics to ensure the maximum flow accumulation values for each buffered segment were captured. 

To capture the maximum flow accumulation value:

* **Step 1**: Buffered your stream network at 100 meters 
* **Step 2**: Ran a maximum zonal statistics within that buffer.  
* **Step 3**: This zonal statistics raster is then used to derive the flow accumulation value in Geospatial modeling. 

<- [Back to Step 3]({{ site.baseurl }}/Documentation/matBRAT/3-VegetationClassification)        [Ahead to Step 5](http://brat.joewheaton.org/home/documentation/manual-implementation/beaver-dam-capacity-model/potential-conflict) ->