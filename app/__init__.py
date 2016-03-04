__author__ = 'zcq'
#coding:utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import jinja2, ast

#实例化一个Flask对象,
#用__name__是让Flask知道到哪去找模板、静态文件之类的东西
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

#自定义过滤器
def stringtodict(strDict):
    other = ast.literal_eval(strDict)
    return other

#将自定义的过滤器注册到模板环境中
jinja2.filters.FILTERS['stringtodict'] = stringtodict

from app import views

