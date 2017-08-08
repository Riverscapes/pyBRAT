[![BRAT_Banner_Web]({{ site.url }}/assets/Images/BRAT_Banner_Web.png)]({{ site.baseurl }})

### 2. Vegetation Input Derivation

![Ungulate_veg_class]({{ site.baseurl }}/assets/Images/Ungulate_veg_class.png)

Figure 5 shows the LANDFIRE land cover classification by ungulate forage preferences established in the literature.

**Task 1** **: Classify the LANDFIRE land cover data**

- **Step 1:** Load LANDFIRE land cover type raster: Us_110evt.img (existing land cover type)
- **Step 2:** Export the Existing LANDFIRE Raster as Grazing_Veg_Capacity.img
- **Step 3**: Add a new field to Grazing_Veg_Capacity.img and name it “Code” to represent ungulate grazing preferences (0-4) (Table 4).
- **Step 4**: Assign the ungulate land cover preferences (0-4) to the field named “Code” based on Table 2 using field SAF_SRM in Us_110evt.img

Table 4. Suitability of LANDFIRE land cover classes for ungulate grazing

O - Unsuitable - LANDFIRE land cover = Cropland, developed, roads, barren, or water.

1 - Barely Suitable - LANDFIRE land cover = sparsely vegetated.

2 - Moderately Suitable - LANDFIRE land cover = conifer forest.

3 - Suitable - LANDFIRE land cover = woodland or evergreen shrubland.

4 - Preferred - LANDFIRE land cover = grasslands, scrubland steep or riparian.

- **Step 5:** Use the raster to ASCII command to convert the .img raster to an ASCII raster for use in MATLAB.



[![Escalante_Veg_Cap_Ungulate_distribution]({{ site.baseurl }}/assets/Images/Escalante_Veg_Cap_Ungulate_distribution.png)]({{ site.baseurl }}/assets/Images/hr/Escalante_Veg_Cap_Ungulate_distribution.png)

Figure 6 - Your classified output should look something like the above for the Escalante (click on image for larger view).

**Output file: **

- Grazing_Veg_Capacity.img 
- Grazing_Veg_Capacity.asc

------

←Back to [1. Input Data]({{ site.baseurl }}/ Documentation/Ungulate/1-InputData)         Ahead to [3. Slope Input Derivation]({{ site.baseurl }}/Documentation/Ungulate/3-SlopeInput) →