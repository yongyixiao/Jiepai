import requests
from urllib.parse import urlencode
import os
from hashlib import md5
from multiprocessing import Pool
from requests import codes


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

def get_page(offset):
    params = {
        'offset': offset,
        'format':'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab',

    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    try:
        response = requests.get(url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None


def get_image(json):
    if json.get('data'):
        data = json.get('data')
        for item in data:
            if item.get('cell_type') is not None:
                continue
            title = item.get('title')
            images = item.get('image_list')
            for image in images:
                yield {
                    'image': 'https:' + image.get('url'),
                    'title': title
                }

def save_image(item):
    img_path = 'jiepai' + os.path.sep + item.get('title').strip()
    dir = os.path.join('jiepai', item.get('title').strip())
    if not os.path.exists(dir):
        os.makedirs(dir)
    try:
        response = requests.get(item.get('image'))
        if codes.ok == response.status_code:
            file_path = img_path + os.path.sep + '{file_name}.{file_suffix}'.format(file_name=md5(response.content).hexdigest(),
                file_suffix='jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as file:
                    file.write(response.content)
            else:
                print('already download', file_path)
    except requests.ConnectionError:
        print('error')

def main(offset):
    json = get_page(offset)
    for item in get_image(json):
        print(item)
        save_image(item)


if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(0, 7)])
    pool.map(main, groups)
    pool.close()
    pool.join()


