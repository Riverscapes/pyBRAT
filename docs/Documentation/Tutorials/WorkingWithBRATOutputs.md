---
title: BRAT v2.0 Outputs
---

The majority of users of BRAT will not actually run BRAT themselves, but instead download BRAT outputs and interact with them. In the videos tutorials below, we walk you through various ways to interact with the outputs of BRAT. We cover options in order from simplest to most complex. 

## The BRAT Default Legends

### Capacity Layer
The **capacity model** outputs use the following color scheme to bin the output data (note each ≤250 m reach has a specific continuous dam density output). Existing capacity output is found in the `OCC_EX` field and potential (historic) capacity is found in the `oCC_PT` field. In areas that we have actual dam counts the translated capacity dam count are found in `mCC_EX_CT` (for exisiting) and `mCC_PT_CT` (for potential) fields: 

![Legend_BRAT_DamDensity_WIDE]({{ site.baseurl }}/assets/images//Legend_BRAT_DamDensity_WIDE.png)

### Conflict Potential Layer
The **conflict potential** model output (`oPC_Prob`) uses the following color scheme to describe the potential for human-beaver conflict:

![Legend_BRAT_ConflictProb]({{ site.baseurl }}/assets/images/Legend_BRAT_ConflictProb.png)

### Preliminary Management Layer
The **preliminary management** output layer (`oPBRC`) uses the following color scheme:

![Legend_BRAT_ManagementZones]({{ site.baseurl }}/assets/images/Legend_BRAT_ManagementZones.png)

## Attribute Field Descriptions

What do all those attribute fields correspond to?  Below is a table describing of all the outputs that appear in the BRAT KMZs and feature class attribute tables.

![Attribute_Table_Statewide]({{ site.baseurl }}/assets/images/Attribute_Table_BRATv2.0.png)

## Visualizing BRAT Outputs

### Web GIS Portal on DataBasin

If you are not a GIS user and you either don't have installed or don't want to install [Google Earth Desktop](https://www.google.com/earth/), you can visualize the results in an interactive [WebGIS Browser on DataBasin](http://databasin.org/datasets/1420ffb7e9674753a5fb626e2b830c1f) (currently only for Utah). 

<iframe width="560" height="315" src="https://www.youtube.com/embed/YCb1Gq3DORI" frameborder="0" allowfullscreen></iframe>

### Google Earth

If you want to browse around the BRAT outputs in [Google Earth](https://www.google.com/earth/), you can download KMZ files [from our data repository](http://brat.joewheaton.org/BRATData) and virtually fly away.

<iframe width="560" height="315" src="https://www.youtube.com/embed/gl8hn9xfeHg" frameborder="0" allowfullscreen></iframe>

### ArcGIS

If you have access to ArcGIS and are [comfortable getting around](http://gis.joewheaton.org/) in ArcGIS, this video shows you how to download the shapefiles and layer files and visualize them in ArcGIS.

<iframe width="560" height="315" src="https://www.youtube.com/embed/6sZ6Y5tGPso" frameborder="0" allowfullscreen></iframe>

Looking further into working with BRAT layer packages for interrogation and visualization.

<iframe width="560" height="315" src="https://www.youtube.com/embed/nTEgbR65EOo" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Queries in ArcGIS

If you want to interrogate the BRAT results and run queries to summarize them in more useful ways for your areas of interest, this video shows you how (warning > 20 minutes). 

<iframe width="560" height="315" src="https://www.youtube.com/embed/rLsnBZ6YcU0" frameborder="0" allowfullscreen></iframe>



------
<div align="center">

	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>

