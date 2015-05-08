#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
Quick and dirty module for making WDQ queries
'''

import WikiApi as wikiApi
# import pycurl

class WDQApi(wikiApi.WikiApi):
    '''
    When possible connect through the api
    Need to override setUpApi
    Should replace login/token/logout by dummyfunction to prevent
    these from being executed
    '''

    # dummy functions to prevent these from being executed
    def login(self, userName, userPass, verbose=True): self.dummyFunction(u'login')
    def setToken(self, token, verbose=True): self.dummyFunction(u'setToken')
    def setEditToken(self, verbose=True): self.dummyFunction(u'setEditToken')
    def clearEditToken(self): self.dummyFunction(u'clearEditToken')
    def logout(self): self.dummyFunction(u'logout')
    def dummyFunction(self, name):
        print u'%s() not supported by WDQApi' % name
        exit(2)

    @classmethod
    def setUpApi(cls, user, site='https://wdq.wmflabs.org', scriptidentify=u'tastyData/1.0', verbose=False):
        '''
        Creates a WDQApi object
        '''
        # Provide url and identify (using e-mail)
        wdq = cls('%s/api' % site, user, scriptidentify)

        # Set reqlimit for odok
        wdq.reqlimit = 50

        return wdq

    def apiaction(self, action, form=None):
        return self._apiurl + "?action=" + action

    def failiure(self, jsonr, debug=False):
        '''
        Standardised function to present errors
        '''
        return jsonr['status']['error']

    def clean(self, qList):
        '''
        removes the initial P/Q from an entry or list of entries
        '''
        if isinstance(qList, str) or isinstance(qList, unicode):
            return qList[1:]
        elif isinstance(qList, list):
            newList = []
            for q in qList:
                newList.append(q[1:])
            return newList
        else:
            print 'invalid object to clean()'

    def dirty(self, qList, prefix):
        '''
        the oposite of clean()
        '''
        if isinstance(qList, int):
            return '%s%r' % (prefix, qList)
        elif isinstance(qList, list):
            newList = []
            for q in qList:
                newList.append('%s%r' % (prefix, q))
            return newList
        else:
            print 'invalid object to dirty()'

    def getIdsWithClaim(self, idList, claim, members=None, debug=False):
        '''
        Returns list of all objects in idList also containing the given claim
        :param idList: A list of ids to look for
        :param claim:
        :param members: (optional) A list to which to add the results (internal use)
        :return: list odok objects (dicts)
        '''
        if members is None:
            members = []

        # Single run
        # action=query&list=embeddedin&cmtitle=Template:!
        q = 'ITEMS[%s] AND CLAIM[%s]' % (','.join(self.clean(idList)),
                                         self.clean(claim))
        jsonr = self.httpGET("get", [('q', q)], debug=debug)

        if debug:
            print u'getIdsWithClaim(): idList=%s\n' % idList
            print jsonr

        # find errors
        if not jsonr['status']['error'] == 'OK':
            print self.failiure(jsonr)
            return None

        members += jsonr['items']

        return self.dirty(members, 'Q')
# End of OdokReader()
