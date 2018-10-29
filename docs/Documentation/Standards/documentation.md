---
title: Documentation Standards
weight: 2
---

If I spell aa 

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

Below, I illustrate some edits using  [Typora](https://typora.io/) and my favorite local GIT client, [GitKraken]( [Typora](https://typora.io/)). I also am using a local version of [Jekyll](http://riverscapes.northarrowresearch.com/Technical_Reference/jekyll_toolbox.html#running-jekyll-locally) so I can preview the changes in a web browser before uploading or committing them. 

### Spellchecking in Typora

Always, spellcheck your markdown. In  [Typora](https://typora.io/) that is simple:
<iframe width="560" height="315" src="https://www.youtube.com/embed/VAOSId6Cyi4" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>


------
## Authoring New Content
### Making a New File & Folder

### Understanding Automatic Sidebar Navigation, Naming & Ordering

The Page Contents and [Site Contents](http://riverscapes.northarrowresearch.com/Technical_Reference/jekyll_toolbox.html#site-table-of-contents) are auto populated. Page contents are based on your use of headings (e.g. `## Heading 1, ### Heading 2, #### Heading 3...`) in your mark down. The Site Contents are based on the [front matter](http://riverscapes.northarrowresearch.com/Technical_Reference/jekyll_toolbox.html#front-matter) and [page sorting](http://riverscapes.northarrowresearch.com/Technical_Reference/jekyll_toolbox.html#page-sorting)  you populate at top of your page.

### Embedding a Video

The video I want to [embed](http://riverscapes.northarrowresearch.com/Technical_Reference/jekyll_toolbox.html#youtube-videos) is [https://www.youtube.com/watch?v=JFzYE_Cnjjw&feature=youtu.be](https://www.youtube.com/watch?v=JFzYE_Cnjjw&feature=youtu.be). 

Watch this [video](https://youtu.be/4UKe5BkzJEY) for how to embed a video.

<iframe width="560" height="315" src="https://www.youtube.com/embed/4UKe5BkzJEY" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>



### Embedding an Image

------
## Making your documentation consistent

------
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
