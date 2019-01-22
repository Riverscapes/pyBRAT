---
title: BRAT v3X Outputs
---

The majority of users of BRAT will not actually run BRAT themselves, but instead will download BRAT outputs and summary products for investigating beaver and watershed management. In the text and videos tutorials below, we walk you through various ways to interact with the outputs of BRAT. We cover the outputs BRAT produces, provide a lookup table for investigative purposes, and provide illustrative videos into helpful ways to access and interrogate the outputs. 

## The BRAT Default Legends

### Capacity Layer
The **capacity model** outputs use the following color scheme to bin the output data (note each ≤300 m reach has a specific continuous dam density output). Existing capacity output is found in the `OCC_EX` field and historic capacity is found in the `oCC_HPE` field. This is a modeled number of dams per kilometer or mile  of the particular segment within the stream network. The following color scheme is used to illustrate these outputs:

   ![Legend_BRAT_DamDensity_WIDE]({{ site.baseurl }}/assets/images/Capacity_BRATv3X.png){: width="300" height="300"}

In addition, the capacity outputs and reach lengths were used to report estimated dam complex size `mCC_EX_CT` (for existing) and `mCC_HPE_CT` (for historic) fields. This is a modeled number of the dams on that particular segment of the stream network. The following color scheme is used to illustrate these outputs:

   ![Legend_BRAT_DamDensity_WIDE]({{ site.baseurl }}/assets/images/Dam_Complex_Size_BRATv3X.png){: width="300" height="300"}

### Management Layers
The **management output** layers include outputs that describe the limiting factors which contribute to unsuitable or limited beaver dam opportunities (`oPBC_UD`), risk categories which are based on land use and anthropogenic proximity (`oPBC_UI`), and finally a measure of the effort exhibited to perform restoration or conservation in the segment (`oPCRC_CR`).  For the (`oPCRC_CR`) output a sub-set of the segments classified as 'Negligible Risk' and 'Minor Risk' (`oPBC_UI`) is used to focus restoration or conservation efforts. Segments that are 'Considerable Risk' or 'Some Risk' (`oPCRC_UI`) are defined as 'Other' for (`oPCRC_CR`) field. Further documentation and discussion/development of these layers can be found [here](https://github.com/Riverscapes/pyBRAT/issues/207). The following color schemes were used to define the management fields:

- **Unsuitable or Limited Beaver Dam Opportunities (`oPBRC_UD`)** identifies areas where beaver cannot build dams now, and also differentiates into anthropogenically and naturally limiting areas. The following color scheme is used to illustrate these distinctions:

  ![Legend BRAT Management Unsuitable or Limited Beaver Dam Opportunities]({{ site.baseurl }}/assets/images/Unsuitable_or_Limited_Opportunities.png){: width="300" height="300"}

- **Potential Risk Areas (`oPBRC_UI`)** identifies areas -- streams that are close to human infrastructure or high land use intensity and where the capacity model estimates that beavers can build dams. The layer/map is called ‘areas beavers can build dams, but could be undesirable’ and is broken out into: "Considerable Risk", "Some Risk", "Minor Risk", and "Negligible Risk". The following color scheme is used to illustrate these distinctions:

  ![Legend BRAT Management Areas Beavers Can Build Dams, but Could Be Undesirable]({{ site.baseurl }}/assets/images/Anthropogenic_Risk.png){: width="300" height="300"}

- **Restoration or Conservation Opportunities (`oPCRC_CR`)** identifies opportunities where low-risk restoration and conservation opportunities exist for using beaver in stream conservation
  and restoration. This management output consists of the following categories: i) ‘easiest - low
  hanging fruit’ has capacity, just needs beaver if beaver ar not there yet, ii) ‘straight forward - quick return’ is currently occasional capacity but historically was higher capacity, iii) ‘strategic’ is a currently degraded condition with historically higher capacity. These areas typically need long-term riparian recovery before beaver can be introduced (e.g. grazing
  management), and 4) ‘other’. The ‘other’ category is based on higher ‘risk’ of human-beaver conflict and lower existing dam building capacity (i.e., reaches that are likely not worth investing in beaver dam related conservation and restoration actions). The following color scheme is used to illustrate these distinctions:

  ![Legend BRAT Management Restoration or Conservation Opportunities]({{ site.baseurl }}/assets/images/Restoration_or_Conservation_Opportunities.png){: width="300" height="300"}

## Attribute Field Descriptions

Because shapefile field names are limited to ten characters, there is a limit to how descriptive those names can be. Below is a screen capture of the lookup table that describes what the attribute field names within the shapefiles, Layer Packages and KMZs corresponds to. The actual lookup table can be found [here](https://usu.box.com/s/ekjw3e2iuxafpj0ttl0uzdyh9ifydmtl) for closer inspection and a glossary of all current pyBRAT values can be found [here](http://brat.riverscapes.xyz/Documentation/Documentation%20by%20Version/Concepts/Glossary.html).

![Attribute_Table_BRATv3X]({{ site.baseurl }}/assets/images/BRAT_3X_Alias.png)

## Visualizing BRAT Outputs

### Web GIS Portal on DataBasin

If you are not a GIS user and you either don't have or don't want to install [Google Earth Desktop](https://www.google.com/earth/), you can visualize the results in an interactive [WebGIS Browser on DataBasin](http://databasin.org/datasets/1420ffb7e9674753a5fb626e2b830c1f) (currently only for Utah). 

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

## Management Outputs Overview



------
<div align="center">

	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>

