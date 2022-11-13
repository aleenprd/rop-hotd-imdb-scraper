FROM python:3.8

############################
#### OS #####
############################

# Update apt-get
RUN apt-get -qq -y update
# Install sudo and apt-utils
RUN apt-get -y install sudo
#RUN sudo apt-get install -y apt-utils
# We don't want to be interrupted during docker installabion by e.g. tzdata
ARG sudo DEBIAN_FRONTEND=noninteractive
# Install curl
RUN sudo apt-get -qq -y install curl

############################
##### POETRY #####
############################

# Install poetry with the official method and update it
RUN sudo curl -sSL https://install.python-poetry.org | python3 -
# Add poetry to PATH
ENV PATH="${PATH}:/root/.poetry/bin"
ENV PATH /root/.local/bin:$PATH
# Ensure a virtual environment is not created first (we already will have docker)
RUN poetry config virtualenvs.create false

############################
##### SRC #####
############################

# Working directory
RUN mkdir /imdb-scraper
# Copy source to this imdb-scraper project
COPY /src /imdb-scraper/src
# Setting work directory
WORKDIR /imdb-scraper
# Copying all including lock requirements
COPY poetry.lock /imdb-scraper 
COPY pyproject.toml /imdb-scraper 
COPY LICENSE /imdb-scraper
COPY README.md /imdb-scraper 


############################
#### DEPENDENCEIS #####
############################

# Update poetry
RUN poetry update
RUN ls -l
# Install all dependencies minus development ones (--no-dev is deprecated)
#RUN poetry install --only main

# Command to run on docker run
ENTRYPOINT ["python3", "./src/scrape_imdb_reviews.py"]