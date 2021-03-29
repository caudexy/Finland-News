import os
import re
from re import search
import time
import json

import feedparser
import telegram
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

CHANNEL_ID = "@Finland_News_Feed"
CHANNEL_ID = "@yle_news_live"
NEWSFEED = "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_NEWS"
GOOD_NEW_FEED = "https://www.goodnewsfinland.com/"

INTERVAL = 30

def titleEditor(title):
    """
    This function edits the article title.
    - Escapes possible special charecters with Regular Expressions
    """
    escaped_title = re.escape(title)
    return str(escaped_title)

def linkEditor(link):
    """
    This function edits the link for instant view.
    """

    # link start and rhash by telegram
    instant_view_start = "https://t.me/iv?url=https%3A%2F%2F"

    if search("yle.fi", link):
        instant_view_rhash = "&rhash=04f872b445da2a" # Yle instant view

    elif search("goodnewsfinland.com", link):
        instant_view_rhash = "&rhash=28aaa3b7244f2a" # Good News finland instant view

    else:
        instant_view_rhash = "&rhash=04f872b445da2a" # if not found use YLE instant view

    # splitting the link
    link = link.split("//",1)
    link = link[1]
    # replacing "/"" with "%2F"
    link = link.replace("/", "%2F")

    # Adding link start and rhash by telegram
    link = instant_view_start + link + instant_view_rhash

    return link

def sender(title,link):
    """
    This function sends the message(as a link) to the Telegram Channel.
    """
    try:   
        bot = telegram.Bot(token=TOKEN)

        edited_link = linkEditor(link)

        bot.send_message(
                    chat_id=CHANNEL_ID, 
                    text=f"{title}[\.]({edited_link})\n[Link to the Article]({link})",
                    parse_mode=telegram.ParseMode.MARKDOWN_V2
                )
    except:
        print("Experienced a problem when sending the article")

def openMemory():
    """
    This function reads the name of last article from memory.
    """
    try:
        with open("memory.json", "r") as read_file:
            memory = json.load(read_file)
        return memory
    except:
        print("Experienced a problem when reading from memory")

def writeMemory(memory, feed_id):
    """
    This function writes the name of last article to memory.
    """
    try:
        with open("memory.json", "w") as write_file:
            json.dump(memory, write_file)
    except:
        print("Experienced a problem writing to memory.json")
            
def yle_parser():
    """
    """
    # parsing the RSS feed
    NewsFeed = feedparser.parse(NEWSFEED)
    # selecting the last article on the feed
    newest_article = NewsFeed.entries[0]
    # Save the title of last article
    memory = openMemory()
    sent_articles = memory["yle_feed"]

    # checking for new articles
    if newest_article.id not in sent_articles:
        # Parsing the link & the title
        link = newest_article.link
        title = newest_article.title
        
        # formatting the link & the title
        edited_title = titleEditor(title)
        
        # sending the message
        sender(edited_title, link)
        print("New article from YLE sent!!!")

        sent_articles.clear()
        # appending last 5 articles to a list
        for article in NewsFeed.entries[:5]:
            sent_articles.append(article.id)

        memory["yle_feed"] = sent_articles

        # writing to memory
        writeMemory(memory,"yle_feed")
        
    else:
        print("No new articles found in YLE RSS feed.")

def good_fin_parser():
    """
    """
    try:
        page = requests.get(GOOD_NEW_FEED)
        soup = BeautifulSoup(page.content, 'html.parser')

        results = soup.find(id='primary')

        titles = results.find_all('div', class_='yarpp-thumbnail-title')
        articles = results.find_all('a', class_='post-thumbnail-link')

        # Getting the first article form main page
        link = articles[0].get('href')
        title = titles[0].text.strip()

        # If first article is "WEEKEND WRAP" switch to previous article
        if search("WEEKEND WRAP", title):
            link = articles[1].get('href')
            title = titles[1].text.strip()

        memory = openMemory()
        sent_article = memory["good_feed"]

        if title != sent_article:
            edited_title = titleEditor(title)
            sender(edited_title, link)
            print("Good News Finland Article sent")

            memory["good_feed"] = title
            writeMemory(memory,"good_feed")
        else:
            pass

    except:
        print("Experienced a problem when parsing the GOOD NEWS article.")

def main():
    """
    """
    while True:
        
        yle_parser()
        time.sleep(INTERVAL)

        # If its 10:00 run this script
        current_time = time.strftime("%H:%M", time.localtime())
        if (current_time >= "10:00") and (current_time < "10:05"):
            good_fin_parser()
            time.sleep(INTERVAL)


if __name__ == "__main__":
    main() 