from ollama import Client
import sqlite3


client = Client(host = "http://127.0.0.1:11434")

# generate_text = pipeline(model="databricks/dolly-v2-12b", torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="auto")

sqliteConnection = sqlite3.connect('sql.db')
cursor = sqliteConnection.cursor()
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
    othersummary = row[3]
    otherurl = row[4]

    if othersummary and otherurl:
        # Split the strings back into lists
        urls = otherurl.split(delimiter)
        # page_contents = othersummary.split(delimiter)
        # Append the data as a tuple to the people_data list
        people_data.append((name, urls, othersummary))
        # for page in page_contents:
        othersummary = othersummary.replace("\n", " ")
        try:
                text = f"""{othersummary}"""
                prompt =  f"""Your task is to extract specific information from the provided "text". Follow the instructions carefully and provide only the relevant data regarding {name} in the specified format.
                                Text = {text}
                                Instructions:
                                1. Find the birthdate (date of birth) and place of birth:
                                2. Find any publication:
                                3. Find the advisors and descendants:
                                4. Find any additional relevant information about the person:

                                Format your response as follows:
                                Name: {name}
                                Birthdate: <birth place and date>
                                Publication: <short summary of publication>
                                Students: <number or list of students>
                                Extra information: <additional relevant information>                
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
sqliteConnection.close()