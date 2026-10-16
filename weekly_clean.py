from megclass import MegaMan
from redis_man import res
import logging
import os
logger = logging.getLogger(__name__)


def initialize_logger ():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',filename='/tmp/weekly_delete.log', level=logging.INFO)
    logger.info('Started Logging from main ')



def delete_all_records():
 nonMega=noFile=deleted=others=0
 del_list=res.get_all_keys()
 keys_before=len(del_list)
 for key in del_list:
   print(key)
   if 'mega.co.nz' not in key:
       nonMega+=1
       res.delete_a_key(key)
       continue
   ret= MegaMan.delete_url(key)
   if ret ==1:  #Could not get fileName for this URL (-2), delete success (1)
      res.delete_a_key(key)
      deleted+=1
      continue
   if ret == -2:
       res.delete_a_key(key)
       noFile+=1
   else:
       others+=1
 keys_after=len(res.get_all_keys())
 params={"redis_before":keys_before,
         "Nomega":nonMega,
         "Others":others,
         "deleted":deleted,
         "nofile":noFile,
         "redis_after":keys_after }
 final_html = html_template.format(**params)
 return final_html
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Parameter Table</title>
</head>
<body>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; font-family: sans-serif;">
  <thead>
    <tr>
      <th>Items</th>
      <th>Count</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Keys to be Deleted:</strong></td>
      <td>{redis_before}</td>
    </tr>
    <tr>
      <td><strong>Non mega files:</strong></td>
      <td>{Nomega}s</td>
    </tr>
    <tr>
      <td><strong>URLS with no files:</strong></td>
      <td>{nofile}</td>
    </tr>
    <tr>
      <td><strong>Others:</strong></td>
      <td>{Others}</td>
    </tr>
    <tr>
      <td><strong>URLs deleted :</strong></td>
      <td>{deleted}</td>
    </tr>
    <tr>
      <td><strong>Redis entries after deletion :</strong></td>
      <td>{redis_after}</td>
    </tr>


  </tbody>
</table>
</body>
</html>
"""


def weekly_delete():
    initialize_logger ()
    htm=delete_all_records()
    file_path = "/tmp/weekly_delete_table.html"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
      file.write(htm)

    print(f"File successfully saved to: {file_path}")
weekly_delete()
