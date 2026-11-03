import json
import os
import ast
import sys
import time
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
from flask import Flask, render_template, request, redirect, url_for,Blueprint
from stockutils import create_dic,check_if_present,db,get_last_ndays_data,res,sb,brokers
sudb_bp=Blueprint("sudb",__name__)
pdftext=[]
rows_for_logical_delete=[]
entries=[]

# row_deleted  in supabase means row is deleted. Deleted means it was deleted through UI . It row_deleted is False and deleted True, UI will show tick 


def initialize_logger ():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',filename='/tmp/analysissudb_bp.log', level=logging.INFO)

def delete_mega_file(link):
 print("Deleting link ",link)
 res.set_a_value(link)

def save_data(pdftext,Sneeded=True):
    print("Sneeded is ",Sneeded)
    for i in pdftext:
       sb_up_st=time.perf_counter()
       sb.upsert_report(i["id"],i["date"],i['company'],i["recommendation"],i["target_price"],i["link"],i['broker'],i['delete'],i['sector'])
       sb_up_so=time.perf_counter()
       print("Time for sb upsert ",sb_up_so-sb_up_st)
    if Sneeded:
       print("Hello Sneeded",Sneeded)
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
    sb_up_st=time.perf_counter()
    delete_a_report_logically()
    sb_up_so=time.perf_counter()
    print("Time for   delete_a_report_logically",sb_up_so-sb_up_st)
    sb_up_st=time.perf_counter()
    insert_sector_reports()
    sb_up_so=time.perf_counter()
    print("Time for   insert_sector_report_logically",sb_up_so-sb_up_st)

    insert_company_reports()
    print("Rows that will be deleted",rows_for_logical_delete)
    return sb.delete_logically_ids(rows_for_logical_delete)


def delete_a_report_logically():
 global rows_for_logical_delete
 global entries
 for row in entries:
  if not  row['row_deleted']:
   continue
  link = row["link"]
  row_id = row["id"]
  if link is not None:
      sb_up_st=time.perf_counter()
      delete_mega_file(link)
      sb_up_so=time.perf_counter()
      print("Time for cache delete  ",sb_up_so-sb_up_st)
  rows_for_logical_delete.append(row['id'])

 print("After deleted reports",rows_for_logical_delete)
def insert_sector_reports():
 global rows_for_logical_delete
 for row in entries:
  if  not row['row_deleted'] and row['sector']:
   if is_a_good_row(row,"sector"):
    mrow=[{"company":row["company"],"site":"tel","link":row['link'],"report-date":row['publish_date'],"broker":row['broker']}]
    rows_for_logical_delete.append(row["id"])
    db.insert_into_sector(mrow)
 print("After Sector reports",rows_for_logical_delete)





def insert_company_reports():
 global  rows_for_logical_delete
 global entries
 good_rows=[]
 ids=[]
 for row in entries:
   if  row['row_deleted']:
     continue
   if is_a_good_row(row,"company"):
    mydict={"Company": row['company'],"link": row['link'],"report-date": row['publish_date'],
                    "broker":row['broker'],"recommendation":row['Recommendation'],"target":row['Target'] }
    good_rows.append(mydict)
    ids.append(row["id"])
 print("Rows that may be inserted",good_rows)
 new_list=check_if_present(good_rows,"telgram")
 delete_duplicate_company_reports(good_rows,new_list)
 rows_for_logical_delete.extend([id for id  in ids])
 db.insert_into_database(new_list,"tel")
 print("After Company reports",rows_for_logical_delete)


def find_changed_entries(original_list, modified_list):
 field_map = {
    "date": "publish_date",
    "recommendation": "Recommendation",
    "target_price": "Target",
    "link": "link",
    "company": "company",
    "broker": "broker",
    "sector": "sector",
    "delete": "row_deleted",
}
  
 original_lookup = {item["id"]: item for item in original_list}
 changed_entries = []
 for mod_item in modified_list:
    orig_item = original_lookup.get(int(mod_item["id"]))
    if orig_item is None:
        changed_entries.append(mod_item)
        continue
    changed_fields = {}
    for mod_field, orig_field in field_map.items():

        orig_value = orig_item.get(orig_field)
        mod_value = mod_item.get(mod_field)
        if orig_field=="publish_date":
            mod_value= datetime.strptime(mod_value, "%Y-%m-%d").date()
        if orig_value != mod_value:
          print("Issue with the value",orig_value,mod_value)
          changed_entries.append(mod_item) 
 return changed_entries               


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
    global entries
    entries =sb.get_active_recommendations()
    for i in entries:
     date_obj2 = datetime.fromisoformat(i['publish_date']).date()
     i['publish_date']=date_obj2
    return render_template('sudbindex.html', entries=entries,brkrs=BRKRS)

@sudb_bp.route('/process', methods=['POST'])
def save():
    global entries
    ids = request.form.getlist('id')
    brokers = request.form.getlist('broker')
    companies = request.form.getlist('company')
    dates = request.form.getlist('date')
    recommendations = request.form.getlist('recommendation')
    targets = request.form.getlist('target_price')
    links = request.form.getlist('URL')
    updated_data = []
    for i in range(len(ids)):
        current_id =ids[i]
        is_delete_checked = f"delete_{current_id}" in request.form
        is_sector_checked = f"sector_{current_id}" in request.form
        entry = {
            "id": ids[i],
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
    flist=find_changed_entries(entries,updated_data)
    print ("Changed List ",flist)
    action = request.form.get('action')
    print("Action is ",action)
    if action == 'save_file':
        save_data(flist,False)
    elif action == 'update_db':
        save_data(flist,True)
        print("Database updated successfully!", "info")
    return redirect(url_for('sudb.index'))


initialize_logger()
get_last_ndays_data(20)
BRKRS= list(dict.fromkeys(brokers.values()))
