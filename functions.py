# File defines functions used for web crawling and iterative bfs algorithms.
import requests
import time
import typing
from bs4 import BeautifulSoup
import urllib
import numpy as np


# many nodes make a graph
class node:
    def __init__(
        self,
        url: str,
        parent = False,
        g: int = 0,
        bad_url = 0
    ):
        # defines a node
        # add redefenition to ch.
        self.url = url
        self.expanded = False
        self.content = None
        self.parent = parent
        self.init_time = time.time()
        self.unexpandable = False
        self.wait = 0.1

        self.netloc = 'https://' + urllib.parse.urlparse(url).netloc
        self.g = g
        self.h = 0
        self.f = float(g)**1.5 + float(bad_url) + float(self.heuristic())

    def request(self):
        try:
            time.sleep(self.wait)
            response = requests.get(self.url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                self.content = soup
                self.expanded = True
            elif response.status_code == 429:
                time.sleep(60)
                self.wait += 0.1
                print("rate limited, 429")
                self.unexpandable = True
            else:
                print(f"{response.status_code}")
                self.unexpandable = True
        except Exception as E:
            print("ERROR OCCURED WHEN TRYING TO RETRIEVE URL:")
            print(self.url)
            print(E)
            print("==============================")
            self.unexpandable = True

    def existsin(self, node_list) -> bool:
        for element in node_list:
            if element == self:
                return True
        return False

    def expand_children(self) -> typing.List:
        # returns a list of nodes
        if not self.unexpandable:
            if self.expanded:
                children = []
                for element in self.content.find_all('a'):
                    link = element.get('href')
                    # case with no href
                    if not link:
                        continue

                    if link[0] == '/':
                        bad_url = 0
                        link = self.netloc + link
                    bad_url = 0 if self.netloc in link else 50
                    ch = node(link, parent=self, g=self.g+1, bad_url=bad_url)
                    children.append(ch)

                return children

            self.request()
            return self.expand_children()

        return []

    def goal(self):
        # a node is either
        # unexpandable, -> 0
        # or not expanded -> expand
        if self.unexpandable:
            return 0
        if not self.expanded:
            self.request()
            return self.goal()
        # goal nodes in this case are defined as nodes that are graduate programs
        negative_scoring_phrases = {"school", "apprenticeship", "indigenous"}
        # usually indigenous programs are offered sepperately
        # bias against high school and apprenticeship programs, only want grad programs
        high_scoring_phrases = {"grad", "graduate", "stream", "pathway"}

        # key[score] -> value[phrases] # TODO fix this, poor implemntation
        indepth_score_dict = {
            -100: ["high", "school", "leaver",
                   "internship", "year 12", 'aps1', 'aps2'
                   "iii", "cert", "certified", 'qualification',
                   "news", 'media', 'release'],
            -30: ["aps6", 'heritage', 'aborginal', 'torres'],
            -20: [
                    "covid", "report", "languages", "aps5"
            ],
            -10: ["diversity", "indigenous"],
            11: ["stage"],
            20: ["months", "candidate", 'training',
                 'development', 'opportunities'
                 'career', 'rotations'],
            10: ["apply", "now", "closed",
                 "open", "data"],
            40: ["policy", "corporate", "tech", "intel",
                 "degree", "bachelors", "honors"],
            40: ["maths", "mathematics", "information", "engineering",
                 "degree", "bachelors", "honors"],
            50: ["graduate", "stream", "data",
                 "resource", "corporate", "technology", "legal",
                 "12", "aps3", "aps4", 'final', 'tertiary']
        }

        # like 3d n x hn tensor bruh, bad idea
        # hn as in h1, h2, h3, h4
        hn_score: int = 0
        for n in range(1, 6):
            hns = self.content.find_all(f"h{n}")
            for hn in hns:
                for word in high_scoring_phrases:
                    try:
                        if word in hn.string.lower():
                            hn_score += 5 * (6-n)  # size of the heading determines the size of the score
                    except Exception as e:
                        pass
        title_score: int = 0
        try:
            title_text = self.content.find('title').string
            for w in high_scoring_phrases:
                if w in title_text:
                    title_score = 100

            for w in negative_scoring_phrases:
                if w in title_text:
                    title_score = -150
        except Exception as e:
            pass

        # title
        all_text = (' '.join(self.content.get_text().split())).lower()
        wc = len(all_text.split(' '))
        word_score = 0
        length_score = 0
        if wc < 400:
            length_score = -100
        elif wc < 750:
            length_score = 54
        elif wc < 1500:
            length_score = 150
        elif wc < 2500:
            length_score = 100
        elif wc < 3000:
            length_score = 50
        else:
            length_score = -0.25 * wc + 150

        for score, phrases in indepth_score_dict.items():
            for phrase in phrases:
                if phrase in all_text:
                    word_score += score

        weights = np.array([3, 1, 2, 0.001])
        vector = np.array([hn_score, word_score, title_score, length_score])
        self.vector = vector
        return np.inner(weights, vector)

    def heuristic(self):
        # defines the heuristic value for a url. Based of parent url, and keyphrases in url

        # heuristic has to be purely defined base of url, to prevent the number of requests made
        # key [score] -> value [list of phrases associated with score]
        score_dict = {
            -80: ["grad", "graduate"],
            -40: ["program", "career", "work", "vac"],
            -10: ["data", "legal", "entry", "level", "join", "stream"],
            10: ["about", 'questions'],
            20: ['news', 'events', 'contact', "other", "diversity", "languages"],
            40: ["privacy", "policy"],
            1000: ["apprenticeship", "login", "sign"]
        }

        if not self.parent:
            return 0 # case when roote node, no parent

        if ((self.netloc == self.parent.netloc) or
                ('nga.net.au' in self.netloc)):
            hsum = 50
            # cycle through the phrases dictionary
            # make a better hueristic in the future potentially # TODO
            for score, value in score_dict.items():
                for phrase in value:
                    if phrase in self.url:
                        hsum += score
            return hsum
        else:
            # not matching domain = bad
            return 10e3

    def __str__(self):
        # formatting function
        url_part = self.url.replace("https://", "")[-25:] if len(self.url) > 25 else self.url
        return f"{self.netloc} | {url_part} | {self.f}, {self.g}, {self.heuristic()}"

    def __repr__(self):
        return self.url

    def __eq__(self, other):
        return self.url == other.url

    def __lt__(self, other):
        # expand this method.
        # allow for heapq ordering
        # order by self.f, self.time
        if self.f == other.f:
            return self.init_time < self.init_time
            # init times are always unique
        return self.f < other.f
        # return id(self) < id(other)
