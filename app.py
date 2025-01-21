from flask import Flask, request, send_file
import csv
import urllib.parse as urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller  # Automatically installs the correct ChromeDriver version
import os  # Added for environment variable handling

app = Flask(__name__)

def scrape_flipkart(search_term):
    # Set up Chrome options for headless mode and resource optimization
    options = Options()
    options.add_argument("--headless=new")  # Use the new headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Automatically install the correct ChromeDriver version
    chromedriver_autoinstaller.install()

    # Initialize the Chrome driver
    driver = webdriver.Chrome(options=options)

    # Prepare the search URLs
    search = search_term.replace(" ", "+")
    urls = [f"https://www.flipkart.com/search?q={search}&sort=recency_desc&page={i}" for i in range(1, 6)]  # Limit pages to 5
    raw_data = []

    try:
        for page_number, url in enumerate(urls, start=1):
            driver.get(url)
            wait = WebDriverWait(driver, 60)  # Increase timeout to 60 seconds
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cPHDOP")))

            link_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'cPHDOP')]//a")

            for element in link_elements:
                link = element.get_attribute("href")
                if link and not link.endswith("&marketplace=FLIPKART"):
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

        # Filter out duplicate links
        unique_data = {d["link"]: d for d in raw_data if d["pid"]}.values()
        
        # Save data to a CSV file
        csv_filename = f"flipkart_product_links_{search_term}.csv"
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["search_term", "page_number", "link", "pid", "lid"])
            writer.writeheader()
            writer.writerows(unique_data)

        return csv_filename
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        driver.quit()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        search_term = request.form.get("search_term")
        csv_file = scrape_flipkart(search_term)
        if csv_file:
            return send_file(csv_file, as_attachment=True)
        else:
            return "An error occurred during scraping. Please try again.", 500
    return '''
        <form method="POST">
            <label for="search_term">Enter Search Term:</label>
            <input name="search_term" id="search_term">
            <button type="submit">Submit</button>
        </form>
    '''

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))  # Use the PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
