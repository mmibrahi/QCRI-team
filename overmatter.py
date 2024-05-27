import scrapy
from bs4 import BeautifulSoup
import requests 
import time as t
import sqlite3
#print(r.content)
#print(soup.prettify())      
# getAdvisors(newsoup)
# getStudents(newsoup)

sqliteConnection = sqlite3.connect('sql.db')
cursor = sqliteConnection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS people (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL
)
''')

#step 3: getting the students
def getStudents(soup,url):
    
    table = soup.find('table') #, attrs = {'a' : ''}) 
    students = table.find_all('a') if table else []

    def parse_student_element(student_element):
        student_id = student_element['href'].split('=')[-1]
        student_name = student_element.text.strip()
        student_url = url.split('?')[0] + f'?id={student_id}'
        return {'id': student_id, 'name': student_name, 'url': student_url}

    newstudents = []
    #print("Students:")
    for student in students:
        newstudents.append(parse_student_element(student))
    #print(newstudents)
    return newstudents

#step 4: getting advisors
def getAdvisors(soup,url):
    advisors = []
    if soup:
        # Find all <p> tags in the page
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
                    advisors.append({'id' : advisor_url , 'name': advisor_name, 'url': advisor_url})
    return advisors 


# Global data structures to hold unique students and advisors
# unique_students = []
# unique_advisors = []
people = []
visited_urls = set()

# Function to process a URL and extract students and advisors
def process_url(url):
    if url in visited_urls:
        return  # Skip if URL already visited
    visited_urls.add(url)

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    
    # Get students and advisors from the current URL
    students = getStudents(soup, url)
    advisors = getAdvisors(soup, url)
    
    #print(students)
    
    # Add unique students and advisors to global lists
    for student in students:
        if student not in people:
            if student.get('name') != "Unknown":
                people.append(student)
                #process_url(student.get('url'))
                
    for advisor in advisors:
        if advisor not in people:
            if advisor.get('name') != "Unknown":
                people.append(advisor)
                #process_url(advisor.get('url'))
    t.sleep(0.5)


#step 1: accesing the html content from the webpage
#person 1


with open("log.txt", "a") as f:
    
    try:
        url1 = "https://genealogy.math.ndsu.nodak.edu/id.php?id=310782"
        process_url(url1)
        url2 = "https://genealogy.math.ndsu.nodak.edu/id.php?id=298616"
        process_url(url2)
        url3 = "https://genealogy.math.ndsu.nodak.edu/id.php?id=287468"
        process_url(url3)
        url4 = "https://genealogy.math.ndsu.nodak.edu/id.php?id=287466"
        process_url(url4)
        url5 = "https://genealogy.math.ndsu.nodak.edu/id.php?id=230926"
        process_url(url5)
        url6 = "https://genealogy.math.ndsu.nodak.edu/id.php?id=287478"
        process_url(url6)
        url7 = "https://genealogy.math.ndsu.nodak.edu/id.php?id=287479"
        process_url(url7)
        url8 = "https://genealogy.math.ndsu.nodak.edu/id.php?id=223724"
        process_url(url8)
        url9 = "https://genealogy.math.ndsu.nodak.edu/id.php?id=287480"
        process_url(url9)
        url10 = "https://genealogy.math.ndsu.nodak.edu/id.php?id=217509"
        process_url(url10)
        
    except Exception as e:
        f.write(f"[{t.time()}] ", e)
    
    
# print("everyone:")
# print(len(people))
counter = 0
# for p in people:
#     process_url(p.get('url'))
#     counter = counter + 1
#     print(counter)
#     #print(p)
# print(len(people)) 

for p in people:
    counter += 1
    print(counter)
    try:
        process_url(p.get('url'))
        cursor.execute('INSERT INTO people (id, name, url) VALUES (?, ?, ?)', (p['id'], p['name'], p['url']))
        sqliteConnection.commit()
        #print(counter)
    except sqlite3.IntegrityError:
        # Skip if the person is already in the database
        continue


print(len(people))
# Close the connection
sqliteConnection.close()

print(f"Total people processed and stored: {counter}")