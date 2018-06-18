---
title: Step 8 - Summary Report (Optional)
---

# Creating a Summary Report (Optional)

After running the BRAT tool, it can sometimes be useful calculate additional metrics on the output. The Summary Report tool adds and calculates a number of fields that further contextualize the results of a BRAT run.

## Running the Tool

Running the tool is fairly simple. The tool takes three inputs:
* The Conservation Restoration Model output network
* An optional shapefile containing points that correspond to observed beaver dams
* The name of the output
  If not given a beaver dam shapefile, the tool will not produce the fields that rely on dams data. Be warned, the tool will snap the points of the beaver dam shapefile to the nearest reach, which will change the file given to it. If you want to retain the original position of the beaver dams, give the tool a copy of your shapefile.

## Output of the Tool
The tool produces eight new fields. Three of these fields are reliant on the dams input. The fields are as follows:
* `e_DamCt`: The observed number of dams per segment (based on the beaver dam shape file).
* `e_DamDens`: The number of dams per kilometer. Calculated by dividing `e_DamCt` by the segment length.
* `e_DamPcC`: The ratio between the observed dam count and the calculated existing capacity. Calculated by dividing `e_DamCt` by `oCC_EX`.
* `Ex_Categor`: The category of the calculated existing capacity. It is determined based on the `oCC_EX` (the calculated existing capacity), as follows:
  * If `oCC_EX` = 0, `Ex_Categor` = "None"
  * If 0 < `oCC_EX` <= 1, `Ex_Categor` = "Rare"
  * If 1 < `oCC_EX` <= 5, `Ex_Categor` = "Occasional"
  * If 5 < `oCC_EX` <= 15, `Ex_Categor` = "Frequent"
  * If 15 < `oCC_EX`, `Ex_Categor` = "Pervasive"
* `Pt_Catego`r: The category of the calculated potential capacity. It is determined based on the `oCC_PT` (the calculated potential capacity), as follows:
  * If oCC_PT = 0, Pt_Categor = "None"
  * If 0 < oCC_PT <= 1, Pt_Categor = "Rare"
  * If 1 < oCC_PT <= 5, Pt_Categor = "Occasional"
  * If 5 < oCC_PT <= 15, Pt_Categor = "Frequent"
  * If 15 < oCC_PT, Pt_Categor = "Pervasive"
* `mCC_EX_Ct`: The existing capacity density. Calculated by dividing `oCC_EX` by the segment length.
* `mCC_PT_Ct`: The potential capacity density. Calculated by dividing `oCC_PT` by the segment length.
* `mCC_EXtoPT`: The ration between existing and potential capacity. Calculated by dividing `oCC_EX` by `oCC_PT`.



<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/7-BRATCombinedFIS"><i class="fa fa-arrow-circle-left"></i> Back to Step 7 </a>
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/9-LayerPackageGenerator"></i> Continue to Step 9 </a><i class="fa fa-arrow-circle-right">
	
</div>	



<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/7-BRATCombinedFIS"><i class="fa fa-arrow-circle-left"></i> Back to Step 7 </a>
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/9-LayerPackageGenerator"><i class="fa fa-arrow-circle-right"></i> Continue to Step 9 </a>
</div>	

------
<div align="center">

	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>