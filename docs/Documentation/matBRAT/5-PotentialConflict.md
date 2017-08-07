[![BRAT_Banner_Web]({{ site.baseurl }}/assets/Images/BRAT_Banner_Web.png)]({{ site.baseurl }})

## 5. Potential Conflict Layer Processing

## Task 1: Code Land Ownership Layer & Convert to Raster

- **Step 1**: Open the attribute table of your land ownership layer
- **Step 2**: Add a new field called 'Code'
- **Step 3:** Assign each entry of the 'Code' field with a ownership value of 1, 2 or 3 based on the following lookup table.

**Land Ownership Code Lookup Table**

(1) Conservation Emphasis Land

> Includes: Conservation Areas, Division of Natural Resources, National Park, National Historic 					Site,National Monument, National Wildlife Refuge/National Wildlife Reserve, Primitive Area, US Fish and Wildlife, Wilderness, Wildlife Management Area.

(2) Federal or State Land

> Includes: Bureau of Indian Affairs/ Indian Reservation, BLM, BOR/Reclamation , County, State, State Sovereign Land, State Trust Land, US Forest Service, National Recreation Area, Parks and Recreation.

(3) Private land

- **Step 4:** Convert the Landownership shapefile to a raster using the "Polygon to Raster" command.
  * Assign a 30 m pixel value


## Task 2: Code Water Related Land Use Layer & Convert to Raster

* **Step 1**: Open the attribute table of the water related land use layer
* **Step 2**: Add a new field called 'Code'
* **Step 3:** Assign each entry of the 'Code' field with a Land use value of 1, 2 or 3 based on the following lookup table.


### Water Related Land Use Lookup Table

(1) Conversation Emphasis Land

>Includes: Riparian, No Land Use, and Open Water

(2) Agricultural 

>Include: Irrigated, Non Irrigated, Naturally Irrigated

(3) Urban 

- **Step 4:** Convert the Land Use shapefile to a raster using the "Polygon to Raster" command.

- - Assign a 30 m pixel value



##Task 3: Generating Euclidean Distance Potential Conflict Rasters



- **Step 1: **Generate Euclidean Distance Rasters for each of your potential conflict layers (adjacent roads, railroads, culverts, stream/road crossings, and canals using "Euclidean Distance" (ArcToolbox under Spatial Analyst Tools -> Distance). 
- - Use an output cell size of 5 meters for adjacent roads (this smaller pixel value helps to better gauge potential conflict in areas where roads are within 30 meters of the stream center line). 
  - An output cell size of 30 meters is appropreate for the remaining conflict layers (railroads, culverts, stream crossings and canals).
  - ** **Assign an output grid name
- The example below uses canal data:



![Euclidean_distance](C:\Users\A00805535\Documents\GitHub\pyBRAT\docs\assets\Images\Euclidean_distance.PNG)

The output raster of canals should looks something like this (the UDWR Regions are shown for scale):

![Euclidean_distance_raster](C:\Users\A00805535\Documents\GitHub\pyBRAT\docs\assets\Images\Euclidean_distance_raster.PNG)

Remember to repeat this step for each of the potential conflict layers that you have captured. 

​                                          

​                                                                         <- [Back to Step 4]({{ site.baseurl }}/Documentation/matBRAT/4-CalcUpstream)       [Ahead to Step ](http://brat.joewheaton.org/home/documentation/manual-implementation/beaver-dam-capacity-model/putting-attributes-on-stream-network)6 ->