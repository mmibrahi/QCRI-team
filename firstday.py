import scrapy
from bs4 import BeautifulSoup
import requests
import time as t
import sqlite3
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# test
# Set up logging
logging.basicConfig(filename="log.txt", level=logging.INFO, format='%(asctime)s %(message)s')

sqliteConnection = sqlite3.connect("sql.db")
cursor = sqliteConnection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS people (
    id varchar2(20) PRIMARY KEY,
    name varchar2(20) NOT NULL,
    url varchar2(20) NOT NULL,
    othersummary varchar2(20),
    otherurl varchar2(20) 
);
''')

# Step 3: getting the students
def getStudents(soup, url):
    table = soup.find('table')
    students = table.find_all('a') if table else []

    def parse_student_element(student_element):
        student_id = student_element['href'].split('=')[-1]
        student_name = student_element.text.strip()
        student_url = url.split('?')[0] + f'?id={student_id}'
        return {'id': student_id, 'name': student_name, 'url': student_url}

    return [parse_student_element(student) for student in students]

# Step 4: getting advisors
def getAdvisors(soup, url):
    advisors = []
    if soup:
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if text.startswith("Advisor"):
                advisor_name = text.split(":")[1].strip()
                a_tag = p.find('a')
                if a_tag:
                    href = a_tag.get('href')
                    advisor_id = href.split('=')[-1]
                    advisor_url = url.split('?')[0] + f'?id={advisor_id}'
                    advisors.append({'id': advisor_url, 'name': advisor_name, 'url': advisor_url})
    return advisors

# Global data structures to hold unique students and advisors
people = []
visited_urls = set()
timeout_urls = []

# Function to process a URL and extract students and advisors
def process_url(url, retries=3, delay=5):
    if url in visited_urls:
        return  # Skip if URL already visited
    
    visited_urls.add(url)

    for i in range(retries):
        try:
            r = requests.get(url, timeout=10)  
            r.raise_for_status()  # Raise an HTTPError for bad responses
            soup = BeautifulSoup(r.content, 'html5lib')
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
        return

    # Get students and advisors from the current URL
    students = getStudents(soup, url)
    advisors = getAdvisors(soup, url)

    # Add unique students and advisors to global lists
    for student in students:
        if student not in people:
            if student.get('name') != "Unknown":
                people.append(student)

    for advisor in advisors:
        if advisor not in people:
            if advisor.get('name') != "Unknown":
                people.append(advisor)

# Initial URLs to process
initial_urls = [
    "https://genealogy.math.ndsu.nodak.edu/id.php?id=310782",
    "https://genealogy.math.ndsu.nodak.edu/id.php?id=298616",
    "https://genealogy.math.ndsu.nodak.edu/id.php?id=287468",
    "https://genealogy.math.ndsu.nodak.edu/id.php?id=287466",
    "https://genealogy.math.ndsu.nodak.edu/id.php?id=230926",
    "https://genealogy.math.ndsu.nodak.edu/id.php?id=287478",
    "https://genealogy.math.ndsu.nodak.edu/id.php?id=287479",
    "https://genealogy.math.ndsu.nodak.edu/id.php?id=223724",
    "https://genealogy.math.ndsu.nodak.edu/id.php?id=287480",
    "https://genealogy.math.ndsu.nodak.edu/id.php?id=287481",
]
    
    # Number of URLs to generate
num_urls = 30000

# Get the last URL in the list
last_url = initial_urls[-1]

# Extract the id from the last URL
last_id = int(last_url.split('=')[-1])

# Generate new URLs by incrementing the id
for i in range(1, num_urls + 1):
    new_id = last_id + i
    new_url = f"https://genealogy.math.ndsu.nodak.edu/id.php?id={new_id}"
    initial_urls.append(new_url)   
# Define the URL of the page with the list of advisors
url = "https://genealogy.math.ndsu.nodak.edu/most-students.php?count=250"

# Fetch the page content
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all the advisor links in the table
advisor_links = []
table = soup.find('table')
if table:
    for row in table.find_all('tr')[1:]:  # Skip the header row
        columns = row.find_all('td')
        if columns:
            advisor_link = columns[0].find('a')
            if advisor_link and advisor_link.get('href'):
                advisor_links.append('https://genealogy.math.ndsu.nodak.edu/' + advisor_link.get('href'))

# Limit to the first 250 advisors
advisor_links = advisor_links[:250]

# Process URLs in parallel using ThreadPoolExecutor
MAX_THREADS = 10  # Adjust based on your system's capabilities

with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    futures = {executor.submit(process_url, url): url for url in initial_urls }
    
    for future in as_completed(futures):
        url = futures[future]
        try:
            future.result()
        except Exception as e:
            logging.error(f"Error processing URL: {url} - {e}")
            print(f"Error processing URL: {url} - {e}")

# Insert the people into the database
counter = 0
for p in people:
    counter += 1
    print(counter)
    try:
        sql_query = """INSERT INTO people (id, name, url) VALUES (?, ?, ?);"""
        values = (p['id'], p['name'], p['url'])
        cursor.execute(sql_query, values)
        sqliteConnection.commit()
    except sqlite3.IntegrityError:
        # Skip if the person is already in the database
        continue

# Close the connection
sqliteConnection.close()

print(f"Total people processed and stored: {counter}")
print(f"Total timeout URLs: {len(timeout_urls)}")


# print("Unique Students:")
# print(unique_students)
# print(len(unique_students))
# print("\nUnique Advisors:")
# print(unique_advisors)
# print(len(unique_advisors))
# r = requests.get(url)
# newsoup = BeautifulSoup(r.content,'html5lib')
#step 5: doing this for all students 

# for student in unique_students:
#     if student.get('name') != "Unknown":
#         process_url(student.get('url'))
#         print(student)
# print(len(unique_students))

# for advisor in unique_advisors:
#         process_url(advisor.get('url'))
#         print(advisor)
# print(len(unique_advisors))
# try:
 #          lirierut
 
#  except e: 
     
#hi
# test
