import pandas as pd
import requests
from bs4 import BeautifulSoup

DBLP_BASE_URL = 'https://dblp.uni-trier.de/'
VENUE_URL = DBLP_BASE_URL + 'search/venue/'


def query_db(venue_string: str):
    resp = requests.get(VENUE_URL, params={'q': venue_string})
    return BeautifulSoup(resp.content)



if __name__ == "__main__":
    resp = query_db('usenix')
    print(resp)

