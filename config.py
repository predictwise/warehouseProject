__author__ = 'zcq'
#coding:utf-8

import os

#配置数据库
basedir = os.path.abspath(os.path.dirname(__file__))
#当前目录下的warehouse.db数据库
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'warehouse.db')
SQLALCHEMY_COMMIT_ON_TEARDOWN = True

#支持Flask的唯一纯python全文搜索引擎Whoosh
WHOOSH_BASE = os.path.join(basedir, 'search.db') #配置

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

#pagination
MODELS_PER_PAGE = 10

#全文搜索最大返回结果数
MAX_SEARCH_RESULTS = 20