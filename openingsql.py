import sqlite3
import requests
from bs4 import BeautifulSoup
from googlesearch import search
# test

# Function to get the whole HTML content from a URL
def get_whole_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        soup = BeautifulSoup(response.text, "html.parser")
        plain_text = soup.get_text()
        return plain_text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def url_meets_criteria(url, name):
    if "wikipedia" in url.lower():
        return False
    if "edu" in url.lower() or "biography" in url.lower():
        return True
    return False

# Function to check if page content meets the criteria
def content_meets_criteria(content, name):
    return content.lower().count(name.lower()) >= 5

# Connect to the SQLite database
sqliteConnection = sqlite3.connect('sql.db')
cursor = sqliteConnection.cursor()

# Query to select all records from the people table
cursor.execute("""SELECT * FROM people;""")

# Fetch all results
results = cursor.fetchall()

# Delimiter to join and split the URLs and page contents
delimiter = '---PAGE BREAK---'

# Process each row
count = 0
for row in results:
    name = row[1]
    count += 1
    print(count)
    # Perform a Google search for the name
    search_query = f"{name}"
    search_results = list(search(search_query, num_results=2)) 
    
    if search_results:
        page_contents = []
        urls = []

        for url in search_results:
            if not url_meets_criteria(url, name):
                continue
            
            page_content = get_whole_page(url)
            if page_content and content_meets_criteria(page_content, name):
                page_contents.append(page_content)
                urls.append(url)
        
        if page_contents and urls:
            # Join the page contents and URLs with a delimiter
            final_page_content = delimiter.join(page_contents)
            final_url = delimiter.join(urls)
            
            # Update the row in the database
            cursor.execute('''
                UPDATE people
                SET othersummary = ?, otherurl = ?
                WHERE name = ?;
            ''', (final_page_content, final_url, name))
            
            # Commit the changes after each update
            sqliteConnection.commit()
            print(f"Updated {name}")

# Close the connection
cursor.close()
sqliteConnection.close()

#https://www.google.com/search?q=ibn+sina
