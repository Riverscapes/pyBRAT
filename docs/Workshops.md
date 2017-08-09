[![BRAT_Banner_Web]({{ site.baseurl }}/assets/Images/BRAT_Banner_Web.png)]({{ site.url }})

### April 2013 - Logan

### Purpose

Participants will learn about the beaver dam capacity model in BRAT and how to modify the model and run it for their own study areas. 

### Schedule

- 9:00 - 10:30 ish - [Background & Theory on Beaver ](http://brat.joewheaton.org/home/workshops/goog_634673309)[Restoration](http://brat.joewheaton.org/home/workshops/goog_634673309)[ Assessment Tool](http://etal.usu.edu/BRAT/Workshops/1-BRAT_Background.pdf)  ![img](http://brat.joewheaton.org/_/rsrc/1468872180390/home/workshops/april-2013---logan/pdfIcon.png)
- 10:30 - 10:45 - Break
- 10:45 - 12:00 - [Prepping your Data](http://etal.usu.edu/BRAT/Workshops/2-DataPrep.pdf)  ![img](http://brat.joewheaton.org/_/rsrc/1468872180390/home/workshops/april-2013---logan/pdfIcon.png)
- 12:00- 12:30 - LUNCH
- 12:30 - 1:30 - [Using LANDFIRE to run Vegetation Capacity Model](http://etal.usu.edu/BRAT/Workshops/3-VegCapacity.pdf)  ![img](http://brat.joewheaton.org/_/rsrc/1468872180390/home/workshops/april-2013---logan/pdfIcon.png)
- 1:30 - 2:30 - [Deriving Stream Power](http://etal.usu.edu/BRAT/Workshops/4-StreamPower.pdf)  ![img](http://brat.joewheaton.org/_/rsrc/1468872180390/home/workshops/april-2013---logan/pdfIcon.png)
- 2:30 -3:30 - [Running BRAT Dam Building Capacity Model](http://etal.usu.edu/BRAT/Workshops/5-RunningBRAT.pdf)  ![img](http://brat.joewheaton.org/_/rsrc/1468872180390/home/workshops/april-2013---logan/pdfIcon.png)
- 3:30 -4:00 -[ Interpreting Results, Extending Analyses & Verification](http://etal.usu.edu/BRAT/Workshops/6-InterpretingBRAT.pdf)  ![img](http://brat.joewheaton.org/_/rsrc/1468872180390/home/workshops/april-2013---logan/pdfIcon.png)



### What you need to do BEFORE Workhsop

Most of the day will be devoted to nuts and bolts of the GIS processing of BRAT. We'll need and want to move reasonably quick through the different steps and I want to make sure we don't digress into a basic ArcGIS training session (see [here](http://gis.joewheaton.org/assignments/labs/lab01) if you need a refresher). To facilitate this I am going to ask that all participants for the rest of the day will need to:

#### Prepare your Laptop

- Have ArcGIS 10 or later installed on their own laptop (I have licenses if folks need them), 
- Have [Geospatial Modeling Environment](http://www.spatialecology.com/gme/) Installed
- Have Matlab w/ fuzzy logic toolbox (I can come up with a work around for those that don't have access)

#### Choose your Study Watershed

Choose a tractably sized watershed or study area for workshop (e.g. Logan River Watershed as opposed to the Mississippi).



The data requirements for the beaver dam building capacity model we run are s[pelt out here](http://brat.joewheaton.org/home/documentation/manual-implementation/beaver-dam-capacity-model/1-input-data).

- Come prepared with raw inputs for one study area you want to run the capacity model for having:

- 1. Downloaded NHD or NHD+ **drainage network** for their study area from (e.g. [NHD from here](http://nhd.usgs.gov/data.html), [NHD+ from here](http://www.horizon-systems.com/NHDPlus/NHDPlusV2_data.php)). The choice won't be that critical for the purposes of our workshop, but we will discuss tradeoffs between the two datasets. See [1. Getting NHD Data](http://brat.joewheaton.org/home/workshops/april-2013---logan/1-getting-nhd-data) for detailed instructions. 
  2. Downloaded **10 m DEM** rasters (e.g. from [USGS Geospatial Data Gateway](http://datagateway.nrcs.usda.gov/)). See [2. Getting DEM Data](http://brat.joewheaton.org/home/workshops/april-2013---logan/2-getting-dem-data) for detailed instructions.
  3. Downloaded **existing LANDFIRE Vegetation **2008 layer for study area (30 m rasters) from [LANDFIRE](http://landfire.cr.usgs.gov/viewer/). See [3. Getting Vegetation Data](http://brat.joewheaton.org/home/workshops/april-2013---logan/3-getting-vegetation-data) for detailed instructions.

- If possible, please also come with at least a report from the [USGS National Streamflow Statistics](http://water.usgs.gov/osw/programs/nss/pubs.html) for the State(s) your watershed is located in. We will use regional curve regression equations from these reports to estimate baseflow and Q2 streampower. 

- You may also find it helpful to bring some context GIS layers, such as:

- - Hillshade 
  - Watershed Boundary (e.g. HUC6 or HUC8 from NHD's Watershed Boundary Dataset (WBD); available [here](http://viewer.nationalmap.gov/viewer/))
  - Administrative Boundaries (e.g. Property Ownership)

I will have backup datasets to use for each exercise, should someone's 'own' data fall short. 



#### Tutorials on Data Download

- [1. Getting NHD Data](http://brat.joewheaton.org/home/workshops/april-2013---logan/1-getting-nhd-data)
- [2. Getting DEM Data](http://brat.joewheaton.org/home/workshops/april-2013---logan/2-getting-dem-data)
- [3. Getting Vegetation Data](http://brat.joewheaton.org/home/workshops/april-2013---logan/3-getting-vegetation-data)



### Remote Participation

If you are joining us remotely for the Background & Theory Portion (9:00 - 10:30), please use the GoTo Meeting Links or numbers below. If you wish to run through the hands-on session, you will need to be in Logan.

> 1. Please join my meeting.
>
> [https://global.gotomeeting.com/meeting/join/299690645](https://global.gotomeeting.com/meeting/join/299690645)
>
> 2. Use your microphone and speakers (VoIP) - a headset is recommended. Or, call in using your telephone.
>
> United States: +1 (773) 897-3015
>
> Access Code: 299-690-645
>
> Audio PIN: Shown after joining the meeting
>
> Meeting ID: 299-690-645
>
> GoToMeeting®
>
> Online-Meetings made easy®



### Acknowledgements

This workshop was made possible by [Wilburforce](http://www.wilburforce.org/) and the efforts of Mary O'Brien at the [Grand Canyon Trust](http://www.grandcanyontrust.org/). Thanks to Enid Kelly and Wes James for assisting with set up.

![gct-logo2]({{ site.baseurl }}/assets/images/gct-logo2.gif)

![logo-wilburforce]({{ site.baseurl }}/assets/images/logo-wilburforce.gif)



Subpages (3): [1. Getting NHD Data]({{ site.baseurl }}/Workshops/1-GettingNHDData) [2. Getting DEM Data]({{ site.baseurl }}/Workshops/2-GettingDEMData) [3. Getting Vegetation Data]({{ site.baseurl }}/Workshops/3-GettingVegetationData)

