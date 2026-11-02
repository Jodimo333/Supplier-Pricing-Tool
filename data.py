import pandas as pd
import numpy as np
import random

np.random.seed(10)
random.seed(10)

# internal database (10000 SKUs)

base_skus = [f"PRD-{str(i).zfill(3)}" for i in range(1, 10001)]
categories = np.random.choice(["Values", "Pumps", "Sensors", "Filters", "Gaskets"], 10000)
internal_costs = np.random.uniform(20.0, 300.0, 10000).round(2)
target_margins = np.random.choice([0.20, 0.25, 0.30, 0.35], 10000)

retail_prices = (internal_costs / (1 - target_margins)).round(2)

inventory_df = pd.DataFrame({
    "Internal_SKU": base_skus,
    "Category": categories,
    "Current_Cost": internal_costs,
    "Current_Retail_Price": retail_prices,
    "Margin_Target": target_margins
})

inventory_df.to_csv("inventory.csv", index=False)

# supplier

supplier_skus = []
supplier_prices = []
supplier_notes = []

# get the price for 9500 out of 10000 items (let's say 500 are missing)
for sku in base_skus[:9500]:
    # randomly mess up the SKU format (lowercase, add trailing spaces, etc)
    if random.random() > 0.8:
        dirty_sku = sku.lower() + " "
    else:
        dirty_sku = sku

    # simulation of a price increase between 2% and 18%
    original_cost = inventory_df.loc[inventory_df["Internal_SKU"] == sku, "Current_Cost"].values[0]
    new_price_value = round(original_cost * random.uniform(1.02, 1.18), 2)

    # randomly corrupt the price format (string + symbols)
    rand_choice = random.random()
    if rand_choice < 0.05:
        dirty_price = f"${new_price_value}" # dollar sign
    elif rand_choice < 0.10:
        dirty_price = str(new_price_value).replace('.', ',') 
    elif rand_choice < 0.12:
        dirty_price < "TBA" # text instead of number
    elif rand_choice < 0.15:
        dirty_price = " " # empty
    else:
        dirty_price = str(new_price_value)

    supplier_skus.append(dirty_sku)
    supplier_prices.append(dirty_price)
    supplier_notes.append("In stock")

# asymmetry: added 200 completely new products
for i in range(1, 201):
    supplier_skus.append(f"NEW-XYZ-{i}")
    supplier_prices.append(str(round(random.uniform(50, 150), 2)))
    supplier_notes.append("New release")

# duplicate rows for existing products with weird prices
duplicate_skus = random.choices(base_skus[:1000], k=50)
for dup in duplicate_skus:
    supplier_skus.append(dup.lower() + " ")
    supplier_prices.append(random.choice(["1000", "$999", "TBA"]))
    supplier_notes.append("Duplicate row error")

# messy dataframe
supplier_df = pd.DataFrame({
    "ItemCode": supplier_skus,
    "New_Wholesale_Price": supplier_prices,
    "Stock_Notes": supplier_notes
})

# shuffle
supplier_df = supplier_df.sample(frac=1).reset_index(drop=True)
# export
supplier_df.to_csv("supplier_prices.csv", index=False)
print("done")
