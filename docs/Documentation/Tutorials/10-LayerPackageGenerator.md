---
title: Step 10 - Layer Package Generator (Optional)
weight: 12
---
## Purpose of the Layer Package Generator (LPG)

The LPG is meant to be run after all other tools in the BRAT toolbox have been run. Over the course of running BRAT, the tool will automatically create layers for many of the inputs, intermediates and outputs. These layers allow the user to interrogate the model, to investigate what the outputs are derived from, to determine points of failure in the model should a result seem suspect, and possibly to identify why the model failed. Unfortunately, these layers are difficult to share, because they rely on a fixed, absolute file path to their data source. Emailing these layers or uploading them to a cloud storage site breaks that file path, making them useless.

Fortunately, layer packages do not share this weakness. They include the data source for their layers, and so can be transferred and used wherever the user wants them. However, creating them by hand is tedious, time-consuming, and subject to human error. The purpose of the LPG is to automate that process. The LPG will use the project folder structure to find the layers it needs, group them appropriately, and package them as a .lpk file.

## Running the Layer Package Generator

The LPG has two primary inputs: the output folder that the layer package should be based on and the name of the output layer package. An optional input is a clipping network. 

#### Inputs

* **Output folder**: BRAT automatically creates output folders, labelled "Output_01", "Output_02", etc. Layer Packages are meant to contain the outputs of only one run of BRAT. Choose which set of outputs you want to base your layer package off.

* **Layer package name**: Any set of characters is acceptable as input for the layer package name. If you choose to not give the tool a name for the layer package, it will default to "LayerPackage.lpk". 
* **Clipping network**: Network to which all outputs will be clipped. We highly recommend using the perennial network merged with canals as the clipping network because this network represents the areas where water is consistently available for beaver dam building, whereas the full NHD network includes weak intermittent and ephemeral streams which may only see water a few months out of every few years. 

As you run the tool, you may see the layers being rapidly grouped in the Table of Contents, with the map changing accordingly. This is normal. Arcpy requires the layers to be added to the Table of Contents before they can be grouped, which leads to this odd-looking behavior. Once the tool is done saving the layer package, they will be removed from the Table of Contents.

After the tool is run, there should be a layer package file in the  selected output folder. This file can be emailed or uploaded without breaking any links between the symbology and data sources.

[Link to a YouTube video demoing the Layer Package Generator](http://www.youtube.com/watch?v=iIVRsHuT7es)

## Possible Problems Running the LPG

This is a list of known problems that can prevent the LPG from running correctly, and troubleshooting steps to fix them.

#### An Existing Layer/Layer Package in the Table of Contents
Because the layers are grouped and referred to by name in the Table of Contents, having a layer or a layer package in the Table of Contents before running the LPG can lead to naming conflicts and layers being grouped in unexpected ways. Always make sure that the Table of Contents doesn't have any layers or layer packages in it before running the LPG. 

#### Non-standard Folder Structure
The LPG works by looking for layers in the folder structure. If the folders are not in the standard folder structure, created by the latest version of BRAT, the LPG will not work. If you are using data from an old run of BRAT, it may be worthwhile to just run the full toolbox again from start to finish. 

<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/9-DataValidation"><i class="fa fa-arrow-circle-left"></i> Back to Step 9 </a>




​	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/11-SummaryProduct"><i class="fa fa-arrow-circle-right"></i> Continue to Step 11</a>

</div>	



<div align="center">
</div>	
------

<div align="center">

```
<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
```

</div>