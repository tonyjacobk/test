from flask import Flask, render_template, request, redirect, url_for,Blueprint
from aiven import get_rows,get_broker,connect
import urllib.parse
import math
from redis_man import res

#from megclass import MegaMan
crud_bp=Blueprint("crud",__name__)

# Database configuration

def get_connection():
  return connect()
@crud_bp.route('/')
@crud_bp.route('/<int:page>')
@crud_bp.route('/filter/<key>/<value>/<int:page>')
def index(key=None, value=None, page=1):
    print(key,value,page)
    conn = get_connection()
    cursor = conn.cursor()

    page_size = 50
    offset = (page - 1) * page_size

    # Get search parameters
    search_by_code = request.args.get('search_by_code', '')
    search_by_company = request.args.get('search_by_company', '')
    search_by_broker= request.args.get('search_by_broker', '')

    # Base query
    base_query = "FROM reports "
    sort_query= "ORDER BY report_date DESC "
    conditions = []
    params = []

    if key and value:
        conditions.append(f"{key} = %s")
        params.append(value)

    if search_by_code:
        conditions.append("NSEKEY LIKE %s")
        params.append(f"%{search_by_code}%")

    if search_by_company:
        conditions.append("company LIKE %s")
        params.append(f"%{search_by_company}%")
    if search_by_broker:
        conditions.append("broker LIKE %s")
        params.append(f"%{search_by_broker}%")

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    print("Where",where_clause)
    # Get total number of rows for pagination
    count_query = "SELECT COUNT(*) " + base_query + where_clause
    print(count_query)
    cursor.execute(count_query, tuple(params))
    total_rows = cursor.fetchone()['COUNT(*)']
    total_pages = math.ceil(total_rows / page_size)

    # Get data for the current page
    data_query = "SELECT * " + base_query + where_clause +sort_query+ f" LIMIT %s OFFSET %s"
    if not where_clause:
         data_query = "SELECT * " + base_query + sort_query+where_clause + f" LIMIT %s OFFSET %s"
    print(data_query)
    params.extend([page_size, offset])
    cursor.execute(data_query, tuple(params))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('crudindex.html',
                           rows=rows,
                           page=page,
                           total_pages=total_pages,
                           key=key,
                           value=value,
                           search_by_code=search_by_code,
                           search_by_broker=search_by_broker,
                           search_by_company=search_by_company)

@crud_bp.route('/move', methods=['POST'])
def move():
    print(request.form)
    code=request.form.get('search_by_code')
    comp=request.form.get('search_by_company')
    pag=request.form.get('page')
    if not pag:
        pag=1
    print(code,comp,pag)
    search_params={'search_by_code':code,'search_by_company':comp}
    company = request.form['company']
    broker = request.form['broker']
    report_date = request.form['report_date']
    url=request.form['URL']
    site=request.form['site']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
       INSERT into  gen_reports
        (company,report_date,broker,URL,site)
        VALUES (%s,%s,%s,%s,%s)
    """, (company,report_date,broker,url,site))
    cursor.execute("""
        SELECT site  FROM reports
        WHERE company=%s AND broker=%s AND report_date=%s
        """,(company, broker, report_date))
    results=cursor.fetchall()
    cursor.execute("""
        DELETE FROM reports 
        WHERE company=%s AND broker=%s AND report_date=%s
   """, (company, broker, report_date))
    conn.commit()
    cursor.close()
    conn.close()
    search_params={'search_by_code':code,'search_by_company':comp}
    return redirect(url_for('crud.index',page=pag,**search_params))

@crud_bp.route('/multiple_delete', methods=['POST'])
def multiple_delete():
    print("In multiple delete")
    for key, value in request.args.items():
     print(f"{key}: {value}")
    code=request.form.get('search_by_code')
    comp=request.form.get('search_by_company')
    pag=request.form.get('page')
    if not pag:
        pag=1
    print(code,comp,pag)
    search_params={'search_by_code':code,'search_by_company':comp}
    selected_indices = request.form.getlist('selected_rows')

    selected_data = []
    conn = get_connection()
    cursor = conn.cursor()

    for idx in selected_indices:
        print(idx)
        row_data = {
            "code": request.form.get(f"rows[{idx}][code]"),
            "broker": request.form.get(f"rows[{idx}][broker]"),
            "site": request.form.get(f"rows[{idx}][site]"),
            "date": request.form.get(f"rows[{idx}][date]")

        }
        cursor.execute("""
        SELECT site  FROM reports
        WHERE NSEKEY=%s AND broker=%s AND report_date=%s
        """,(row_data["code"],row_data["broker"], row_data["date"]))

        results=cursor.fetchall()
        if results[0]['site'] == 'tel':
          res.set_a_value(f"rows[{idx}][url]")

        cursor.execute("""
        DELETE  FROM reports
        WHERE NSEKEY=%s AND broker=%s AND report_date=%s
        """,(row_data["code"],row_data["broker"], row_data["date"]))
        selected_data.append(row_data)
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('crud.index',page=pag,**search_params))

@crud_bp.route('/save', methods=['POST'])
def save():
    code=request.form.get('search_by_code')
    comp=request.form.get('search_by_company')
    brok=request.form.get('search_by_broker')
    pag=request.form.get('page')

    data = (
        request.form['company'],
        request.form['broker'],
        request.form['URL'],
        request.form['recommendation'],
        request.form['target'],
        request.form['report_date'],
        request.form['site'],
        request.form['code']
    )
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        REPLACE INTO reports 
        (company, broker, URL, recommendation, target, report_date, site,NSEKEY) 
        VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
    """, data)
    conn.commit()
    cursor.close()
    conn.close()
    search_params={'search_by_code':code,'search_by_company':comp,'search_by_broker':brok}
    return redirect(url_for('crud.index',page=pag,**search_params))


