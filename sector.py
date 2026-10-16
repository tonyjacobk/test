from flask import Flask, render_template, request, redirect, url_for,Blueprint
from aiven import get_rows,get_broker,connect,is_present
import urllib.parse
import math
from redis_man import res
from controls import brokers
#from megclass import MegaMan
sector_bp=Blueprint("sector",__name__)
unique_sorted_brokers = sorted(set(brokers.values()))
# Database configuration

def get_connection():
  return connect()
@sector_bp.route('/')
@sector_bp.route('/<int:page>')
@sector_bp.route('/filter/<key>/<value>/<int:page>')
def index(key=None, value=None, page=1):
    conn = get_connection()
    cursor = conn.cursor()

    page_size = 50
    offset = (page - 1) * page_size

    # Get search parameters
    search_by_broker = request.args.get('search_by_broker', '')
    search_by_company = request.args.get('search_by_company', '')

    # Base query
    base_query = "FROM gen_reports "
    sort_query= "ORDER BY report_date DESC "
    conditions = []
    params = []

    if key and value:
        conditions.append(f"{key} = %s")
        params.append(value)

    if search_by_broker:
        conditions.append("broker LIKE %s")
        params.append(f"%{search_by_broker}%")

    if search_by_company:
        conditions.append("company LIKE %s")
        params.append(f"%{search_by_company}%")

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    # Get total number of rows for pagination
    count_query = "SELECT COUNT(*) " + base_query + where_clause
    cursor.execute(count_query, tuple(params))
    total_rows = cursor.fetchone()['COUNT(*)']
    total_pages = math.ceil(total_rows / page_size)

    # Get data for the current page
    data_query = "SELECT * " + base_query + where_clause + f" ORDER BY report_date DESC LIMIT %s OFFSET %s"
    if  where_clause:
         data_query = "SELECT * " + base_query + where_clause + sort_query+f" LIMIT %s OFFSET %s"
  #  print(data_query)
    params.extend([page_size, offset])
    cursor.execute(data_query, tuple(params))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('sectorindex.html',
                           rows=rows,
                           page=page,
                           total_pages=total_pages,
                           key=key,
                           value=value,
                           brokers=unique_sorted_brokers,
                           search_by_broker=search_by_broker,
                           search_by_company=search_by_company)

@sector_bp.route('/delete', methods=['POST'])
def delete_bulk():
    print ("In delete")
    print (request.form)
    conn = get_connection()
    cursor = conn.cursor()
    del_list=request.form.getlist('delete_rows')
    for i in del_list:
     p=i.split("||")
     if "mega.co.nz" in p[3]: 
       res.set_a_value(p[3])

     cursor.execute("""
        DELETE FROM gen_reports 
        WHERE company=%s  AND report_date=%s
    """, (p[0],p[2]))
     conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('sector.index'))

@sector_bp.route('/save', methods=['POST'])
def save():
    data = (
        request.form['company'],
        request.form['broker'],
        request.form['URL'],
        request.form['date'],
        request.form['site'],
    )
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        REPLACE INTO reports 
        (company, broker, URL,  report_date, site) 
        VALUES (%s, %s, %s, %s, %s)
    """, data)
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('sector.index'))
@sector_bp.route('/move', methods=['POST'])
def move():
    print ("In Move")
    company = request.form['company']
    broker = request.form['broker']
    report_date = request.form['date']
    URL=request.form["URL"]
    recomm=request.form['recommendation']
    target=request.form['target']
    site=request.form['site']
    olddate=request.form['olddate']
    fname=request.form['filename']
    nsekey=request.form['nsekey']
    print(request.form)
    conn = get_connection()
    cursor = conn.cursor()

    print(company,broker,report_date)
    stat,reps=is_present(conn,company,broker,report_date)
    if not stat:
     cursor.execute("""
       INSERT INTO reports
        (company, broker, URL,  report_date,recommendation,target ,site,NSEKEY)
        VALUES (%s, %s, %s, %s, %s,%s,%s,%s)
    """, (company,broker,URL,report_date,recomm,target,site,nsekey))
    cursor.execute("""
        DELETE FROM gen_reports
        WHERE company=%s  AND report_date=%s
    """, (fname,olddate))

    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('sector.index'))

@sector_bp.route('/edit', methods=['POST'])
def edit():
    company = request.form['company']
    broker = request.form['broker']
    report_date = request.form['date']
    URL=request.form["URL"]
    site=request.form['site']
    olddate=request.form['olddate']
    fname=request.form['filename']
    cid=request.form['eid']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE gen_reports
        SET company=%s,report_date=%s,broker=%s,URL=%s,site=%s
        where id = %s
    """, (company,report_date,broker,URL,site,cid))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('sector.index')) 
