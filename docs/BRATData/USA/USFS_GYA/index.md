---
title: Greater Yellowstone Area BRAT
weight: 5
---
# Greater Yellowstone Area BRAT


This report presents an application of the [Beaver Restoration Assessment Tool 3.1.00](https://github.com/Riverscapes/pyBRAT/releases/tag/3.1.00)  (BRAT; [brat.riverscapes.xyz](http://brat.riverscapes.xyz/)) a tool for building realistic expectations for partnering with beaver in conservation and restoration (Macfarlane et al., 2017). In this application, we analyzed all the perennial rivers and streams of the Greater Yellowstone Area (GYA) outside of Montana. The Montana portion is currently being run by Montana Natural Heritage Program with Bureau of Land Management funding.

The backbone of BRAT is a capacity model developed to assess the upper limits of riverscapes (e.g., stream networks) to support beaver dam-building activities. The capacity model produces both an estimate of dam density (i.e. dams per length of stream) and an approximate count of how many dams the conditions in and surrounding a reach could support. Both existing and historic capacity were estimated using freely available spatial datasets to evaluate seven lines of evidence: 
* a reliable water source,
* vegetation within 30 m of the stream conducive to foraging and dam building,
* vegetation within 100 m of the stream to support expansion of dam complexes and maintain large beaver colonies, 
* the likelihood that dams could be built across the river/stream channel during low flows,
* the likelihood that a beaver dam on a river/stream can withstand typical floods,
* evidence of suitable river/stream gradient, and 
* evidence that river is too large for beaver to build dams and/or for dams to persist 

The vegetation component of the existing capacity model used 30 m resolution LANDFIRE vegetation data from 2016, whereas the historic capacity model used 30 m LANDFIRE data that represents an estimate of pre-European settlement vegetation based on 2016 models. We used fuzzy inference systems to combine these lines of evidence while accounting for categorical ambiguity and uncertainty in the continuous inputs driving the capacity models.

The estimated existing capacity of the Wyoming and Idaho portions of the GYA is 600,705 dams or roughly 10 dams/km. By contrast, the same model driven with estimates of historic vegetation types estimated capacity for the Wyoming and Idaho portions of the GYA at 809,234 dams or roughly 14 dams/km reflecting a 26% loss compared to historic capacity. Nearly all of the capacity loss from historic conditions can be explained in terms of riparian vegetation loss, vegetation conversion and degradation associated with high intensity land use including: 1) conversion of valley bottoms to urban and agricultural land uses, 2) overgrazing in riparian and upland areas, 3) conifer encroachment of wet meadow areas. Despite the losses in beaver dam capacity, GYA’s waterways are still capable of supporting and sustaining a substantial amount of beaver dam-building activity.

To aid practitioner and end-user groups in their decision making process, including what possible risks may arise from partnering with beaver, the BRAT model produces several management layers: (a) potential risk areas, (b) unsuitable or limited dam building opportunities, and (c) conservation and restoration opportunities. As such, the BRAT model identifies where streams are relative to human infrastructure and high intensity land use, and conservatively shows how that aligns with where beaver could build dams.

Ultimately, we hope the data and model results provided through this project will help guide the understanding of patterns in beaver dam capacity, potential risks to human infrastructure, as well as constraints and opportunities for using dam-building beaver in restoration and conservation. This information has huge potential for use in both GYA-wide planning efforts and individual watershed scale planning as well as design and on-the-ground implementation of conservation and restoration activities.



### Project Extent by Administrative Region

<iframe src="https://www.google.com/maps/d/embed?mid=1LSfus_FgcgOK8wfUh1ci2QeCt_GhvSYP" width="640" height="480"></iframe>

### GIS Data Layers

The GIS data layers that make up the maps are available for the perennial network of each HUC 8 watershed in KMZ, shapefile, and layer package formats. As an example Yellowstone Headwaters KMZ data is found [here](https://usu.box.com/s/v56ylbrcustutlu5o0m4p67qc9e106sn), shapefile [here](https://usu.box.com/s/2b67ynrsjn3d5tkas01z495f0tb5yq3h) and layer package formats [here](https://usu.box.com/s/f3c275yzj3qs29mvvhgh2th9h8rujc08). These data enable visualization and querying in GIS programs. We encourage the use of the layer packages because this format provides all the inputs, intermediates and outputs symbolized in a standard format which increases their usability. Viewing the KMZ files in Google Earth or ArcGIS Earth is an effective way to visualize and interrogate these output datasets because of the 3-D capabilities, image rendering speed and the quality of the base imagery. If you need help using the GIS data we have developed a series of tutorial videos and other instructions found [here](http://brat.riverscapes.xyz/Documentation/Tutorials/). For non-GIS users we have generated an Esri Story Map of the project that can be viewed here and a map atlas of BRAT outputs which, can be found [here](https://usu.box.com/s/mh77t79zi2up11sauo0zkfldtv3dcd0a).


### References:

Macfarlane, W. W., J. M. Wheaton, N. Bouwes, M. L. Jensen, J. T. Gilbert, N. Hough-Snee, and J. A. Shivik. 2017. Modeling the capacity of riverscapes to support beaver dams. Geomorphology 277:72-99.

------
<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/BRATData/"><i class="fa fa-info-circle"></i> Back to BRAT Datasets </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>
