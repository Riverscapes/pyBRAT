---
title: Step 6 - BRAT Vegetation Dam Capacity Model
weight: 8
---

The vegetation dam capacity model estimates the maximum number of dams each reach could support based solely on the streamside and riparian vegetation.  The model predicts dam capacity for both the historic vegetation and existing vegetation.

![veg_fis]({{ site.baseurl }}/assets/images/veg_fis.PNG)

Inputs and Parameters:

- **Input BRAT Network**: select the segmented network that contains all of the attributes from the BRAT Table and iHyd tools

Click OK to run.

After the tool has been run, the network should now include the attributes `oVC_HPE` (historic vegetation dam capacity based on historic vegetation) and `oVC_EX`  (existing vegetation dam capacity based on existing vegetation). It will also create a folder in `01_Intermediates` called `##_VegDamCapacity`, which will contain layers symbolizing existing and historic vegetation dam building capacity.

[Continue to Step 8]({{ site.baseurl }}/Documentation/7-BRATCombinedFIS) ->

<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/5-iHydAttributes"><i class="fa fa-arrow-circle-left"></i> Back to Step 5 </a>
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/7-BRATCombinedFIS"><i class="fa fa-arrow-circle-right"></i> Continue to Step 7 </a>
</div>	
------
<div align="center">

	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>