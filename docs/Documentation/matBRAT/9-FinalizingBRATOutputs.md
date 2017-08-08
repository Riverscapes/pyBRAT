[![BRAT_Banner_Web]({{ site.baseurl }}/assets/Images/BRAT_Banner_Web.png)]({{ site.url }})

### 9. Finalizing BRAT Outputs

**Task 1: Prepare the shapefile to be joined with the FIS output table**

- **Step 1:** "Add Data":  The input BRAT shapefile (watershed_name_Brat_input.shp) to ArcMap
- **Step 2:** Open the attribute table of  and delete all the fields except FID, and Shape. 

Note: You must have at least one other field in this case I had a field called ENABLED. This shapefile is the “empty” shapefile used in the join. I named it Escalante_BRAT_Input.shp

![putting_it_all_togher]({{ site.baseurl }}/assets/images/putting_it_all_togher.png)

**Task 2: Join the BRAT output table with the (Watershed_name)_BRAT_Input.shp**

- **Step 1:** In ArcMap open the “empty shapefile” (watershed_name_BRAT_Input.shp) that will be joined with the above table in the following steps: 
- **Step 2:** Use Add Data to load BRAT_Final_NHD_from_GIS.csv

![add_data]({{ site.baseurl }}/assets/images/add_data.png)

- **Step 3**: Use join the existing vegetation output table with the (watershed_name)_BRAT_Input.shp.

![Join_data]({{ site.baseurl }}/assets/images/Join_data.png)

**Step 4:** To make the join permanent right click on the shapefile export and save as a new shapefile to the output directory. Name the shapefile BRAT_(watershed_name).shp.

![Save_as]({{ site.baseurl }}/assets/images/Save_as.png)

These resulting shapefiles are the **final data** and are featured on the Dam-building Beaver Capacity Maps. Below is an example:.

[![final_FIS_map]({{ site.baseurl }}/assets/images/final_FIS_map.png)]({{ site.baseurl }}/assets/images/hr/final_FIS_map.png)

[Back to Step 8]({{ site.baseurl }}/Documentation/matBRAT/8-RunningBRATModel)

