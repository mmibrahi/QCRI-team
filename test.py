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


import torch
from transformers import pipeline
generate_text = pipeline(model="databricks/dolly-v2-3b", torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="auto")



text = f""" """

input_text = f"""  Your task is to perform the following actions if you did not find information say hello, do not return the prompt only the data: 
                                1 - Find the name of the person
                                2 - Find his place of birth
                                3 - Find any publication
                                4 - Find his advisors and Descendants
                                5 - find any other information you think is relevant about the person's professional life 
                                
                                Text: {text}""",
   


res = generate_text(input_text)
print(res[0]["generated_text"])
