import pandas as pd
from bs4 import BeautifulSoup
import requests

headers_std = {
    'User-Agent':'Mozilla/5.0',
    'Content-Type':'text/html',
}

count = 1
dic = {
    "product_title": [],
    "product_category": [],
    "product_description": [],
    "product_rating": [],
    "product_price": [],
    "product_reviews": []
}

for url in fitness_urls:
    print(count)
    try:
        html = requests.get(url, headers=headers_std).text
        soup = BeautifulSoup(html, 'lxml')
        product_title_class = "a-size-large product-title-word-break"
        product_category_class = "nav-a-content"
        product_description_class = "a-unordered-list a-vertical a-spacing-mini"
        product_rating_class = "a-icon-alt"
        product_price_class = "a-price-whole"

        product_title = soup.find("span", {"class": product_title_class})
        product_category = soup.find("span", {"class": product_category_class})
        product_description = soup.find("ul", {"class": product_description_class})
        product_rating = soup.find("span", {'class': product_rating_class})
        product_price = soup.find("span", {"class": product_price_class})
        # Find the review container element
        review_container = soup.find('div', {'data-hook': 'top-customer-reviews-widget'})

        # Find all individual reviews within the container
        reviews = review_container.find_all('div', {'data-hook': 'review'})
    
        # Check if any required element is None, and skip the URL if so
        if any(elem is None for elem in [product_title, product_category, product_description, product_rating, product_price,review_container]):
            print(f"Skipping URL {url} due to missing elements")
            continue

        dic["product_title"].append(product_title.text.strip())
        dic["product_category"].append(product_category.img.get("alt") if product_category.img else product_category.text.strip())
        
        description_paragraph = '\n'.join([li.get_text(strip=True) for li in product_description.find_all('li')])
        dic["product_description"].append(description_paragraph)
        
        dic["product_rating"].append(product_rating.text.split(" ")[0])
        dic["product_price"].append(product_price.text.strip())

        # Iterate over each review and extract information
        review_list = []
        for review in reviews:
            review_dict = {
                "reviewer_name": "",
                "rating": "",
                "review_heading": "",
                "review_text": "",
                "review_date": "",
                "verified_purchase": ""
            }
            
            # Extract reviewer name
            reviewer_name = review.find('span', {'class': 'a-profile-name'}).get_text(strip=True)
            review_dict["reviewer_name"] = reviewer_name
            
            # Extract rating
            rating = review.find('span', {'class': 'a-icon-alt'}).get_text(strip=True).split(" ")[0]
            review_dict["rating"] = rating
            
            # Extract review heading
            review_heading = review.find('a', {'data-hook': 'review-title'}).get_text(strip=True)
            review_dict["review_heading"] = review_heading
            
            # Extract entire review text, including content behind "Read more"
            review_text_element = review.find('span', {'data-hook': 'review-body'})
            review_text = review_text_element.get_text(separator='\n', strip=True).strip("\nRead more")
            review_dict["review_text"] = review_text
            
            # Extract review date
            review_date = review.find('span', {'data-hook': 'review-date'}).get_text(strip=True)
            review_dict["review_date"] = review_date
            
            # Extract whether it's a verified purchase
            verified_purchase = review.find('span', {'data-hook': 'avp-badge-linkless'}).get_text(strip=True)
            review_dict["verified_purchase"] = verified_purchase
            
            # Append the review dictionary to the list
            review_list.append(review_dict)
        
        dic["product_reviews"].append(review_list)
        count += 1
    
    except Exception as e:
        print(f"Error scraping URL {url}: {str(e)}")

# Create a DataFrame from the extracted data
df = pd.DataFrame(dic)

# Save the DataFrame to a CSV file
df.to_csv("amazon_product_data.csv", index=False)
print("Data saved to amazon_product_data.csv")
