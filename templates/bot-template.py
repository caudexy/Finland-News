import os
import re
from re import search
import time
import json

import feedparser
import telegram

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

def titleEditor(title):
    """
    This function edits the article title. Escapes possible special charecters with Regular Expressions
    Args: 
        Title (str): The Title of the Article
    Returns: 
        link (str): Escaped title of the article
    """
    escaped_title = re.escape(title)
    escaped_title = escaped_title.replace("!","\!")
    return str(escaped_title)

def linkEditor(link, newsfeed_link):
    """
    This function edits the link for instant view.
    Args:
        link (str): Link of the article
        newsfeed_link (str): Link of the newsfeed RSS
    Returns:
        link (str): link with correct Instant View rhash added
    """
    # link start and rhash by telegram
    instant_view_start = "https://t.me/iv?url=https%3A%2F%2F"
    instant_view_rhash = "&rhash=04f872b445da2a" # Yle ENG instant view

    # splitting the link
    link = link.split("//",1)[1]
    # replacing "/"" with "%2F"
    link = link.replace("/", "%2F")

    # Adding link start and rhash by telegram
    link = instant_view_start + link + instant_view_rhash

    return link

def sender(title, link, channel_id, newsfeed_link):
    """
    This function sends the message(as a link) to the Telegram Channel.
    Args:
        title (str): Article Title 
        link (str): Article Link
        channel_id (str): Telegram channel ID
        newsfeed_link (str): RSS newsfeed link
    Returns:
        (bool) True if article was sent otherwise False
    """
    try:   
        bot = telegram.Bot(token=TOKEN)

        edited_link = linkEditor(link, newsfeed_link)

        bot.send_message(
                    chat_id=channel_id, 
                    text=f"{title}[\.]({edited_link})\n[Link to the Article]({link})",
                    parse_mode=telegram.ParseMode.MARKDOWN_V2
                )
        return True
    except:
        print("Experienced a problem when sending the article")
        return False

def openMemory():
    """
    This function reads the names of last articles from memory.
    Args: None
    Returns: None
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
            
def rss_parser():
    """
    """
    news_feed_link = "YOUR RSS LINK"
    memory_key = "NEWS FEED NAME"
    channel_id = "YOUR TELEGRAM CHANNEL ID"

    # Parsing the RSS feed
    newsfeed = feedparser.parse(news_feed_link)
    # Selecting the last article on the feed
    newest_article = newsfeed.entries[0]
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
        sender(edited_title, link, channel_id)
        
        sent_articles.clear()
        # Appending last 5 articles to a list
        for article in newsfeed.entries[:5]:
            sent_articles.append(article.id)

        # Saving ID's of last 5 articles
        memory[memory_key] = sent_articles

        # writing to memory
        writeMemory(memory, memory_key)
    else:
        print("No new articles found in RSS feed.")

def main():
    """
    """
    while True:
        rss_parser()

if __name__ == "__main__":
    main() 