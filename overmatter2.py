import sqlite3
import wikipediaapi
import csv
import unidecode
import requests
from bs4 import BeautifulSoup
from googlesearch import search

# Function to get the first paragraph from a URL
def get_first_paragraph(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Get the first paragraph
        paragraph = soup.find('p')
        if paragraph:
            return paragraph.text
        else:
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# Connect to the SQLite database
sqliteConnection = sqlite3.connect('sql.db')
cursor = sqliteConnection.cursor()

# Query to select all records from the people table
cursor.execute('SELECT * FROM people')

# Fetch all results
results = cursor.fetchall()

# Process each row
for row in results:
    name = row[1]
    
    # Perform a Google search for the name
    search_query = f"{name}"
    search_results = list(search(search_query, num_results=2))
    
    if search_results:
        summaries = []
        urls = []

        for url in search_results[:2]:
            summary = get_first_paragraph(url)
            if summary:
                summaries.append(summary)
                urls.append(url)
        
        if summaries and urls:
            # Join the summaries and URLs with a delimiter if necessary
            final_summary = ' '.join(summaries)
            final_url = ' '.join(urls)
            
            # Update the row in the database
            cursor.execute('''
                UPDATE people
                SET othersummary = ?, otherurl = ?
                WHERE name = ?
            ''', (final_summary, final_url, name))
            
            # Commit the changes after each update
            sqliteConnection.commit()
            print(row)

# Close the connection
cursor.close()
sqliteConnection.close()