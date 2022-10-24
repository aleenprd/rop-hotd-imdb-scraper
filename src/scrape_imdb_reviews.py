"""Python executable which scrapes IMDB for reviews."""


import argparse
import pandas as pd
from time import sleep
from tqdm import tqdm

from dependencies.general import timing
from dependencies.scrapers import ImdbReviewScraper


parser = argparse.ArgumentParser()


parser.add_argument(
    "--title_page",
    type=str,
    required=False,
    help="URL to Show Main page.",
    default="https://www.imdb.com/title/tt7631058/"
)
parser.add_argument(
    "--output_path",
    type=str,
    required=False,
    help="Path where to save the CSV result file.",
    default="./data/rop_season1.csv"
)


@timing
def main(title_page: str, output_path: str):
    """Main function to scrape an IMDB season's reviews for each episode and also the general reviews.

    Args:
        title_page (str): URL pointing to show title page.
        output_path (str): path including filename where we want to save the CSV.
    """
    # Results dataframes: one for each episode in the season
    re_dfs = []  # Will concatenate all dataframes at the end.
    
    # Initialize scraper; this will also initialzie a Chrome driver.
    scraper = ImdbReviewScraper()
    
    print("\nScraping Title Page Reviews...")
    show_reviews_link = reviews_page = ImdbReviewScraper.get_reviews_page(title_page)
    show_reviews_soup = scraper.scroll_reviews_and_cook_soup(link=show_reviews_link)
    df_temp = scraper.scrape_reviews_page(show_reviews_soup)
    df_temp["episode_number"] = 0
    df_temp["season_number"] = 0
    re_dfs.append(df_temp)
    
    # Fetch links to seasons
    season_1_link = ImdbReviewScraper.get_season_page(title_page=title_page, season_number=1)
    season_1_soup = scraper.make_soup_with_selenium(season_1_link)
    seasons = ImdbReviewScraper.get_number_of_seasons(season_1_soup)
    print(f"\nShow has {max(seasons)} episodes.")
    
    for season in seasons:
        print(f"\nScraping Season {season}...")
        
        # We use TQDM to construct a progress bar, showing us how far off we are with scraping.
        # For each episode, we want to get the reviws page, scroll till the end and make our DF.
        season_link = ImdbReviewScraper.get_season_page(title_page, season)
        episodes_links = scraper.get_episodes_links(link=season_link)

        for ep in tqdm(episodes_links):
            reviews_page = ImdbReviewScraper.get_reviews_page(ep)
            reviews_soup = scraper.scroll_reviews_and_cook_soup(
                link=reviews_page)
            df_temp = scraper.scrape_reviews_page(reviews_soup)
            df_temp["episode_number"] = int(ep.split("ep")[-1])
            df_temp["season_number"] = season
            re_dfs.append(df_temp)
            sleep(5)  # Sleep again again for a while to not overwhelm server with requests
        
    season_reviews_df = pd.concat(re_dfs)
    season_reviews_df.to_csv(output_path, header=True, index=False)


if __name__ == "__main__":
    args = parser.parse_args()

    print("\nScraper starting...")
    main(
        title_page=args.title_page,
        output_path=args.output_path
    )
    print("\nScraper finished task.\n")
