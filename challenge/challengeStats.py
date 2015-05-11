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


def getLabels(entities, dDict=None):
    MAXID = 50  # max number of ids per call
    if dDict is None:
        dDict = {}

    # max ids per call
    if len(entities) > MAXID:
        getLabels(entities[MAXID:], dDict)
        entities = entities[:MAXID]

    # single call
    jsonr = wdApi.httpPOST("wbgetentities", [
        ('props', 'labels'),
        ('ids', '|'.join(entities).encode('utf-8'))])

    # deal with problems
    if not jsonr['success'] == 1:
        print 'Some went wrong in getLabels()'

    # all is good
    pages = jsonr['entities']  # a dict
    for k, v in pages.iteritems():
        lang = v['labels'].keys()
        dDict[k] = lang

    return dDict


def getClaimQualifier(entity, claim, qualifier):
    '''
    given an entity, a claim/propery and a qualifier property this identifies
    the value of that qualifier (or all in case of several claims
    Requires the value to be a wikibase-entity
    '''
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


def makeTable(outinfo, entities, ministats):
    '''
    produces the desired wiki table
    '''
    txt = ''
    txt += u'In total there are %r languages that have labels in the list. \
             %r of them have more than 100 labels in their language. \
             %r have more than 200 labels in their language. \
             %r languages have all the labels - and will look perfect in \
             the menus!\n\n' % (ministats['total'],
                                ministats['100+'],
                                ministats['200+'],
                                ministats['done'])
    txt += u'In addition there are %r items with images and %r items with \
             at least one pronunciation.\n\n' % (ministats['images'],
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
    txt += '{| class="wikitable sortable"\n'
    txt += '|-\n'
    txt += '! Q item !! # has image !! # pronunciations\n'
    for e in entities:
        img = '{{no}}'
        pro = ''
        if e in outinfo['images']:
            img = '{{yes}}'
        if e in outinfo['sounds']:
            pro = '{{Q|%s}}' % '}}, {{Q|'.join(outinfo['sounds'][e])
            pro = pro.replace('{{Q|}}', 'no lang')
        txt += '|-\n'
        txt += '| {{Q|%s}} || %s || %s\n' % (e, img, pro)
    txt += '|}\n\n'

    return txt


def makeMinistats(outinfo, ministats, total):
    '''
    Some quick bucketing
    '''
    plus100 = 0
    plus200 = 0
    done = 0
    for lang, entities in outinfo['lables'].iteritems():
        if len(entities) == total:
            done += 1
        elif len(entities) >= 200:
            plus200 += 1
        elif len(entities) >= 100:
            plus100 += 1

    # add to dict
    ministats['done'] = done
    ministats['200+'] = plus200 + done
    ministats['100+'] = plus100 + plus200 + done
    ministats['total'] = len(outinfo['lables'].keys())

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
    wdApi = wikiApi.WikiDataApi.setUpApi(user=getpass(u'Username:'),
                                         password=getpass(),
                                         site=site,
                                         scriptidentify=scriptidentify)

# input params
infile = u'entities.json'
if fromConf:
    infile = u'%s%s' % (config.path, infile)
f = open(infile, 'r')
entities = json.load(f)
f.close()
outwikiPage = u'Wikidata:Menu_Challenge/statistics'

# get all labels
lDict = getLabels(entities)

# invert
allLang = {}
for k, v in lDict.iteritems():
    for lang in v:
        if lang in allLang.keys():
            allLang[lang].append(k)
        else:
            allLang[lang] = [k, ]

# claims
wdqApi = wdq.WDQApi.setUpApi(user='TastyData')
p18claims = wdqApi.getIdsWithClaim(entities, 'P18')
p443claims = wdqApi.getIdsWithClaim(entities, 'P443')

# process P443
p443langs = {}
for entity in p443claims:
    # P407 is the qualifier for language
    p443langs[entity] = getClaimQualifier(entity, 'P443', 'P407')

# output
outinfo = {}
outinfo['lables'] = allLang
outinfo['images'] = p18claims
outinfo['sounds'] = p443langs
ministats = {'images': len(p18claims), 'sounds': len(p443claims)}
makeMinistats(outinfo, ministats, len(entities))
wdApi.editText(outwikiPage,
               makeTable(outinfo, entities, ministats),
               u'Updated statistics',
               minor=True,
               bot=False,
               userassert=None)
print u'langs: %r, entities: %r' % (len(allLang.keys()), len(entities))
