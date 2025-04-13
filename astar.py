from functions import node
import heapq
from typing import List

def astar(start: str, avoid: List = [], WAIT_TIME=1):
    assert isinstance(start, str), "Start must be a string url"
    assert "https://" in start, "start must have https://"
    for u in avoid:
        assert isinstance(u, str), "All urls in avoid must be of type string"

    expanded = []
    avoid = [node(u) for u in avoid]
    fringe = [node(start)]  # heap
    max_nodes = 20
    count = 0
    bn_order = []
    best_node = None

    while fringe:
        current = heapq.heappop(fringe)

        if current in expanded or current in avoid:
            continue

        if not best_node:
            best_node = current
            bn_order.append(current)
        elif best_node.goal() < current.goal():
            best_node = current
            bn_order.append(current)

        if count > max_nodes:
            break

        print("Expanding & Retrieving:", current.url)
        current.wait = WAIT_TIME
        for child in current.expand_children():
            if (child in expanded) or (child in avoid):
                continue

            heapq.heappush(fringe, child)

        count += 1

    return bn_order


if __name__ == '__main__':
    gporder = astar('https://www.westpac.com.au/')
    print("--------------------------------")
    for p in gporder:
        print(p.url, p.goal())

