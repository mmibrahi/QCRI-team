import unidecode
import wikipediaapi
import csv
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed

# Connect to the SQLite database
sqliteConnection = sqlite3.connect('sql.db')
cursor = sqliteConnection.cursor()

# Query to select all records from the people table
cursor.execute("""SELECT * FROM people;""")

# Fetch all results
results = cursor.fetchall()

# Define the user agent with application name, version, and contact information
user_agent = 'QCRI-geonology (mmibrahi@andrew.cmu.edu)'

# Initialize Wikipedia API with user agent
wiki_wiki = wikipediaapi.Wikipedia(user_agent,'ar')

# Function to get Wikipedia page and extract details
def get_wikipedia_details(name):
    # Removing special accents from the name
    page = wiki_wiki.page(unidecode.unidecode(name))
    if page.exists():
        details = {
            'Name': name,
            'Summary': page.summary,
            #'Summary': page.summary[:200],  # First 200 characters of the summary
            'URL': page.fullurl
        }
        return details
    else:
        return {'Name': name, 'Summary': 'Not found', 'URL': ''}

# Extract details for each name in parallel
data = []

# Use ThreadPoolExecutor to parallelize the API calls
with ThreadPoolExecutor(max_workers=10) as executor:
    # Submit tasks to the executor
    future_to_name = {executor.submit(get_wikipedia_details, row[1]): row[1] for row in results}

    # Process the results as they complete
    for future in as_completed(future_to_name):
        name = future_to_name[future]
        try:
            details = future.result()
            data.append(details)
            print(details)
        except Exception as exc:
            print(f'{name} generated an exception: {exc}')

# Write the extracted data to a CSV file
with open('wikipedia_details.csv', 'w', newline='') as csvfile:
    fieldnames = ['Name', 'Summary', 'URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)

print("Data extraction complete. Check wikipedia_details.csv for results.")

