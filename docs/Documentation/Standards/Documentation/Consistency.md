---
title: Consistency & Utility
weight: 4
---

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
