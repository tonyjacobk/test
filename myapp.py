from flask import Flask, render_template,Blueprint,request,redirect,url_for
from aiven import get_rows,get_broker,get_stock,get_stock_partial,add_company
from price import get_price,load_price,get_date
import urllib.parse
from controls import brokers

rows_per_page=2
row_dict=load_price()
report_date=row_dict["Bhavdate"]
report_bp=Blueprint("report",__name__)
unique_sorted_brokers = sorted(set(brokers.values()))
# MySQL configurations
@report_bp.route('/')
@report_bp.route('/<int:page>')
def index(page=1):
    data,total_pages=get_rows(page,rows_per_page)
    get_price(data,row_dict)
    print(data)
    return render_template('index.html', data=data, page=page, total_pages=total_pages,report_date=report_date, brokers=unique_sorted_brokers)
@report_bp.route('/brk/<brok>')
@report_bp.route('/brk/<brok>/<int:page>')
def search_broker(brok,page=1):
    brok=urllib.parse.unquote(urllib.parse.unquote(brok))
    print(brok)
    data,total_pages=get_broker(page,rows_per_page,brok)
    get_price(data,row_dict)
    return render_template('index.html', data=data, page=page, total_pages=total_pages,broker=brok,report_date=report_date)
@report_bp.route('/stok/<stock>')
@report_bp.route('/stok/<stock>/<int:page>')
def search_stock(stock,page=1):
    print (stock)
    stock=urllib.parse.unquote(urllib.parse.unquote(stock))
    print(stock)
    data,total_pages=get_stock(page,rows_per_page,stock)
    get_price(data,row_dict)
    return render_template('index.html', data=data, page=page, total_pages=total_pages,company=stock,report_date=report_date)

@report_bp.route('/partialstok/<stock>')
@report_bp.route('/partialstok/<stock>/<int:page>')
def search_stock_partial(stock,page=1):
    print (stock)
    stock=urllib.parse.unquote(urllib.parse.unquote(stock))
    print(stock)
    data,total_pages=get_stock_partial(page,rows_per_page,stock)
    get_price(data,row_dict)
    return render_template('index.html', data=data, page=page, total_pages=total_pages,company=stock,report_date=report_date)

@report_bp.route('/addcomp', methods=['POST'])
def addcomp():
    company = request.form['company']
    broker = request.form['broker']
    report_date = request.form['date']
    URL=request.form["URL"]
    recomm=request.form['recommendation']
    target=request.form['target']
    site="manu"
    fname=request.form['filename']
    nsekey=request.form['nsekey']
    add_company(company,broker,URL,report_date,recomm,target,site,nsekey)
    return redirect(url_for('report.index'))





