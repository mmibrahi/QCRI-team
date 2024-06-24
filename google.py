from urllib.parse import urlparse
import requests
import ssl
# import face_recognition
import os
import cv2
import spacy 
from rapidfuzz import fuzz
from bs4 import BeautifulSoup
from googlesearch import search
import psycopg2
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
        img_urls = []
        parsed_url = urlparse(url)
        root = parsed_url.netloc
        for img in soup.find_all("img"):
            src = img["src"]
            if not src.startswith("https:"):
                src = "https://"+ root+"/" + src
            img_urls.append(src)
        return plain_text, img_urls
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None, None

# Function to save images with an offset to avoid overriding
def save_images( image_urls ,folder_name="image_directory", start_index=0):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    for i, url in enumerate(image_urls,start=start_index):
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
    if "wiki" in url.lower() or "genealogy" in url.lower() or "amazon" in url.lower() or "linkedin" in url.lower() or "facebook" in url.lower() or "twitter" in url.lower() or "instagram" in url.lower():
        return False
    # if "bio" in url.lower() or "edu" in url.lower() or (name[0].lower() in url.lower() and name[-1].lower() in url.lower()):
    #     return True
    return True

# vectorization is used to check similarity between names
def content_meets_criteria(content, name):
    name1 = name.split(" ")
    f1 = content.find(name1[0])
    f2 = content.find(name1[-1])
    name2 = content[f1:f2+len(name1[-1])]
    similarity = fuzz.ratio(name, name2)
    print(similarity)
    if similarity > 80:
        return True
    

# Connect to the SQLite database
def main():
    try:
        cursor = conn.cursor()
        # Query to select all records from the people table
        cursor.execute("SELECT * FROM people2 ORDER BY id::INTEGER ASC; ")

        # Fetch all results
        results = cursor.fetchall()

        # Initialize image index
        image_index = 0

        # Process each row
        for count, row in enumerate(results, start=1):
            name = row[1]
            print(f"Processing {count}: {name}")

            # Initialize page contents and URLs
            page_contents = []
            urls = []

            # Get content and image URLs from the main URL
            genology_content, genology_imgs = get_whole_page(row[2])
            page_contents.append(genology_content)
            image_urls = genology_imgs

            # Perform a Google search for the name
            query = f"{name}"
            search_results = list(search(query, num=10, stop=10, pause=2))

            if search_results:
                for url in search_results:
                    if not url_meets_criteria(url, name):
                        continue
                    
                    # Get content and image URLs from the search result URL
                    page_content, img_urls = get_whole_page(url)
                    if page_content is not None:
                        if content_meets_criteria(page_content, name):
                            page_contents.append(page_content)
                            image_urls.extend(img_urls)
                            urls.append(url)

                if page_contents and urls:
                    # Join the page contents and URLs with a delimiter
                    final_page_content = '---PAGE BREAK---'.join(page_contents)
                    final_image_urls = '---PAGE BREAK---'.join(image_urls) if image_urls else None

                    # Save images
                    if image_urls:
                        save_images(image_urls, "image_directory", image_index)
                        image_index += len(image_urls)

                    # Update the row in the database
                    cursor.execute('''
                        UPDATE people2
                        SET othersummary = %s, otherurl = %s, imageurls = %s
                        WHERE name = %s;
                    ''', (final_page_content, urls, final_image_urls, name))
                    # Commit the changes after each update
                    conn.commit()
                    print(f"Updated {name}")

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# def face_rec():
#     for image in os.listdir("/Users/arwaelaradi/Documents/GitHub/QCRI-team/image_directory"):
#         img = cv2.imread(image)
if __name__ == "__main__":
    main()

