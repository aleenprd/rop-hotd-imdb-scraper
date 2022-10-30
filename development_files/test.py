import pandas as pd
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import re as regex
from typing import Dict, List
import numpy as np
from tqdm import tqdm
from time import sleep
import traceback
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def make_soup(url: str, header: str) -> BeautifulSoup:
    """
    Return an HTML body from an URL.

    Obs: Soup is not enoug hfor this site.
    We need to interact with the JavaScript,
    so we will use Selenium with ChromeDriver.
    """
    r = requests.get(url, headers=header)
    soup = BeautifulSoup(r.text, 'html.parser')

    return soup

def make_soup_with_selenium(
    url: str,
    driver_service
) -> BeautifulSoup:
    """
    Return an HTML body from an URL.

    Obs: Soup is not enoug hfor this site.
    We need to interact with the JavaScript,
    so we will use Selenium with ChromeDriver.
    """
    chromedriver = webdriver.Chrome(service=driver_service)
    chromedriver.maximize_window()
    #chromedriver.get(url)
    sleep(5)

    page_source = chromedriver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    chromedriver.quit()
    return soup

def get_episodes_links(link, driver_service):
    soup = make_soup_with_selenium(link, driver_service)
    website = "https://www.imdb.com"
    
    links = []
    for link in soup.find_all('a', href=True):
        href = link["href"]
        if bool(regex.search('=ttep_ep\d$', href)):
            links.append(href) 
            
    links = list(set(links))
    links.sort()
    links = [f"{website}{l}" for l in links]
    
    return links

def get_ratings_page(episode_page, suffix="/ratings/?ref_=tt_ov_rt"):
    return ("/").join(episode_page.split("/")[:-1]) + suffix 

def get_reviews_page(episode_page, suffix="/reviews?ref_=tt_urv"):
    return ("/").join(episode_page.split("/")[:-1]) + suffix 

def scroll_reviews_and_cook_soup(link: str, driver_service):
    chromedriver = webdriver.Chrome(service=driver_service)
    chromedriver.maximize_window()
    chromedriver.get(link)
    sleep(10)

    while True:
        try:
            loadMoreButton = chromedriver.find_element(By.ID, "load-more-trigger")
            sleep(2)
            loadMoreButton.click()
            sleep(3)
        except Exception as e:
            #print("Exception :", e)
            break
    # Get page source code
    page_source = chromedriver.page_source
    reviews_soup = BeautifulSoup(page_source, 'lxml')
    #chromedriver.quit()
    return reviews_soup

def fetch_el_if_available(soup, element_type: str, class_type: str):
    element = soup.find(element_type, class_type)
    if element is not None:
        element = element.text
    return element

def scrape_reviews_page(reviews_soup):
    review_ratings = []
    user_names = []
    review_dates = [] 
    review_titles = []
    review_texts = []
    num_helpful_reactions = []
    num_total_reactions = []
    
    review_boxes = reviews_soup.find_all('div', {"class": "lister-item"})
    
    for review in review_boxes:
        # Rating of review
        review_rating = fetch_el_if_available(review, "div", "ipl-ratings-bar")
        if review_rating is not None:
            review_rating = review_rating.replace("\n", "").split("/")[0]
        review_ratings.append(review_rating)

        # User name plus date of review
        user_name_and_date = fetch_el_if_available(review, "div", "display-name-date")
        if user_name_and_date is not None:
            user_name_and_date = user_name_and_date.replace("\n", "").split(" ")
            user_names.append(user_name_and_date[0])
            review_dates.append(user_name_and_date[1] + " " + user_name_and_date[1])
        else:
            user_names.append(None)
            review_dates.append(None)
        
        # Title of review
        review_title = fetch_el_if_available(review, "a", "title")
        if review_title is not None:
            review_title = review_title.replace("\n", "")
        review_titles.append(review_title)
        
        # Text of review
        review_text = fetch_el_if_available(review, "div", "text")
        if review_title is not None:
            review_text = review_text.replace("\n", "")
        review_texts.append(review_text)
        
        # Review Reactions
        reactions = fetch_el_if_available(review, "div", "actions")
        if reactions is not None:
            reactions = reactions.replace("\n", "").strip().split(" ")
            num_helpful_reactions.append(reactions[0])
            num_total_reactions.append(reactions[3])
        else:
            num_helpful_reactions.append(None)
            num_total_reactions.append(None)
    
    df_out = pd.DataFrame()
    df_out["review_rating"] = review_ratings
    df_out["user_name"] = user_names
    df_out["review_date"] = review_dates
    df_out["review_title"] = review_titles
    df_out["review_text"] = review_texts
    df_out["num_helpful_reactions"] = num_helpful_reactions
    df_out["num_total_reactions"] = num_total_reactions

    return df_out


season_link = "https://www.imdb.com/title/tt7631058/episodes?ref_=tt_eps_sm"
show_link = "https://www.imdb.com/title/tt7631058/?ref_=tt_urv"
output_path = "rop_s1.csv"
driver_service = Service(ChromeDriverManager().install())
episodes_links = get_episodes_links(link=season_link, driver_service=driver_service)
print(episodes_links)