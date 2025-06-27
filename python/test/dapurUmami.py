url = "https://www.dapurumami.com/resep?tested=du&sortby=terbaru"

path_to_file = r"D:\recipe_scrape\python\test\\"

from selenium import webdriver
import pandas as pd
import time
from bs4 import BeautifulSoup
import json
import re

# mode = "scrape" 
# mode = "extract" 
mode = "scrape2" 

if(mode == "scrape"):
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)

    last_height = 0
    while True:
        driver.execute_script('window.scrollBy(0, 1000)')
        time.sleep(6)

        new_height = driver.execute_script("return document.body.scrollHeight")
        print(str(new_height) + "-" + str(last_height))

        if(new_height == last_height):
            break
        else:
            last_height = new_height
            
    page_source = driver.page_source
    f = open(path_to_file + "source.txt", "w", encoding="utf-8")
    f.write(page_source)
    f.close()

elif(mode == "extract"):
    data = []

    f = open(path_to_file + "source.txt", "r", encoding="utf-8")
    page_source = f.read()
    f.close()

    soup = BeautifulSoup(page_source, features="lxml")

    food_links = []
    items = soup.find_all("div", class_="wrappedInfo")

    for item in items:
        link_tag = item.find("a", class_="transparent")
        if link_tag and "href" in link_tag.attrs:
            food_links.append(link_tag["href"])
    
    with open(path_to_file + "links.txt", "w", encoding="utf-8") as f:
        for link in food_links:
            f.write(link + "\n")

elif(mode == "scrape2"):
    protein_keywords = [
        "ayam", "ikan", "sapi", "telur", "susu", "udang", "cumi", "kerang", "keju"
    ]

    with open(path_to_file + "links.txt", "r", encoding="utf-8") as f:
        food_links = [line.strip() for line in f.readlines()]

    driver = webdriver.Chrome()
    driver.maximize_window()

    food_data = []

    for food_link in food_links:
        driver.get(food_link)
        time.sleep(2)  

        soup = BeautifulSoup(driver.page_source, "lxml")

        recipe_tag = soup.find("h1", class_="text-center m-0 py-3")  
        title = recipe_tag.text.strip() if recipe_tag else "No title"

        nutrition_data = {}
        nutrition_rows = soup.find_all("div", class_="col pb-2")

        for row in nutrition_rows:
            label = row.find("h5")
            value = row.find("p")  

            if label and value:
                nutrition_data[label.text.strip()] = value.text.strip()

        nutrition_keys = ["Kalori", "Protein", "Karbo", "Lemak", "Serat"]

        nutrition_values = {key: nutrition_data.get(key, "N/A") for key in nutrition_keys}

        # Extract protein sources from ALL ingredients tables
        protein_found = set()
        tables = soup.find_all("table", class_="tableCustomized")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                row_text = row.get_text().lower()
                for keyword in protein_keywords:
                    if re.search(rf"\b{keyword}\b", row_text):
                        protein_found.add(keyword)


        # Append structured data
        food_data.append({
            "RecipeName": title,
            **nutrition_values,
            "ProteinName": list(protein_found),
            "url": food_link
        })

    driver.quit()

    # Save to CSV
    df = pd.DataFrame(food_data)
    df.to_csv(path_to_file + "recipes.csv", index=False, encoding="utf-8")

    # Save to JSON
    with open(path_to_file + "recipes.json", "w", encoding="utf-8") as f:
        json.dump(food_data, f, indent=4, ensure_ascii=False)