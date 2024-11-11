import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import NewsURLLoader
from config import HEADER

DOMAIN = "https://thenextweb.com"
def get_category_link():
    res_index = requests.get(
    DOMAIN,
    headers=HEADER)
    print(res_index)
    soup = BeautifulSoup(res_index.text, "lxml")
    categories = soup.find(class_="c-nav__level2").find_all(class_="c-nav__menuItem")
    category_links = {}
    for i in range(len(categories)):
        link = categories[i].find("a")["href"]
        if link.startswith("/"):
            category_links[categories[i].text.strip()] = f"{DOMAIN}{link}"
    return category_links


def get_news_links(url, pages=1):
    links = []
    for i in range(1, pages + 1):
        res = requests.get(f"{url}/page/{i}", headers=HEADER)
        print(res)
        soup = BeautifulSoup(res.text, "lxml")
        news = soup.find_all("article")
        for i in range(len(news)):
            link = f"{DOMAIN}/{news[i].find('a')['href']}"
            links.append(link)
    return links


def load_doc(news_links, category):
    loader = NewsURLLoader(urls=news_links, nlp=True, show_progress_bar=True)
    data = loader.load()
    for i in range(len(data)):
    # print(data[i].metadata["title"])
        data[i].metadata["keywords"] = ' '.join(data[i].metadata["keywords"])
        data[i].metadata["category"] = category
        data[i].page_content = data[i].metadata["summary"]
        del data[i].metadata["summary"]
    return data
