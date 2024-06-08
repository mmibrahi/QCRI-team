import requests
from bs4 import BeautifulSoup
import json

def extract_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find name
    name = soup.find('div', {'class': 'name'}).text

    # Find birthdate and place of birth
    birth_info = soup.find('div', {'id': 'birth_info'}).text
    birthdate, place_of_birth = birth_info.split(',')

    # Find publications
    publications = [pub.text for pub in soup.find_all('div', {'class': 'publication'})]

    # Find advisors and descendants
    advisors = [advisor.text for advisor in soup.find_all('div', {'class': 'advisor'})]
    descendants = [descendant.text for descendant in soup.find_all('div', {'class': 'descendant'})]

    # Find additional information
    additional_info = soup.find('div', {'id': 'additional_info'}).text

    # Save the information in a dictionary
    info = {
        'name': name,
        'birthdate': birthdate,
        'place_of_birth': place_of_birth,
        'publications': publications,
        'advisors': advisors,
        'descendants': descendants,
        'additional_info': additional_info,
    }

    # Save the dictionary in a JSON file
    with open('info.json', 'w') as f:
        json.dump(info, f)

# Replace 'url' with the URL of the webpage you want to scrape
extract_info('url')