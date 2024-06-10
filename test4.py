
import requests
import ssl
import face_recognition
import os
import cv2
from bs4 import BeautifulSoup
from googlesearch import search
import psycopg2
# comment
# Set SSL context to unverified
ssl._create_default_https_context = ssl._create_unverified_context
conn = psycopg2.connect(dbname="postgres",
                        user="postgres",
                        password="1245!Taha",
                        host="localhost",
                        port="5432")

cursor = conn.cursor()

# Function to get the whole HTML content from a URL along with image URLs
def get_whole_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        soup = BeautifulSoup(response.text, "html.parser")
        plain_text = soup.get_text()

        # Extract image URLs
        # img_urls = [img["src"] for img in soup.find_all("img")]
        return plain_text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, None

# Function to save images with an offset to avoid overriding
# def save_images( image_urls ,folder_name="image_directory"):
#     if not os.path.exists(folder_name):
#         os.makedirs(folder_name)

#     for i, url in enumerate(image_urls):
#         try:
#             response = requests.get(url)
#             response.raise_for_status()

#             with open(os.path.join(folder_name, f"image_{i}.jpg"), "wb") as f:
#                 f.write(response.content)
#                 print(f"Saved image_{i}.jpg")
#         except Exception as e:
#             print(f"Error saving image from {url}: {e}")
#     return os.listdir(folder_name)


# Function to check if URL meets criteria
def url_meets_criteria(url, name):
    name = name.split(" ")
    if "wikipedia" in url.lower() or "genealogy" in url.lower() or "amazon" in url.lower() or "linkedin" in url.lower() or "facebook" in url.lower() or "twitter" in url.lower() or "instagram" in url.lower():
        return False
    # if "bio" in url.lower() or "edu" in url.lower() or (name[0].lower() in url.lower() and name[-1].lower() in url.lower()):
    #     return True
    return True

def content_meets_criteria(content, name):
    return content.lower().count(name.lower()) >= 2

# Connect to the SQLite database
def main():
    try:
        cursor = conn.cursor()

        # Query to select all records from the people table
        cursor.execute("SELECT * FROM people")

        # Fetch all results
        results = cursor.fetchall()

        # Delimiter to join and split the URLs and page contents
        delimiter = '---PAGE BREAK---'

        # Initialize image index
        image_index = 0

        # Process each row
        count = 0
        for row in results:
            name = row[1]

            count += 1
            print(f"Processing {count}: {name}")

            # Perform a Google search for the name
            query = f"{name}"
            search_results = list(search(query, num=15, stop=15, pause=2))

            if search_results:
                page_contents = []
                image_urls = []
                urls = []

                for url in search_results:
                    if not url_meets_criteria(url, name):
                        continue

                    page_content = get_whole_page(url)

                    if page_content and content_meets_criteria(page_content, name):
                        page_contents.append(page_content)
                        # image_urls.extend(img_urls)
                        # for image_url in img_urls:
                        #     image = cv2.imread(image_url)
                        #     face_locations = face_recognition.face_locations(image)
                        #     # Check if any faces were found
                        #     if face_locations:
                        #         print("Face detected in the image.")
                        #     else:
                        #         print("No face detected in the image.")
                        urls.append(url)

                if page_contents and urls:
                    # Join the page contents and URLs with a delimiter
                    final_page_content = delimiter.join(page_contents)
                    final_url = delimiter.join(urls)
                    # final_image_urls = delimiter.join(image_urls) if image_urls else None
                    # if image_urls:
                    #     directory = save_images(image_urls, "image_directory")
                    # for image in os.listdir("/Users/arwaelaradi/Documents/GitHub/QCRI-team/image_directory"):
                    #     image = face_recognition.load_image_file("/Users/arwaelaradi/Desktop/download.jpg")
                    #     face_locations = face_recognition.face_locations(image)
                    #         # Check if any faces were found
                    #     if face_locations:
                    #         print("Face detected in the image.")
                            
                    #     else:
                    #         print("No face detected in the image.")
                    # Update the row in the database
                    cursor.execute('''
                        UPDATE people
                        SET othersummary = %s, otherurl = %s
                        WHERE name = %s;
                    ''', (final_page_content, final_url, name))

                    # Commit the changes after each update
                    conn.commit()

                    # Save images with the current image index
                    

                        # Update the image index
                        # image_index += len(image_urls)

                    print(f"Updated {name}")

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        # Close the connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def face_rec():
    for image in os.listdir("/Users/arwaelaradi/Documents/GitHub/QCRI-team/image_directory"):
        print(image)
if __name__ == "__main__":
    main()

