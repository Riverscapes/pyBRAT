---
title: Step 4 - iHyd Attributes
weight: 6
---

## Concept

The "iHyd" tool basically helps you prepare the hydrologic inputs to BRAT (namely a baseflow statistic and a typical flood statistic). Since BRAT is not a hydrologic model (i.e. a model that takes precipitation and a routes it as runoff across a watershed), we simply use regional curves to estimate a flow statistic for every reach. In other words, we can calculate upstream drainage area for every reach from the DEM, and use regional curves. These regonal curves take many forms, but generally relate discharge (y in figure below) to drainage area (x in figure below): 

![ihyd_code]({{ site.baseurl }}/assets/images/RegionalCurve.PNG)

## What you need

To populate the "iHyd" or hydrologic attributes to the input table you created in the [previous step]({{ site.baseurl }}/Documentation/Tutorials/StepByStep/3-BRATTableTool.html), regressions for predicting stream flow must first be developed or obtained for your model watershed, and then added to the model.  For example, these regional curves are what drives  [USGS's StreamStats Tool](https://streamstats.usgs.gov/ss/).  Note, you can maually develop your own regional curves for areas they are not defined based on analyzing avialable gage data

<div align="center">
	<a class="button secondary" href="https://streamstats.usgs.gov/ss/"><img src= "{{ site.baseurl }}/assets/images/logos/USGS_logo_White_50w.png"> StreamStats </a>
</div>

Once you have the regressions for both a typical low flow (we often use the flow exceeded 80% of the time) and a typical flood (we often use a two year recurrence interval flow), you must modify the script of the iHyd Attributes tool.  To do so, open the `iHyd.py` file (found inside the toolbox) in a python text editor.  [Pyscripter](https://sourceforge.net/projects/pyscripter/) or [Notepad++](https://notepad-plus-plus.org/) work well.

### Editing the `iHyd.py` to add your Regional Curves

For each area that you want to add a regression for a block of code must be added in the appropriate place.

![ihyd_code]({{ site.url }}/assets/images/ihyd_code.PNG)

The code block should follow this format:

``` python
elif float(region) == <choose an integer>:  # describe the area using the pound/hash sign in front
```
​    `Qlow` = <enter low flow regression here, always referring to drainage area as DAsqm>

​    `Q2` = <enter Q2 regression here, always referring to drainage area as DAsqm>

Note that in line 2 and 3 a TAB is used to indent.

As an example, say I want to add a regression for the Bridge Creek watershed in Oregon.  I would add the following block:
``` python
elif float(region) == 24: #oregon region 5
```

​    `Qlow = 1.31397 * (10 ** -20.5528) * (DAsqm ** 0.9225) * (16.7 ** 3.1868) * (6810 ** 3.8546)`

​   `Q2 = 1.06994 * (10 ** -9.3221) * (DAsqm ** 0.9418) * (16.7 ** 2.692) * (6810 ** 1.5663)` 

the script would then look like this:

![ihyd_code2]({{ site.url }}/assets/images/ihyd_code2.PNG)

After any necessary regressions have been entered, save the changes to the script, and then update the toolbox in ArcMap by right clicking on it and clicking "refresh".  The iHyd Attributes tool can now be run.

#### Inputs and Parameters:

![iHyd]({{ site.url }}/assets/images/iHyd.PNG)


- **Input BRAT Network**  - select the network that was created using the BRAT Table tool
- **Select Hydrologic Region** -  enter the integer that was used to identify the regression you want to use.  In the example here we used the number 24.


-----
## References

- [StreamStats Version 4 Factsheet](https://pubs.usgs.gov/fs/2017/3046/fs20173046.pdf)
- 


<div align="center">
	<a class="button" href="https://water.usgs.gov/osw/streamstats/ss_documentation.html"><img src= "{{ site.baseurl }}/assets/images/logos/USGS_logo_White_50w.png"> StreamStats Documentation </a>
</div>

#### Examples of Estimating Flow Statistics from Regional Curves in Utah

- Kenney, T.A., Wilkowske, C.D., Wright, S.J., 2008. [Methods for Estimating Magnitude and Frequency of Peak Flows for Natural Streams in Utah](http://pubs.usgs.gov/sir/2007/5158/pdf/SIR2007_5158_v4.pdf), U.S. Geological Survey, Prepared in cooperation with Utah Department of Transportation and the Utah Department of Natural Resources, Divisions of Water Rights and Water Resources.  
- Wilkowske, C.D., Kenney, T.A., and Wright, S.J., 2008. [Methods for estimating monthly and annual streamflow statistics at ungaged sites in Utah](http://pubs.usgs.gov/sir/2008/5230): U.S. Geological Survey Scientific Investigations Report 2008-5230, 63 pp. 



<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/3.2-BRATBraidHandler"><i class="fa fa-arrow-circle-left"></i> Back to Step 3.2 </a>
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Tutorials/StepByStep/5-BRATVegetationFIS"><i class="fa fa-arrow-circle-right"></i> Continue to Step 5 </a>
</div>	

------
<div align="center">

	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>