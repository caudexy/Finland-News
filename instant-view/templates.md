
# Instant View Templates
[Instant View](https://instantview.telegram.org/) allows Telegram users to view articles in a consistent way, with zero loading time. Since every website is different, Telegram needs a set of instructions for generating the instant view. These instructions are a set of XPath expressions pointing at the crucial parts of the webpage.

## Yle
```
# Latest available version of Instant View.
~version: "2.0"
title:    //div//h1
body:     //div/article/div[@class="text"]
```
## Iltalehti
```
# Latest available version of Instant View.
~version: "2.0"

title: //h1[@class="article-headline"]
body:  //div[@class="article-body"]
author: "ILTALEHTI"
author_url: "https://www.iltalehti.fi"
@remove: //img[@class='image image-show image-preview']
```
## Helsinki Times
```
# Latest available version of Instant View.
~version: "2.0"
title:    //div//h1[@class="article-title"]
body:     //div[@class="article-content-main"]
image:    //div[@class="pull-right item-image"]
```

## Good News Finland
```
# Latest available version of Instant View.
~version: "2.0"

title:    //h1[@class='mv0 pv4']
body:     //div[@class='center-column']
```
