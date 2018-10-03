---
title: Anabrach Editing Tips
weight: 1
---

## About

The vast majority of BRAT runs in the FHC include identifying parts of the stream network that are anabranched (or multi-channeled) and distinguishing the main channel from the side channel.  

The reason for distinguishing the main channel from side channels is to help compensate for the horizontal alignment issues between the NHD and DEM datasets.  For example, reach stream power is derived from the DEM and then attributed to the NHD network.  Due to horizontal inaccuracies between the datasets the main channel can end up erroneously attributed with a lower stream power than a side channel.  More often than not this scenario results in BRAT predicting artificially high dam densities on side-channels whereas in reality these side-channels are optimal locations for beaver dams, BDAs, and high flow refugia.

## Steps

If tasked with running the anabranch handler tool you should follow these steps:

- Make sure to check the 'Find Clusters' box on the BRAT Table tool 
- If there are any major rivers that don't originate in the watershed add the upstream drainage area value to the 'iGeo_DA' field
- Run the ['Drainage Area Check'](http://brat.riverscapes.xyz/Documentation/Tutorials/StepByStep/3.1-DrainageAreaCheck) tool
- Manually edit the BRAT network classifying whether anabranched segments are the main channel vs side channel.  There are some general tips in [this video](https://youtu.be/JFzYE_Cnjjw).
- Run the ['Anabranch Handler'](http://brat.riverscapes.xyz/Documentation/Tutorials/StepByStep/3.2-BRATBraidHandler.html)  tool (formerly called the 'Braid Handler' tool)

