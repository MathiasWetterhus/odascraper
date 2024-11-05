from bs4 import BeautifulSoup
import requests
import re

url = "https://oda.com"

response = requests.get(url+"/no/products/")
pattern = r"(\/no\/categories\/[^\/]+\/)"

allProducts = BeautifulSoup(response.text, "html.parser")

topcategories = []

for category in allProducts.find_all("a", href=True):
	if re.search(pattern, category["href"]):
		topcategories.append(category["href"])


extracted_categories = {re.search(pattern, category).group(1) for category in topcategories if re.search(pattern, category)} #Set comprehension for å ekstrahere kategorien fra URL, lagres i et set

extracted_categories = list(extracted_categories) #Konverterer det ekstraherte kategorisettet til en liste igjen

allcategories = []

for category in extracted_categories:
	response = requests.get(url + category)
	specificCategory = BeautifulSoup(response.text, "html.parser")
	for subCat in specificCategory.find_all("a", href=True):
		if re.search(pattern, subCat["href"]):
			allcategories.append(subCat["href"])

allcategories = set(allcategories)

allcategories = list(allcategories)

print(allcategories)