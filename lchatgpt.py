import sqlite3
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

from openai import OpenAI
client = OpenAI(api_key='sk-proj-jDnwC5co9MVyaCb4Mbs3T3BlbkFJXPdQydea0cvPWDQ6wZRw')

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

#---------------------------------------
# Connect to the SQLite database
sqliteConnection = sqlite3.connect('sql.db')
cursor = sqliteConnection.cursor()
# Query to select all records from the people table
cursor.execute('SELECT * FROM people')
# Fetch all results
results = cursor.fetchall()
# Delimiter to split the URLs and page contents
delimiter = '---PAGE BREAK---'
# Process each row and convert back to lists
people_data = []

for row in results:
    name = row[1]
    othersummary = row[2]
    otherurl = row[3]

    if othersummary and otherurl:
        # Split the strings back into lists
        page_contents = othersummary.split(delimiter)
        urls = otherurl.split(delimiter)
        
        # Append the data as a tuple to the people_data list
        people_data.append((name, urls, page_contents))
        
        for page in page_contents:
            prompt_2 = f"""
                        Your task is to perform the following actions: 
                        1 - Find the name of the person
                        2 - Find his date of birth
                        3 - Find any publication
                        4 - Find his advisors and students
                        5 - find any other information you think is relevant about the
                            person's professional life 
                        
                        Use the following format:
                        Name: <name>
                        Birth: <date of birth>
                        Publication: <summary translation>
                        Students: <list of students>
                        Output JSON: <json with summary and num_names>

                        Text: <{page}>
                        """
            text = f"""{page}"""
            response = get_completion(prompt_2)
            print("\nCompletion for prompt :")
            print(response)
        
        # Print for debugging
        print(f"Name: {name}")
        print(f"URLs: {urls}")
        print(f"Page Contents: {page_contents[:2]}")  # Printing only the first 2 contents for brevity

# Close the connection
cursor.close()
sqliteConnection.close()





