#!/usr/bin/env python3
from exceptions import *

import os
import sys
import re
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from datetime import datetime
import warnings

# Generalaj funkcioj
def fixwidth(cad, widthpad=80, charpad=' ', alignpad='center'):
    '''Provides advanced filling and aligning.
Prototype: string fixwidth(string cad, int widthpad=80, string charpad=' ', string alignpad='center')
Parameters:
* string cad: the string to be formatted
* int widthpad: Width in cols that will be formatted the string. By default 80
* string charpad: String which will be used to wrap the string. By default, the ASCII character 20.
* string alignpad: String that sets the align of the content. The values can be 'right', left, or 'center'. By default, 'center'.'''
    if len(str(cad))>int(widthpad): return str(cad)[:widthpad]
    else:
        if str(alignpad) == 'right': return str(cad).rjust(int(widthpad), str(charpad))
        if str(alignpad) == 'left': return str(cad).ljust(int(widthpad), str(charpad))
        if str(alignpad) == 'center': return str(cad).center(int(widthpad), str(charpad))

def invCenter(tuplecad, widthpad=80, charpad=' '):
    if len(str(tuplecad[0]) + str(tuplecad[1])) > int(widthpad): return (str(tuplecad[0]) + ' ' + str(tuplecad[1]))[:widthpad]
    else: return str(tuplecad[0]) + charpad*(widthpad-len(tuplecad[0])-len(tuplecad[1])) + str(tuplecad[1])

class transaction(object):
    '''Class for store a single transaction.
Init: __init__(self, string date, string desc, float amount, string *cat)
Methods:
* addCategories(string catlist): Add the specified categories from a string. The categories must be separated by a space character.
Attributes:
* list categories: a list containing a category per item
* date date: a datetime.date object containing the date of the transaction
* string description: a string containing a description about the transaction
* float amount: a float containing the amount of money in the transaction'''
    def addCategories(self, catlist):
        cat = re.findall(r'([A-Za-z_\-]*)', catlist)
        self.categories = []
        if cat:
            it = 0
            for i in cat:
                if not i:
                    it += 1
                    continue
                else:
                    self.categories.append(cat[it])
    def __init__(self, date, desc, amount, *cat):
        try:
            self.date=datetime.strptime(date,'%Y-%m-%d')
        except ValueError:
            raise DateNotValidError(date)
        self.description = desc
        if re.search(r'[a-zA-z]', amount):
            raise BadAmountValueError(amount)
        else:
            try:
                self.amount = float(eval(str(amount)))
            except:
                raise BadAmountValueError(amount)
        if cat:
            self.addCategories(cat)
        else:
            self.categories = []
    def __str__(self):
        strcat = ':'
        for i in self.categories:
            strcat = strcat + i
        if strcat != ':':
            strcat = strcat + ': '
        else:
            strcat = ''
        return('[' + self.date.strftime('%Y-%m-%d') + '] ' + strcat + self.description + ' $' + self.amount)

class account(object):
    def __init__(self, name, kind='cash', transactions = []):
        self.name = name
        self.type = kind
        self.transactions = []
        if transactions:
            self.transactions.extend(transactions)
            self.balance = self.__getBalance()
        else:
            self.balance = 0
    def __getBalance(self):
        if self.transactions:
            amount = 0.0
            for i in self.transactions:
                amount += eval(str(i.amount))
            return amount
    def addTransaction(tr,pos=0):
        if isinstance(tr, transaction) and pos:
            self.transactions.insert(pos-1, tr)
        else:
            self.transactions.append(tr)
        self.balance = self.__getBalance()
    def delTransaction(pos=0):
        if not pos:
            self.transactions.pop()
        else:
            self.transactions.pop(pos-1)
        self.balance = self.__getBalance()

