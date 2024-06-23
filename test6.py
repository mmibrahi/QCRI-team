import logging
import scrapy
from bs4 import BeautifulSoup
import requests
import time as t
import sqlite3
import psycopg2
import json
from concurrent.futures import ThreadPoolExecutor, as_completed 

logging.basicConfig(filename="log.txt", level=logging.INFO, format='%(asctime)s %(message)s')

conn = psycopg2.connect(dbname="postgres",
                        user="postgres",
                        password="6uGEFkYvuBJLQMP",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()

cursor.execute('''
DROP TABLE IF EXISTS people;

CREATE TABLE IF NOT EXISTS people (
    id varchar(50) PRIMARY KEY,
    name varchar(50) NOT NULL,
    url varchar(50) NOT NULL,
    students varchar[],
    advisors varchar[],
    othersummary varchar(50),
    otherurl varchar(50),
    imageurls varchar(200)    
);
''')

conn.commit()

timeout_urls = []

# Step 3: getting the students
def getStudents(soup, url):
    table = soup.find('table')
    students = table.find_all('a') if table else []

    def parse_student_element(student_element):
        student_id = student_element['href'].split('=')[-1]
        # student_name = student_element.text.strip()
        # student_url = url.split('?')[0] + f'?id={student_id}'
        return student_id

    return [parse_student_element(student) for student in students]

# Step 4: getting advisors
def getAdvisors(soup, url):
    advisors = []
    if soup:
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if text.startswith("Advisor"):
                # advisor_name = text.split(":")[1].strip()
                a_tag = p.find('a')
                if a_tag:
                    href = a_tag.get('href')
                    advisor_id = href.split('=')[-1]
                    # advisor_url = url.split('?')[0] + f'?id={advisor_id}'
                    advisors.append(advisor_id)
    return advisors

def process_url(url, retries=3, delay=5):
    for i in range(retries):
        try:
            r = requests.get(url, timeout=10)  
            r.raise_for_status()  # Raise an HTTPError for bad responses
            soup = BeautifulSoup(r.content, 'html5lib')
            scientist_id = url.split('=')[-1]
            scientist_name = soup.find('h2').text.replace("\n"," ")
            students = getStudents(soup, url)
            advisors = getAdvisors(soup, url)
            sql_query = """INSERT INTO people (id, name, url,students,advisors) VALUES (%s,%s,%s,%s,%s);"""
            values = (scientist_id, scientist_name, url, students, advisors)
            cursor.execute(sql_query,values)
            conn.commit()
            print(f"Processed URL: {url}")
            break
        except requests.exceptions.Timeout:
            logging.error(f"Timeout error for URL: {url}. Retrying in {delay} seconds...")
            print(f"Timeout error for URL: {url}. Retrying in {delay} seconds...")
            t.sleep(delay)  # Wait for some time before retrying
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error for URL: {url} - {e}")
            print(f"Request error for URL: {url} - {e}")
            return
    else:
        # We've run out of retries
        logging.error(f"Failed to process URL: {url} after {retries} retries.")
        print(f"Failed to process URL: {url} after {retries} retries.")
        timeout_urls.append(url)
    
   



initial_urls = [
    "https://genealogy.math.ndsu.nodak.edu/id.php?id=1",
]
    
    # Number of URLs to generate
num_urls = 30000

# Get the last URL in the list
last_url = initial_urls[-1]

# Extract the id from the last URL
last_id = int(last_url.split('=')[-1])

# Generate new URLs by incrementing the id
for i in range(1, num_urls ):
    new_id = last_id + i
    new_url = f"https://genealogy.math.ndsu.nodak.edu/id.php?id={new_id}"
    print(new_url)
    initial_urls.append(new_url)   

# with ThreadPoolExecutor(max_workers=5) as executor:
MAX_THREADS = 10
with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    futures = [executor.submit(process_url, url) for url in initial_urls]

print("done")