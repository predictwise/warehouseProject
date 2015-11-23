__author__ = 'zcq'
#coding:utf-8

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class SearchForm(Form):
    #validators: 验证器
    #DataRequired验证器是检查相应域提交的数据是否为空
    search = StringField('search', validators=[DataRequired()])
