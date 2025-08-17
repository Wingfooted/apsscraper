from bs4 import BeautifulSoup
import requests
import tqdm
import time
import urllib

# get_government_agencies -> process_agencies


def get_links(url):
    netloc = urllib.parse.urlparse(url).netloc
    response = requests.get(url)
    links = []
    external, internal = set(), set()
    if response.status_code == 200:
        text = response.text
        soup = BeautifulSoup(text, 'html.parser')
        for l in soup.find_all('a'):
            link = l.get('href')
            if not link:
                continue

            if link[0] == '/':
                internal.add('https://'+netloc+link)
            else:
                external.add(link)
    else:
        print("Error", response.status_code, url)

    return external, internal


def get_governemnt_agencies():
    agencies = set()
    e, i = get_links('https://en.wikipedia.org/wiki/List_of_Australian_Government_entities')

    for internal in tqdm.tqdm(i):
        external, _ = get_links(internal)
        for e in external:
            if ".gov.au" in urllib.parse.urlparse(e).netloc:
                agencies.add(e)

    return agencies


def process_agencies(filename):
    with open(filename, 'r') as ag:
        links = [
            f"https://www.{urllib.parse.urlparse(l.replace("\n", "")).netloc.replace('www.', '')}\n"
            for l in ag.readlines()]
        links = set(links)

    with open(f"{filename.replace('.txt', '')}_processed.txt", "w") as agp:
        for l in links:
            agp.write(l)


if __name__ == '__main__':
    process_agencies("ag.txt")
