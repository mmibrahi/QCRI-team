import sqlite3

# Connect to the SQLite database
sqliteConnection = sqlite3.connect('sql.db')
cursor = sqliteConnection.cursor()

# Query to select all records from the people table
cursor.execute("""SELECT * FROM people;""")

# Fetch all results
results = cursor.fetchall()

# Delimiter to join and split the URLs and page contents
delimiter = '---PAGE BREAK---'

with open("wikidata5m_text.txt", "r", encoding="utf-8") as f:
    data = f.read()

# Split the data using the delimiter
entries = data.split(delimiter)

# Create a dictionary to store name and corresponding details
wikidata_dict = {}
for i in range(0, len(entries) - 1, 2):
    name = entries[i].strip()
    detail = entries[i + 1].strip()
    wikidata_dict[name] = detail

# Function to find details for a given name
def find_details(name):
    return wikidata_dict.get(name, "Details not found.")

# Process each row in the results from the database
count = 0 
for row in results:
    name = row[1]
    details = find_details(name)
    count += 1
    if count > 100: break
    print(f"Details for {name}:\n{details}\n")

# Close the database connection
sqliteConnection.close()
