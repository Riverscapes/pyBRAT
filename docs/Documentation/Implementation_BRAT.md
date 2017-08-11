---
title: Implementation - Beaver Restoration Assessment Tool (BRAT)
---

## Introduction

This documentation provides step-by-step instructions on manual implementation of the GIS and Fuzzy Inference System (FIS) processing tasks that were performed for the Utah statewide run of the Beaver Restoration Assessment Tool (BRAT), a decision support and planning tool for beaver management (Macfarlane et al. 2014 and Macfarlane et al. 2016). 

The backbone to BRAT is a capacity model developed to assess the upper limits of riverscapes to support beaver dam-building activities. The beaver-dam building capacity model uses both existing and historic vegetation layers to show current capacity and historic capacity. 

Capacity is estimated using readily available spatial data sets to evaluate five key lines of evidence: 

​	1) a perennial water source, 

​	2) availability of dam building materials, 

​	3) ability to build a dam at baseflow, 

​	4) likelihood of dams to withstand a typical flood, and 

​	5) likelihood that stream gradient would limit or completely eliminate dam building by beaver.

The decision support and planning tool side of BRAT uses rule sets to account for the recovery potential of riparian habitat and human conflict with beaver dam building to segregate the stream network into various conservation and restoration zones. 

By combining capacity and decision support approaches, researchers and resource managers have the information necessary to determine where and at what level reintroduction of beaver and/or conservation is appropriate. 

**Beaver Restoration Assessment Tool (BRAT) v 1.0** consists of an innovative combination of vector and raster based geoprocessing along with FIS processing. The processing steps are described in the following pages. The manual uses Escalante and Weber watershed data as examples and you'll be required to obtain and process the specific data for your study area.

**Beaver Restoration Assessment Tool (BRAT) v 2.0** consists of an ArcGIS Toolbox. The steps to use the ArcGIS Toolbox are described in the following pages. 



#### Steps

- [The Beaver Restoration Assessment Tool (matBRAT) - v 1.0 to 2.03](https://riverscapes.github.io/matBRAT/)

  ​
- The Beaver Restoration Assessment Tool (pyBRAT) - v 2.0
  - [0- Computer Setup]({{ site.baseurl }}/Documentation/pyBRAT/0-ComputerSetup)
  - [1- Input Data]({{ site.baseurl }}/Documentation/pyBRAT/1-InputData)
  - [2- Preprocessing]({{ site.baseurl }}/Documentation/pyBRAT/)
  - [3- BRAT Table Tool]({{ site.baseurl }}/Documentation/pyBRAT/3-BRATTableTool)
  - [4- iHyd Attributes]({{ site.baseurl }}/Documentation/pyBRAT/4-iHydAttributes)
  - [5- BRAT Vegetation FIS]({{ site.baseurl }}/Documentation/pyBRAT/5-BRATVegetationFIS)
  - [6- BRAT Combined FIS]({{ site.baseurl }}/Documentation/pyBRAT/6-BRATCombinedFIS)
- Ungulate Capacity Model
  - [1. Input Data]({{ site.baseurl}}/Documentation/Ungulate/1-InputData)
  - [2. Vegetation Input Derivation]({{ site.baseurl}}/Documentation/Ungulate/2-VegetationInput)
  - [3. Slope Input Derivation]({{ site.baseurl}}/Documentation/Ungulate/3-SlopeInput)
  - [4. Distance to Water Source Input - Derivation]({{ site.baseurl}}/Documentation/Ungulate/4-DistanceToWater)
  - [5. Running Probability of Ungulate Utilization FIS Model]({{ site.baseurl}}/Documentation/Ungulate/5RunningProbability)


### Prerequisites

This manual assumes a good working knowledge of ArcGIS 10.X (ESRI, 2013). For BRAT V 1.0 at least some exposure to the MathWorks Matlab R2012b Fuzzy Logic Toolbox (MathWorks, 2013) is required. 

**BRAT v 1.0:**

- ArcGIS 10.X and Spatial Analyst Extension
- GME - [Geospatial Modeling Environment](http://www.spatialecology.com/gme/)
- Matlab & the [Fuzzy Logic Toolbox](http://www.mathworks.com/products/fuzzy-logic/index.html)

**BRAT v 2.0:**

- ArcGIS 10.1 or later and Spatial Analyst Extension
- [Beaver Restoration Assessment Tool (BRAT) toolbox v2.0](https://s3-us-west-2.amazonaws.com/etalweb.joewheaton.org/Courses/Beaver/Excercises/Homework_02/BRAT_2.0.zip),

**References**

- Kenney, T.A., Wilkowske, C.D., Wright, S.J., 2008. [Methods for Estimating Magnitude and Frequency of Peak Flows for Natural Streams in Utah](http://pubs.usgs.gov/sir/2007/5158/pdf/SIR2007_5158_v4.pdf), U.S. Geological Survey, Prepared in cooperation with Utah Department of Transportation and the Utah Department of Natural Resources, Divisions of Water Rights and Water Resources.  


- Macfarlane W.W. , Wheaton J.M.**, **Bouwes N., Jensen M., Gilbert J.T., Hough-Snee N., and Shivick J. 2015. [Modeling the capacity of riverscapes to support beaver dams](https://www.researchgate.net/publication/285590037_Modeling_the_capacity_of_riverscapes_to_support_beaver_dams). Geomorphology. DOI: [10.1016/j.geomorph.2015.11.019](http://dx.doi.org/10.1016/j.geomorph.2015.11.019).
- Macfarlane W.W., Wheaton J.M., and Jensen, M.L. 2014. The Beaver Restoration Assessment Tool: A Decision Support & Planning Tool for Utah. Ecogeomorphology and Topographic Analysis Lab, Utah State University, Prepared for Utah Division of Wildlife Resources, Logan, Utah, 72 pp.
- Macfarlane WW and Wheaton J.M. 2013. [Modeling the Capacity of Riverscapes to Support Dam-Building Beaver - Case Study: Escalante River Watershed](http://etal.usu.edu/GCT/BRAT_Final_Report.pdf), Final Report Prepared for Grand Canyon Trust and the Walton Family Foundation, Logan, UT, 78 pp.


- Wilkowske, C.D., Kenney, T.A., and Wright, S.J., 2008. [Methods for estimating monthly and annual streamflow statistics at ungaged sites in Utah](http://pubs.usgs.gov/sir/2008/5230): U.S. Geological Survey Scientific Investigations Report 2008-5230, 63 pp. 