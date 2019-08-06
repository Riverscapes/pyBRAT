---
title: Step 8 - Conservation Restoration Model
weight: 10
---

# Using the Conservation Restoration tool (Optional)

After running the BRAT tool to model capacity, the conservation restoration tool can be run to identify reasons why capacity is limited, areas where beaver dams could damage human infrastructure, and strategies for conserving and restoring beaver dams on the landscape.

## Running the Tool

Running the tool is fairly simple. The tool takes three inputs:
* The path to the BRAT project folder
* The Combined Capacity Model output network
* The name of the output

The optional beaver dam management strategies map requires the following additional inputs:

* A shapefile for surveyed beaver dam locations
* A shapefile for conservation protection areas
* A shapefile for conservation easements (optional)

## Output of the Tool
The tool produces seven new fields. Three of these fields come from the optional beaver dam management strategies map. The fields are as follows:
* `oPBRC_UI`: Areas beavers can build dams but could have undesirable impacts based on distance to infrastructure, land use intensity, and estimated beaver dam capacity. Categories include:
  * *Negligible Risk* 
    * Nearest infrastructure is at least 300 meters away
    * Existing dam capacity is zero
  * *Minor Risk* 
    * Nearest infrastructure is at least 100 meters away and existing dam capacity is less than 5 dams/km 
    * Nearest infrastructure is 100 - 300 meters away or landuse is agricultural, and existing dam capacity is not none
  * *Considerable Risk*
    * Nearest infrastructure is within 30 meters or landuse is high but existing dam capacity is less than 5 dams/km
    * Nearest infrastructure is within 100 meters and existing dam capacity is at least 5 dams/km
  * *Major Risk* 
    * The reach is on a canal
    * Nearest infrastructure is within 30 meters or land use intensity is high, and existing dam capacity is at least 5 dams/km
* `oPBRC_UI`: Identifies reasons for unsuitable or limited-dam building opportunities, including:
  * *Naturally Vegetation Limited* - historic and existing vegetation capacity are both zero
  * *Slope Limited* - slope is greater than 23%
  * *Anthropogenically Limited* - landuse is at least agricultural and no dams can be supported
  * *Stream Power Limited* - baseflow stream power is at least 190 cfs or high flow stream power is at least 2400 cfs and no dams can be supported
  * *Stream Size Limited* - areas where combined dam building capacity was set to zero because of the drainage area threshold set in the [Combined Capacity Model](/Documentation/Tutorials/7-BRATCombinedFIS)
  * *Potential Reservoir or Landuse Conversion* - historic vegetation capacity is zero but existing vegetation capacity is greater than zero
  * *Dam Building Possible* - existing capacity is not none
* `oPBRC_CR`: Possible conservation restoration opportunities based on capacity, departure from historic capacity, and land use. The categories describe levels of effort required for establishing beaver dams on the landscape and include:
  * *Easiest - Low-Hanging Fruit* - Reaches where beaver conservation or translocation can offer quick results with little risk of conflict based on high existing dam capacity, low departure from historic capacity, and low risk
  * *Straight Forward - Quick Return* - Reaches where short-term riparian vegetation restoration can quickly increase capacity with little risk of conflict based on some existing dam capacity, low departure from historic, and low intensity land use
  * *Strategic - Long-Term Investment* - Reaches where long-term riparian vegetation re-establishment is the only option based on low existing dam capacity, high historic dam capacity, and low land use
  * *NA* - Any reaches that do not fit into the above categories due to high risk, no existing capacity, or high land use intensity

**Strategies Map Fields**

* `ConsArea` - Binary field designating "Yes" if the reach occurs within a conservation/protection area and "No" otherwide
* `ConsEase` - Binary field designating "Yes" if the reach occurs within a conservation easement and "No" otherwise
* `ObsDam` - Binary field designating "Yes" if any surveyed beaver dams were observed along the reach and "No" if none were
* `DamStrat`: **This field is a work in progress.** Beaver dam management strategies based on current beaver dam locations and protected areas, including:
  * *1. Beaver conservation* - A stream reach with beaver dam building or lodges observed 
  * *2. Highest restoration potential* - A stream reach without recent beaver dam building that can likely
    support the greatest number of dams (2 or more dams) and is on a protected area or conservation easement
  * *3. High restoration potential* - A stream reach without recent beaver dam building that can likely support a high number of beaver dams (more than 2 dams per reach)
  * *3a. Vegetation restoration first-priority* - A stream reach that had more suitable historic vegetation than is currently present and may need replanting or grazing management before beaver can build dams
  * *4. Medium-low restoration potential* - A stream reach that can likely support between one and
    two dams per reach
  * *4a. Vegetation restoration first-priority* - A stream reach that had more suitable historic vegetation than is currently present and may need replanting or grazing management before beaver can build dams
  * *5. Restoration with infrastructure modification* - A stream reach that can likely support one or more dams, but where infrastructure (roads, culverts, railroads) is close to the stream and may limit beaver dam building
  * *6. Restoration with urban or agricultural modification* - A stream reach that can likely support one or more dams, but where urban or agricultural land uses may limit beaver dam building
  * *Other* - Low capacity habitat that does not fit into any of the above categories

<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/7-BRATCombinedFIS"><i class="fa fa-arrow-circle-left"></i> Back to Step 7 </a>
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/9-DataValidation"><i class="fa fa-arrow-circle-right"></i> Continue to Step 9 </a>
</div>	
------
<div align="center">

	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>
