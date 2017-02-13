import lxml
from bs4 import BeautifulSoup

# Python 3
from urllib.request import urlopen
import pandas as pd
     

def scrape():

    print("Scraping Team Abbreviations...")
    url = "https://sportsdelve.wordpress.com/abbreviations/"
    
    page = urlopen(url)
    soup = BeautifulSoup(page, "lxml")
    

    tab = soup.find_all('table')
    nba = tab[2]
    data = nba.find_all('tr')

    nba_dict = {}

    for team_data in data:
        team = team_data.find_all('td')
        abbr = team[0].find(text = True)
        name = team[1].find(text = True)

        nba_dict[abbr] = name
    
    return nba_dict

def scrape_reverse():
    print("Scraping Team Abbreviations...")
    url = "https://sportsdelve.wordpress.com/abbreviations/"
    
    page = urlopen(url)
    soup = BeautifulSoup(page, "lxml")
    

    tab = soup.find_all('table')
    nba = tab[2]
    data = nba.find_all('tr')

    nba_dict = {}

    for team_data in data:
        team = team_data.find_all('td')
        abbr = team[0].find(text = True)
        name = team[1].find(text = True)

        nba_dict[name] = abbr
    
    return nba_dict

