import logging
import scrapy
from bs4 import BeautifulSoup
import requests
import time as t
import sqlite3
import psycopg2
import json
from concurrent.futures import ThreadPoolExecutor, as_completed 
import networkx as nx
import matplotlib.pyplot as plt

logging.basicConfig(filename="log.txt", level=logging.INFO, format='%(asctime)s %(message)s')

conn = psycopg2.connect(dbname="postgres",
                        user="postgres",
                        password="1245!Taha",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()

cursor.execute('''
DROP TABLE IF EXISTS people2;

CREATE TABLE IF NOT EXISTS people2 (
    id text PRIMARY KEY,
    name text NOT NULL,
    url text NOT NULL,
    students text[],
    advisors text[],
    othersummary text,
    otherurl text[],
    imageurls text    
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
            scientist_name = soup.find('h2').text.replace("\n"," ").strip()
            students = getStudents(soup, url)
            advisors = getAdvisors(soup, url)
            sql_query = """INSERT INTO people2 (id, name, url,students,advisors) VALUES (%s,%s,%s,%s,%s);"""
            values = (scientist_id, scientist_name, url, students, advisors)
            cursor.execute(sql_query,values)
            conn.commit()
            t.sleep(0.01)
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
    # "https://genealogy.math.ndsu.nodak.edu/id.php?id=217509"
]
    
    # Number of URLs to generate
num_urls = 10

# Get the last URL in the list
last_url = initial_urls[-1]

# Extract the id from the last URL
last_id = int(last_url.split('=')[-1])

# Generate new URLs by incrementing the id
for i in range(1, num_urls ):
    new_id = last_id + i
    new_url = f"https://genealogy.math.ndsu.nodak.edu/id.php?id={new_id}"
    initial_urls.append(new_url)   

# with ThreadPoolExecutor(max_workers=5) as executor:
MAX_THREADS = 16
with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    futures = [executor.submit(process_url, url) for url in initial_urls]
# for i in timeout_urls:
#     print(i)
# for url in initial_urls:
#     process_url(url)
print("done")

# def displaying():
#     # user inout  for the ID
#     user_id = input("Please enter the ID of the node: ")

#     # Retrieve the node from the database
#     cursor.execute("SELECT id, name FROM people WHERE id = %s;", (user_id,))
#     first_node = cursor.fetchone()
#     if not first_node:
#         print(f"No data found in the database for id = {user_id}.")
#         return

#     root_id, root_name = first_node
#     print(first_node)
#     G = nx.DiGraph()
#     G.add_node(root_id, label=root_name)

#     def add_descendants(node_id):
#         cursor.execute("SELECT students FROM people WHERE id = %s;", (node_id,))
#         students = cursor.fetchone()[0]
#         print(students)
#         if not students:
#             return
#         for student_id in students:
#             cursor.execute("SELECT id, name FROM people WHERE id = %s;", (student_id,))
#             student = cursor.fetchone()
#             if student:
#                 student_id, student_name = student
#                 G.add_node(student_id, label=student_name)
#                 G.add_edge(node_id, student_id)
#                 add_descendants(student_id)
#     def add_advisors(node_id):
#             cursor.execute("SELECT advisors FROM people WHERE id = %s;", (node_id,))
#             advisors = cursor.fetchone()[0]
#             print(advisors)
#             if not advisors:
#                 return 
#             for advisor_id in advisors:
#                 cursor.execute("SELECT id, name FROM people WHERE id = %s;", (advisor_id,))
#                 advisor = cursor.fetchone()
#                 if advisor:
#                     advisor_id, advisor_name = advisor
#                     G.add_node(advisor_id, label=advisor_name)
#                     G.add_edge(advisor_id, node_id)
#                     add_advisors(advisor_id)

#     add_descendants(root_id)
#     add_advisors(root_id)

#     pos = nx.spring_layout(G)
#     labels = nx.get_node_attributes(G, 'label')
#     nx.draw(G, pos, labels=labels, with_labels=True, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold", arrows=True)
#     plt.title(f"Genealogy Tree of {root_name}")
#     plt.show()

# displaying()