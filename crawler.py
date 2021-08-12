import requests
from bs4 import BeautifulSoup
import queue
from threading import Thread

starting_url = 'https://scrapeme.live/shop/page/1/'
visited = set()
max_visits = 100  # careful, it will crawl all the pages
num_workers = 5
data = []

headers = {
    'authority': 'httpbin.org',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-US,en;q=0.9',
}

proxies = {'http': 'http://190.64.18.177:80'}


def get_html(url):
    try:
        response = requests.get(url)
        # response = requests.get(url, headers=headers, proxies=proxies)
        return response.content
    except Exception as e:
        print(e)
        return ''


def extract_links(soup):
    return [a.get('href') for a in soup.select('a.page-numbers')
            if a.get('href') not in visited]


def extract_content(soup):
    for product in soup.select('.product'):
        data.append({
            'id': product.find('a', attrs={'data-product_id': True})['data-product_id'],
            'name': product.find('h2').text,
            'price': product.find(class_='amount').text
        })


def crawl(url):
    visited.add(url)
    print('Crawl: ', url)
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    extract_content(soup)
    links = extract_links(soup)
    for link in links:
        if link not in visited:
            q.put(link)


def queue_worker(i, q):
    while True:
        url = q.get()  # Get an item from the queue, blocks until one is available
        if (len(visited) < max_visits and url not in visited):
            crawl(url)
        q.task_done()  # Notifies the queue that the item has been processed


q = queue.Queue()
for i in range(num_workers):
    Thread(target=queue_worker, args=(i, q), daemon=True).start()

q.put(starting_url)
q.join()  # Blocks until all items in the queue are processed and marked as done

print('Done')
print('Visited:', visited)
print('Data:', data)
