import csv
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

# Input and output file paths
# input_csv = "flipkart_product_links.csv"
input_csv = "flipkart_product_links_shoes for men.csv"
# output_csv = "flipkart_product_links_with_details.csv"
output_csv = f"{input_csv}_details.csv"

# Function to extract the title, price, color_type, and size_type
def get_product_details(url):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 30)  # 30 seconds timeout

        # Extract the title
        title_element = wait.until(EC.presence_of_element_located((By.XPATH, "//h1[@class='_6EBuvT']")))
        title_part1 = title_element.find_element(By.CLASS_NAME, "mEh187").text  # First part of the title
        title_part2 = title_element.find_element(By.CLASS_NAME, "VU-ZEz").text  # Second part of the title
        title = f"{title_part1} {title_part2}"

        # Extract the price
        price_element = driver.find_element(By.CLASS_NAME, "Nx9bqj")
        price = price_element.text

        # Extract color_type links using class "GK7Ljp"
        color_elements = driver.find_elements(By.CLASS_NAME, "GK7Ljp")
        color_types = [element.get_attribute("href") for element in color_elements]

        # Extract size_type links using class "CDDksN"
        size_elements = driver.find_elements(By.CLASS_NAME, "CDDksN")
        size_types = [element.get_attribute("href") for element in size_elements]

        return title, price, color_types, size_types
    except Exception as e:
        print(f"Error extracting data from {url}: {e}")
        return "N/A", "N/A", [], []

try:
    # Read the input CSV and process each row
    with open(input_csv, mode='r', encoding='utf-8') as infile, open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["title", "price", "color_type", "size_type"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            print(f"Processing URL: {row['link']}")
            title, price, color_types, size_types = get_product_details(row["link"])

            # Determine the maximum number of rows for this link
            max_rows = max(len(color_types), len(size_types))

            # Pad the shorter list with "N/A" to match the length of the longer list
            color_types += ["N/A"] * (max_rows - len(color_types))
            size_types += ["N/A"] * (max_rows - len(size_types))

            # Create rows for each combination of color_type and size_type
            for i in range(max_rows):
                new_row = row.copy()
                new_row["title"] = title
                new_row["price"] = price
                new_row["color_type"] = color_types[i]
                new_row["size_type"] = size_types[i]
                writer.writerow(new_row)

    print(f"Product details extracted and saved to {output_csv}")

finally:
    # Close the browser
    driver.quit()
