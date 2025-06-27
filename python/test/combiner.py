import pandas as pd
import glob

path = "d:/recipe_scrape/python/test/"  
all_files = glob.glob(path + "recipes_part_*.csv")

df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)
df.to_csv(path + "recipes_combined.csv", index=False, encoding="utf-8")
