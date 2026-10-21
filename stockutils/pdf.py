from pypdf import PdfReader
import re
import requests
import certifi
import urllib3
import os
import fitz
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime, date
import logging
logger = logging.getLogger(__name__)

def download_file(url):
 print("Download")
 non_safe=["joindre"]
 lurl=url.lower()
 safety=not(any(word in lurl for word in non_safe))
 print("Safety is ",safety)
 try:
     response=None
     if safety:
        response = requests.get(url, stream=True)
     else:
        response = requests.get(url, stream=True,verify=False)
     response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

     with open("tempfile", 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

 except requests.exceptions.RequestException as e:
       raise e 

def download_and_return_text(url):
 download_file(url)
 reader = PdfReader("tempfile")
 page = reader.pages[0]  # Access the first page
 return(page.extract_text())

def return_text(file_path,num_words):

    try:
        # Create a PdfReader object
        reader = PdfReader(file_path)
        full_text = ""
        
        # Iterate through all pages to get the full text
        for page in reader.pages:
            full_text += page.extract_text()
            
            # If we've already extracted enough text, we can stop
            # and process what we have.
            if len(full_text.split()) >= num_words:
                break
        
        # Split the full text into a list of words
        words = full_text.split()
        
        # Take only the first `num_words` from the list
        first_n_words = " ".join(words[:num_words])
        
        return first_n_words
        
    except FileNotFoundError:
        return f"Error: The file '{file_path}' was not found."
    except Exception as e:
        return f"An error occurred: {e}"


def find_rating_from_file():
 reader = PdfReader("tempfile")
 page = reader.pages[0]  # Access the first page
 text = page.extract_text()
 print(text)
 match = re.search(r'Rating:\s*(\w+)', text)

    # Return the matched word if found, otherwise return None
 return match.group(1) if match else None

def get_target_price_recomm_idbi(url): 
 value=recom=""
 try:
  download_file(url)
  value,recom=get_target_price_recomm_idbi2()
 except Exception as e:
  pass
 return (value,recom)

def get_target_price_recomm_idbi2():
 recomms=["buy","sell","hold"]
 recom=""
 reader = PdfReader("tempfile")
 page = reader.pages[0]  # Access the first page
 text = page.extract_text()
 lines =text.split('\n')
 lc=-1
 while lc<20:
  lc=lc+1
  i=lines[lc]
  sline=i.strip()
  slen=len(sline)
  if slen ==3 or slen==4:
    if sline.lower() in recomms:
     recom=sline
 tp=get_target_price_from_file()
 return(tp,recom)

def get_target_price_from_file():
 reader = PdfReader("tempfile")
 page = reader.pages[0]  # Access the first page
 text = page.extract_text()
 print(text)
 pattern = re.compile(
                r'(?:target price|tp)[^\d]*([\d,]+(?:\.\d+)?|[\d.]+(?:,\d+)?)', 
                re.IGNORECASE
            )
            
 match = pattern.search(text)
            
 if match:
                # Get the matched number string and clean it
  num_str = match.group(1)
                
                # Handle thousand separators and decimal points
  if ',' in num_str and '.' in num_str:
                    # Assume commas are thousand separators and . is decimal
                    num_str = num_str.replace(',', '')
  elif ',' in num_str:
                    # Check if comma is used as decimal separator (European style)
                    if num_str.count(',') == 1 and len(num_str.split(',')[1]) <= 2:
                        num_str = num_str.replace(',', '.')
                    else:
                        num_str = num_str.replace(',', '')
  return(num_str)              
                # Convert to appropriate numeric type
 return " "
def get_target_price(url):
 value=" "
 try:
  download_file(url)
  value=get_target_price_from_file()
 except Exception as e:
  pass
 return (value)

def get_recommendation(url):
 value=" "
 try:
  download_file(url)
  value=find_rating_from_file()
 except Exception as e:
  pass
 return (value)

def get_recomm_and_target(url):
 print(url)
 value=" "
 recomm=" "
 try:
  download_file(url)
  recomm=find_rating_from_file()
  value=get_target_price_from_file()
  print ("recommendation ",recomm," Target ",value)
 except Exception as e:
  print("Could not get from :",url)
  print(str(e))
 print (value,recomm)
 return value ,recomm

def get_data_and_recomm_icicid(url):
 try:
  text= download_and_return_text(url)
  print(text)
  results = {
        'recommendation': None,
        'date': None
    }
  non_empty_lines = [line.strip() for line in text.splitlines() if line.strip()]
  first_six_lines = non_empty_lines[:6]

  recommendation_pattern = re.compile(r'\b(BUY|HOLD|REDUCE|SELL)\b', re.IGNORECASE)
  date_pattern = re.compile(
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
    )

  for line in first_six_lines:
        if not results['recommendation']:
            rec_match = recommendation_pattern.search(line)
            if rec_match:
                results['recommendation'] = rec_match.group(1).upper()

        if not results['date']:
            date_match = date_pattern.search(line)
            if date_match:
                results['date'] = date_match.group(0)

        # Stop searching if both have been found
        if results['recommendation'] and results['date']:
            break
  if not results['date'] and len(non_empty_lines) > 6:
        last_three_lines = non_empty_lines[-3:] # Get the last 3 elements
        for line in last_three_lines:
            date_match = date_pattern.search(line)
            if date_match:
                results['date'] = date_match.group(0)
                break # Stop searching the last 3 lines once found 
  return results

 except Exception as e:
  print("Could not get from :",url)
  print(str(e))

def get_title_from_meta(fileName):
  try:
    reader = PdfReader(fileName)
    meta = reader.metadata
    title=meta['\Title']
    if title:
      return title
    return None
  except Exception as e:
      logger.error("Error with meta data for file %s : %s",fileName,str(e)) 
      return None



def generic_target_price(text):
 pattern = re.compile(
    r"""(?ix)
    \b(?:TP|Target\s+Price|Price\s+Target|PT)\b         # TP or Target Price
    \s*
    (?:to\s+)?                        # allow 'to'
    (?:[:\-–—]\s*)?
    (?:of\s+)?                        # allow 'of'
    (?:[:\-–—]\s*)?
    (?:(Rs\.?|INR|₹))?\s*             # currency optional (allow attached)
    ((?:\d{1,3}(?:,\s?\d{3})*|\d+))      # capture number with or without commas
    """
 )
 m = pattern.search(text)
 if m:
   return re.sub(r"[ ,]","",m.group(2))
 else:
   return ""

def generic_recommendation(text):
 RATINGS = [
    "buy", "sell", "reduce", "hold","add",
    "accumulate", "neutral", "initiating coverage","initiate covereage"
]

# Build alternation pattern (longest first to avoid partial matches)
 ratings_pattern = r"|".join(
    fr"{r}" for r in sorted(RATINGS, key=len, reverse=True)
)

# Pattern 1: Upgrade/Downgrade/Reiterate → extract NEW rating only
 upgrade_pattern = re.compile(
    fr"""(?ix)
        (?:upgrade[d]?|downgrade[d]?|reiterate[d]?)   # action
         (?:\s+\w+)*
        \s+to\s+
        (?P<new>{ratings_pattern})                    # NEW rating
    """
)

# Pattern 2: Direct rating lines such as "Rating: BUY", "Rating – Hold"
 direct_pattern = re.compile(
    fr"""(?ix)
        (?:
            rating|recommendation\s*[:\-–—]?\s*(?P<rate1>{ratings_pattern})      # Rating: BUY
            |
            (?P<rate2>{ratings_pattern})\s+rating                 # BUY rating
            |
            (?:maintain|maintains|maintained
              |retain|retains|retained
              |reiterate|reiterates|reiterated
              |recommend|recommends
              |reaffirm|reaffirms|reaffirmed)

            \s+(?:a\s+)?(?P<rate3>{ratings_pattern})              # maintain HOLD / maintain a BUY
        )
    """
)


    # 1. Check upgrade/downgrade type
 m1 = upgrade_pattern.search(text)
 if m1:
        return m1.group("new").upper()

    # 2. Check direct rating
 m2 = direct_pattern.search(text)
 if m2:
  for key in ("rate1", "rate2", "rate3"):
         if m2.group(key):
             return m2.group(key).upper()
 return None

def cdanalysis(text):
 pattern = r'Price target \(Rs/\$\)\s*(\d+)'
 match = re.search(pattern, text)
 if match:
   price =int(match.group(1))
 recomm=generic_recommendation(text)
 return recomm,price
 
def get_target_and_recomm(url,count=2000):
 anal_funcs={"cdresearch":cdanalysis}
 print("Downloading from ...",url)
 try:
  download_file(url)
 except  Exception as e:
    logger.info("Could not download from URL %s",url)
    return "",""
 text=return_text("tempfile",count)
 for i in anal_funcs.keys():
     if i in url:
      recomm,target=anal_funcs[i](text)
      return recomm,target

 recomm=generic_recommendation(text)
 target=generic_target_price(text)
 return recomm,target

def get_lines_from_pdfFile(url,line_numbers):
    download_file(url)
    result = []

    with fitz.open("tempfile") as doc:
        if not doc:
            return result

        page = doc[0]
        flags = fitz.TEXT_DEHYPHENATE | fitz.TEXT_PRESERVE_WHITESPACE
        text = page.get_text("text", flags=flags, sort=True)

        non_empty_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        result=non_empty_lines[0:line_numbers]
    return result





def parse_and_convert_date(date_string: str):
    """
    Checks if a string represents a valid date against common formats.
    If valid, returns a datetime.date object. Otherwise, returns False.
    """
    # Define a list of common date formats you want to check against
    common_formats = [
        "%Y-%m-%d",  # 2026-10-16 (ISO format)
        "%m/%d/%Y",  # 10/16/2026
        "%d/%m/%Y",  # 16/10/2026
        "%Y/%m/%d",  # 2026/10/16
        "%d-%m-%Y",  # 16-10-2026
        "%b %d, %Y", # Oct 16, 2026
        "%B %d, %Y",  # October 16, 2026
        "%d %b, %Y",
        "%d %B, %Y"
    ]

    for fmt in common_formats:
        try:
            # Try to parse the string into a datetime object
            dt_obj = datetime.strptime(date_string.strip(), fmt)
            # Extract and return just the date object (Year, Month, Day)
            return dt_obj.date()
        except ValueError:
            # If the format doesn't match, keep checking the other formats
            continue

    # Return False if the string did not match any of the provided formats
    return False
"""
g,b=get_target_and_recomm('https://www.mangalkeshav.com/research-reports/wp-content/uploads/2026/04/Inox-India-limited-fundamental-analysis-stock-report.pdf')
print(g,b)

download_file('https://www.mangalkeshav.com/research-reports/wp-content/uploads/2026/04/Inox-India-limited-fundamental-analysis-stock-report.pdf')
text=return_text('tempfile',2000)
print(text)
text="PT of Rs. 70"

#recomm=generic_recommendation(text)
target=generic_target_price(text)
print( target) 
"""
