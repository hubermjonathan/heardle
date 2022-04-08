from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
from time import sleep
import urllib.parse
import json


BILLBOARD_URL = "https://www.billboard.com/charts/hot-100/"
SOUNDCLOUD_URL = "https://soundcloud.com/search/sounds?q="

# path for selenium chromedriver exec
CHROMEDRIVER_PATH = r"chromedriver\chromedriver_win32\chromedriver.exe"


def get_billboard(year: int, month: int, day: int, top=5) -> dict:
    """
    Get the top results from the Bilboard Hot 100 for a date.
    """
    # build the billboard url with the date
    url = BILLBOARD_URL + str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2)

    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')

    # get all song entries in the table
    entries = soup.find_all('div', {'class': 'o-chart-results-list-row-container'})

    # list of song strings
    songs = []
    for i in range(top):
        title_tag = entries[i].find('h3', {'id': 'title-of-a-story'})
        title, artist = (title_tag.get_text().strip(), title_tag.parent.find('span').get_text().strip())
        songs.append(f'{title} - {artist}\n')
    
    return songs


def generate_songs_file(start_year, end_year=2022, start_month=1, end_month=13):
    """
    Generate a file with all songs from the Billboard Hot 100 for each month for specified dates.
    """
    # iterate over year and month ranges
    for year in range(start_year, end_year):
        for month in range(start_month, end_month):
            print(f'getting {month} {year}')
            with open('songs.txt', 'a') as file:
                songs = get_billboard(year, month, 1)
                file.writelines([f'=== {month} {year} ===\n', *songs])


def get_soundcloud_url(driver, song: str) -> str:
    """
    Get the soundcloud URL for the given song string.
    """
    try:
        print(f'getting soundcloud for: {song}')

        # generate soundcloud search url
        url = SOUNDCLOUD_URL + urllib.parse.quote(song)
        
        # open webpage in selenium
        driver.get(url)
        sleep(3)
        html = driver.page_source

        soup = BeautifulSoup(html)

        # get url for first search result
        song_url = soup.find('div', {'class': 'searchItem'}).find('a', {'sc-link-primary'})['href']
        return f'https://soundcloud.com{song_url}'
    # ctrl-c input
    except KeyboardInterrupt:
        exit()
    # catch other exceptions and log error
    except:
        print(f'FAILED TO GET SOUNDCLOUD URL: {song}')
        return 'FAILED_TO_GET_SOUNDCLOUD_URL'


def parse_songs_file(driver):
    """
    Remove duplicates from songs file and generate json output with song URLs.
    """
    # read songs from file and remove header lines
    with open('songs.txt', 'r') as file:
        songs = file.readlines()
    songs = [x.strip() for x in songs if "===" not in x]

    # add songs to dictionary to remove duplicates
    songs_dict = {}
    for song in songs:
        songs_dict[song] = ''

    print(f'=== found {len(songs_dict)} songs ===')
    
    # add open bracket for json format
    with open('songs.json', 'w') as file:
        file.write('[\n')
    
    # create json object for each song
    for song in songs_dict:
        formatted_song = {
            'url': get_soundcloud_url(driver, song),
            'string': song,
        }
        # append json object to file
        with open('songs.json', 'a') as file:
            json.dump(formatted_song, file, indent=4)
            file.write(',\n')

    # add closing bracket to json file
    with open('songs.json', 'a') as file:
        file.write(']\n')


def start_driver():
    """
    Start the selenium webdriver.
    """
    return webdriver.Chrome(CHROMEDRIVER_PATH)


if __name__ == "__main__":
    #generate_songs_file(1980)
    driver = start_driver()
    parse_songs_file(driver)
