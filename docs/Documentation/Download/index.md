---
title: Download
weight: 1
---

## BRAT

<a href="http://brat.riverscapes.net"><img class="float-right" src="{{ site.baseurl }}/assets/images/BRAT_Logo-wGrayTxt.png"></a> The current version of pyBRAT is a series of Python scripts with ArcPy dependencies deployed currently as an ArcGIS 10.4 or later toolbox. There are a few dependencies [described here]({{ site.baseurl }}/Documentation/Download/ComputerSetup) such as [NumPy_mkl](https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy). Additionally, the fuzzy inference system (FIS) in pyBRAT uses the [scikit-fuzzy](https://pypi.python.org/pypi/scikit-fuzzy) python library. The latest version of pyBRAT can be found here:

<div align="center">
	<a class="button large" href="https://github.com/Riverscapes/pyBRAT/releases/latest">
	    <i class="fa fa-download"></i>
	    &nbsp;&nbsp;pyBRAT Download</a>
</div>


The last stable release of pyBRAT (with ArcPy 10.x depenencies) was 3.1.0 ([latest realease](https://github.com/Riverscapes/pyBRAT/releases/latest)) and that was also published as: 

- Jordan Gilbert, Joe Wheaton, Wally Macfarlane, & Margaret Hallerud. (2019). pyBRAT - Beaver Restoration Assessment Tool (Python) (3.1.0). Zenodo. DOI: [10.5281/zenodo.7086388](https://doi.org/10.5281/zenodo.7086388)

A Riverscapes Consortium [Report Card for v 3.1.00 is available here](http://brat.riverscapes.net/Documentation/Status/Tool_ReportCard_3-1-00.html). 

####  Next Versions
Note pyBRAT as an ArcGIS toolbox is no longer supported as we have shifted our development focus to a Production-Grade [sqlBRAT](http://tools.riverscapes.net/BRAT) and ESRI is sunsetting support for 10.X. sqlBRAT is currently a command-line tool. 

### BRAT as a 'Tool'
Please note that most *users* of BRAT use the model outputs to inform planning, restoration, conservation and nuisance beaver management. Such *users* typically interact with the GIS layers in either a GIS, WebGIS interface or static map outputs (pdfs, pngs, hard copies). BRAT transparently packages all the inputs, intermediates, parameters, outputs and various realizations therein in a Riverscapes-compliant project for ease of sharing. As with all our [Riverscapes Tools](http://riverscapes.net/rc-tools.html), we are committed to making the source-code and models both open source and freely available. However, please recognize that pyBRAT is currently NOT a polished tool or piece of software, with an easy-to-use GUI interface or Add-In to ArcGIS (like [GCD](http://gcd.riverscapes.net) for example). We have packaged the scripts in an [Arc Toolbox](https://desktop.arcgis.com/en/arcmap/10.4/analyze/managing-tools-and-toolboxes/a-quick-tour-of-managing-tools-and-toolboxes.htm). We simply created this operational tool to make it easier for our own analysts to run the model. As the user-community for BRAT expands to more GIS model users, we have become [interested in refactoring BRAT into a polished, and professional GIS tool]({{ site.baseurl }}/Vision.html) and have scoped this with [North Arrow Research](http://northarrowresearch.com).   <a href="{{ site.baseurl }}/support.html"><i class="fa fa-battery-empty"></i></a>

------

## Source Code
### pyBRAT Source Code


For those wishing to view or modify the source code, the open source version of pyBRAT is available in the [pyBRAT repo](https://github.com/Riverscapes/pyBRAT) on GitHub. 

<div align="center">
	<a class="hollow button" href="https://github.com/Riverscapes/pyBRAT"> <i class="fa fa-file-code-o"></i>&nbsp;&nbsp;pyBRAT Source Code on GitHub <i class="fa fa-github"></i></a>
</div>
- Jordan Gilbert, Joe Wheaton, Wally Macfarlane, & Margaret Hallerud. (2019). pyBRAT - Beaver Restoration Assessment Tool (Python) (3.1.0). Zenodo. DOI: [10.5281/zenodo.7086388](https://doi.org/10.5281/zenodo.7086388)


### matBRAT Source Code
The Matlab versions of BRAT source code are available from the [matBRAT repo](https://github.com/Riverscapes/matBRAT) on GitHub.  The matBRAT code is a legacy version of BRAT, which is no longer maintained.  For the most current BRAT models use the pyBRAT code.

<div align="center">
	<a class="hollow button" href="https://github.com/Riverscapes/matBRAT"> <i class="fa fa-github"></i>&nbsp;&nbsp; matBRAT Source Code on GitHub </a>
</div>
------

## Sister Tools

<a href="http://riverscapes.net"><img class="float-left" src="{{ site.baseurl }}/assets/images/logos/RiverscapesConsortium_Logo_Black_BHS_200w.png"></a>
The PyBRAT source code is avialble on GitHub as part of the [Riverscapes Consoritum](http://https://github.com/Riverscapes) family of tools. 

<a href="http://rcat.riverscapes.net"><img class="float-right" src="{{ site.baseurl }}/assets/images/RCAT_Logo-wTxt.png"></a>
BRAT uses as one of its inputs a Valley Bottom, which can be derived in a variety of ways. We tend to use our own [Valley Bottom Extraction Tool](http://rcat.riverscapes.net/Documentation/Version_1.0/VBET.html) (VBET) to do this (one of BRAT's sister tools). VBET is part of the [Riparian Condition Assessment Toolbox](http://rcat.riverscapes.net) (RCAT).  Those interested in using BRAT, are often interested in riparian condition and may find the sister RCAT toolbox quite useful as well. RCAT uses similar inputs to BRAT, but is focused on assessing riparian condition instead of understanding the ability of the riverscape to support dam building activity by beaver. All the same, if riparian restoration is needed to increase capacity, RCAT can help give insights into types and causes of degradation and assessing realistic recovery targets. 

### UK BRAT - Beaver Capacity Modeling & Monitoring

Led by [Hugh Graham](https://github.com/h-a-graham) and partners at Exeter University ([Allan Puttock](https://geography.exeter.ac.uk/staff/index.php?web_id=A_Puttock), [Richard Brazier](https://geography.exeter.ac.uk/staff/index.php?web_id=Richard_Brazier) and others), BRAT was adpated for UK data. The Graham et al (2020) paper 
- Graham HA, Puttock A, Macfarlane WW, Wheaton JM, Gilbert JT, Campbell-Palmer R, Elliott M, Gaywood MJ, Anderson K, Brazier RE. 2020. Modelling Eurasian beaver foraging habitat and dam suitability, for predicting the location and number of dams throughout catchments in Great Britain. European Journal of Wildlife Research 66 : 42. DOI: [10.1007/s10344-020-01379-w](http://dx.doi.org/10.1007/s10344-020-01379-w)

The source code for the Beaver Dam Capacity model (v 1.2) is [here on Github](https://github.com/h-a-graham/BDC_V1.2)

That team also built [BeaverTools](https://github.com/h-a-graham/beavertools), which is a package that provides some standardised methods to monitor beaver populations and predict future population dynamics.  

- Hugh Graham. (2022). h-a-graham/beavertools: beavertools (v1.0.0). Zenodo. DOI: [10.5281/zenodo.6818269](https://doi.org/10.5281/zenodo.6818269)

See also: 
- Graham, Puttock, Chant, Elliott, Campbell-Palmer, Anderson, Brazier, (In Review); Monitoring, modelling and managing beaver populations at the catchment scale. 

------
<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Download/ComputerSetup"><i class="fa fa-info-circle"></i> Setup Instructions </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>
