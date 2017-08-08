[![BRAT_Banner_Web]({{ site.baseurl }}/assets/Images/BRAT_Banner_Web.png)]({{ site.url }})

### 5. Running Probability of Ungulate Utilization FIS Model

**Task 1: Run the Probability of Ungulate Utilization (grazing capacity) three input FIS**

- **Step 1: ** Click on the **MATLAB R2012a** icon to start the program.

![3C]({{ site.baseurl }}/assets/Images/3C.png)

- **Step 2:** Browse to the location where GrazingCapacity_3input is stored.

![Ungulate_FIS_1]({{ site.baseurl }}/assets/Images/Ungulate_FIS_1.png)

- **Step 3:** In the command window type FIS_IT and the press enter:

The below dialog box should open and prompt you to select an FIS:

![Ungulate_FIS_2]({{ site.baseurl }}/assets/Images/Ungulate_FIS_2.png)

- **Step 4:** Select GrazingProb_3input.fis

The below dialog box should open and prompt you to select Vegetation_Preference Input Raster:

![Ungulate_FIS_3]({{ site.baseurl }}/assets/Images/Ungulate_FIS_3.png)

- **Step 5:** Path to the GrazingCapacityFIS/Input folder and selected the input_veg.asc

The below dialog box should open and prompt you to load slope input raster:

![ungulate_FIS_4]({{ site.baseurl }}/assets/Images/ungulate_FIS_4.png)

- **Step 6:** Path to the  GrazingCapacityFIS/Input folder and selected the input_slope.asc.

The below dialog box should open and prompt you to load water source input raster:

![Ungulate%20dist_water]({{ site.baseurl }}/assets/Images/Ungulate%20dist_water.png)

- **Step 7:** Path to the GrazingCapacityFIS and selected the distance_to_water.asc

The FIS should now start calculating… this may take a several minutes.

The below dialog box should open and prompt you to save your FIS 

![Ungulate_FIS_save]({{ site.baseurl }}/assets/Images/Ungulate_FIS_save.png)

Then it will need to save the FIS Grid to a File.  This will take even a bit longer.



**Task 2: Convert the FIS output ASCII raster to .img raster**

- **Step 1:** Open ArcMap
- **Step 2:** load the output FIS output ASCII
- **Step 3:** Use the ASCII to Raster command

![ASCII_to_Raster]({{ site.baseurl }}/assets/Images/ASCII_to_Raster.png)

- **Step 4:** Output the FIS grid to the output folder.  This is the final step of the probability of ungulate utilization.  

![Escalante_Prob_Ungulate_distribution]({{ site.baseurl }}/assets/Images/Escalante_Prob_Ungulate_distribution.png)

The final output should look something like the above.

← Back to [4. Distance to Water Source Input - Derivation]({{ site.baseurl}}/Documentation/Ungulate/4-DistanceToWater)

