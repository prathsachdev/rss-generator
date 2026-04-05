from bs4 import BeautifulSoup
from email.utils import format_datetime
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, ElementTree, register_namespace
import cloudscraper
from urllib.parse import urljoin

try:
    URL = "https://idrw.org"

    # Scraping
    scraper = cloudscraper.create_scraper(
        browser = {
            "browser": "chrome", 
            "platform": "windows"
        }
    )

    html = scraper.get(URL, timeout=10).text
    soup = BeautifulSoup(html, "lxml")

    print("Fetched length:", len(html))

    items = []

    articles = soup.select("article.art-post.art-article.post.type-post.status-publish.format-standard")
    print("Articles found:", len(articles))

    for article in articles:
        link_element = article.select_one("h2.art-postheader.entry-title > a")
        link = urljoin(URL, link_element.get("href"))
        
        title = link_element.get_text(strip=True)
        
        desc_element = article.select_one("div.art-postcontent > p:nth-child(3)")
        desc = desc_element.get_text(strip=True)
        
        date_element = article.select_one("span.entry-date.updated")
        date = format_datetime(
                    datetime.strptime(date_element.get_text(strip=True), "%B %d, %Y").replace(hour=0, minute=0, second=0, tzinfo=timezone.utc)
                )
        
        author_element = article.select_one("span.author.vcard > a")
        author = author_element.get_text()
        
        img_element = article.select_one("img")
        img = img_element.get("data-src")
        
        items.append({
            "title": title,
            "link": link,
            "description": desc,
            "pubDate": date,
            "author": author,
            "image": img,
        })

    # Generating RSS
    rss = Element("rss", {
        "version": "2.0"
        # "xmlns:media": "http://search.yahoo.com/mrss/",
        # "xmlns:atom": "http://www.w3.org/2005/Atom",
        # "xmlns:dc": "http://purl.org/dc/elements/1.1/"
    })

    register_namespace("media", "http://search.yahoo.com/mrss/")
    register_namespace("atom", "http://www.w3.org/2005/Atom")
    register_namespace("dc", "http://purl.org/dc/elements/1.1/")

    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "Indian Defence Research Wing"
    SubElement(channel, "description").text = "INDIAN DEFENCE NEWS, LATEST DEFENCE NEWS, INDIAN ARMY, INDIAN AIR FORCE, INDIAN NAVY, DEFENSE NEWS"
    SubElement(channel, "link").text = URL
    SubElement(channel, "{http://www.w3.org/2005/Atom}link", {
        "href": URL,
        "rel": "self",
        "type": "application/rss+xml"
    })

    SubElement(channel, "generator").text = "GitHub Actions"

    image = SubElement(channel, "image")

    SubElement(image, "link").text = URL
    SubElement(image, "url").text = "https://www.google.com/s2/favicons?domain=https://idrw.org"
    SubElement(image, "title").text = "Indian Defence Research Wing"

    for item in items:
        entry = SubElement(channel, "item")
        
        if item.get("title"):
            title = SubElement(entry, "title")
            title.text = item["title"]
        
        if item.get("link"):
            link = SubElement(entry, "link")
            link.text = item["link"]
        
        if item.get("description"):
            description = SubElement(entry, "description")
            description.text = item["description"]
        
        if item.get("pubDate"):
            pubDate = SubElement(entry, "pubDate")
            pubDate.text = item["pubDate"]
        
        if item.get("author"):
            author = SubElement(entry, "{http://purl.org/dc/elements/1.1/}creator")
            author.text = item["author"]
        
        if item.get("image"):
            image = SubElement(entry, "{http://search.yahoo.com/mrss/}content")
            image.set("url", item["image"])
            image.set("medium", "image")
        
        if item.get("link"):
            guid = SubElement(entry, "guid")
            guid.set("isPermalink", "true")
            guid.text = item["link"]

    ElementTree(rss).write("feed/idrw.xml", encoding="utf-8", xml_declaration=True)
except Exception as e:
    print("Exception in idrw_scraper")
    print(e)