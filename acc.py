#!/usr/bin/env python3
import sys
from xml.dom import minidom
arbol = minidom.parse('accounts.xml')
cuentas = arbol.getElementsByTagName('account')
def getBalance(i):
  amount = 0
  j = i.getElementsByTagName('tr')
  for k in j:
    l = k.attributes.items()
    for m in l:
      if m[0] == 'amount':
        amount += float(m[1])
        break
  return amount
for i in cuentas:
  balance = getBalance(i)
  for y in i.attributes.items():
    if y[0] == 'name':
      print(y[1] + ": $" + str(balance))
      break

'''def getParams():
  i = {}
  for j in sys.argv:
#    if j =
  return

if __name__ == '__main__':
  params = getParams()'''
