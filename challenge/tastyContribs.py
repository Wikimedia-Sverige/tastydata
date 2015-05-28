#!/usr/bin/python
# -*- coding: utf-8  -*-
'''
Identifies and lists contributors to to the challenge

Largely based on contributors.py in the ÖDOK project
'''

import codecs
import json
import challengeStats
import WikiApi as wikiApi
import contributors  # this one lives in the ÖDOK project


def run(start='2015-05-08', end=None):
    # connect to api
    site = 'https://www.wikidata.org/w/api.php'
    scriptidentify = 'TastyDataContribs/1.0'
    fromConf = False
    try:
        import config
        fromConf = True
        wdApi = wikiApi.WikiDataApi.setUpApi(user=config.username,
                                             password=config.password,
                                             site=site,
                                             scriptidentify=scriptidentify)
    except ImportError:
        from getpass import getpass
        user = challengeStats.raw_encoded_input('Username: ')
        wdApi = wikiApi.WikiDataApi.setUpApi(user=user,
                                             password=getpass(),
                                             site=site,
                                             scriptidentify=scriptidentify)

    # find changed pages
    entities_file = u'entities.json'
    if fromConf:
        entities_file = u'%s%s' % (config.path, entities_file)
    fin = codecs.open(entities_file, 'r', 'utf8')
    pageList = json.load(fin)
    fin.close()

    contribs, ministats, users = contributors.handleContributions(wdApi,
                                                                  pageList,
                                                                  start=start,
                                                                  end=end)
    userInfo = wdApi.getUserData(users)

    # outputs
    output_contrib_file = 'contribs.json'
    output_user_file = 'users.json'
    if fromConf:
        output_contrib_file = u'%s%s' % (config.path, output_contrib_file)
        output_user_file = u'%s%s' % (config.path, output_user_file)

    f = codecs.open(output_user_file, 'w', 'utf8')
    f.write(json.dumps(userInfo, indent=4, ensure_ascii=False))
    f.close()

    f = codecs.open(output_contrib_file, 'w', 'utf8')
    f.write(json.dumps(contribs, indent=4, ensure_ascii=False))
    f.close()
    print json.dumps(ministats, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    usage = '''Usage: python contributors.py start end
\tstart (optional): YYYY-MM-DD start date (default 2015-01-01)
\tend (optional): YYYY-MM-DD end date (default None)'''
    argv = sys.argv[1:]
    if len(argv) == 0:
        run()
    elif len(argv) == 1:
        run(start=argv[0])
    elif len(argv) == 2:
        run(start=argv[0], end=argv[1])
    else:
        print usage
# EoF
