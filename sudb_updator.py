import json
import os
import ast
import sys
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
from flask import Flask, render_template, request, redirect, url_for,Blueprint
from stockutils import create_dic,check_if_present,db,get_last_ndays_data,res,sb,brokers
sudb_bp=Blueprint("sudb",__name__)
pdftext=[]
rows_for_logical_delete=[]


def initialize_logger ():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',filename='/tmp/analysissudb_bp.log', level=logging.INFO)

def delete_mega_file(link):
 print("Deleting link ",link)
 res.set_a_value(link)

def save_data(pdftext,Sneeded=True):
    for i in pdftext:
       sb.upsert_report(i["id"],i["date"],i['company'],i["recommendation"],i["target_price"],i["link"],i['broker'],i['delete'],i['sector'])
    if Sneeded:
       update_db()

def delete_duplicate_company_reports(oldlist,new_list):
    lookup=  {
    (d["broker"],  d["Company"]) for d in new_list} 
    for entry in oldlist:
     if (entry['broker'],entry['Company']) not in lookup:
         print (entry['Company'] ," is duplicate")
         delete_mega_file(entry['link'])


def is_a_good_row(row,rtype):
  mrow=["broker","company","publish_date","Recommendation","Target","link"]
  if rtype=="sector":
    mrow=["broker","publish_date","link"]
  for i in mrow:
      if row[i] =="" or not row[i]:
        return False
  return True

def update_db():
    global rows_for_logical_delete
    delete_a_report_logically()
    insert_sector_reports()
    insert_company_reports()
    print("Rows that will be deleted",rows_for_logical_delete)
    return sb.delete_logically_ids(rows_for_logical_delete)
def delete_a_report_logically():
 global rows_for_logical_delete
 rows = sb.get_reports_set_for_delete()
 for row in rows:
  link = row["link"]
  row_id = row["id"]
  if link is not None:
      delete_mega_file(link)
 rows_for_logical_delete.extend([row["id"] for row in rows])
 print("After deleted reports",rows_for_logical_delete)
def insert_sector_reports():
 global rows_for_logical_delete
 rows = sb.get_reports_marked_as_sector()
 for row in rows:
  if is_a_good_row(row,"sector"):
   mrow=[{"company":row["company"],"site":"tel","link":row['link'],"report-date":row['publish_date'],"broker":row['broker']}]
   rows_for_logical_delete.append(row["id"])
   db.insert_into_sector(mrow)
 print("After Sector reports",rows_for_logical_delete)
def insert_company_reports():
 global  rows_for_logical_delete
 rows = sb.get_reports_marked_as_company()
 good_rows=[]
 ids=[]
 for row in rows:
   if is_a_good_row(row,"company"):
    mydict={"Company": row['company'],"link": row['link'],"report-date": datetime.fromisoformat(row['publish_date']).date(),
                    "broker":row['broker'],"recommendation":row['Recommendation'],"target":row['Target'] }
    good_rows.append(mydict)
    ids.append(row["id"])
 new_list=check_if_present(good_rows,"telgram")  
 delete_duplicate_company_reports(good_rows,new_list)
 rows_for_logical_delete.extend([id for id  in ids])
 db.insert_into_database(new_list,"tel")
 print("After Company reports",rows_for_logical_delete)


def main_func(readNeeded=True,data=None):
 complist,dellist=classifier(pdftext)
 new_list=check_if_present(complist,"telgram")
 delete_files_not_needed(complist,new_list) 
 db.insert_into_database(new_list,"tel")
 print ("Deleting ..",len(dellist))
 for i in dellist:
   pdftext.pop(i)
 save_data(pdftext)

def unique_brokers(brokers):
    return list(sorted(dict.fromkeys(d.values())))






@sudb_bp.route('/')
def index():
    entries =sb.get_active_recommendations()
    for i in entries:
     date_obj2 = datetime.fromisoformat(i['publish_date']).date()
     i['publish_date']=date_obj2
    return render_template('sudbindex.html', entries=entries,brkrs=BRKRS)

@sudb_bp.route('/process', methods=['POST'])
def save():
    # Retrieve lists of data from the form
    ids = request.form.getlist('id')
 #   texts = request.form.getlist('text')
    brokers = request.form.getlist('broker')
    companies = request.form.getlist('company')
    dates = request.form.getlist('date')
    recommendations = request.form.getlist('recommendation')
    targets = request.form.getlist('target_price')
    links = request.form.getlist('URL')
    print(len(ids),len(brokers),len(companies),len(links))
    updated_data = []
    for i in range(len(ids)):
        current_id =ids[i]
        is_delete_checked = f"delete_{current_id}" in request.form
        is_sector_checked = f"sector_{current_id}" in request.form
           
        entry = {
            "id": ids[i],
         #   "text": mtext,
            "broker": brokers[i],
            "company": companies[i],
            "date": dates[i],
            "recommendation": recommendations[i],
            "target_price": targets[i],
            "link": links[i],
            "delete": is_delete_checked,  # True or False
            "sector": is_sector_checked   # True or False
        }
        updated_data.append(entry)
    action = request.form.get('action')
    print("Action is ",action)
    if action == 'save_file':
        save_data(updated_data,"False")
    elif action == 'update_db':
        save_data(updated_data,True)
        print("Database updated successfully!", "info")
    return redirect(url_for('sudb.index'))


initialize_logger()
get_last_ndays_data(20)
BRKRS= list(dict.fromkeys(brokers.values()))
