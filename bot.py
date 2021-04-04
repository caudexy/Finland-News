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
INTERVAL = 5
TESTING = False

def titleEditor(title):
    """
    This function edits the article title.
    - Escapes possible special charecters with Regular Expressions
    """
    escaped_title = re.escape(title)
    escaped_title = escaped_title.replace("!","\!")
    return str(escaped_title)

def linkEditor(link, newsfeed_link):
    """
    This function edits the link for instant view.
    """

    # link start and rhash by telegram
    instant_view_start = "https://t.me/iv?url=https%3A%2F%2F"

    if search("Ids=YLE_NEWS", newsfeed_link):
        instant_view_rhash = "&rhash=04f872b445da2a" # Yle ENG instant view

    elif search("goodnewsfinland.com", newsfeed_link):
        instant_view_rhash = "&rhash=28aaa3b7244f2a" # Good News finland instant view

    elif search("YLE_UUTISET.rss", newsfeed_link):
        instant_view_rhash = "&rhash=09be4d57db5cf1" # Yle FIN instant view

    elif search("Ids=YLE_NOVOSTI", newsfeed_link):
        instant_view_rhash = "&rhash=04f872b445da2a" # Yle RUS instant view

    elif search("www.iltalehti.fi", newsfeed_link):
        instant_view_rhash = "&rhash=237fbc14463822" # Iltalehti Fin instant view

    else:
        instant_view_rhash = "&rhash=04f872b445da2a" # if not found use YLE ENG instant view

    # splitting the link
    link = link.split("//",1)
    link = link[1]
    # replacing "/"" with "%2F"
    link = link.replace("/", "%2F")

    # Adding link start and rhash by telegram
    link = instant_view_start + link + instant_view_rhash

    return link

