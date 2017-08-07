### 2. Stream Network Geoprocessing

[TOC]

Figure 1 shows the three straightforward GIS processing tasks that the NHD data undergoes.![Fig2]({{ site.baseurl }}/docs/assets/images/Fig2.png)



Figure 1 -  Diagram showing NHD stream GIS processing tasks.



### Task 1: Subset the NHD Stream Network to Perennial and Certain Artificial Path Streams

[![PerennialSteps]({{ site.baseurl }}/docs/assets/images/PerennialSteps.png)]({{ site.baseurl }}/docs/assets/images/hr/PerennialSteps.png)



- **Step 1:** Download the BRAT Tools.zip file found at the bottom of the page.  This file contains a toolbox called BRAT.  Within this toolbox is a script tool called "NHD Network Builder."  
- **Step 2:** Run the "NHD Network Builder" tool in ArcMap.  There are a few parameters required to run this tool:  1.Setting a workspace.  It is a good idea to have a subfolder that includes both the stream network and water body shapefiles that can also be used as the tools working directory. 2.The stream network input. 3.The water body input (optional). 4.A NHD area input (optional). 5.You can choose to subset any segments that are coded as artificial paths that exist within waterbodies. 6. A waterbody threshold size can be used. Any values above this number will be considered lakes, and the stream network flowlines will be removed within these bodies of water.  Values below this threshold will be considered potential beaver ponds, and the flowlines within them will not be removed.  Appropriate values for this threshold will vary depending on the region for which BRAT is being run (optional). 7. Select appropriate attributes Remove artifical paths, canals, aqueducts, stormwater, connectors, general streams, intermittent streams, perennial streams, and ephemeral streams. For the purposes of BRAT, select all these variables EXCEPT perennial streams, connectors, and artificial paths. This tool may also be used for other applications besides BRAT. 8. Select a stream network output name and location.

![NSB]({{ site.baseurl }}/docs/assets/images/NSB.PNG)

* **Step 3:**Add the output shapefile to ArcMap.  The output will be stored in the workspace selected in the tool, and will be called "NHD_Perennial_Streams.shp." The figure below shows the original stream network input in black, and the subsetted stream network that the tool produces in blue.

![2B]({{ site.baseurl }}/docs/assets/images/2B.png)

- **Output:** `NHD_Perennial_Streams.shp`

## Task 2: Dissolve NHD Stream Network

- **Step 1:** Dissolve all segments of NHD perennial streams into one segment. Use the "Dissolve" command. Do NOT use any Dissolve_Field(s) and select (check)  "Create multi-part features (optional)". 


![Diss]({{ site.baseurl }}/docs/assets/images/Diss.png)



## **Task 3: Segment NHD Streams by 300 m Lengths **

- **Step 1:** Go to Customize - Toolbars - check COGO
- **Step 2:**  Start **Editing** the dissolved NHD line
- **Step 3:**  Right Click on the line.  Go to Selection - Select All.
- **Step 4:** Click on the COGO proportion tool in the COGO toolbar

![COGO]({{ site.baseurl }}/docs/assets/images/COGO.PNG)

The COGO Proportion tool



- **Step 5:**  Enter your desired stream length in the Length 1 box (i.e. 300 meters).  
- **Step 6:** Click on the DUPLICATE box on the right hand side of the Proportion tool
- **Step 7:**  Enter the amount of duplicates of stream length desired.  You can obtain this number by dividing the Feature Length (in the proportion tool) by your desired stream length.  Enter the number in the duplicate box and hit OK.

![fig1]({{ site.baseurl }}/docs/assets/images/fig1.PNG)

- **Step 8:** Choose FROM END POINT OF LINE, then OK.  It may take a few minutes to segment your line.

![fig-2]({{ site.baseurl }}/docs/assets/images/fig-2.PNG)

This video below goes through the above steps using the **COGO PROPORTION TOOL**

<iframe width="560" height="315" src="https://www.youtube.com/embed/ZMxREAWZBvA" frameborder="0" allowfullscreen></iframe>

