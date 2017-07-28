### 1. Getting NHD Data

NHD stands for 

National Hydrography Dataset

 and is the surface water component of the United States Geologial Survey's National Map.  The NHD datasets include a wide variety of layers and there are multiple versions and multiple download sources. In the context of BRAT, there are three primary layers we are after:

1. A drainage network layer (in NHD, this is the NHDFlowline layer) - This is the layer which we will segment, and run our model on.
2. A watershed boundary (in NHD this will be a WBD or watershed boundary dataset) - This is the layer you will use to choose your watershed(s) of interest and clip your drainage network and other inputs to.
3. A waterbodies layer that includes ponds, reservoirs and lakes (in NHD this will be NHDWaterbody)

You don't have to use NHD or any specific version of NHD to run BRAT. As long as you can get a drainage network layer (whether you download it or derive it yourself), you can run BRAT. However, for most applications we reccomend using [NHDPlus](http://www.horizon-systems.com/NHDPlus/index.php) Version 2.1 , which (as of 2013) is the most current version of the NHD. You can download the original NHD data files [here](http://nhd.usgs.gov/data.html) from the USGS among many other sites.  However, we have found it easiest and fasted to download NHDPlus version 2.1 from [here](http://www.horizon-systems.com/NHDPlus/NHDPlusV2_data.php).

The video below walks you through the download.

<iframe width="560" height="315" src="https://www.youtube.com/embed/Tqw5ZJaU5vc" frameborder="0" allowfullscreen></iframe>