class accountBook(object):
    def __init__(self, *config):
        if config:
            self.version = config[0].get('version')
            if not self.version:
                raise AttributeMissingError(self, 'version')
            self.currency = config[0].get('currency') if config.get('currency') else ''
            self.decimals = config[0].get('decimals') if config.get('decimals') else '2'
        else:
            self.version = ''
            self.currency = ''
            self.decimals = ''
        self.accounts = []
    def parseFile(self, filename):
        try:
            bookfile = minidom.parse(filename)
            xmlattr = bookfile.documentElement.attributes.items()
            dictattr = {}
        except:
            raise SyntaxError
        for i in xmlattr:
            attr, val = i
            dictattr[attr] = val
        self.version = dictattr.get('version')
        if not self.version:
            raise AttributeMissingError(filename, 'version')
        self.currency = dictattr.get('currency')
        if not self.currency:
            raise AttributeMissingError(filename, 'currency')
        self.decimals = int(dictattr.get('decimals'))
        if not self.decimals:
            raise AttributeMissingError(filename, 'decimals')
        accsElem = bookfile.documentElement.getElementsByTagName('accounts')[0]
        for i in accsElem.getElementsByTagName('account'):
            #typetmp = i.getAttribute('type')
            #if not typetmp:
            #    raise WrongTypeAccountError(i.toxml().partition('>')[0])
            nametmp = i.getAttribute('name')
            if not nametmp:
                raise AttributeMissingError(i.toxml().partition('>')[0], 'name')
            trelemtmp = i.getElementsByTagName('tr')
            trtmp = []
            for ii in trelemtmp:
                if ii.getAttribute('date') and ii.getAttribute('amount'):
                    if not ii.getAttribute('desc'):
                        warnings.warn('You should have a desc atrribute on \'' + ii.toxml() + '\'')
                    trobjtmp = transaction(ii.getAttribute('date'), ii.getAttribute('desc'), ii.getAttribute('amount'))
                    if ii.getAttribute('cat'):
                        trobjtmp.addCategories(ii.getAttribute('cat'))
                    trtmp.append(trobjtmp)
                else:
                    raise BadTransaction(ii.toxml())
            self.accounts.append(account(nametmp,'cash',trtmp))

    def __str__(self):
        ts = os.get_terminal_size()
        amountlen = 0
        catlen = 0
        for i in self.accounts:
            for ii in i.transactions:
                amounttmp = len(str(eval(str(ii.amount))))
                amountlen = amounttmp if amounttmp > amountlen else amountlen
                cattmp = len(':'+':'.join(ii.categories)+':')
                catlen = cattmp if cattmp > catlen else catlen
        amountlen = amountlen if amountlen >=6 else 6
        catlen = catlen if catlen >= 10 else 10
        sizecols = (10,80-11-10-catlen-amountlen,amountlen,catlen)  # [date, description, amountlen, categories]
        outstr = " Report sheet ".center(ts.columns,"=") + '\n'
        outstr = outstr + invCenter((' Version: ' + self.version, 'Currency: ' + self.currency + ' ')) + '\n'
        for i in self.accounts:
            outstr = outstr + '*'*80 + '\n'
            outstr = outstr + invCenter((' Account: ' + i.name, 'Type: ' + i.type + ' ')) + '\n\n'
            outstr = outstr + ' Date       | ' + fixwidth('Description', sizecols[1]) + ' | ' + fixwidth('Amount', sizecols[2]) + ' | ' + fixwidth('Categories', sizecols[3]) + '\n'
            outstr = outstr + '------------|-' + '-'*(sizecols[1]+1) + '|' + '-'*(sizecols[2]+2) + '|' + '-'*(sizecols[3]+1) + '\n'
            for ii in i.transactions:
                outstr = outstr + ' ' + ii.date.strftime('%Y-%m-%d') + ' | ' + fixwidth(ii.description, sizecols[1], ' ', 'left') + ' | ' + fixwidth(eval(str(ii.amount)), sizecols[2], ' ', 'right') + ' | ' + fixwidth(':'+':'.join(ii.categories)+':', sizecols[3], ' ', 'left') + '\n'
            outstr = outstr + '—'*80 + '\n' + ' Balance: $' + str(i.balance) + '\n\n'
        return outstr
    def createAccount(self, name, typeac):
        pass
    def deleteAccount(self, name, typeac):
        pass
