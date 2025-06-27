url = "https://www.allrecipes.com/recipes-a-z-6735880"

path_to_file = r"D:\recipe_scrape\python\test\\"

from selenium import webdriver
import pandas as pd
import time
from bs4 import BeautifulSoup
import json
import re

# mode = "scrape" 
# mode = "extract" 
# mode = "extract2" 
mode = "scrape2" 

if(mode == "scrape"):
    driver = webdriver.Chrome()
    driver.maximize_window()

    driver.get(url)

    page_source = driver.page_source

    f = open(path_to_file + "sourceAllRecipe.txt", "w", encoding="utf-8")
    f.write(page_source)
    f.close()

elif(mode == "extract"):
    data = []

    f = open(path_to_file + "sourceAllRecipe.txt", "r", encoding="utf-8")
    page_source = f.read()
    f.close()

    soup = BeautifulSoup(page_source, features="lxml")

    food_links = []
    items = soup.find_all("li", class_="comp mntl-link-list__item")

    for item in items:
        link_tag = item.find("a")
        if link_tag and "href" in link_tag.attrs:
            food_links.append(link_tag["href"])
    
    with open(path_to_file + "linkAllRecipes.txt", "w", encoding="utf-8") as f:
        for link in food_links:
            f.write(link + "\n")

elif(mode == "extract2"):
    data = []

    with open(path_to_file + "linkAllRecipes.txt", "r", encoding="utf-8") as f:
        food_links = [line.strip() for line in f.readlines()]

    driver = webdriver.Chrome()
    driver.maximize_window()

    food_info = []

    for food_link in food_links:
        driver.get(food_link)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "lxml")
        items = soup.select("a.mntl-card-list-items") 

        for item in items:
            if item and "href" in item.attrs:
                href = item["href"]
                if "/recipe/" in href:
                    food_info.append(href)

    with open(path_to_file + "categoryLinks.txt", "w", encoding="utf-8") as f:
        for link in food_info:
            f.write(link + "\n")

elif(mode == "scrape2"):
    protein_keywords = {
        "chicken": "ayam",
        "fish": "ikan",
        "beef": "sapi",
        "egg": "telur",
        "milk": "susu",
        "shrimp": "udang",
        "squid": "cumi",
        "clam": "kerang",
        "cheese": "keju"
    }

    with open(path_to_file + "linkAllRecipeAllSections.txt", "r", encoding="utf-8") as f:
        food_links = [line.strip() for line in f.readlines()]

    start_index = 6500
    food_links = food_links[start_index:]

    driver = webdriver.Chrome()
    driver.maximize_window()

    recipe_data = []

    for idx, food_link in enumerate(food_links, start=start_index + 1):
        try:
            driver.get(food_link)
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, "lxml")

            recipe_tag = soup.find("h1", class_="article-heading text-headline-400")
            title = recipe_tag.text.strip() if recipe_tag else "No title"

            nutrition_data = {}
            nutrition_table = soup.find("table", class_="mm-recipes-nutrition-facts-label__table")

            if nutrition_table:
                tbody = nutrition_table.find("tbody")
                rows = tbody.find_all("tr")

                for row in rows:
                    td = row.find("td")
                    if td:
                        span = td.find("span", class_="mm-recipes-nutrition-facts-label__nutrient-name")
                        if span:
                            name = span.get_text(strip=True)
                            value_text = td.get_text(strip=True).replace(name, "").strip()
                            if name in ["Protein", "Total Carbohydrate", "Total Fat", "Dietary Fiber"]:
                                nutrition_data[name] = re.sub(r"[^\d.]", "", value_text)

            calorie_row = soup.find("tr", class_="mm-recipes-nutrition-facts-label__calories")
            calories = (
                calorie_row.find_all("span")[-1].get_text(strip=True)
                if calorie_row else "N/A"
            )

            servings_row = soup.find("tr", class_="mm-recipes-nutrition-facts-label__servings")
            servings = (
                servings_row.find_all("span")[-1].get_text(strip=True)
                if servings_row else "N/A"
            )

            try:
                servings = float(servings)
            except ValueError:
                servings = 1.0 

            def divide_by_servings(value):
                try:
                    return round(float(value) / servings, 2)
                except:
                    return value

            nutrition_keys = {
                "Calories": divide_by_servings(calories),
                "Protein": divide_by_servings(nutrition_data.get("Protein", "N/A")),
                "Total Carbohydrate": divide_by_servings(nutrition_data.get("Total Carbohydrate", "N/A")),
                "Total Fat": divide_by_servings(nutrition_data.get("Total Fat", "N/A")),
                "Dietary Fiber": divide_by_servings(nutrition_data.get("Dietary Fiber", "N/A"))
            }

            protein_found = set()
            ingredients = soup.select("ul.mm-recipes-structured-ingredients__list li")

            for item in ingredients:
                text = item.get_text().lower()
                for en, idn in protein_keywords.items():
                    if re.search(rf"\b{en}\b", text):
                        protein_found.add(idn)

            recipe_data.append({
                "RecipeName": title,
                **nutrition_keys,
                "ProteinName": list(protein_found),
                "url": food_link
            })

            print(f"[{idx}] Scraped: {food_link}")

            if idx % 500 == 0:
                part_num = idx // 500
                df = pd.DataFrame(recipe_data)
                df.to_csv(path_to_file + f"recipes_part_{part_num}.csv", index=False, encoding="utf-8")

                with open(path_to_file + f"recipes_part_{part_num}.json", "w", encoding="utf-8") as f:
                    json.dump(recipe_data, f, indent=4, ensure_ascii=False)

                recipe_data = []

        except Exception as e:
            print(f"[{idx}] Error scraping {food_link}: {e}")

    driver.quit()