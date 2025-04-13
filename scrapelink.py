import typing
from .functions import node
import heapq


urlList = typing.List[str]


def grad_programs(start_url: str) -> urlList:
    max_depth = 5
    expanded = []
    queue = [node(start_url)]
    

    pass


if __name__ == '__main__':
    print(grad_programs('https://www.ndiscommission.gov.au/'))
    #print(grad_programs('https://aasb.gov.au/'))
    #print(grad_programs('https://www.asa.gov.au/'))
