---
title: Step 9 - Data Validation (Optional)
weight: 10
---

# Using the Data Validation tool (Optional)

After running the BRAT tool, it can sometimes be useful calculate additional metrics on the output. The Data Validation tool adds and calculates a number of fields that further contextualize the results of a BRAT run.

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
* `Hpe_Categor`: The category of the calculated historic capacity. It is determined based on the `oCC_HPE` (the calculated historic capacity), as follows:
  * If oCC_HPE = 0, Hpe_Categor = "None"
  * If 0 < oCC_HPE <= 1, Hpe_Categor = "Rare"
  * If 1 < oCC_HPE <= 5, Hpe_Categor = "Occasional"
  * If 5 < oCC_HPE <= 15, Hpe_Categor = "Frequent"
  * If 15 < oCC_HPE, Hpe_Categor = "Pervasive"
* `
* `mCC_EXtoHPE`: The ratio between existing and historic capacity. Calculated by dividing `oCC_EX` by `oCC_HPE`.
* `ConsVRest`: A reclassification of the `oPBCR_CR` field from the [conservation restoration model](/Documentation/Tutorials/8-ConservationRestoration.html) based on surveyed dam locations, with categories including:
  * *Immediate: Beaver conservation* - reaches classified as "easiest -low-hanging fruit" with at least 25% of existing dam capacity already occupied by surveyed dams
  * *Immediate: Potential Beaver Translocation* - reaches classified as "easiest - low-hanging fruit" with less than 25% of existing dam capacity occupied by surveyed dams
  * *Mid Term: Process-based Riparian Vegetation Restoration* - reaches classified as "Straight Forward - Quick Return"
  * *Long Term: Riparian Vegetation Reestablishment* - reaches classified as "Strategic - Long-Term Investment"
  * *Low Capacity Habitat* - reaches classified as "NA"
* `BRATvSurv`: The ratio between the estimated existing capacity count and the surveyed dam capacity count

Additionally, the tool adds a field named `Snapped` to the input beaver dams which designates whether each dam location was "snapped" to the network and therefore used in the validation or not. 

### Caveats 

Currently the Data Validation tool is limited by the distance and relationship of dam survey locations to the NHD line. The NHD network is a rough approximation of a stream network, and often the true stream does not directly correspond with the location of the NHD line due to meandering and side channels that are not represented in the NHD. Because dams are snapped to the nearest segment of the NHD network, short reaches can be assigned multiple dams while longer adjacent reaches are assigned fewer. This causes surveyed dam densities to be overestimated on the short reaches and underestimated on the long reaches. 

![Original validation issue]({{ site.baseurl }}/assets/images/Summary_Report_Caveat1.png)

To remedy this BRAT has integrated multichannel line segments from the original NHD file that warrant the classification of a perennial network. BRAT was previously not able to handle multichannel features. This has not fixed all these cases but many of them, because these slower flows in multichannel clusters can result in refuge from high streampower which can results in blown out or breached dams.

![Multichannel/Anabranch incorporated into the model]({{ site.baseurl }}/assets/images/Summary_Report_Caveat2.png)

<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/8-ConservationRestoration"><i class="fa fa-arrow-circle-left"></i> Back to Step 8 </a>
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/10-SummaryProduct"><i class="fa fa-arrow-circle-right"></i> Continue to Step 10 </a>
</div>	
------
<div align="center">

	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>
