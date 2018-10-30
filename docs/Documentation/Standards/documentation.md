---
title: Documentation Standards
weight: 2
---

If you are unsure how to make edits to our BRAT documentation, the following resources might be helpful. For basics:
- [How things look](https://riverscapes.github.io/TemplateDocs/styleguide.html) - and [corresponding markdown](https://github.com/Riverscapes/TemplateDocs/edit/master/styleguide.md)
- [Jekyll Themed Standards for Riverscapes Sites](http://riverscapes.northarrowresearch.com/Technical_Reference/jekyll_toolbox.html)
- [Documentation Standards](http://riverscapes.northarrowresearch.com/Technical_Reference/how_to_document_a_model.html)
- [The Base Template Site Theme & Helpful References](https://github.com/Riverscapes/TemplateDocs) and [what that looks like rendered](https://riverscapes.github.io/TemplateDocs/)
- [Icon Library we use in buttons](https://fontawesome.com/v4.7.0/icons/)

------
## Edits

### Making a Simple Edit in Browser
For simple edits to an existing Git-Hosted markdown page, you simply browse to the page in the [Code repository under `docs`](https://github.com/Riverscapes/pyBRAT/tree/master/docs), make edits, and then commit. See the example below:

<iframe width="560" height="315" src="https://www.youtube.com/embed/5wTvqMnCZio" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>


### Making a More Complicated Edit Localy & Pushing Up

You can use any text editor for editing markdown. [Typora](https://typora.io/) is a free text editor specifically for markdown that has the added advantage that it can render the code in the application so you can preview it. 

Below, I illustrate some edits using  [Typora](https://typora.io/) and my favorite local GIT client, [GitKraken]( [Typora](https://typora.io/)). I also am using a local version of Jekyll and Linux ([see here for how](http://riverscapes.northarrowresearch.com/Technical_Reference/jekyll_toolbox.html#running-jekyll-locally)) so I can preview the changes in a web browser before uploading or committing them. 

<iframe width="560" height="315" src="https://www.youtube.com/embed/aIqSoQwi0N4" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>



### Spellchecking in Typora

Always, spellcheck your markdown. In  [Typora](https://typora.io/) that is simple:
<iframe width="560" height="315" src="https://www.youtube.com/embed/VAOSId6Cyi4" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>

------
## Authoring New Content
### Making a New File & Folder

### Understanding Automatic Sidebar Navigation, Naming & Ordering

The Page Contents and [Site Contents](http://riverscapes.northarrowresearch.com/Technical_Reference/jekyll_toolbox.html#site-table-of-contents) are auto populated. Page contents are based on your use of headings (e.g. `## Heading 1, ### Heading 2, #### Heading 3...`) in your mark down. The Site Contents are based on the [front matter](http://riverscapes.northarrowresearch.com/Technical_Reference/jekyll_toolbox.html#front-matter) and [page sorting](http://riverscapes.northarrowresearch.com/Technical_Reference/jekyll_toolbox.html#page-sorting)  you populate at top of your page.

-------
## Some Common Components of Pages
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



------
## Making your documentation consistent

Always attempt to follow the template set by previous pages in the same parent folders (e.g. if writing a [command page]({{ site.baseurl }}/Documentation/Commands/) ).

### Making your documentation useful with hyperlinks

Poorly cross-referenced webpages (especially those on documented) are just annoying and a missed opportunity. Empathize with your audience enough to make sure they can find whatever you talk about. 

So an example  would be to mention that we have good ETAL BRAT Standards, but fail to link you to that page.

#### Example 1 - No references
_How its rendered:_
We have good ETAL BRAT Standards.

_How its written in markdown:_
``` markdown
We have good ETAL BRAT Standards.
```

_Annoying: without references this is vague._

#### Example 2 - Amateur hyperlink listed but not linked
_How its rendered:_  We have good ETAL BRAT Standards (http://brat.riverscapes.xyz/Documentation/Standards/).

_How its written in markdown:_ 
``` markdown
We have good ETAL BRAT Standards (http://brat.riverscapes.xyz/Documentation/Standards/).
```

_Annoying: as a user can't even click on this, they need to copy and paste it into their browser ._

#### Example 3 - Amateur hyperlink listed and linked
_How its rendered:_ We have good ETAL BRAT Standards ([http://brat.riverscapes.xyz/Documentation/Standards/](http://brat.riverscapes.xyz/Documentation/Standards/)).

_How its written in markdown:_
``` markdown
We have good ETAL BRAT Standards ([http://brat.riverscapes.xyz/Documentation/Standards/](http://brat.riverscapes.xyz/Documentation/Standards/)).
```

_Amateurish: do we need to list the URL out?._

#### Example 4 -  hyperlink only - preferred
_How its rendered:_
We have good [ETAL BRAT Standards](http://brat.riverscapes.xyz/Documentation/Standards/).

_How its written in markdown:_
``` markdown
We have good ETAL BRAT Standards We have good [ETAL BRAT Standards](http://brat.riverscapes.xyz/Documentation/Standards/).
```

_Our default standard._









------
<div align="center">
	<a class="hollow button" href="{{ site.baseurl }}/Documentation/Standards"><i class = "fa fa-check-square-o"></i> Back to ETAL Standards</a>
	<a class="hollow button" href="{{ site.baseurl }}/Documentation"><i class="fa fa-info-circle"></i> Back to Help </a>
	<a class="hollow button" href="{{ site.baseurl }}/"><img src="{{ site.baseurl }}/assets/images/favicons/favicon-16x16.png">  Back to BRAT Home </a>  
</div>
