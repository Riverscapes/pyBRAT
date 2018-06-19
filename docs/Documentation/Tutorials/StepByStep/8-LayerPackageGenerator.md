---
title: Step 8 - Layer Package Generator (Optional)
weight: 10
---
## Purpose of the Layer Package Generator (LPG)

The LPG is meant to be run after all other tools in the BRAT toolbox have been run. Over the course of running BRAT, the tool will automatically create layers for many of the inputs, iintermediates and outputs. These layers allow the user to interrogate the model, to find what the outputs are derived from, and to determine points of failure in the model, should a result seem suspect. Unfortunately, these layers are difficult to share, because they rely on a fixed, absolute path to their data source. Emailing these layers or uploading them to a cloud storage site is likely to break that path, making them useless.

Fortunately, layer packages do not share this weakness. They include the data source for their layers, and so can be transfered and used wherever the user wants them. However, creating them by hand is tedious, time consuming, and subject to human error. The purpose of the LPG is to automate that process. The LPG will use the project folder structure to find the layers it needs, group them appropriately, and package them as a .lpk file.

## Running the Layer Package Generator

The LPG only has two input: the output folder that the layer package should be based on, and the name of the output layer package.

BRAT automatically creates output folders, labelled "Output_1", "Output_2", etc. Layer Packages are meant to contain the outputs of only one run of BRAT. Choose what output file you want to base your layer package off of.

Any set of characters is acceptable as input for the layer package name. If you choose to not give the tool a name for the layer package, it will default to "LayerPackage.lpk". 

As you run the tool, you may see the layers being rapidly grouped in the Table of Contents, with the map changing accordingly. This is normal. Arcpy requires the layers to be added to the Table of Contents before they can be grouped, which leads to this odd-looking behaviour.

After the tool is run, there should be a layer package file in the output folder selected. This file can be emailed or uploaded without breaking any dependencies.

```
<a href="http://www.youtube.com/watch?feature=player_embedded&v=iIVRsHuT7es" target="_blank"><img src="http://img.youtube.com/vi/iIVRsHuT7es/0.jpg" 
alt="Layer Package Generator Demo" width="240" height="180" border="10" /></a>
```

## Possible Problems Running the LPG

This is a list of known problems that can prevent the LPG from running correctly, and troubleshooting steps to fix them.

#### An Existing Layer Package in the Table of Contents
Because the layers are grouped by name in the Table of Contents, having a layer package in the Table of Contents before running the LPG can lead to layers being grouped in unexpected ways. Always make sure that the Table of Contents doesn't have any layer packages or group layers in it before running the LPG. 

#### Non-standard Folder Structure
The LPG works by looking for layers in the folder structure. If the folders are not in the standard folder structure, created by the latest version of BRAT, the LPG will not work. If you are using data from an old run of BRAT, it may be worthwhile to just run it again all the way through. 

<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/7-SummaryReport"><i class="fa fa-arrow-circle-left"></i> Back to Step 7 </a>
</div>	