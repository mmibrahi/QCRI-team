import sqlite3
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from googlesearch import search

# Function to get the whole HTML content from a URL
def get_whole_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        soup = BeautifulSoup(response.text, "html.parser")
        # Get text without HTML tags
        plain_text = soup.get_text()
        return plain_text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# Connect to the SQLite database
sqliteConnection = sqlite3.connect('sql.db')
cursor = sqliteConnection.cursor()

# Query to select all records from the people table
cursor.execute("""SELECT * FROM people;""")

# Fetch all results
results = cursor.fetchall()

# Delimiter to join and split the URLs and page contents
delimiter = '---PAGE BREAK---'
MAX_THREADS = 10

# Process each row
count = 0
for row in results:
    name = row[1]
    count += 1
    print(count)
    
    # Perform a Google search for the name
    search_query = f"{name}"
    search_results = list(search(search_query, num_results=5))
    
    if search_results:
        page_contents = []
        urls = []

        # Use ThreadPoolExecutor to fetch pages in parallel
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_url = {executor.submit(get_whole_page, url): url for url in search_results}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    page_content = future.result()
                    if page_content:
                        page_contents.append(page_content)
                        urls.append(url)
                except Exception as e:
                    print(f"Error processing {url}: {e}")

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