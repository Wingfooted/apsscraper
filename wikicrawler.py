from bs4 import BeautifulSoup
import requests


def get_links(url):
    response = requests.get(url)
    links = []

    if response.status_code == 200:
        text = response.text
        soup = BeautifulSoup(text, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a')]
        return links

    else:
        print("Error", response.status_code, url)

    return links


if __name__ == '__main__':

    links = get_links('https://en.wikipedia.org/wiki/List_of_Australian_Government_entities')

    for l in links:
        print(l)
