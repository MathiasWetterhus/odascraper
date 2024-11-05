from bs4 import BeautifulSoup
import requests

products = requests.get("https://oda.com/no/products/")

print(products.response)

#soup = BeautifulSoup(html, "html.parser")