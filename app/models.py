__author__ = 'zcq'
#coding:utf-8

from app import db, app
import sys

#判断python版本是否大于3.0, 大于3.0的版本还不能用Whoosh
if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask_whooshalchemy as whooshalchemy


class Warehouseinfo(db.Model):
    #__searchable__字段中包含数据库中所有能被搜索并被建立索引的字段
    #即, "title"字段可以被全文搜索引擎搜索到
    __tablename__ = 'warehouseinfo'
    __searchable__ = ['title']

    id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(30))
    tags = db.Column(db.String(100))
    desc = db.Column(db.String(700))
    imgurl = db.Column(db.String(250))
    kmzurl = db.Column(db.String(250))
    imgfile = db.Column(db.String(30))
    kmzfile = db.Column(db.String(30))
    other = db.Column(db.String(100))


if enable_search:
    #whoosh_index()为Warehouseinfo模型初始化了全文搜索索引
    #即, 为"title"初始化了全文搜索索引
    whooshalchemy.whoosh_index(app, Warehouseinfo)