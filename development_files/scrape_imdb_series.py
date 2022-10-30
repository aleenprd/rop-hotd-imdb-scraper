# Data manipulation
import pandas as pd
import re as regex

# Scraping
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Miscelaneous
from typing import Callable
from tqdm import tqdm
from time import sleep
from typing import List
import argparse


def timing(f: Callable) -> None:
    """Times a function runtime in minutes.

    Args:
        f (callable): a function/method.
    """
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        exec_time = round((te - ts) / 60, 4)
        print(f"\nExecution time: {exec_time} minutes.")

    return wrap


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

def make_soup_with_selenium(url: str, driver_service: Service) -> BeautifulSoup:
    """Return an HTML body from an URL.


    """
    chromedriver = webdriver.Chrome(service=driver_service)
    chromedriver.maximize_window()
    chromedriver.get(url)
    sleep(5)

    page_source = chromedriver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    return soup

def get_episodes_links(link: str, driver_service) -> List[str]:
    """Retrieve links to episodes, from series' season main page.
    
    Args:
        link (str): link to season main page.
        driver_service (Service): a Chrome web driver.
        
    Returns:
        links (List[str]): a list of links to the episodes.
    """
    soup = make_soup_with_selenium(link, driver_service)
    website = "https://www.imdb.com"
    
    links = []
    for link in soup.find_all('a', href=True):
        href = link["href"]
        # Episode links end with the following Regex
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

def scroll_reviews_and_cook_soup(link: str, driver_service: Service):
    """Scroll reviews page until the end using Selenium.

    Args:
        link (str): link to page, in this case the reviews page.
        driver_service (Service): a Chrome web driver.
    Reeturns:
        reviews_soup (BeautifulSoup): soup of the fully loaded page.
    """
    chromedriver = webdriver.Chrome(service=driver_service)
    chromedriver.maximize_window()  # make sure we capture everything on display
    chromedriver.get(link)
    sleep(5)  # Wait for the page to load

    while True:
        try:
            loadMoreButton = chromedriver.find_element(By.ID, "load-more-trigger")
            loadMoreButton.click()
            sleep(2)  # For it to laod and also to be friendlier on the server
        # At one point, there will be no more buttons to push
        # but the browser session continues. It just can't click any more
        except Exception as e:
            break

    page_source = chromedriver.page_source
    reviews_soup = BeautifulSoup(page_source, 'lxml')

    return reviews_soup


def fetch_el_if_available(soup: BeautifulSoup, element_type: str, class_type: str):
    """Returns element text if found, otherwise returns None.
    
    Args:
        soup (BeautifulSoup): a b24 soup.
        element_type (str): HTML type e.g. 'div'.
        class_type (str): the class of the desired element.
        
    Returns:
        element (str): text inside element.
    """
    element = soup.find(element_type, class_type)
    if element is not None:
        element = element.text

    return element

def scrape_reviews_page(reviews_soup: BeautifulSoup) -> pd.DataFrame:
    """Scrape IMDB reviews page.
    
    Note: Extracts ratings, usernames, review date, titles, review body text,
    number of reactions, total reactions to review.
    
    Args:
        reviews_soup (BeautifulSoup): soup of the entirely loaded reviews page.
        
    Returns:
        df_out (pd.DataFrame): a Pandas DataFrame with all the above information
        structured as columns.
    """
    # Initialize dataframe columns as empty lists to pe populated
    df_out = pd.DataFrame()
    review_ratings = []
    user_names = []
    review_dates = [] 
    review_titles = []
    review_texts = []
    num_helpful_reactions = []
    num_total_reactions = []
    
    # Find all review boxes on the page so we can iterate over them
    review_boxes = reviews_soup.find_all('div', {"class": "lister-item"})
    
    for review in review_boxes:
        # Rating of review
        review_rating = fetch_el_if_available(review, "div", "ipl-ratings-bar")
        if review_rating is not None:
            review_rating = review_rating.replace("\n", "").split("/")[0]
        review_ratings.append(float(review_rating))

        # User name
        user_name_and_date = fetch_el_if_available(review, "div", "display-name-date")
        if user_name_and_date is not None:
            user_name_and_date = user_name_and_date.replace("\n", "").split(" ")
            user_names.append(user_name_and_date[0])
        else:
            user_names.append(None)
        
        # Review date
        review_date = fetch_el_if_available(review, "span", "review-date")
        if review_date is not None:
            review_date = review_date.replace("\n", "").strip()
        review_dates.append(review_date)
        
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
            num_helpful_reactions.append(float(reactions[0]))
            num_total_reactions.append(float(reactions[3]))
        else:
            num_helpful_reactions.append(None)
            num_total_reactions.append(None)
    
    df_out["review_rating"] = review_ratings
    df_out["user_name"] = user_names
    df_out["review_date"] = review_dates
    df_out["review_title"] = review_titles
    df_out["review_text"] = review_texts
    df_out["num_helpful_reactions"] = num_helpful_reactions
    df_out["num_total_reactions"] = num_total_reactions

    return df_out

@timing
def main(season_link: str, show_link: str, driver_service: Service, output_path: str) -> None:
    """Main function to scrape an IMDB season's reviews for each episode and also the general reviews.
    
    Args:
        season_link (str): URL pointing to season page.
        show_link (str): URL pointing to show general reviews.
        driver_service (Service): a Chrome web driver.
        output_path (str): path including filename where we want to save the CSV.
    """
    # Results dataframes: one for each episode in the season
    re_dfs = []  # Will concatenate all dataframes at the end.
    

    episodes_links = get_episodes_links(link=season_link, driver_service=driver_service)
    print("Episodes: ", episodes_links)

    # We use TQDM to construct a progress bar, showing us how far off we are with scraping.
    # For each episode, we want to get the reviws page, scroll till the end and make our DF.
    for ep in tqdm(episodes_links):
        reviews_page = get_reviews_page(ep)
        print("Parsing Reviews at: ", reviews_page)
        reviews_soup = scroll_reviews_and_cook_soup(
            link=reviews_page, driver_service=driver_service)
        df_temp = scrape_reviews_page(reviews_soup)
        df_temp["episode_number"] = int(ep.split("ep")[-1])
        re_dfs.append(df_temp)
        
        sleep(5)  # Sleep again again for a while to not overwhelm server with requests

    show_reviews_link = reviews_page = get_reviews_page(show_link)
    print("Parsing Reviews at: ", show_reviews_link)
    show_reviews_soup = scroll_reviews_and_cook_soup(link=show_reviews_link, driver_service=driver_service)
    df_temp = scrape_reviews_page(show_reviews_soup)
    df_temp["episode_number"] = 0
    re_dfs.append(df_temp)
        
    season_reviews_df = pd.concat(re_dfs)
    season_reviews_df.to_csv(output_path, header=True, index=False)


import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--season_link",
    type=str,
    required=True,
    help="URL to Show Season page.",
    default="https://www.imdb.com/title/tt7631058/episodes"
)
parser.add_argument(
    "--show_link",
    type=str,
    required=True,
    help="URL to Show Main page.",
    default="https://www.imdb.com/title/tt7631058/"
)
parser.add_argument(
    "--output_path",
    type=str,
    required=True,
    help="Path where to save the CSV result file.",
    default="./data/results.csv"
)


if __name__ == "__main__":
    args = parser.parse_args()
    driver_service = Service(ChromeDriverManager().install())
    print("\nScraper starting...")
    main(
        season_link=args.season_link,
        show_link=args.show_link,
        driver_service=driver_service,
        output_path=args.output_path
    )
    print("\nScraper finished task.\n")
