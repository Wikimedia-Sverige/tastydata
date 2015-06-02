#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# By: André Costa, Wikimedia Sverige
# License: MIT
# 2015
#
# From a json of data and a json of str to qLabel matches generate one
# html+css per restaurant using the style developed by Midas N at
# https://github.com/MidasN/WikimediaTastydata
#
# TODO: Add support for dish-categories
#
import codecs
import json

qMatches = {}
block = '  '


def run(dataFile, mathchesFile, directory=u'.'):
    '''
    Given a data file and an output directory generate one html+css per
    restaurant to said directory. Also generates an index page.
    '''
    global qMatches
    # load datafile
    f = codecs.open(dataFile, 'r', 'utf8')
    data = json.load(f)
    f.close()

    # load qMatches
    f = codecs.open(mathchesFile, 'r', 'utf8')
    qMatches = json.load(f)
    f.close()

    i = 0
    index = []
    for restaurantData in data:
        i += 1
        index.append(makeRestaurant(i, restaurantData, directory))

    # make html from index
    f = codecs.open(u'%s/index.html' % directory, 'w', 'utf8')
    f.write(makeIndex(index))
    f.close()


def makeRestaurant(no, restaurantData, directory):
    '''
    Given a restaurantData object and an id-no create the required
    html and css files.
    @return restaurantData['name']
    '''
    dishes = []
    for dishData in restaurantData['dishes']:
        dishes.append(makeDish(dishData))

    # make intro
    txt = intro(restaurantData['name'], no)

    # add title
    txt += u'''
%s<p class="restaurant-name"><mark>%s</mark></p>
%s<ul class="menu flow-text">''' % (4*block, restaurantData['name'], 4*block)
    # add dishes
    txt += ''.join(dishes)

    # footer
    txt += u'''
%s</ul>
%s</div>
%s<div class="row footer">
%sAdapted by <a href="http://wikimedia.se">Wikimedia Sverige</a> based on work by <a href="http://denny.vrandecic.de">Denny Vrandecic</a>. Funded by <a href="http://vinnova.se">Vinnova</a>.
%s<br />''' % (3*block, 2*block, 2*block, 3*block, 3*block)

    # add imageref
    txt += u'''
%sImage: <a href="https://commons.wikimedia.org/wiki/File:%s">%s</a> by %s, license: %s''' % (3*block, restaurantData['bg_img'].replace(' ', '_'), restaurantData['bg_img'], restaurantData['bg_credit'], restaurantData['bg_license'])

    # add outro
    txt += outro()

    # output
    f = codecs.open(u'%s/%r.html' % (directory, no), 'w', 'utf8')
    f.write(txt)
    f.close()

    # make css
    css = makeCss(restaurantData['colour'],
                  restaurantData['active_colour'],
                  restaurantData['bg_img'])
    f = codecs.open(u'%s/%r.css' % (directory, no), 'w', 'utf8')
    f.write(css)
    f.close()

    # return name for index
    return restaurantData['name']


def makeDish(dishData):
    '''
    Given a dish object return a formated string
    '''
    indent = 6
    ingredients = []
    for ingredientData in dishData['ingredients']:
        ingredients.append(makeIngredient(ingredientData, indent+1))

    # add title (and possibly coment)
    txt = u'\n%s<li>' % ((indent-1)*block)
    txt += u'\n%s<p class="dish">' % (indent*block)
    txt += addQlabel(dishData['name'], indent+1)
    if 'cmt' in dishData.keys():
        txt += addComment(dishData['cmt'], indent+2)

    # add price
    txt += u'\n%s<span class="price">%s</span>' % ((indent+1)*block, dishData['price'])
    txt += u'\n%s</p>' % (indent*block)

    # ingredients with wrapper
    txt += u'''
%s<p class="ingredient">%s
%s</p>''' % ((indent*block), ', '.join(ingredients), (indent*block))
    # close
    txt += '\n%s</li>' % ((indent-1)*block)

    return txt


def makeIngredient(ingredientData, indent):
    '''
    Given an ingredient object return a formated string
    '''
    txt = addQlabel(ingredientData['name'], indent)
    if 'cmt' in ingredientData.keys():
        txt += addComment(ingredientData['cmt'], indent+1)
    return txt


def addComment(cmt, indent):
    '''
    Given a cmt string add it inside brackets
    '''
    txt = addQlabel(cmt, indent)
    # If brackets are not wrapped tightly then spaces sneak in
    return txt.replace('<span', '(<span').replace('</span>', '</span>)')


def addQlabel(entity, indent):
    '''
    Given a text string look for the equivalent Qno.
    If one is found then return ahref + encoded span otherwise just
    span.
    '''
    i = '' + indent * block
    if entity in qMatches.keys():
        return u'''
%s<a href="#" title="%s" data-toggle="popover" data-trigger="focus" data-placement="auto" data-content="Data not loaded yet :/" data-html="true">
%s<span class="qlabel" its-ta-ident-ref="http://www.wikidata.org/entity/%s">%s</span>
%s</a>''' % (i, entity, (indent+1)*block, qMatches[entity], entity, i)
    else:
        return u'''
%s<span>%s</span>''' % (i, entity)


