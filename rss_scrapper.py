import requests
from bs4 import BeautifulSoup
from email.utils import format_datetime
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

URL = "https://idrw.org"

# Scraping
html = requests.get(URL, timeout=10).text
soup = BeautifulSoup(html, "lxml")

print("Fetched length:", len(html))

items = []

articles = soup.select("article.art-post.art-article.post.type-post.status-publish.format-standard")
print("Articles found:", len(articles))

for article in articles:
    link_element = article.select_one("h2.art-postheader.entry-title > a")
    link = link_element.get("href")
    
    title = link_element.get_text(strip=True)
    
    desc_element = article.select_one("div.art-postcontent > p:nth-child(3)")
    desc = desc_element.get_text(strip=True)
    
    img_element = article.select_one("img")
    img = img_element.get("data-src")
    
    date_element = article.select_one("span.entry-date.updated")
    date = format_datetime(
                datetime.strptime(date_element.get_text(strip=True), "%B %d, %Y").replace(hour=12)
            )
    
    items.append({
        "title": title,
        "link": link,
        "image": img,
        "description": desc,
        "pubDate": date
    })

# Generating RSS
rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Indian Defence Research Wing"
SubElement(channel, "link").text = URL
SubElement(channel, "description").text = "INDIAN DEFENCE NEWS, LATEST DEFENCE NEWS, INDIAN ARMY, INDIAN AIR FORCE, INDIAN NAVY, DEFENSE NEWS"

for item in items:
    entry = SubElement(channel, "item")

    SubElement(entry, "title").text = item["title"]
    SubElement(entry, "link").text = item["link"]
    SubElement(entry, "description").text = item["description"]
    SubElement(entry, "pubDate").text = item["pubDate"]
    SubElement(entry, "guid").text = item["link"]

ElementTree(rss).write("idrw.xml", encoding="utf-8", xml_declaration=True)