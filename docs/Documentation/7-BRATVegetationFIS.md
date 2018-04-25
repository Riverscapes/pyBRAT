---
title: Step 7 - BRAT Vegetation FIS
---

Now that the input file is totally prepared, you should be ready to run the fuzzy inference tools.  The first is the vegetation FIS, which estimates a stream segments capacity to support beaver dam building based solely on the quality of the streamside and riparian vegetation.  "The BRAT Vegetation FIS" tool must be run two times.  The first time predicts capacity based on historic vegetation, and the second predicts capacity based on existing vegetation.

![veg_fis]({{ site.baseurl }}/assets/images/veg_fis.PNG)

Inputs and Parameters:

- **Input BRAT Network**: select the segmented input network that contains all of the attributes from the previous 2 tools
- **FIS Type**: the first time you run the tool type: PT  the second time you run the tool type: EX
- **Set Scratch Workspace**: choose a file geodatabase where intermediate files will be dumped. The default is the ArcMap default GDB.

Click OK to run.

After the tool has been run both times, the network should now include the attributes "oVC_PT" and "oVC_EX"

[Continue to Step 8]({{ site.baseurl }}/Documentation/8-BRATCombinedFIS) ->

