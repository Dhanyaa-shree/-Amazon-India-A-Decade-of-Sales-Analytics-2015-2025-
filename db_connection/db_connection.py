import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import os
from tqdm import tqdm

# =========================
# STEP 1: Load .env file
# =========================
load_dotenv()

host = os.getenv('HOST')
user = os.getenv('USER')
password = os.getenv('PASS')
database = os.getenv('DATABASE')
port = os.getenv('PORT')

# =========================
# STEP 2: MySQL Connection
# =========================
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    port=int(port),
    autocommit=False
)

cursor = conn.cursor()
print("✅ MySQL Connected Successfully")

# =========================
# STEP 3: Create Table
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS amazon_sales_cleaned (
    transaction_id VARCHAR(50),
    order_date DATE,
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    product_name TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    original_price_inr FLOAT,
    discount_percent FLOAT,
    final_amount_inr FLOAT,
    customer_rating FLOAT,
    return_status VARCHAR(20),
    order_month INT,
    order_year INT,
    order_quarter INT,
    product_weight_kg FLOAT,
    is_prime_eligible BOOLEAN,
    product_rating FLOAT,
    price_outlier_IQR BOOLEAN,
    price_outlier_3sigma BOOLEAN
)
""")

conn.commit()
print("✅ Table created successfully")

# =========================
# STEP 4: Load Cleaned Dataset (FIXED PATH)
# =========================
file_path = r"D:\Amazon_EDA_Project\D__Amazon_EDA_Project_amazon_india_cleaned_data.csv"

# Safety check (IMPORTANT)
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

df = pd.read_csv(file_path)

print("📊 Dataset Loaded:", df.shape)

# =========================
# STEP 5: Select Required Columns
# =========================
cols = [
    'transaction_id', 'order_date', 'customer_id', 'product_id', 'product_name',
    'category', 'subcategory', 'brand',
    'original_price_inr', 'discount_percent', 'final_amount_inr',
    'customer_rating', 'return_status',
    'order_month', 'order_year', 'order_quarter',
    'product_weight_kg', 'is_prime_eligible', 'product_rating',
    'price_outlier_IQR', 'price_outlier_3sigma'
]

df = df[cols].copy()

# =========================
# STEP 6: Handle Missing Values
# =========================
df = df.where(pd.notnull(df), None)

# =========================
# STEP 7: Insert Query
# =========================
insert_query = """
INSERT INTO amazon_sales_cleaned (
transaction_id, order_date, customer_id, product_id, product_name,
category, subcategory, brand,
original_price_inr, discount_percent, final_amount_inr,
customer_rating, return_status,
order_month, order_year, order_quarter,
product_weight_kg, is_prime_eligible, product_rating,
price_outlier_IQR, price_outlier_3sigma
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# =========================
# STEP 8: Batch Insert (FAST)
# =========================
batch_size = 5000

for i in tqdm(range(0, len(df), batch_size), desc="Uploading to MySQL"):
    batch = df.iloc[i:i+batch_size].values.tolist()
    cursor.executemany(insert_query, batch)
    conn.commit()

print("🚀 Data successfully inserted into MySQL")

# =========================
# STEP 9: Close Connection
# =========================
cursor.close()
conn.close()

print("🔌 MySQL connection closed")