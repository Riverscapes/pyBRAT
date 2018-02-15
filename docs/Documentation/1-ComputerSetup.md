---
title: Step 1 - Computer Setup & Installation
---
# Python Prerequisites
In order to use the [Beaver Restoration Assessment Tool (BRAT) Toolbox v2.x](https://github.com/Riverscapes/pyBRAT/releases/latest), your computer needs to have ArcGIS version 10.1 or later with the Spatial Analyst Extension as well as the scikit-fuzzy python module. Don't panic, even if you've never used a command line, you can follow these instructions. All this does is show you how to install a few dependencies (NumPy_mkl and scikit-fuzzy) that BRAT uses. The video below provides detailed instructions on installing the scikit-fuzzy python module.

<iframe width="560" height="315" src="https://www.youtube.com/embed/6-Je5jtH-j8" frameborder="0" allowfullscreen></iframe>

You can download the software menitoned in the video from these links:
- [PipInstall](https://pip.pypa.io/en/stable/installing/) - only if you don't have it (usually installs with ArcGIS 10.4 or later)
- [NumPy_mkl](https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy)
   - From the location you downloaded the NumPY_mkl file, run a command prompt and type: `c:\Python27\ArcGIS10.4\Scripts\pip install "numpy-1.13.3+mkl-cp27-cp27m-win32.whl"` to install NumPY
- To install the [scikit-fuzzy module](https://pypi.python.org/pypi/scikit-fuzzy), navigate in a command prompt to where Pip is located (e.g.  `c:\Python27\ArcGIS10.4\Scripts\`) and at command prompt type: `pip install scikit-fuzzy`. Note, the beauty of pip (Python Install Package) is that you don't have to go download these files, you just run ip and it downloads and installs them for you. 

[Continue to Step 2]({{ site.baseurl }}/Documentation/2-InputData) ->

# Installing BRAT
You can download the latest version of BRAT [here](https://github.com/Riverscapes/pyBRAT/releases/latest). The video below walks you through the install process.

<iframe width="560" height="315" src="https://www.youtube.com/embed/MVEXXMOPTBI" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
