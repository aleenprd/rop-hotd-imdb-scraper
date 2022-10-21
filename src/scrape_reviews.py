"""Python executable which scrapes IMDB for reviews."""


import argparse
import pandas as pd
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from tqdm import tqdm

from dependencies.general import timing
import dependencies.scraping_utils as su


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
    

    episodes_links = su.get_episodes_links(link=season_link, driver_service=driver_service)
    print("Episodes: ", episodes_links)

    # We use TQDM to construct a progress bar, showing us how far off we are with scraping.
    # For each episode, we want to get the reviws page, scroll till the end and make our DF.
    for ep in tqdm(episodes_links):
        reviews_page = su.get_reviews_page(ep)
        print("Parsing Reviews at: ", reviews_page)
        reviews_soup = su.scroll_reviews_and_cook_soup(
            link=reviews_page, driver_service=driver_service)
        df_temp = su.scrape_reviews_page(reviews_soup)
        df_temp["episode_number"] = int(ep.split("ep")[-1])
        re_dfs.append(df_temp)
        sleep(5)  # Sleep again again for a while to not overwhelm server with requests

    show_reviews_link = reviews_page = su.get_reviews_page(show_link)
    print("Parsing Reviews at: ", show_reviews_link)
    show_reviews_soup = su.scroll_reviews_and_cook_soup(link=show_reviews_link, driver_service=driver_service)
    df_temp = su.scrape_reviews_page(show_reviews_soup)
    df_temp["episode_number"] = 0
    re_dfs.append(df_temp)
        
    season_reviews_df = pd.concat(re_dfs)
    season_reviews_df.to_csv(output_path, header=True, index=False)
    

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
