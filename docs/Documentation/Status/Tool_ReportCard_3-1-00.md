---
title: RC- Tool Report Card v. 3.1.00
weight: 1
---

<a href="https://riverscapes.xyz"><img class="float-left" src="{{ site.baseurl }}/assets/images/rc/RiverscapesConsortium_Logo_Black_BHS_200w.png"></a>
The [Riverscapes Consortium's](https://riverscapes.xyz) Techncial Committee provides report cards for tools either deemed as "[riverscapes-compliant](https://riverscapes.xyz/Tools/#riverscapes-compliant)" <img  src="{{ site.baseurl }}/assets/images/rc/RiverscapesCompliant_24.png"> or "[pending riverscapes-compliance](https://riverscapes.xyz/Tools/#tools-pending-riverscapes-compliance)" <img  src="{{ site.baseurl }}/assets/images/rc/RiverscapesCompliantPending_28.png">. 

-----
# Grade
<a href="https://riverscapes.xyz/Tools/#tool-status"><img class="float-right" src="{{ site.baseurl }}/assets/images/rc/RiverscapesCompliantPending_128.png"></a> [pyBRAT 3.1.0](https://github.com/Riverscapes/pyBRAT/releases/tag/3.1.00) has been demed to be an [**Operational-Grade**]() that is [*pending riverscapes-compliance*](https://riverscapes.xyz/Tools/#tools-pending-riverscapes-compliance) on account of its:
<img class="float-left" src="{{ site.baseurl }}/assets/images/tools/TRL_badges_pngs/TRL_orange/3_badges+status+text/128w/TRL_(128px)4-orange-text.png">

- [Tool Status]({{ site.baseurl }}/Tools#tool-status) of **Operational-Grade** <img src="{{ site.baseurl }}/assets/images/tools/TRL_badges_pngs/TRL_orange/2_badges+status/24px/TRL_4_orange_24.png">
- Developer has indicated intent to modify code to produce [riverscapes projects]({{ site.baseurl }}/Tools/Technical_Reference/Documentation_Standards/Riverscapes_Projects/) as output of all analyses - Moving up to **Commercial-Grade** <img src="{{ site.baseurl }}/assets/images/tools/TRL_badges_pngs/TRL_orange/2_badges+status/24px/TRL_6_orange_24.png">
- Developer has indicated intent to add Project Type registration with [`program.xml`]({{ site.baseurl }}/Tools/Technical_Reference/Documentation_Standards/Riverscapes_Projects/Program/) in [Program Repo](https://github.com/Riverscapes/Program) 

--------
# Report Card
## Assessment  Info

| Attribute | Value | Comments |
|--------------------------------|-----------------------------------------------------------------------------|--------------------------------|
| :----------------------------- | :----------------------------- | :----------------------------- |
| Tool | [BRAT - Beaver Restoration Assessment Tool](https://brat.riverscapes.xyz) |  |
| Version Assessed | version [3.1.00](https://github.com/Riverscapes/pyBRAT/releases/tag/3.1.00) |  |
| Date Assessed | 3/18/20 |  |
| Assessment Team | Bailey & Wheaton |  |

## Tool Discrimination
This tool's [discrimnation](https://riverscapes.xyz/Tools/#model-discrimination) evaluation by the [Riverscapes Consortium's](https://riverscapes.xyz) is:

| Criteria | Value | Evaluation | Comments |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| :----------------------------- | :----------------------------- |  | :----------------------------- |
| Tool Interface(s) | <img src="{{ site.baseurl }}/assets/images/tools/ArcPyToolbox.png">:  [ArcPy Toolbox in ArcGIS](https://desktop.arcgis.com/en/arcmap/10.7/analyze/creating-tools/a-quick-tour-of-python-toolboxes.htm) | <i class="fa fa-battery-half" aria-hidden="true"></i> | Tool is a series of steps (wizard-driven) that is very specific to freely available US data. |
| Scale | Network (reach scale resolution, watershed extent) | <i class="fa fa-battery-full" aria-hidden="true"></i> | This tool has been applied across entire states, regions and watersheds, resolving detail down to 250 m to 300 m length reaches of riverscape. |
| Language(s) and Dependencies | Python with ArcPy, [NumPy_mkl](https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy) and <br>[scikit-fuzzy dependencies](https://pypi.python.org/pypi/scikit-fuzzy). | <i class="fa fa-battery-full" aria-hidden="true"></i> | Dependencies are well documented [here](http://brat.riverscapes.xyz/Documentation/Download/ComputerSetup.html#python-prerequisites). |
| Vetted in Peer-Reviewed Literature | Yes. One [paper](http://brat.riverscapes.xyz/references.html#peer-reviewed-publication): Macfarlane et al. (2015) | <i class="fa fa-battery-half" aria-hidden="true"></i> | The existing capacity model is vetted, and the historical capacity model is well described. The version in the publication is [2.0](https://github.com/Riverscapes/pyBRAT/releases/tag/v2.0.0), but the capacity model is basically the same in 3.0. Many of the risk, beaver management, conservation and restoration concepts have not yet been vetted in scholarly literature but have been applied, tested and vetted by many scientists and managers across the US and UK. |
| Source Code Documentation | Source code is clearly organized and documented | <i class="fa fa-battery-full" aria-hidden="true"></i> |  |
| Open Source | [open-source](https://github.com/Riverscapes/pyBRAT) <i class="fa fa-github" aria-hidden="true"></i> with [GNU General Public License v 3.0](https://github.com/Riverscapes/pyBRAT/blob/master/LICENSE) | <i class="fa fa-battery-half" aria-hidden="true"></i> | Open source code, but code requires ArcGIS licenses to run. |
| User Documentation | Includes: [Installation](http://brat.riverscapes.xyz/Documentation/Download/), [Tutorials](http://brat.riverscapes.xyz/Documentation/Tutorials/) with videos, and implementation tips | <i class="fa fa-battery-half" aria-hidden="true"></i> | The documentation is very comprehensive, but could be streamlined, contains many out of date components (e.g. applies to V 2.0). It would be helpful to separate tutorials from a command reference. Also it would be helpful to have conceptual references. |
| Easy User Interface | Tool is primarily accessed via ArcToolbox custom tools or command prompt. | <i class="fa fa-battery-quarter" aria-hidden="true"></i> | For a power ArcGIS user that is familiar with geoprocessing and really understands the model, they can make this work. However, the user experience is fragile, not very flexible and this is not an easy-to-use tool for end user. Most "users" or consumers of BRAT, do not run pyBRAT, but instead think of the "tool" as the outputs of the model. |
| Scalability | Tool can be batched, and development team made major strides in implementing batch-processing (typically applied to HUC-8s). | <i class="fa fa-battery-half" aria-hidden="true"></i> | The scalability is functional, but requires lots of custom scripting, has unnecessary hard-coding built in, and requires extensive manual pre-processing and preparation of data. |
|  Produces [Riverscapes Projects]({{ site.baseurl }}/Tools/Technical_Reference/Documentation_Standards/Riverscapes_Projects/) <img  src="{{ site.baseurl }}/assets/images/data/RiverscapesProject_24.png"> | Tool is outputing to disk data in a Rivescapes Project. | <i class="fa fa-battery-half" aria-hidden="true"></i> | Unfortunately, [3.1.00](https://github.com/Riverscapes/pyBRAT/releases/tag/3.1.00) is not producing Riverscapes Projects that are fully-compatible or registered with [RAVE](https://rave.riverscapes.xyz) |
| **TOOL GRADE** | <img class="float-left" src="{{ site.baseurl }}/assets/images/tools/TRL_badges_pngs/TRL_orange/2_badges+status/32px/TRL_4_orange_32.png"> Operational-Grade  | <i class="fa fa-battery-half" aria-hidden="true"></i> | This tool has been [applied extensively](http://brat.riverscapes.xyz/BRATData/) throughout the Western US and in the UK. It has been used extensively to inform policy and planning and state-wide, regional and watershed extents, but also to inform restoration planning and design at the reach-scale. Others have picked up and applied the model, but for the most part it has been implemented by the [USU ETAL team](http://etal.joewheaton.org). It is well deserving of an **Operational Grade**. |

**Evaluation Key:**
None or Not Applicable: <i class="fa fa-battery-empty" aria-hidden="true"></i> •
Minimal or In Progress: <i class="fa fa-battery-quarter" aria-hidden="true"></i> •
Functional: <i class="fa fa-battery-half" aria-hidden="true"></i> •
Fully Developed: <i class="fa fa-battery-full" aria-hidden="true"></i>  

## Tool Output Utility

| Criteria | Value | Evaluation | Comments |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|----------------------------------------------------------|--------------------------------|
| :----------------------------- | :----------------------------- | :----------------------------- | :----------------------------- |
| [RAVE](https://rave.riverscapes.xyz)- Compliant Riverscapes Projects <img  src="{{ site.baseurl }}/assets/images/data/RiverscapesProject_24.png">? | Produces Riverscapes Project, but not RAVE-compliant | <i class="fa fa-battery-quarter" aria-hidden="true"></i> | Simple refactoring needed and add Project Type registration with [`program.xml`]({{ site.baseurl }}/Tools/Technical_Reference/Documentation_Standards/Riverscapes_Projects/Program/) in [Program Repo](https://github.com/Riverscapes/Program) . |
| [RAVE](https://rave.riverscapes.xyz) Business Logic Defined? | Not for [3.1.00](https://github.com/Riverscapes/pyBRAT/releases/tag/3.1.00), but example exists for BETA [sqlBRAT](https://github.com/Riverscapes/sqlBRAT) that is functional | <i class="fa fa-battery-empty" aria-hidden="true"></i> | Simple to remedy. Projects do currently have Arc Layer Packages following project structure and entirely symbolized. |
| Riverscapes Projects hosted in public-facing [Riverscapes Warehouse(s)](https://riverscapes.xyz/Data_Warehouses/#warehouse-explorer-concept) <img src="{{ site.baseurl }}/assets/images/data/RiverscapesWarehouseCloud_24.png"> | No. Data is primarily on USU Box Servers and some on DataBasin.org. Users are pointed to where publicly available data exists from [here]({{ site.baseurl }}/BRATData/). | <i class="fa fa-battery-empty" aria-hidden="true"></i> | The data is very, very difficult to find from the inconsistent and incomplete [data pages]({{ site.baseurl }}/BRATData/). Warehousing is the goal, but in the meantime this could be made easier. |
| Riverscapes Projects connected to [Web-Maps](https://riverscapes.xyz/Data_Warehouses#web-maps) <i class="fa fa-map-o" aria-hidden="true"></i> | Not consistently. A proof of concept exist for [Idaho BRAT](https://riverscapes.github.io/BratMap/#/), but has not been cartographically curated. Similarly, a [DataBasin](https://databasin.org/datasets/1420ffb7e9674753a5fb626e2b830c1f) entry exists for [Utah BRAT](http://brat.riverscapes.xyz/BRATData/USA/UDWR_Utah/) | <i class="fa fa-battery-quarter" aria-hidden="true"></i> | All old data sets should be made Web Map accessible and clear about what version they were produced from and what years they correspond to (i.e. Riverscapes Project metadata) |
| Riverscapes Projects connected to Field [Apps](https://riverscapes.xyz//Data_Warehouses#apps---pwas) <img src="{{ site.baseurl }}/assets/images/tools/PWA.png"> | Not publicly. Some simple Arc Data Collector field apps have been used, but they are not reliable, scalable or deployable to external audiences. | <i class="fa fa-battery-quarter" aria-hidden="true"></i> | The workflows and forms are well tested and vetted. This needs funding to develop as commercial, professional-grade reliable web app. |

## Developer Intent

The BRAT [devleopment team]({{ site.baseurl }}/support.html) are actively seeking funding to build a **Commercial-Grade** <img src="{{ site.baseurl }}/assets/images/tools/TRL_badges_pngs/TRL_orange/2_badges+status/24px/TRL_7_orange_24.png"> version of BRAT, which would:
- Have an inviting [web-map interface](https://riverscapes.xyz/Data_Warehouses/#web-maps) so non GIS-users can discover BRAT runs and explore them and interrogate them.
- Making it easy for GIS users to download BRAT for use in [RAVE](https://rave.riverscapes.xyz) with [Riverscapes Projects](https://riverscapes.xyz/Tools/Technical_Reference/Documentation_Standards/Riverscapes_Projects/) <img  src="{{ site.baseurl }}/assets/images/data/RiverscapesProject_24.png">
- Encourage more user-interaction with BRAT outputs and crowd-sourcing of information to create ownership of outputs
  - Allow users to visualize dynamic outputs of BRAT through time 
  - Allow users to upload their own BRAT projects
  - Allow users to provide their own inputs locally (@ a reach) and produce local realizations.
  - Allow users to upload (or make) their own beaver dam and activity observations
  - Allow discovery of past BRAT runs in Warehouse
  - Present transparent ranking of level of BRAT model curation or [dataset rank](https://riverscapes.xyz/Data_Warehouses/#dataset-rank) and facilitate community commenting
  - Facilitate users paying modest prices (i.e. commercial) to have new runs or more carefully curated (validated, resolved, etc.) for a specific watershed and then share them with broader community

The development team at this point has already produced a beta version of a **Production-Grade** <img  src="{{ site.baseurl }}/assets/images/tools/TRL_badges_pngs/TRL_orange/2_badges+status/24px/TRL_4_orange_24.png"> version of BRAT ([sqlBRAT](https://github.com/Riverscapes/sqlBRAT) with no release yet), which will be necessary to support the **Commercial-Grade**  <img src="{{ site.baseurl }}/assets/images/tools/TRL_badges_pngs/TRL_orange/2_badges+status/24px/TRL_6_orange_24.png"> product. 

If you share this [vision]({{ site.baseurl }}/Vision.html), get in touch with the developers to support/fund the effort. 