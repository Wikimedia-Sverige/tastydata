#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# By: André Costa, Wikimedia Sverige
# License: MIT
# 2015
#
import WikiApi as wikiApi
import wdq
import json
from getpass import getpass


def getLabels(entities, dDict=None, redirects=None, lang=None):
    '''
    Given a list of entity ids this returns the known lables
    also, until T97928 is resolved, it returns a list of known redirects

    if lang is given then instead of returning a list of languages
    only that language, and its value is returned
    '''
    MAXID = 50  # max number of ids per call
    if dDict is None:
        dDict = {}
    # while T97928 remains unresolved
    if redirects is None:
        redirects = {}

    # max ids per call
    if len(entities) > MAXID:
        getLabels(entities[MAXID:], dDict, redirects, lang)
        entities = entities[:MAXID]

    # single call
    requestparams = [('props', 'labels'),
                     ('redirects', 'yes'),
                     ('ids', '|'.join(entities).encode('utf-8'))]
    if lang is not None:
        requestparams.append(('languages', lang.encode('utf-8')))
    jsonr = wdApi.httpPOST("wbgetentities", requestparams)

    # deal with problems
    if not jsonr['success'] == 1:
        print 'Some went wrong in getLabels()'

    # all is good
    pages = jsonr['entities']  # a dict
    for k, v in pages.iteritems():
        if lang is None:
            langs = v['labels'].keys()
            dDict[k] = langs
        else:
            if lang in v['labels'].keys():
                dDict[k] = v['labels'][lang]['value']
        # while T97928 remains unresolved
        if 'redirects' in v.keys():
            redirects[v['redirects']['from']] = v['redirects']['to']

    return dDict, redirects


def getClaimQualifier(entity, claim, qualifier):
    '''
    given an entity, a claim/propery and a qualifier property this identifies
    the value of that qualifier (or all in case of several claims
    Requires the value to be a wikibase-entity
    '''
    # cannot resolve redirects, per T97928
    jsonr = wdApi.httpPOST("wbgetclaims", [
        ('entity', entity.encode('utf-8')),
        ('property', claim.encode('utf-8'))])

    # deal with problems
    if 'claims' not in jsonr.keys():
        print 'Some went wrong in getClaimQualifier() for %s' % entity
        return []

    # all is good
    qualValues = []
    pages = jsonr['claims'][claim]  # a list
    for k in pages:
        try:
            vals = k['qualifiers'][qualifier]  # a list
            for v in vals:
                if v['datatype'] == 'wikibase-item':
                    qualValues.append('Q%r' % v['datavalue']['value']['numeric-id'])
        except KeyError:
            qualValues.append('')
    return qualValues


def makeTable(outinfo, entities, redirects, langLabels, ministats):
    '''
    produces the desired wiki table
    '''
    txt = ''
    txt += u'In total there are %r languages that have labels in the list. \
             %r of them have more than 100 labels in their language. \
             %r have more than 200 labels in their language. \
             %r languages have all the labels - and will look perfect in \
             the menus!\n\n' % (ministats['totalLang'],
                                ministats['100+'],
                                ministats['200+'],
                                ministats['done'])
    txt += u'In total there are %r labels for the %r items. \
             In addition there are %r items with images and %r items with \
             at least one pronunciation.\n\n' % (ministats['totalLabel'],
                                                 ministats['items'],
                                                 ministats['images'],
                                                 ministats['sounds'])
    txt += '__TOC__\n\n'
    # lables
    langs = sorted(outinfo['lables'].keys())  # ensure same order
    txt += '==Labels==\n'
    txt += '{| class="wikitable sortable"\n'
    txt += '|-\n'
    txt += '! Language code !! # done !! # left\n'
    for lang in langs:
        e = outinfo['lables'][lang]
        txt += '|-\n'
        txt += '| %s || %r || %r\n' % (lang, len(e), (len(entities) - len(e)))
    txt += '|}\n\n'

    # images and pronunciations
    txt += '==Images and pronunciations==\n'
    txt += 'To avoid the dreaded \'\'Lua error: not enough memory\'\' \
            languages for pronunciations use their english lables if \
            one is available, othewise their linked Q number. \
            \'\'no lang\'\' indicates that a pronunciations statment \
            is missing its {{P|P407}} value. \n'
    txt += '{| class="wikitable sortable"\n'
    txt += '|-\n'
    txt += '! Q item !! # has image !! # pronunciations\n'
    for e in entities:
        e_orig = e
        if e in redirects.keys():
            e = redirects[e]
        img = '{{no}}'
        pro = ''
        if e in outinfo['images']:
            img = '{{yes}}'
        if e in outinfo['sounds']:
            pro = ''
            for l in outinfo['sounds'][e]:
                if l in langLabels.keys():
                    pro += u'%s, ' % langLabels[l]
                else:
                    pro += u'{{Q|%s}}, ' % l
            pro = pro.replace('{{Q|}}', 'no lang')
            pro = pro[:-2]  # trim trailing ', '
        txt += '|-\n'
        txt += '| {{Q|%s}} || %s || %s\n' % (e_orig, img, pro)
    txt += '|}\n\n'

    return txt


