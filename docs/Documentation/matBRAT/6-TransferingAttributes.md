[![BRAT_Banner_Web]({{ site.baseurl }}/assets/Images/BRAT_Banner_Web.png)]({{ site.url }})



### 6. Transfering Attributes onto the Stream Network



### Task 1: Transfer Elevations from DEM to Stream Network for Channel Slope

**Step 1**: Download Geospatial Modeling Environment (GME) Open Source GIS software [http://www.spatialecology.com/gme/gmedownload.htm](http://www.spatialecology.com/gme/gmedownload.htm)



![GME]({{ site.baseurl }}/assets/images/GME.png)

GMES has dependencies on R and ArcGIS. Therefore, select the download that matches the version of R or ArcGIS you are running. 

> *Note*: GME’s predecessor was called HawthsTools.  It is likely that you may have used this software in the past.

- **Step 2**: Install GME software 

1. Download and extract the zip file. 
2. You must use the `setup.exe` program, not the `gme.msi` program, to install GME. 
3. GME is a stand-alone program that can be started from the* Windows Start button --> Programs --> SpatialEcolog*y. 

- **Step 3**: Click on the Geospatial Modeling Icon and run the software.![3C]({{ site.baseurl }}/assets/images/3C.png)

Note: GME does **NOT** work with Geodatabases or with rasters that are stored in Geodatabases. Transferring values to the NHD require both shapefiles to also be in the same projection.



![3D]({{ site.baseurl }}/assets/images/3D.png)

- **Step 4**: Transfer raster DEM elevations to your stream network

- - Click on the **Geospatial Modeling** Icon and run the software. 

  - - Note GME is stand along software that is run outside of ArcGIS. You must close ArcGIS in order to run GME.![3C]({{ site.baseurl }}/assets/images/3C.png)

- The following tool "isectlinerst" (Intersect Lines With Raster) will do the trick. 



![3J]({{ site.baseurl }}/assets/images/3J.png)

- For “prefix” use “Elev” for elevation and extract values from your DEM (e.g. 10 m USGS DEM). 



- For the **in** use Final_NHD_Perennial.shp for the **raster*** *use the Digital Elevation Model and for the **prefix** use Elev.


- **Step 5**: For the output shapefile: Final_NHD_Perennial.shp **remove** the field with the suffix LWM **Length Weighted Mean** (LWM). 

##Task 2:  Transfer Dam-building Material Preference Values to Stream Network

- **Step 1**: Transfer raster dam-building material preference values to your stream network 
- Use the Geospatial Modeling Environment software again. ![3C]({{ site.baseurl }}/assets/images/3C.png)

- Use the "isectlinerst" command



![3E]({{ site.baseurl }}/assets/images/3E.png)

> **Conduct this step a total of four times.**

- 1st for the *in* use Final_NHD_Perennial.shp, for the *raster *use `Existing_100m_Veg_Cap.img` and for the *prefix *use `ex_100`. 
- 2nd for the *in* use Final_NHD_Perennial.shp for the *raster *use `Existing_30m_Veg_Cap.img `and for the *prefix *use `ex_30`. 
- 3rd for the *in* use `Final_NHD_Perennial.shp `for the *raster *use `Potential_100m_Veg_Cap.img` and for the *prefix *use `pot_100`. 
- 4th for the *in* use Final_NHD_Perennial.shp for the *raster *use `Potential_30m_Veg_Cap.img` and for the *prefix *use `pot_30`. 
- Note: You must close Arcmap and reopen the program to view GME assigned attributes on Final_NHD_Perennial.shp 


- **Step 2**: For the output shapefile: Final_NHD_Perennial.shp remove the fields with the suffix MIN, MAX, END. **Keep** the field with the suffix **Length Weighted Mean** (LWM). LWM is calculated by multiplying the length of each segment by the raster cell value of that segment, summing this value across all segments, and finally dividing that sum by the total length of the polyline:

![Step5Eq]({{ site.baseurl }}/assets/images/Step5Eq.png)

where l is the length of a segment, v is the value of the raster cell for that segment, and L is the total line length.

Below is what the resulting feature class attribute table should look like (click on for larger version). Do the same for the 30m buffer data.

![3F]({{ site.baseurl }}/assets/images/3F.png)

The above generated tables (30 m and 100 m) become inputs for the VEG FIS model.



The video below highlights how to use GME to get the vegetation values onto the stream network:

<iframe width="560" height="315" src="https://www.youtube.com/embed/FBmnnTQfg4o" frameborder="0" allowfullscreen></iframe>

### Task 3: Transfer Upstream Drainage Area from Flow Accumulation Raster to Stream Network

- **Step 1**: Transfer upslope drainage area to the stream network

- - Once again use the Geospatial Modeling Environment software. ![3C]({{ site.baseurl }}/assets/images/3C.png)

Again use the "*isectlinerst" * tool. 

![3J]({{ site.baseurl }}/assets/images/3J.png)



- For the **in** use the Final_NHD_Perennial.shp and for the **raster** use the (watershed_name)_100m_ZS_Max_FAC.img 
- For “prefix” use “Drain” for uplsope drainage area 
- For the output shapefile,** keep** the MAX field (delete all other  DRAIN fields)

### Task 4: Transfer Potential Conflict Raster Data to Stream Network

- **Step 1**: Transfer euclidean distance raster values to the stream network

- - Once again use the Geospatial Modeling Environment software. ![3C]({{ site.baseurl }}/assets/images/3C.png)

And yet again use the "*isectlinerst" * tool. 

![3J]({{ site.baseurl }}/assets/images/3J.png)



Conduct this step a total of five times



- For each run** keep** the MIN field 


- - 1st for the **in** use Final_NHD_Perennial.shp for the raster use Culverts.img and for the prefix use Culvert. 
  - 2nd for the **in **use Final_NHD_Perennial.shp for the raster use Roadcrossing.img and for the prefix use RoadX. 
  - 3rd for the **in** use Final_NHD_Perennial.shp, for the raster use Adjacent_roads.img and for the prefix use RoadAdj. 
  - 4th for the **in** use Final_NHD_Perennial.shp for the raster use Railroads.img and for the prefix use RR. 
  - 5th for the **in **use Final_NHD_Perennial.shp for the raster use Canals.img and for the prefix use Canal.


- For each run** keep** the MAX field 

- - 6th for the **in** use Final_NHD_Perennial.shp for the raster use LandUse.img and for the prefix use LU.
  - 7th for the **in** use Final_NHD_Perennial.shp for the raster use Ownership.img and for the prefix use Own.


- - **Note:** You must close Arcmap and reopen the program to view GME assigned attributes on Final_NHD_Perennial.shp railroads



## Task 5 (optional): Collect Actual Dam Counts in Google Earth

For the Utah statewide run of BRAT actual dam counts were collected for the Logan/Little Bear, Strawberry, Price and Fremont HUC 8 watersheds. 

- A technician examined every stream segment using virtual reconnaissance in Google Earth within the given watershed for beaver dams and recorded their location as a KMZ placemarker. 
- Each point was given an accuracy assessment of very high, high, medium and low based on the likelihood of the perceived location actually being a beaver dam. 
- Dam locations with a medium and low status were reexamined in Google Earth by an expert to determine if the dam should remain in the dataset or not. 
- The resulting dam location data was used for model calibration and validation.

We found this method to be a cost effective means for collecting actual dam count data and highly recommend using this approach if time/resources permit. 

## **Task 6 (optional): Transferring Dam Counts to the Stream Network**

- **Step 1**: Convert the KMZ file to a layer file using *Conversion - Layer to KML*

![DamCounts]({{ site.baseurl }}/assets/images/DamCounts.PNG)

- **Output**: `(watershed_name)_DamCounts.shp`


- **Step 2**: Change the projection of the output shapefile to the projection you are working (i.e. UTM or other).  Use *Data Management - Project*

![project]({{ site.baseurl }}/assets/images/project.PNG)



- **Step 3:**  Use *Analysis-Near *to determine the dams that are within 100 m of the stream line.  This will add a Near FID attribute field to your dam count shapefile.   This field indicates the nearest stream segment FID to the dam.



![near]({{ site.baseurl }}/assets/images/near.PNG)

- **Step 4:**  Use *Analysis-Frequency *to determine the count of dams on the stream segments.  Choose the NEAR_FID field for Frequency.  The output is a table with a count of Near FIDs.  

![frequency]({{ site.baseurl }}/assets/images/frequency.PNG)



- **Step 5:**  Join the Frequency table to the NHD_Perennial_Final.shp on the FID field and the NearFID field.  To do this, right click on the stream line.  Go to Join and Relates - Join.  Choose 1. FID, 2. the Frequency table, 3. Near FID.  Click OK.


- **Step 6:**  Export the joined shapefile.   Right click on the stream line.  Go to Data, Export Data.  Name the file Final_NHD_Perrennial_BRATInput.shp


- **Output:**  FInal_NHD_Perennial_BRATInput.shp 

​                                                               <- [Back to Step 5]({{ site.baseurl }}/Documentation/matBRAT/5-PotentialConflict)        [Ahead to Step 7]({{ site.baseurl }}/Documentation.matBRAT/7-FormattingBRATInputData) ->