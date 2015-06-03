#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# By: André Costa, Wikimedia Sverige
# License: MIT
# 2015
#
# Convert the menudata tsv to a json
# each field is either a string (wihtout a comma) or a
# quoted string, with a comma
#
import codecs
import json

qMatches = {}
block = '  '


def run(dataFile, mathchesFile):
    '''
    Given a data file and an output directory generate one html+css per
    restaurant to said directory. Also generates an index page.
    '''
    global qMatches
    # load datafile
    f = codecs.open(dataFile, 'r', 'utf8')
    lines = f.read().split('\n')
    f.close()

    # do restaurant data
    rId = -1
    dId = -1
    data = []
    for l in lines:
        if len(l) == 0:
            continue
        p = l.split('\t')

        if p[0] != '':
            # restaurant line
            rId += 1
            dId = -1
            data.append({
                'name': '%s' % p[0],
                'bg_img': '%s' % p[1],
                'colour': '%s' % p[2],
                'active_colour': '%s' % p[3],
                'bg_credit': '%s' % p[4],
                'bg_license': '%s' % p[5],
                'dishes': []
            })
        elif p[1] != '':
            # dish line
            dId += 1
            dData = {
                'name': '%s' % p[1],
                'price': '%s' % p[2],
                'ingredients': []
            }
            if len(p[3]) > 0:
                dData['cmt'] = '%s' % p[3]
            data[rId]['dishes'].append(dData.copy())
        elif p[2] != '':
            # ingredients line
            iData = {
                'name': '%s' % p[2]
            }
            if len(p[3]) > 0:
                iData['cmt'] = '%s' % p[3]
            data[rId]['dishes'][dId]['ingredients'].append(iData.copy())
        else:
            print 'shit!'

    f = codecs.open(u'%s.json' % dataFile[:-len('.tsv')], 'w', 'utf8')
    f.write(json.dumps(data, indent=4, ensure_ascii=False))
    f.close()

    # do matches
    f = codecs.open(mathchesFile, 'r', 'utf8')
    lines = f.read().split('\n')
    f.close()

    matches = {}
    for l in lines:
        if len(l) == 0:
            continue
        p = l.split('\t')
        if p[0] in matches.keys():
            print 'duplicate word: %s' % p[0]
        else:
            matches[p[0]] = p[1]

    f = codecs.open(u'%s.json' % mathchesFile[:-len('.tsv')], 'w', 'utf8')
    f.write(json.dumps(matches, indent=4, ensure_ascii=False))
    f.close()
