#!/usr/bin/env python3

class WrongAccountTypeError(TypeError):
    def __init__(self, obj):
        print('The \'' + obj + '\' element must have a type attribute with either \'out\' or \'in\' values')

class DateNotValidError(ValueError):
    def __init__(self, date):
        print('\'' + date + '\' isn\'t a valid date')

class BadAmountValueError(ValueError):
    def __init__(self, amount):
        print('\'' + amount + '\' must not contain alphabetical characters')

class AttributeMissingError(AttributeError):
    def __init__(self, objstr, attrib):
        print(objstr + ' must have a \'' + attrib + '\' attribute')

class BadTransaction(AttributeError):
    def __init__(self, objstr):
        print('The \''+ objstr + '\' element must have these attributes: \'date\', \'desc\' and \'amount\', and optionally, \'cat\'')
