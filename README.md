# NLP and Scraping using IMDB Data.

## Introduction
This repository provides code for scraping IMDB for reviews on Series such as House of The Dragon and Rings of Power. It will take a few inputs from the user and save data in .csv format at a specified location. Check out my [series on Medium](https://medium.com/@alin.preda/r-o-p-vs-h-o-t-d-episode-1-scraping-imdb-reviews-7efe240ad74b) to understand more about the project. In the future it will be extended to offer capabilities for data analysis mainly focused on data mining the review text.
<br>
<br>

## Building the Project
This build assumes you are using a Linux/Mac with Python version at least 3.8 installed.
<br>

### Installing Poetry
[<b>Poetry</b>](https://python-poetry.org/) is the packageing and dependency management tool of choice. A .toml and a .lock file is provided. Poetry will install dependencies based on these. 

The [official way](https://python-poetry.org/docs/) of installing Poetry:
```
curl -sSL https://install.python-poetry.org | python3 -
```

If you need to install curl (try using sudo if needed):
```
apt update && apt upgrade
apt install curl
```

You might need to add it to path:
```
ENV PATH /root/.local/bin:$PATH
```

To activate the Poetry virtual environment and shell:
```
poetry shell
```

Update Poetry:
```
poetry update
```

Install main dependencies (without dev):
```
poetry install --only main
```
<br>

Quit Poetry Shell
```
deactivate
```

### Alternative to Poetry
If you are having problems with installing or using Poetry, you can simply do the old:
```
pip install -r requirements.txt
```
<br>

## Running IMDB Review Scraper
The scraper comes ready-use and takes user-defined input through the command line.

Set current directory to source file code:
```
cd src
```
And from here you can access the script which will start the scraper. There are parameters which you will need to set from the command line, in order to scrape your desired series. For the IMDB review scraper, you only need specify the title page of the show. Then what happens is that the scraper will mine all data from the reviews of the show itself and each episode of each season.
```
python3 scrape_imdb_reviews.py --title_page https://www.imdb.com/title/tt7631058/ --output_path ./data/rop.csv
```

## Running with Docker
Using the Dockerfile, you can build an image and run the scraper interactively with Docker.
```
sudo docker build -t imdb-scraper .
```
If all is right, Docker should build the image. Your output should be something like:
```
Successfully built fa10565946f9
Successfully tagged imdb-scraper:latest
```
To run it with Docker, simply do:
```
```
