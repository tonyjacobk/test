import pymysql
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
from math import ceil
from datetime import datetime, timedelta
import os
password=os.environ.get('password')
print(password)
timeout = 10
def connect():
 connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db="defaultdb",
  password=os.environ.get('password'),
  host="mysql-debe0f5-tonyjacobk-250a.j.aivencloud.com",
  read_timeout=timeout,
  port=19398,
  user="avnadmin",
  write_timeout=timeout,
)

 return connection

def row_exists(broker,company,date):
    query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM {table_name}
            WHERE broker = %s AND company = %s AND report_date = %s
        ) AS row_exists
    """

    cursor.execute(query, (broker,company,date))
    result = cursor.fetchone()
def row_exists_no_comp(broker,recom,target):
    found=[]
    query = f"""
            SELECT *
            FROM reports
            WHERE  recommendation = %s AND broker =%s AND target = %s
    """
    connection=connect()
    cursor=connection.cursor()
    cursor.execute(query, (recom,broker,target))
    for row in cursor:
     found.append(row)
    return (found)


def get_rows(pageNo,per_page):
    mysql=connect()
    cursor=mysql.cursor()
    cur = mysql.cursor()
    cur.execute("SELECT COUNT(*) FROM reports")
    total_rows = cur.fetchone()['COUNT(*)']
    total_pages = ceil(total_rows / per_page)
    offset = (pageNo - 1) * per_page
    cur.execute(f"SELECT * FROM reports ORDER BY report_date DESC,broker  LIMIT 20 OFFSET %s", (offset) )
    data = cur.fetchall()
    cursor.close()
    return data,total_pages
def get_broker(pageNo,per_page,broker):
    mysql=connect()
    cursor=mysql.cursor()
    per_page = 20
    ibrk="%"+broker+"%"
    cur = mysql.cursor()
    cur.execute("SELECT COUNT(*) FROM reports where broker LIKE %s",(ibrk))
    total_rows = cur.fetchone()['COUNT(*)']
    total_pages = ceil(total_rows / per_page)
    offset = (pageNo - 1) * per_page
    cur.execute(f"SELECT * FROM reports where broker LIKE %s ORDER BY report_date DESC  LIMIT 20 OFFSET %s", (ibrk,offset) )
    data = cur.fetchall()
    cursor.close()
    return data,total_pages
def get_stock(pageNo,per_page,stock):
    mysql=connect()
    cursor=mysql.cursor()
    per_page = 20
    cur = mysql.cursor()
    cur.execute("SELECT COUNT(*) FROM reports where company= %s",(stock))
    total_rows = cur.fetchone()['COUNT(*)']
    total_pages = ceil(total_rows / per_page)
    offset = (pageNo - 1) * per_page
    cur.execute(f"SELECT * FROM reports where company = %s ORDER BY report_date DESC  LIMIT 20 OFFSET %s", (stock,offset) )
    data = cur.fetchall()
    cursor.close()
    return data,total_pages
def get_stock_partial(pageNo,per_page,stock):
    mysql=connect()
    cursor=mysql.cursor()
    per_page = 20
    cur = mysql.cursor()
    istock="%"+stock+"%"
    cur.execute("SELECT COUNT(*) FROM reports where company LIKE %s",(istock))
    total_rows = cur.fetchone()['COUNT(*)']
    print(total_rows)
    total_pages = ceil(total_rows / per_page)
    offset = (pageNo - 1) * per_page
    cur.execute(f"SELECT * FROM reports where company LIKE  %s ORDER BY report_date DESC  LIMIT 20 OFFSET %s", (istock,offset) )
    data = cur.fetchall()
    cursor.close()
    return data,total_pages
def is_present(conn, comp, brok, date_str):
    base_date = datetime.strptime(date_str, "%Y-%m-%d")
    start_date = (base_date - timedelta(days=10)).date()
    end_date = (base_date + timedelta(days=10)).date()

    query = """
        SELECT *
        FROM reports
        WHERE company = %s
          AND broker = %s
          AND report_date BETWEEN %s  AND %s
    """

    cur = conn.cursor()
    cur.execute(query, (comp, brok, start_date, end_date))
    rows = cur.fetchall()

    if rows:
        return True, rows
    return False, []
def add_company(company,broker,URL,report_date,recomm,target,site,nsekey):
    mysql=connect()
    cursor=mysql.cursor()
    cursor.execute("""
       INSERT INTO reports
        (company, broker, URL,  report_date,recommendation,target ,site,NSEKEY)
        VALUES (%s, %s, %s, %s, %s,%s,%s,%s)
    """, (company,broker,URL,report_date,recomm,target,site,nsekey))

    mysql.commit()
    cursor.close()
    mysql.close()
def just_test():
    mysql=connect()
    cursor=mysql.cursor()
    cur=cursor.execute("DESCRIBE gen_reports")
    cols=cursor.fetchall()
    for col in cols:
        print(col)