def sender(title, link, channel_id, newsfeed_link):
    """
    This function sends the message(as a link) to the Telegram Channel.
    """
    try:   
        bot = telegram.Bot(token=TOKEN)

        edited_link = linkEditor(link, newsfeed_link)

        bot.send_message(
                    chat_id=channel_id, 
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
        with open("memory/memory.json", "r") as read_file:
            memory = json.load(read_file)
        return memory
    except:
        print("Experienced a problem when reading from memory")

def writeMemory(memory, feed_id):
    """
    This function writes the name of last article to memory.
    """
    try:
        with open("memory/memory.json", "w") as write_file:
            json.dump(memory, write_file)
    except:
        print("Experienced a problem writing to memory.json")
            
def yle_eng_parser():
    """
    """
    yle_newsfeed_eng = "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_NEWS"
    memory_key = "yle_feed"

    if TESTING == False:
        channel_id = "@Finland_News_Feed" 
    else:
        channel_id = "@yle_news_live"

    # parsing the RSS feed
    NewsFeed = feedparser.parse(yle_newsfeed_eng)
    # selecting the last article on the feed
    newest_article = NewsFeed.entries[0]
    # Save the title of last article
    memory = openMemory()
    sent_articles = memory[memory_key]

    # checking for new articles
    if newest_article.id not in sent_articles:
        # Parsing the link & the title
        link = newest_article.link
        title = newest_article.title
        
        # formatting the link & the title
        edited_title = titleEditor(title)
        
        # sending the message
        sender(edited_title, link, channel_id, yle_newsfeed_eng)
        print("New article from YLE (ENG) sent!!!")

        sent_articles.clear()
        # appending last 5 articles to a list
        for article in NewsFeed.entries[:5]:
            sent_articles.append(article.id)

        memory[memory_key] = sent_articles

        # writing to memory
        writeMemory(memory, memory_key)
        
    else:
        print("No new articles found in YLE (ENG) RSS feed.")

def good_fin_parser():
    """
    """
    good_newsfeed_eng = "https://www.goodnewsfinland.com/"
    channel_id = "@yle_news_live"


    try:
        page = requests.get(good_newsfeed_eng)
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
            sender(edited_title, link, channel_id, good_newsfeed_eng)
            print("Good News Finland Article sent")

            memory["good_feed"] = title
            writeMemory(memory,"good_feed")
        else:
            pass

    except:
        print("Experienced a problem when parsing the GOOD NEWS article.")

def yle_fin_parser():
    """
    """
    #yle_newsfeed_fi = "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET" # Recent news (too many news)
    yle_newsfeed_fi = "https://feeds.yle.fi/uutiset/v1/majorHeadlines/YLE_UUTISET.rss"
    memory_key = "yle_fin_feed"

    if TESTING == False:
        channel_id = "@suomiuutiset" 
    else:
        channel_id = "@yle_news_live"

    # Parsing the RSS feed
    NewsFeed = feedparser.parse(yle_newsfeed_fi)
    # selecting the last article on the feed
    newest_article = NewsFeed.entries[0]
    # Save the title of last article
    memory = openMemory()
    sent_articles = memory[memory_key]

    # checking for new articles
    if newest_article.id not in sent_articles:
        # Parsing the link & the title
        link = newest_article.link
        title = newest_article.title
        
        # formatting the link & the title
        edited_title = titleEditor(title)
        
        # sending the message
        sender(edited_title, link, channel_id, yle_newsfeed_fi)
        print("New article from YLE (FIN) sent!!!")

        sent_articles.clear()
        # appending last 5 articles to a list
        for article in NewsFeed.entries[:5]:
            sent_articles.append(article.id)

        memory[memory_key] = sent_articles

        # Writing to Memory
        writeMemory(memory, memory_key)
        
    else:
        print("No new articles found in YLE (FIN) RSS feed.")

def yle_rus_parser():
    """
    """
    yle_newsfeed_ru = "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_NOVOSTI"
    memory_key = "yle_rus_feed"

    if TESTING == False:
        channel_id = "@Finland_News_RUS"
    else:
        channel_id = "@yle_news_live"

    # Parsing the RSS feed
    NewsFeed = feedparser.parse(yle_newsfeed_ru)
    # Selecting the last article on the feed
    newest_article = NewsFeed.entries[0]
    # Save the title of last article
    memory = openMemory()
    sent_articles = memory[memory_key]

    # Checking for new articles
    if newest_article.id not in sent_articles:
        # Parsing the link & the title
        link = newest_article.link
        title = newest_article.title
        
        # Formatting the link & the title
        edited_title = titleEditor(title)
        
        # Sending the message
        sender(edited_title, link, channel_id, yle_newsfeed_ru)
        print("New article from YLE (RUS) sent!!!")

        sent_articles.clear()
        # Appending last 5 articles to a list
        for article in NewsFeed.entries[:5]:
            sent_articles.append(article.id)

        memory[memory_key] = sent_articles

        # Writing to Memory
        writeMemory(memory, memory_key)
        
    else:
        print("No new articles found in YLE (RUS) RSS feed.")

def iltalehti_fin_parser():
    """
    """
    iltalehti_newsfeed_fin = "https://www.iltalehti.fi/rss/uutiset.xml"
    memory_key = "iltalehti_fin_feed"

    if TESTING == False:
        channel_id = "@suomiuutiset" 
    else:
        channel_id = "@yle_news_live"

    # Parsing the RSS feed
    NewsFeed = feedparser.parse(iltalehti_newsfeed_fin)
    # selecting the last article on the feed
    newest_article = NewsFeed.entries[0]
    # Save the title of last article
    memory = openMemory()
    sent_articles = memory[memory_key]

    # checking for new articles
    if newest_article.id not in sent_articles:
        # Parsing the link & the title
        link = newest_article.link
        title = newest_article.title
        
        # formatting the link & the title
        edited_title = titleEditor(title)
        
        # sending the message
        sender(edited_title, link, channel_id, iltalehti_newsfeed_fin)
        print("New article from Iltalehti FIN sent!!!")

        sent_articles.clear()
        # appending last 5 articles to a list
        for article in NewsFeed.entries[:5]:
            sent_articles.append(article.id)

        memory[memory_key] = sent_articles

        # Writing to Memory
        writeMemory(memory, memory_key)
        
    else:
        print("No new articles found in Iltalehti FIN RSS feed.")
   

def main():
    """
    """
    while True:
        
        # If its 10:00 run this script
        current_time = time.strftime("%H:%M", time.localtime())
        if (current_time >= "10:00") and (current_time < "10:05"):
            good_fin_parser()
            time.sleep(INTERVAL)

        
        yle_eng_parser()
        time.sleep(INTERVAL)

        yle_rus_parser()
        time.sleep(INTERVAL)

        yle_fin_parser()
        time.sleep(INTERVAL)

        current_hour = time.strftime("%H", time.localtime())
        if int(current_hour) % 6 == 0:
            iltalehti_fin_parser()
            time.sleep(INTERVAL)



if __name__ == "__main__":
    main() 