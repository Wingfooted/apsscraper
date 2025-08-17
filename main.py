import pandas
import os
import astar
import sys

def get_grad_program(url):
    # url -> url, most likely grad program, score, scope
    current_scope = 'gov'
    scopes = ['nsw', 'tas', 'wa',
              'qld', 'nt', 'vic', 'act',
              'embassy', 'highcomission']
    for scope in scopes:
        if f".{scope}." in url:
            current_scope = scope

    try:
        grad_program_rankings = astar.astar(url, WAIT_TIME=1)
        grad_program = grad_program_rankings[-1]
        grad_program_url = grad_program.url
        score = grad_program.goal()

    except Exception as E:
        print(E)
        grad_program_url = None
        score = -1

    return (url, scope, grad_program_url, score)

if __name__ == '__main__':
    filename = sys.argv[1]
    blacklist = sys.argv[2]
    output = sys.argv[3]
    with open(filename, 'r') as inputs:
       urls = set([
           url.replace('\n', '')
           for url in
           inputs.readlines()
           ])
       with open(blacklist, 'r') as banned:
           banned_urls = set([
               url.replace('\n', '')
               for url in
               banned.readlines()
               ])

    urls = urls - banned_urls
    print("=== running program ===")
    print(f" == {blacklist} == ")
    for b in banned_urls:
        print("    -", b)

    print(f" == Main Program == ")
    with open(output, 'w') as log:
        for url in urls:
            print(" ## Searching:", url)
            url, scope, grad_program_url, score = get_grad_program(url)
            print(" ## Found:", grad_program_url, "Score:",score)
            print("key, generally values over 600 are grad programs")
            log.write(
                    f"{url},{current_scope},{grad_program_url},{score}\n"
                    )