def makeMinistats(outinfo, ministats, total):
    '''
    Some quick bucketing
    '''
    plus100 = 0
    plus200 = 0
    done = 0
    labels = 0
    for lang, entities in outinfo['lables'].iteritems():
        if len(entities) == total:
            done += 1
        elif len(entities) >= 200:
            plus200 += 1
        elif len(entities) >= 100:
            plus100 += 1
        labels += len(entities)

    # add to dict
    ministats['done'] = done
    ministats['200+'] = plus200 + done
    ministats['100+'] = plus100 + plus200 + done
    ministats['totalLang'] = len(outinfo['lables'].keys())
    ministats['totalLabel'] = labels


def raw_encoded_input(txt):
    return raw_input(txt).decode(sys.stdin.encoding or
                                 locale.getpreferredencoding(True))

# Check if running from config and set up Wikidata connection
# load config.py if present otherwise request input
site = 'https://www.wikidata.org/w/api.php'
scriptidentify = 'TastyData/1.0'
fromConf = False
try:
    import config
    fromConf = True
    wdApi = wikiApi.WikiDataApi.setUpApi(user=config.username,
                                         password=config.password,
                                         site=site,
                                         scriptidentify=scriptidentify)
except ImportError:
    # needed for input_raw
    import sys
    import locale
    user = raw_encoded_input('Username: ')
    wdApi = wikiApi.WikiDataApi.setUpApi(user=user,
                                         password=getpass(),
                                         site=site,
                                         scriptidentify=scriptidentify)

# input params
entities_file = u'entities.json'
page_file = u'page.txt'
if fromConf:
    entities_file = u'%s%s' % (config.path, entities_file)
    page_file = u'%s%s' % (config.path, page_file)
f = open(entities_file, 'r')
entities = json.load(f)
f.close()
f = open(page_file, 'r')
page = f.read()
f.close()

# output page
if fromConf:
    outwikiPage = config.outwikiPage
else:
    outwikiPage = raw_encoded_input('Wikidata page: ')

# get all labels
lDict, redirects = getLabels(entities)

# invert
allLang = {}
for k, v in lDict.iteritems():
    for lang in v:
        if lang in allLang.keys():
            allLang[lang].append(k)
        else:
            allLang[lang] = [k, ]

# deal with redirects until T97928 is resolved (and implemented in wdq)
reEntities = entities[:]  # clone
for r_from, r_to in redirects.iteritems():
    reEntities.remove(r_from)
    reEntities.append(r_to)

# claims
wdqApi = wdq.WDQApi.setUpApi(user='TastyData')
p18claims = wdqApi.getIdsWithClaim(reEntities, 'P18')
p443claims = wdqApi.getIdsWithClaim(reEntities, 'P443')

# process P443
p443langs = {}
for entity in p443claims:
    # P407 is the qualifier for language
    p443langs[entity] = getClaimQualifier(entity, 'P443', 'P407')

# convert lang Q-numbers to text to get around Lua memory error
langItems = []
for e, vals in p443langs.iteritems():
    langItems += vals
langItems = list(set(langItems))  # remove duplicates
langLabels_en, dummy = getLabels(langItems, lang='en')

# output
outinfo = {}
outinfo['lables'] = allLang
outinfo['images'] = p18claims
outinfo['sounds'] = p443langs
ministats = {'images': len(p18claims),
             'sounds': len(p443claims),
             'items': len(entities)}
makeMinistats(outinfo, ministats, len(entities))
wdApi.editText(outwikiPage,
               page.replace(u'{{{title}}}', u'Current statistics')
                   .replace(u'{{{text}}}', makeTable(outinfo,
                                                     entities,
                                                     redirects,
                                                     langLabels_en,
                                                     ministats)
                            ),
               u'Updated statistics',
               minor=True,
               bot=False,
               userassert=None)
print u'langs: %r, labels: %r, images: %r, sounds: %r, entities: %r' % (
      ministats['totalLang'],
      ministats['totalLabel'],
      ministats['images'],
      ministats['sounds'],
      ministats['items'])
