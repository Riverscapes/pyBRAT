[![BRAT_Banner_Web]({{ site.baseurl }}/assets/Images/BRAT_Banner_Web.png)]({{ site.url }})

### 3. Slope Input Derivation

**Task 1: Create a project area slope map**

- **Step 1:** Open the 10 m DEM in ArcMap
- **Step 2:** Generate a slope map using the "Slope Tool" (ArcToolbox under Spatial Analyst Tools -> Surface). Use the Percent option for the output measurement.
- **Step 3**: Use "Extract by Mask" with your project area boundary to confine the slope map to the project area.
- **Step 4:** Use the "Raster to ASCII" command to convert the .img raster to an ASCII raster format for use in MATLAB.

[![Escalante_Slope_Ungulate_distribution]({{ site.baseurl }}/assets/Images/Escalante_Slope_Ungulate_distribution.png)]({{ site.baseurl }}/assets/Images/hr/Escalante_Slope_Ungulate_distribution.png)

Your slope analysis should look something like the above.

**Output files: **

- Ungulate_Capacity_Slope.img 
- Ungulate_Capacity_Slope.asc 

------

← Back to  [2. Vegetation Input Derivation]({{ site.baseurl }}/Documentation/Ungulate/2-VegetationInput)           Ahead to [4. Distance to Water Source Input - Derivation]({ site.baseurl }}/Documentation/Ungulate/4-DistanceToWater) →

