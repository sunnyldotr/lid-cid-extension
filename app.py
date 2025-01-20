from flask import Flask, request, render_template, send_file
import csv
import urllib.parse as urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

def scrape_flipkart(search_term):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    search = search_term.replace(" ", "+")
    urls = [f"https://www.flipkart.com/search?q={search}&sort=recency_desc&page={i}" for i in range(1, 30)]
    raw_data = []

    try:
        for page_number, url in enumerate(urls, start=1):
            driver.get(url)
            wait = WebDriverWait(driver, 30)
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

        unique_data = {d["link"]: d for d in raw_data if d["pid"]}.values()
        csv_filename = f"flipkart_product_links_{search_term}.csv"
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["search_term", "page_number", "link", "pid", "lid"])
            writer.writeheader()
            writer.writerows(unique_data)

        return csv_filename
    finally:
        driver.quit()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        search_term = request.form.get("search_term")
        csv_file = scrape_flipkart(search_term)
        return send_file(csv_file, as_attachment=True)
    return '''
        <form method="POST">
            <label for="search_term">Enter Search Term:</label>
            <input name="search_term" id="search_term">
            <button type="submit">Submit</button>
        </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
