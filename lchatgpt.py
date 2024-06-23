from ollama import Client
import sqlite3
import json
import requests
from bs4 import BeautifulSoup
import psycopg2
# ss
client = Client(host = "http://127.0.0.1:11434")

# generate_text = pipeline(model="databricks/dolly-v2-12b", torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="auto")

conn = psycopg2.connect(dbname="postgres",
                        user="postgres",
                        password="1245!Taha",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()
# Query to select all records from the people table
cursor.execute("""SELECT * FROM people;""")
# Fetch all results
results = cursor.fetchall()
# Delimiter to split the URLs and page contents
delimiter = '---PAGE BREAK---'
# Process each row and convert back to lists
people_data = []
#ignore this comment

for row in results:
    name = row[1]
    url = row[2]
    othersummary = row[5]
    otherurl = row[6]

    if othersummary and otherurl:
        # Split the strings back into lists
        # urls = otherurl.split(delimiter)
        # page_contents = othersummary.split(delimiter)
        # Append the data as a tuple to the people_data list
        people_data.append((name,url, otherurl, othersummary))
        # for page in page_contents:
        othersummary = othersummary.replace("\n", " ")
        try:
                text = f"""{othersummary}"""
                prompt =  f"""Your task is to extract specific information from the provided "text". Follow the instructions carefully and provide only the relevant data regarding {name} in the specified format
                                only display the json format answer, do not display anything before or after the answer:
                                Text = {text}
                                Instructions:
                                1. Find the birthdate (date of birth) and place of birth, the bithdate should be in the format of "Month Day, Year" (e.g., January 1, 2000) and the place of birth should be in the format of "City, Country" (e.g., New York City, USA):
                                2. Find any publication:
                                3. Find the advisors and descendants:
                                4. Find any additional relevant information about the person:

                                Format your response as a json file and save it:
                                Name: {name}
                                Birthdate: <birth place and date>
                                Publication: <names of publication: summary of publications>
                                Advisors: <number or list of Advisors>
                                Descendants: <number or list of Descendants>
                                Extra information: <additional relevant information>   

                                only display the json format answer, do not display anything before or after the answer:
                                """
                response = client.chat(model = "llama3", messages = [{
                    'role': 'user',
                    'content': prompt
                }])
                print(response['message']['content'])

        except Exception as e:
                print(f"Error processing page: {e}")
        # Print for debugging
    # print(f"Name: {name}")
        # print(f"URLs: {urls}")
        # print(f"Page Contents: {page_contents[:2]}")  # Printing only the first 2 contents for brevity

# Close the connection
cursor.close()
conn.close()