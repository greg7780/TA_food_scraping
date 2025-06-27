import pandas as pd

df = pd.read_csv("recipes.csv")

# List of drink-related keywords (expandable)
drink_keywords = [
    "mojito", "juice", "tea", "coffee", "smoothie", "milkshake",
    "cocktail", "soda", "latte", "lemonade", "shake", "drink", "chai", "punch", "float", "brew"
]

def is_drink(title):
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in drink_keywords)

# Filter out rows where RecipeName contains drink keywords
df_cleaned = df[~df["RecipeName"].apply(is_drink)]

df_cleaned.to_csv("recipes_filtered.csv", index=False, encoding="utf-8")