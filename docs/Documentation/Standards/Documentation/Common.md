---
title: Common Content
weight: 3
---

## Some Common Components of Pages

These days, there are many websites that allow you to create content (e.g. videos, tweets, spreadsheet, etc.) and embed it in your website. The git hosted web pages we use are written in markdown, but can recognize blocks of html like `<iframe>`, which are the most standard way to embed something. 

### Embedding a Video

The video I want to [embed](http://riverscapes.northarrowresearch.com/Technical_Reference/jekyll_toolbox.html#youtube-videos) is [https://www.youtube.com/watch?v=JFzYE_Cnjjw&feature=youtu.be](https://www.youtube.com/watch?v=JFzYE_Cnjjw&feature=youtu.be). 

Watch this [video](https://youtu.be/4UKe5BkzJEY) for how to embed a video.

<iframe width="560" height="315" src="https://www.youtube.com/embed/4UKe5BkzJEY" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>



### Embedding an Image
Of all the things to do in these markdown Git-hosted webpages, embedding an image is actually the most annoying and difficult (compared with WYSWYG web platforms like Weebly or Google Sites).  The reasons are it is not a drag and drop operation and you kind of need to know what you are doing. The steps are:
1. Get your image prepared.
2. Resize your image to desired size that it will appear on page (e.g. width of 300 pixels would be half width, 600 pixels would be fuller). You can use Photoshop or [Faststone Capture](http://www.faststone.org/FSCaptureDetail.htm) (for example).
3. It is best practice to then tinify (make smaller) your image using something like [TinyPng](https://tinypng.com/). These typically achieve 20 to 50% compression and help your images and whole page load faster.
4. Copy your image to the appropriate folder path (for BRAT, that is [`\docs\assets\images\`](https://github.com/Riverscapes/pyBRAT/tree/master/docs/assets/images) or subfolder and will be referred to by path as `"{{ site.baseurl }}/assets/images/"`)
5. Reference the image in your markdown page. This is done with following syntax for the [`BRAT_Logo-wGrayTxt.png`](https://github.com/Riverscapes/pyBRAT/blob/master/docs/assets/images/BRAT_Logo-wGrayTxt.png):

``` markdown
![BRAT_Logo-wGrayTxt]({{ site.baseurl }}\assets\images\BRAT_Logo-wGrayTxt.png)
```

And will look like:

![BRAT_Logo-wGrayTxt]({{ site.baseurl }}\assets\images\BRAT_Logo-wGrayTxt.png)

To make that image hyperlinkable (clickable), you enclose it in square brackets `[]` and then put hyperlink in `()` parentheses.  For example, to make image above clickable and linking to  [http://google.com](http://google.com)

``` markdown
[![BRAT_Logo-wGrayTxt]({{ site.baseurl }}\assets\images\BRAT_Logo-wGrayTxt.png)](http://google.com)
```
In this video, I illustrate how to do steps 2-5 of this with a screen shot taken in Faststone Capture:

<iframe width="560" height="315" src="https://www.youtube.com/embed/CucZ7tU0Amo" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

## Adding a Button

The best places to look for examples of buttons is on the [styleguide template](https://riverscapes.github.io/TemplateDocs/styleguide.html) - and [corresponding markdown](https://github.com/Riverscapes/TemplateDocs/edit/master/styleguide.md) or to copy a button you like from an existing page. Buttons can be:
- Just text: <a class="hollow button" href="{{ site.baseurl }}/">  Back to BRAT Home </a>
- Image and Text: <a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>
- or Icon and Text: <a class="hollow button" href="{{ site.baseurl }}/Documentation/Standards"><i class = "fa fa-check-square-o"></i> Back to ETAL Standards</a>

See [Icon Library](https://fontawesome.com/v4.7.0/icons/) for a list of icons that our Riverscapes recognize and you can use.  

The basic syntax for a button goes something like:
``` markdown
<a class="hollow button" href="{{ site.baseurl }}/Documentation/Standards"><i class = "fa fa-check-square-o"></i> Back to ETAL Standards</a>
```

In the video below, we walk you through how to make your own button to navigate to a specific page on the website <a class="hollow button" href="{{ site.baseurl }}/Documentation/Standards"><i class = "fa fa-check-square-o"></i> Back to ETAL Standards</a>  and an external URL (http://google.com) <a class="hollow button" href="{{ site.baseurl }}/Documentation/Standards"><i class = "fa fa-google"></i> Take me Away to Google</a>. 

<iframe width="560" height="315" src="https://www.youtube.com/embed/4kAN1dA819c" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>



### Embed a Slideshow

Its nice to be able to embed slideshows on a page:


<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vRQPbDbYvEaL9GXhS4QfhEBe0fwOq0XBZmBBSXZ5EJFOknRxkG1tdO2OVhuUC4TkSqQwMUF2aOQWSBs/embed?start=false&loop=false&delayms=3000" frameborder="0" width="550" height="450" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

This video walks you through how to:

<iframe width="560" height="315" src="https://www.youtube.com/embed/oZHBn5DrY0k" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>


------
<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Standards"><i class = "fa fa-check-square-o"></i> Back to ETAL Standards</a>
	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>
