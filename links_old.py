import csv
import urllib.parse as urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure Selenium to use headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Initialize the WebDriver
driver = webdriver.Chrome(options=options)

# Search term to be passed as a parameter
# search_term = "shoes for men"
search_term = "lakme"
search = search_term.replace(" ", "+")

# List of URLs to scrape
urls = [
    f"https://www.flipkart.com/search?q={search}&sort=recency_desc&page={i}" for i in range(1, 16)
]

# Initialize an empty list to store the data
data = []

try:
    for page_number, url in enumerate(urls, start=1):
        print(f"Processing URL: {url} (Page {page_number})")
        # Open each URL
        driver.get(url)

        # Wait for the main container that holds the product links
        wait = WebDriverWait(driver, 30)  # 30 seconds timeout
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cPHDOP")))

        # Extract product links
        product_containers = driver.find_elements(By.XPATH, "//div[contains(@class, '_75nlfW')]//a[@class='rPDeLR']")
        print(f"Number of products found on this page: {len(product_containers)}")

        for container in product_containers:
            link = container.get_attribute("href")
            parsed_url = urlparse.urlparse(link)
            query_params = urlparse.parse_qs(parsed_url.query)
            pid = query_params.get('pid', [''])[0]
            lid = query_params.get('lid', [''])[0]

            # Extract the title
            try:
                title_element = container.find_element(By.XPATH, "../..//a[@class='WKTcLC BwBZTg']")
                title = title_element.get_attribute("title")
            except Exception:
                title = "N/A"

            # Append all data
            data.append({
                "search_term": search_term,
                "page_number": page_number,
                "title": title,
                "link": link,
                "pid": pid,
                "lid": lid
            })

    # Save all data to a CSV file
    # csv_filename = "flipkart_product_links_with_search_and_page.csv"
    csv_filename = "flipkart_product_links "+search_term+".csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["search_term", "page_number", "title", "link", "pid", "lid"])
        writer.writeheader()
        writer.writerows(data)

    print(f"Data saved to {csv_filename}")

finally:
    # Close the browser
    driver.quit()