def intro(name, no):
    return u'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <title>%s</title>
    <!-- Universal Language Selector CSS -->
    <link href="lib/jquery.uls/css/jquery.uls.css" rel="stylesheet" type="text/css"/>
    <link href="lib/jquery.uls/css/jquery.uls.grid.css" rel="stylesheet" type="text/css"/>
    <link href="lib/jquery.uls/css/jquery.uls.lcd.css" rel="stylesheet" type="text/css"/>
    <!-- Bootstrap and Main CSS files -->
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css" rel="stylesheet" type="text/css">
    <link href="main.css" rel="stylesheet" type="text/css"/>
    <!-- Menu-specific CSS that overrides Bootstrap and Main -->
    <link href="%r.css" rel="stylesheet" type="text/css">
    <!-- Custom fonts -->
    <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700" rel="stylesheet" type="text/css">
    <link href="https://fonts.googleapis.com/css?family=Droid+Serif:400,700,400italic,700italic" rel="stylesheet" type="text/css">
    <link href="https://fonts.googleapis.com/css?family=Roboto+Slab:400,100,300,700" rel="stylesheet" type="text/css">
    <!-- Scripts -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js" type="text/javascript"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js" type="text/javascript"></script>
    <!-- Qlabel libraries -->
    <script src="lib/jquery.qlabel.js" type="text/javascript"></script>
    <!-- Universal Language Selector libraries -->
    <script src="lib/jquery.uls/src/jquery.uls.data.js" type="text/javascript"></script>
    <script src="lib/jquery.uls/src/jquery.uls.data.utils.js" type="text/javascript"></script>
    <script src="lib/jquery.uls/src/jquery.uls.lcd.js" type="text/javascript"></script>
    <script src="lib/jquery.uls/src/jquery.uls.languagefilter.js" type="text/javascript"></script>
    <script src="lib/jquery.uls/src/jquery.uls.regionfilter.js" type="text/javascript"></script>
    <script src="lib/jquery.uls/src/jquery.uls.core.js" type="text/javascript"></script>
    <script src="menu.js" type="text/javascript"></script>
  </head>
  <body>
    <div class="container-fluid">
      <div class="row header">
        <button type="button" class="btn btn-primary uls-trigger">Select language</button>
      </div>
      <div class="row">''' % (name, no)


def outro():
    return u'''
      </div>
    </div>
  </body>
</html>'''


def makeCss(colour, active_colour, img):
    img_url = u'https://commons.wikimedia.org/wiki/Special:Redirect/file?wptype=file&wpvalue=%s' % img.replace(' ', '+')
    return u'''body{
    background-image: url("%s");
}

mark,
.menu,
.btn-primary {
    border-color: %s;
    background-color: %s;
}

.btn-primary:hover,
.btn-primary:focus,
.btn-primary:active,
.btn-primary.active {
    border-color: %s;
    background-color: %s;
}
''' % (img_url, colour, colour, active_colour, active_colour)


def makeIndex(index):
    txt = u'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <title>Tastydata restaurant index</title>
    <!-- Bootstrap and Main CSS files -->
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css" rel="stylesheet" type="text/css">
    <link href="main.css" rel="stylesheet" type="text/css"/>
    <!-- Menu-specific CSS that overrides Bootstrap and Main -->
    <link href="index.css" rel="stylesheet" type="text/css">
    <!-- Custom fonts -->
    <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700" rel="stylesheet" type="text/css">
    <link href="https://fonts.googleapis.com/css?family=Droid+Serif:400,700,400italic,700italic" rel="stylesheet" type="text/css">
    <link href="https://fonts.googleapis.com/css?family=Roboto+Slab:400,100,300,700" rel="stylesheet" type="text/css">
    <!-- Scripts -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js" type="text/javascript"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js" type="text/javascript"></script>
  </head>
  <body>
    <div class="container-fluid">
      <div class="row">
        <p class="restaurant-name"><mark>Restaurant index</mark></p>
        <ul class="menu flow-text">'''

    for i in range(0, len(index)):
        txt += u'''
        <li>
          <p class="dish"><a href="%r.html">%r. %s</a></p>
        </li>''' % (i+1, i+1, index[i])

    txt += u'''
      </ul>
    </div>
    <div class="row footer">
      A project by <a href="http://wikimedia.se">Wikimedia Sverige</a>. Funded by <a href="http://vinnova.se">Vinnova</a>.
      <br />
      Image: <a href="https://commons.wikimedia.org/wiki/File:Wikidata_tastydata.svg">Wikidata tastydata</a> by <a href="https://commons.wikimedia.org/wiki/User:ArildV">Offnfopt</a>, license: <a href="https://creativecommons.org/publicdomain/zero/1.0/deed.sv" rel="license">CC0</a>
      </div>
    </div>
  </body>
</html>'''
    return txt
