# import sqlite3

# sqliteConnection = sqlite3.connect("/Users/arwaelaradi/Documents/GitHub/QCRI-team/test.db")
# cursor = sqliteConnection.cursor()

# # cursor.execute('''
# # CREATE TABLE IF NOT EXISTS people (
# #     id number PRIMARY KEY,
# #     name varchar2(20) NOT NULL
# # )
# # ''')
# # sql_query = """INSERT INTO people (id, name) VALUES (?, ?);"""
# # values = (1,'Arwa')

# # try:
# #     # Execute the INSERT INTO statement
# #     cursor.execute(sql_query, values)

# #     # Commit the transaction
# #     sqliteConnection.commit()
# #     print("Data inserted successfully.")

# # except sqlite3.DatabaseError as e:
# #     print(f"Database error: {e}")

# # except Exception as e:
# #     print(f"Error: {e}")

# # finally:
# #     # Close the cursor and connection
# #     cursor.close()
# #     sqliteConnection.close()

# sql_query = """SELECT * FROM PEOPLE;"""
# try:
#     # cursor.execute(sql_query)
#     cursor.execute(sql_query)
#     rows = cursor.fetchall()
#     for r in rows:
#         print(r)   
# except sqlite3.DatabaseError as e:
#     print(f"Database error: {e}")
# except Exception as e:
#     print(f"Error: {e}")
# finally:
#     # Close the cursor and connection
#     cursor.close()
# sqliteConnection.close()

# import sqlite3
# database_path = "/Users/arwaelaradi/Documents/GitHub/QCRI-team/test.db"
# def check_integrity(database_path):
#     try:
#         connection = sqlite3.connect(database_path)
#         cursor = connection.cursor()
#         cursor.execute("PRAGMA integrity_check;")
#         result = cursor.fetchone()
#         print(result)
#         cursor.close()
#         connection.close()
#     except sqlite3.DatabaseError as e:
#         print(f"Database error: {e}")

# check_integrity('your_database.db')

# from gpt4all import GPT4All
# model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
# url = 'https://genealogy.math.ndsu.nodak.edu/id.php?id=310782'
# text = f""" retrieve the name the person from the url:
#         {url}"""
# response = model.generate(text)

# print(response)


from ollama import Client
import sqlite3
# import os
# os.environ["OPENAI_API_KEY"] = "sk-proj-wzoCUE9g8TJ9pytcOWFKT3BlbkFJ7hN1VNyAxSEEDPsrq4Zc"


# messages = [{ "content": "Hello, how are you?","role": "user"}]

# # openai call


client = Client(host = "http://127.0.0.1:11434")

# generate_text = pipeline(model="databricks/dolly-v2-12b", torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="auto")

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

# import sqlite3
# import requests
# import ssl
# from bs4 import BeautifulSoup
# from googlesearch import search

# # Function to get the whole HTML content from a URL
# def get_whole_page(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise HTTPError for bad responses
#         soup = BeautifulSoup(response.text, "html.parser")
#         plain_text = soup.get_text()
#         return plain_text
#     except Exception as e:
#         print(f"Error fetching {url}: {e}")
#         return None


# def url_meets_criteria(url, name):
#     if "wikipedia" in url.lower():
#         return False
#     if "com" in url.lower() or "biography" in url.lower():
#         return True
#     return False

# # Function to check if page content meets the criteria
# def content_meets_criteria(content, name):
#     return content.lower().count(name.lower()) >= 5

# # Connect to the SQLite database
# sqliteConnection = sqlite3.connect('sql.db')
# cursor = sqliteConnection.cursor()

# # Query to select all records from the people table
# cursor.execute("""SELECT * FROM people;""")

# # Fetch all results
# results = cursor.fetchall()

# # Delimiter to join and split the URLs and page contents
# delimiter = '---PAGE BREAK---'
# ssl._create_default_https_context = ssl._create_unverified_context

# # Process each row
# count = 0
# for row in results:
#     name = row[1]
#     count += 1
#     print(count)
#     # Perform a Google search for the name
#     query = f"{name}"
#     search_results = list(search(query, num = 10,stop = 10,pause=5))
#     # search_results = list(search(search_query, num_results = 10))
    
#     if search_results:
#         page_contents = []
#         urls = []
        
#         for url in search_results:
#             if not url_meets_criteria(url, name):
#                 continue
                
#             page_content = get_whole_page(url)
#             if page_content and content_meets_criteria(page_content, name):
#                 page_contents.append(page_content)
#                 urls.append(url)
            
#         if page_contents and urls:
#                 # Join the page contents and URLs with a delimiter
#             final_page_content = delimiter.join(page_contents)
#             final_url = delimiter.join(urls)
                
#                 # Update the row in the database
#             cursor.execute('''
#                 UPDATE people
#                     SET othersummary = ?, otherurl = ?
#                     WHERE name = ?;
#                 ''', (final_page_content, final_url, name))
                
#                 # Commit the changes after each update
#             sqliteConnection.commit()
#             print(f"Updated {name}")

# # Close the connection
# cursor.close()
# sqliteConnection.close()

#https://www.google.com/search?q=ibn+sina

