import csv
import urllib.parse as urlparse
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    search_term = data.get('search_term', '').replace(' ', '+')

    if not search_term:
        return jsonify({"error": "No search term provided"}), 400

    # Configure Selenium to use headless Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)

    # Generate Flipkart URLs to scrape
    urls = [
        f"https://www.flipkart.com/search?q={search_term}&sort=recency_desc&page={i}" for i in range(1, 30)
    ]

    # Initialize an empty list to store unique data
    raw_data = []

    try:
        for page_number, url in enumerate(urls, start=1):
            print(f"Processing URL: {url} (Page {page_number})")
            # Open each URL
            driver.get(url)

            # Wait for the main container that holds the links
            wait = WebDriverWait(driver, 30)  # 30 seconds timeout
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cPHDOP")))

            # Extract all links within the cPHDOP class
            link_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'cPHDOP')]//a")
            print(f"Number of links found on this page: {len(link_elements)}")

            for element in link_elements:
                link = element.get_attribute("href")
                if link and not link.endswith("&marketplace=FLIPKART"):  # Exclude links ending with &marketplace=FLIPKART
                    parsed_url = urlparse.urlparse(link)
                    query_params = urlparse.parse_qs(parsed_url.query)
                    pid = query_params.get('pid', [''])[0]
                    lid = query_params.get('lid', [''])[0]

                    raw_data.append({
                        "search_term": search_term,
                        "page_number": page_number,
                        "link": link,
                        "pid": pid,
                        "lid": lid
                    })

        # Filter data to remove duplicates and pick only records where pid is present
        unique_data = {d["link"]: d for d in raw_data if d["pid"]}.values()

        # Save unique data to a CSV file
        csv_filename = f"flipkart_product_links_{search_term}.csv"
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["search_term", "page_number", "link", "pid", "lid"])
            writer.writeheader()
            writer.writerows(unique_data)

        print(f"Filtered unique data saved to {csv_filename}")

        # Convert unique data to CSV string for API response
        csv_output = "search_term,page_number,link,pid,lid\n"
        for row in unique_data:
            csv_output += f"{row['search_term']},{row['page_number']},{row['link']},{row['pid']},{row['lid']}\n"

        return jsonify({"csv": csv_output, "file_saved_as": csv_filename})

    finally:
        # Close the browser
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
