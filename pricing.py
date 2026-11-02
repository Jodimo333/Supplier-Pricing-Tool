import pandas as pd
import numpy as np

# loading inventory + supplier price list
inventory_df = pd.read_csv("inventory.csv")
supplier_df = pd.read_csv("supplier_prices.csv")
print(f"Loaded {len(inventory_df)} internal products and {len(supplier_df)} supplier rows.")

# cleaning 
# remove accidental spaces and convert to uppercase for exact matching
def clean_sku(sku):
    return str(sku).strip().upper()

# remove currency symbols and decimal commas
def clean_price(price):
    price = str(price)
    price = price.replace('$', '')
    price = price.replace(',', '.')
    return price

# cleaning functions
supplier_df['Internal_SKU'] = supplier_df['ItemCode'].apply(clean_sku)
supplier_df = supplier_df.drop(columns=['ItemCode'])
supplier_df['New_Wholesale_Price'] = supplier_df['New_Wholesale_Price'].apply(clean_price)

# convert prices to numeric values (coerce to turn text into NaN)
supplier_df['Clean_New_Cost'] = pd.to_numeric(supplier_df['New_Wholesale_Price'], errors='coerce')

# remove rows with invalid prices and keep only the first instance of duplicated SKUs
supplier_df = supplier_df.dropna(subset=['Clean_New_Cost'])
supplier_df = supplier_df.drop_duplicates(subset=['Internal_SKU'], keep='first')

# merge & business
# join clean supplier prices with internal inventory based on the SKU
merged_df = pd.merge(inventory_df, supplier_df[['Internal_SKU', 'Clean_New_Cost']], on='Internal_SKU', how='inner')
merged_df['Cost_Differences'] = merged_df['Clean_New_Cost'] - merged_df['Current_Cost'] # how much the supplier cost has changed

changed_prices_df = merged_df[merged_df['Cost_Differences']!=0].copy() #only the products where the supplier actually changed the price

# recalculate to maintain target profit margin
changed_prices_df['New_Retail_Price'] = (changed_prices_df['Clean_New_Cost'] / (1 - changed_prices_df['Margin_Target'])).round(2)
changed_prices_df['Old_Profit_Margin'] = (changed_prices_df['Current_Retail_Price'] - changed_prices_df['Clean_New_Cost']).round(2) # financial impact (how much profit we make with old vs new prices)
changed_prices_df['New_Profit_Margin'] = (changed_prices_df['New_Retail_Price'] - changed_prices_df['Clean_New_Cost']).round(2)

changed_prices_df['Profit_Saved_Per_Unit'] = (changed_prices_df['New_Profit_Margin'] - changed_prices_df['Old_Profit_Margin']).round(2)

print(f"Found {len(changed_prices_df)} products that require retail price updates.")
changed_prices_df.to_csv("price_updates.csv", index=False)
