[![BRAT_Banner_Web]({{ site.baseurl }}/assets/Images/BRAT_Banner_Web.png)]({{ site.url }})

### 7. Formatting BRAT Input Data

### Task 1: Export Final_NHD_Perennial_BRATInput.shp as a Text File

- **Step 1:** Open the attribute table of Final_NHD_Perennial_BRATInput.shp and export data.

![Export_1]({{ site.baseurl }}/assets/Images/Export_1.png)

- **Step 2:** Export and save as a .csv file (Final_NHD_From_GIS.csv)

### Task 2: Format the .csv Table

- **Step 1:** Open Final_NHD_From_GIS.csv in Excel
- **Step 2:** Make a column named Slope and make a formula to calculate channel slope (ElevMAX-ElevMIN)/Length for all entries.
- **Step 3:** If dam counts are not available, leave all cells for "e_DamCt" blank.
- **Step 4:** Previously, calculations to convert the DrainMAX column to square kilometers were required, but with the DEM to Flow Accumulation tool, this is no longer necessary.
- **Step 5**: Format the table as follows for FIS input:

Format the table  with columns A-S, as shown below:

![Capture3]({{ site.baseurl }}/assets/Images/Capture3.PNG)

![Capture]({{ site.baseurl }}/assets/Images/Capture.PNG)

![Attribute_Table_Statewide]({{ site.baseurl }}/assets/Images/Attribute_Table_Statewide.png)

- **Output (save as)**: 

- - Final_NHD_BRAT_Input.csv

  <- [Back to Step 6]({{ site.baseurl }}/Documentation/matBRAT/6-TransferingAttributes)        [Ahead to Step 8]({{ site.baseurl }}/Documentation/matBRAT/8-RunningBRATModel) ->


