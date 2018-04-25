---
title: Step 5 - BRAT Braid Handler
---

## Running the Braid Handler

Currently, there is no good way to find the drainage area values of segments where the river splits, braids, and eventually comes back together. The Flow Accumulation tool can only model a single river, and so gives segments either a much higher value than they should have, or a much lower value. Sometimes, the Flow Accumulation line doesn't accurately line up with the real world dominant stem. An example of this problem is depicted in the pictures below. 

##### Stream Network with Imagery
![FlowAccBasemap]({{ site.baseurl }}/assets/images/FlowAccBasemap.PNG)
##### Stream Network with Flow Accumulation Raster
![FlowAccExample]({{ site.baseurl }}/assets/images/FlowAccExample.PNG)

In an effort to more accurately model these sorts of stream networks, we have created an optional tool, called the Braid Handler, that identifies clusters of braided networks. It then assigns the sidechannels with a reasonable Drainage Area value and gives the dominant channel, if one exists, the highest Drainage Area value found in the cluster.

### Input Preparation
The Braid Handler requires the technician to go through and identify with imagery the mainstem of each cluster in the network. Because thiscan be a time intensive process, it is only recommended that the Braid Handler be run on watershed that contain large amounts of heavily braided streams. Outside of these watershed, the Braid Handler offers little benefit for the work put into running it.

The BRAT Table tool produces a stream network with the attributes "IsBraided" and "IsMainstem". In these fields, a value of 0 is "false", and a value of 1 is "true". If the stream is braided, they are automatically assigned a value of 0, "false", for the "IsMainstem" attribute. The most efficient way to identify areas that need editing is to select by attribute streams where "IsBraided"=1. Once this is done, every cluster of braided streams in the network will be hightlighted. Once that is done, visually identify what stream network is on the mainstem of the cluster, and set "IsMainstem" of each of those streams to 1.

Once the mainstems are identified, the user can run the Braid Handler. The Braid Handler will set the value of any stream where "IsMainstem" is 1 to the highest drainage area value found in the cluster, and will set the drainage area value of any other braided stream to 25 square kilometers. We chose 25 square kilometers because it is a small enough value that it will not preclude the possibility of beaver dams on that river. There is no good way to get an accurate value of the drainage area of these sidechannels, so 25 serves as a placeholder.

After the Braid handler is run, the user can run the rest of the tool as normal.

[Continue to Step 6]({{ site.baseurl }}/Documenation/6-iHydAttributes) ->