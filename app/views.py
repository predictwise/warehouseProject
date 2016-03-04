__author__ = 'zcq'
#coding:utf-8

#第一个app是app文件夹, 第二个app是__init__.py中创建的Flask()对象
from app import app
from config import MODELS_PER_PAGE, MAX_SEARCH_RESULTS
from flask import render_template, redirect, url_for, g
from models import Warehouseinfo
from flask_paginate import Pagination
from forms import SearchForm
import ast

#在发送请求之前就给访问的用户创建一个SearchForm对象, 让他在所有的页面中都可以使用
#要达到这种效果, 必须要把SearchForm对象放入全局变量g中
#g保存的是当前请求的全局变量，不同的请求会有不同的全局变量，通过不同的thread id区别
@app.before_request
def before_request():
    g.searchForm = SearchForm()
    return

#从"/"和"/index"网址上都能访问到显示"hello zcq"的这个网页
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    print 'hello, i am index'
    #searchForm应是一个全局变量
    #g.searchForm = SearchForm()

    # 返回Paginate对象, 即pagina是一个Paginate对象,
    # 其中包含这些成员变量: has_next, has_prev, next_num, prev_num
    pagina = Warehouseinfo.query.paginate(page, MODELS_PER_PAGE, False)
    # 但目前pagina只是Paginate对象,需要用pagina.items来解析获取其中的id,title,author等属性
    models = pagina.items
    return render_template('index.html', title='Home', pagina=pagina, models=models)

@app.route('/detail/<id>')
#@app.route('/detail/<id>/<int:page>')
def detail(id):
    #查询id值为"id"的记录, 取第一条, 其实只有这一条, 因为id号是唯一的
    model = Warehouseinfo.query.filter_by(id=id).first()

    #此时的model.other是一个的字符串
    #所以要将String转换为dict
    #other = eval(model.other)
    #但是用eval()的安全性太差, 使用下面的方法来解决此问题
    other = ast.literal_eval(model.other)
    return render_template('detail.html', model=model, other=other)

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/search', methods=['POST'])
def search():
    if not g.searchForm.validate_on_submit():
        return redirect(url_for('index'))
    #url_for()的第一个参数是一个函数名, 这里代表下面的search_results()函数
    #第二个参数query, 是传入search_results()函数中的参数
    return redirect(url_for('search_results', query=g.searchForm.search.data))

@app.route('/search_results/<query>')
#参数query的值, 接受自上面的redirect()中的query
def search_results(query):
    print 'query: ', query
    results = Warehouseinfo.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    print 'results: ', results
    for result in results:
        print 'result: ', result
    return render_template('search_results.html', query=query, results=results)

