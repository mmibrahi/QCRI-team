import unidecode
import wikipediaapi
import csv

# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia('en')

# Function to get Wikipedia page and extract details
def get_wikipedia_details(name):
    #removing special accents from the name
    page = wiki_wiki.page(unidecode.unidecode(name))
    if page.exists():
        details = {
            'Name': name,
            'Summary': page.summary[:200],  # First 200 characters of the summary
            'URL': page.fullurl
        }
        return details
    else:
        return {'Name': name, 'Summary': 'Not found', 'URL': ''}

# Read names from the text file
with open('names.txt', 'r') as file:
    names = [line.strip() for line in file.readlines()]

# Extract details for each name
data = []
for name in names:
    details = get_wikipedia_details(name)
    data.append(details)

# Write the extracted data to a CSV file
with open('wikipedia_details.csv', 'w', newline='') as csvfile:
    fieldnames = ['Name', 'Summary', 'URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow(row)

print("Data extraction complete. Check wikipedia_details.csv for results.")
