---
title: Calibrating Veg Scores
weight: 1
---

### Purpose

Part of calibrating the BRAT model is the [vegetation suitability](http://brat.riverscapes.xyz/Documentation/Tutorials/StepByStep/2-Preprocessing.html)  scores which are assigned to the raster attribute table. These are good guidelines that express how suitable a certain vegetation type is for beavers to use in the construction of their dams. However, there are exceptions to these general classifications due to the understory in particular vegetation classifications. Once these exceptions are realized calibration changes are made by increasing or decreasing the "VEG_CODE" scores in the existing or historic vegetation rasters. 

Regardless of the changes that you make to the vegetation suitability scores it is important to verify that the existing and historic vegetation rasters correlate to one another. Meaning that the for example Douglas Fir in the existing vegetation raster is coded as a 3 for suitability the historic Douglas Fir needs to be coded as a 3 as well. If these two raster classifications do not correlate with one another then there is the possibility that the existing capacity will be rated higher than historic capacity due to the user not properly making this calibration comparison. 

### Examples

An example of this was presented in the following illustrations:

- Improper Calibration

  ![Legend BRAT Management Unsuitable or Limited Beaver Dam Opportunities]({{ site.baseurl }}/assets/images/Vegetation_Improper_Calibration.png){: width="600" height="600"}

- Proper Calibration

  ![Legend BRAT Management Unsuitable or Limited Beaver Dam Opportunities]({{ site.baseurl }}/assets/images/Vegetation_Proper_Calibration.png){: width="600" height="600"}

------
<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Standards/"><i class="fa fa-check-square-o"></i>  Back to ETAL BRAT Standards</a>  

	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  

</div>
