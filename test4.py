import sqlite3
import requests
import ssl
import face_recognition
import os
import cv2
from bs4 import BeautifulSoup
from googlesearch import search
# comment
# Set SSL context to unverified
ssl._create_default_https_context = ssl._create_unverified_context

# Function to get the whole HTML content from a URL along with image URLs
def get_whole_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        soup = BeautifulSoup(response.text, "html.parser")
        plain_text = soup.get_text()

        # Extract image URLs
        img_urls = [img["src"] for img in soup.find_all("img")]
        return plain_text, img_urls
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, None

# Function to save images with an offset to avoid overriding
def save_images( image_urls ,folder_name="image_directory"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url)
            response.raise_for_status()

            with open(os.path.join(folder_name, f"image_{i}.jpg"), "wb") as f:
                f.write(response.content)
                print(f"Saved image_{i}.jpg")
        except Exception as e:
            print(f"Error saving image from {url}: {e}")
    return os.listdir(folder_name)


# Function to check if URL meets criteria
def url_meets_criteria(url, name):
    if "wikipedia" in url.lower() or "genealogy" in url.lower():
        return False
    if "edu" in url.lower() or "biograph" in url.lower() or "bio" in url.lower():
        return True
    return False

# Connect to the SQLite database
def main():
    try:
        sqliteConnection = sqlite3.connect('sql.db')
        cursor = sqliteConnection.cursor()

        # Query to select all records from the people table
        cursor.execute("SELECT * FROM people;")

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
            search_results = list(search(query, num=10, stop=10, pause=2))

            if search_results:
                page_contents = []
                image_urls = []
                urls = []

                for url in search_results:
                    if not url_meets_criteria(url, name):
                        continue

                    page_content, img_urls = get_whole_page(url)
                    if page_content:
                        page_contents.append(page_content)
                        image_urls.extend(img_urls)
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
                    final_image_urls = delimiter.join(image_urls) if image_urls else None
                    if image_urls:
                        directory = save_images(image_urls, "image_directory")
                    for image in os.listdir("/Users/arwaelaradi/Documents/GitHub/QCRI-team/image_directory"):
                        image = face_recognition.load_image_file("/Users/arwaelaradi/Desktop/download.jpg")
                        face_locations = face_recognition.face_locations(image)
                            # Check if any faces were found
                        if face_locations:
                            print("Face detected in the image.")
                            
                        else:
                            print("No face detected in the image.")
                    # Update the row in the database
                    cursor.execute('''
                        UPDATE people
                        SET othersummary = ?, otherurl = ?, imageurls = ?
                        WHERE name = ?;
                    ''', (final_page_content, final_url, final_image_urls, name))

                    # Commit the changes after each update
                    sqliteConnection.commit()

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
        if sqliteConnection:
            sqliteConnection.close()

def face_rec():
    for image in os.listdir("/Users/arwaelaradi/Documents/GitHub/QCRI-team/image_directory"):
        print(image)
if __name__ == "__main__":
    main()

