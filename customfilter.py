__author__ = 'zcq'
#coding:utf-8
import jinja2

def stringtodict(strDict):
    other = eval(strDict)
    return other

jinja2.filters.FILTERS['stringtodict'] = stringtodict