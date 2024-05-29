import sqlite3

from gpt4all import GPT4All
model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")

# def get_completion(prompt, model="gpt-3.5-turbo"):
#     messages = [{"role": "user", "content": prompt}]
#     response = client.chat.completions.create(
#         model=model,
#         messages=messages,
#         temperature=0, # this is the degree of randomness of the model's output
#     )
#     return response.choices[0].message["content"]

def get_completion(prompt, model):
    return model.generate(prompt, temp = 0)

#---------------------------------------
# Connect to the SQLite database
sqliteConnection = sqlite3.connect('/Users/arwaelaradi/Documents/GitHub/QCRI-team/sql.db')
cursor = sqliteConnection.cursor()
# Query to select all records from the people table
cursor.execute("""SELECT * FROM people;""")
# Fetch all results
results = cursor.fetchall()
# Delimiter to split the URLs and page contents
delimiter = '---PAGE BREAK---'
# Process each row and convert back to lists
people_data = []

for row in results:
    name = row[1]
    othersummary = row[3]
    otherurl = row[4]

    if othersummary and otherurl:
        # Split the strings back into lists
        page_contents = othersummary.split(delimiter)
        urls = otherurl.split(delimiter)
        
        # Append the data as a tuple to the people_data list
        people_data.append((name, urls, page_contents))
        
    for page in page_contents:
        try:
            text = f"""{page[0:100]}"""
            prompt_2 = f"""
                        say hello
                            Text: <{text}>
                            """
                # print(page.status())
            response = get_completion(prompt_2,model)
            print("\nCompletion for prompt :")
            print(response)
        except Exception as e:
            print(f"Error processing page: {e}")
        # Print for debugging
    print(f"Name: {name}")
        # print(f"URLs: {urls}")
        # print(f"Page Contents: {page_contents[:2]}")  # Printing only the first 2 contents for brevity

# Close the connection
cursor.close()
sqliteConnection.close()