## Task 4: Convert Multipart Drainage Network to Singlepart Drainage Network

- **Step 1:** Convert the multipart drainage network to a singlepart drainage network.  Use the tool "Multipart to Singlepart"

  ​

  ![multi_single]({{ site.baseurl }}/docs/assets/images/multi_single.png)

- **Step 2:** The length field needs to be recalculated before moving on to Task 5 (See COGO video above).

- **Output:** Final_NHD_Perennial.shp



## Task 5: Buffer NHD Perennial Streams

Step 1: Create a 100 meter (riparian and upland fringe) buffer using the "Buffer" command under the Geoprocessing Tab. Note: Use End Type “FLAT” 

![2F]({{ site.baseurl }}/docs/assets/images/2F.png)

- Step 2: Repeat the above step but this time generate a 30 m (bank and channel level) buffer. Note: Use End Type “FLAT” 


- **Outputs:** 

- - `Buf_100m_Seg_300m_NHD_Perennial.shp`  and 
  - `Buf_30m_Seg_300m_NHD_Perennial.shp`

The video below highlights the simple process of buffering your stream layers for the 30 m and 100 m buffers.

<iframe width="560" height="315" src="https://www.youtube.com/embed/7BdRs-1qNK0" frameborder="0" allowfullscreen></iframe>

## Task 6: Flat End Buffer Type Fix

* If the outputs of task 5 result in missing buffer segments along the NHD flowline as shown below, follow the below process to fill in these missing segments. Perform this task two times. Once for the 30m buffer and once for the 100m buffer.

![Missing_flat_end_buffers]({{ site.baseurl }}/docs/assets/images/Missing_flat_end_buffers.png)



Missing buffer segments from 30m buffer (flat end type)

**Step 1:** Create a second 30m buffer but this time create a round end type buffer. In your table of contents, place this layer below the flat end type buffer to get an idea where you are no longer missing segments.

![two]({{ site.baseurl }}/docs/assets/images/two.png)



Buffer segments from 30m buffer shown in blue (round end type)

**Step 2:** Run the Erase tool using the round end type buffer as the input feature and the flat end type buffer as the erase feature. Name the output feature class *NHD_30m*_buffer_filler.

![three]({{ site.baseurl }}/docs/assets/images/three.png)



Segments created using erase tool. Note: these are the segments the flat end type buffer did not have

 

**Step 3:** To dissolve the semi-circles from the round end type buffer to their respective segment, run the Dissolve tool. The input feature will be the *NHD_30m_buffer_filler. *Name the output feature class *NHD_30m_buffer_filler_dissolve. ***Uncheck **“Create multipart features.”

**Step 4:** Open the attribute of the *NHD­_30m_buffer_filler_dissolve *and create a new field and label it “Area”. Make the type “Double” and precision 6 and scale 2. Right-click on the field and “Calculate Geometry.” Use meters as your units.

 

**Step 5:** To get rid of all the small semi-circles that exist at the upper reaches of the NHD line, we need to start and editing session. First, use the “Select by Attribute” command and set up a query that looks like the following. The values will not be the same. You need to assess what the area is of the majority of the semi-circles and use this value within the query. Once the segments are satisfied, right click on one segment and hit Delete. When satisfied with the edits, save edits and stop the editing session.

![four]({{ site.baseurl }}/docs/assets/images/four.png)



Selecting by attribute to remove unwanted semi-circles

**Step 6:** Run the Merge tool. The input datasets will be the edited *NHD­_30m_buffer_filler_dissolve* and the original flat buffer end type layer. Name the output dataset *NHD_30m_buffer_final. *This will create a more accurate buffer that will not alter the zonal statistics that will be used in the next task.

![five]({{ site.baseurl }}/docs/assets/images/five.png)

Final 30m buffer with missing segments

------

<- [Back to Step 1](http://brat.joewheaton.org/home/documentation/manual-implementation/beaver-dam-capacity-model/1-input-data)        [Ahead to Step 3](http://brat.joewheaton.org/home/documentation/manual-implementation/beaver-dam-capacity-model/3-wood-for-building-materials) ->