---
title: 4-Distance To Water Source Input - Derivation
---

### 4. Distance to Water Source Input - Derivation

**Task 1: Convert NHD waterbodies to polyline (for distance to water input)**

- **Step 1:** Use the "Polygon to Line" command:![polygon_to_line]({{ site.baseurl }}/assets/images/polygon_to_line.png)

**Output:**

- NHD_Lakes_As_Polyline.shp


- **Step 2:** Use the "Merge" command to combine the resulting lakes polyline with the NHD perennial streams include streams outside your project area.

![Merge]({{ site.baseurl }}/assets/images/Merge.png)

**Output:** NHD_Lakes_Perennial_Streams.shp



**Task 2: Use the Euclidean Distance command to calculate distance to water sources**

- **Step 1:** Load the input layer, generated in the previous task: NHD_Lakes_Perennial_Streams
- **Step 2:** Assign an output grid name

![Euclidean_Distance (1)]({{ site.baseurl }}/assets/images/Euclidean_Distance1.png)

**Output:**

- NHD_Lakes_Streams_For Euclidean_Distance.img


- **Step 3**: Clip the output raster NHD_Lakes_Streams_For Euclidean_Distance.img by your area of interest.

Use "Extract by Mask":

![extract_by_mask]({{ site.baseurl }}/assets/images/extract_by_mask.png)

**Step 4:** Convert to an ASCII raster using the "Raster to ASCII" command.

[![Escalante_distance_to_water_Ungulate_distribution]({{ site.baseurl }}/assets/images/Escalante_distance_to_water_Ungulate_distribution.png)]({{ site.baseurl }}/assets/images/hr/Escalante_distance_to_water_Ungulate_distribution.png)

Your euclidean distance should look something like the above.

**Output:** 

- Euclidean_Distance_to_Water.img
- Euclidean_Distance_to_Water.asc

------

← Back to [3. Slope Input Derivation ]({{ site.baseurl}}/Documentation/Ungulate/3-SlopeInput)        Ahead to [5. Running Probability of Ungulate Utilization FIS Model]({{ site.baseurl}}/Documentation/Ungulate/5-RunningProbability) →
