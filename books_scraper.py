import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# User filters
min_price = float(input("Enter minimum price to filter (e.g., 30): "))
category_filter = input("Enter category to filter (leave blank for all): ").strip().lower()

books_data = []

# Convert star-rating text to number
def get_rating_number(rating_text):
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return rating_map.get(rating_text, 0)

# Safe request with retry logic
def safe_get(session, url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"[Retry {attempt+1}] Failed to fetch {url} due to: {e}")
            time.sleep(delay)
    return None

# Reuse session for efficiency
session = requests.Session()

# Scrape all 50 pages
for page_num in range(1, 51):
    page_url = f'https://books.toscrape.com/catalogue/page-{page_num}.html'
    page_response = safe_get(session, page_url)
    if page_response is None:
        print(f"Skipping page {page_num} due to repeated errors.")
        continue

    soup = BeautifulSoup(page_response.content, 'html.parser')
    books = soup.find_all('h3')

    for book in books:
        relative_url = book.find('a')['href']
        full_url = requests.compat.urljoin(page_url, relative_url)

        book_response = safe_get(session, full_url)
        if book_response is None:
            print(f"Skipping book at {relative_url} due to repeated errors.")
            continue

        book_soup = BeautifulSoup(book_response.content, "html.parser")

        title = book_soup.find('h1').text.strip()

        # Get category
        breadcrumb = book_soup.find('ul', class_="breadcrumb")
        category = (
            breadcrumb.find_all('a')[2].text.strip()
            if breadcrumb and len(breadcrumb.find_all('a')) >= 3
            else "Unknown"
        )

        # Get rating
        rating_tag = book_soup.find('p', class_='star-rating')
        rating = get_rating_number(rating_tag['class'][1]) if rating_tag else 0

        # Get price
        price_text = book_soup.find('p', class_='price_color').text.strip()
        price = float(price_text[1:]) if price_text.startswith('£') else 0.0

        availability = book_soup.find('p', class_='availability').text.strip()

        # Apply filters
        if price >= min_price and (category_filter == "" or category.lower() == category_filter):
            books_data.append([title, category, rating, price, availability])

        print(f"✅ {len(books_data)} books collected so far...")
        time.sleep(random.uniform(0.8, 1.5))  # polite random delay

# Save to CSV, Excel, JSON
df = pd.DataFrame(books_data, columns=["Title", "Category", "Rating (1-5)", "Price (£)", "Availability"])
df.to_csv("books_scraped.csv", index=False)
df.to_excel("books_scraped.xlsx", index=False)
df.to_json("books_scraped.json", orient="records", indent=2)

print("\n🎉 Scraping complete!")
print(f"📚 Total books matching filters: {len(books_data)}")
print("📂 Data saved to CSV, Excel, and JSON.")
