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
        vals = k['qualifiers'][qualifier]  # a list
        for v in vals:
            if v['datatype'] == 'wikibase-item':
                qualValues.append('Q%r' % v['datavalue']['value']['numeric-id'])
    return qualValues


def makeTable(outinfo, entities):
    '''
    produces the desired wiki table
    '''
    txt = ''

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

    # images and pronounciations
    txt += '==Images and pronounciations==\n'
    txt += '{| class="wikitable sortable"\n'
    txt += '|-\n'
    txt += '! Q item !! # has image !! # pronounciations\n'
    for e in entities:
        img = '{{no}}'
        pro = ''
        if e in outinfo['images']:
            img = '{{yes}}'
        if e in outinfo['sounds']:
            pro = '{{Q|%s}}' % '}}, {{Q|'.join(outinfo['sounds'][e])
        txt += '|-\n'
        txt += '| {{Q|%s}} || %s || %s\n' % (e, img, pro)
    txt += '|}\n\n'

    return txt

# input params
f = open('entities.json', 'r')
entities = json.load(f)
f.close()
outjson = u'statistik.json'
outwiki = u'statistik.wiki'

# setUp without login
wd_site = 'https://www.wikidata.org/w/api.php'
user = 'TastyData'
scriptidentify = 'TastyData/1.0'
reqlimit = 50
separator = 'w'
wdApi = wikiApi.WikiDataApi(wd_site, user, scriptidentify)

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
wdqApi = wdq.WDQApi.setUpApi(user='Lokal_Profil')
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
f = open(outjson, 'w')
f.write(json.dumps(outinfo))
f.close()
f = open(outwiki, 'w')
f.write(makeTable(outinfo, entities))
f.close()
print u'langs: %r, entities: %r' % (len(allLang.keys()), len(entities))
print u'images: %r, sounds: %r' % (len(p18claims), len(p443claims))
