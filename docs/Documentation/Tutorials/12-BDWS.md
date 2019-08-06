---
title: Step 12 - BDWS (Optional)
weight: 14
---

## Running the Beaver Dam Water Storage (BDWS) Tool

PyBRAT has an [experimental wrapper](https://konradhafen.github.io/beaver-dam-water-storage/) that feeds input into the BDWS tool, developed by Konrad Hafen. If you want to use this wrapper, currently you will need to download the development branch of pyBRAT. Full documentation on installing dependencies, preparing inputs, and running the tool are available [here](https://konradhafen.github.io/beaver-dam-water-storage/).

If you want to run BDFlopy, you will need to enter the optional inputs. If you do not enter these inputs, the tool will simply run the BDLoG and BDSWEA tools.

The tool will create a BDWS project folder in the folder given for the project root. It is recommended that you use the output folder as the project root, but it will run no matter where you choose to store the outputs. The project folder will have an Inputs, Modflow, and Output folder.

<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/11-SummaryProduct"><i class="fa fa-arrow-circle-left"></i> Back to Step 11 </a>
</div>	
------
<div align="center">

	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>
