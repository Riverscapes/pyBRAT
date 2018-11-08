---
title: Issuing a New Release
weight: 6
---

## When to issue a release 
Any time we have made sufficent changes to the code that they require testing or re-running models, we should package them up into a zip file and issue a [Github Relase](https://github.com/Riverscapes/pyBRAT/releases)

### How to tag
We should tag every release.  By default, if you don't check the 'pre release' check box, GitHub flags the release as latest.  Instead, please flag every `Pre Release` as such that we do internally. If we do testing or bug fixes on releases to the point we're happy with them, that's fine we can release a (e.g. `3.1.x`) as `Latest`. But on all these releases that we are making for our own purposes, just flag them as `Pre Release` as to not give any of the users out there the wrong idea that they are supported. 

Reserve the `Latest Release` (currently  BRAT `3.0.1`) for the latest stable, tested and documented release. If it is not stable, tested or documented, leave it as BETA in a `Pre Release`.

### Numbering Versions

Please always issue a release number of format X.Y.ZZ where:
- X is the major version number (currently we're t 3) and represent major platform shifts or complete refactoring of the code.
- Y is the major development version (currently 3.1) where a major family of development enhancements or bug fixes are taking place
- ZZ is the two digit (e.g. 01) version number for the current release (increment each release by one)

## Reference Isssues
See related discussion [here in issue #223](https://github.com/Riverscapes/pyBRAT/issues/223). 

------
<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Standards"><i class = "fa fa-check-square-o"></i> Back to ETAL Standards</a>
	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>
