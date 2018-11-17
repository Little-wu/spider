# coding=utf-8
import requests
from requests.exceptions import ConnectionError
import json
from json.decoder import JSONDecodeError
from bs4 import BeautifulSoup
import re
import os
from hashlib import md5
from config import *
import pymongo
from multiprocessing import Pool
from urllib.parse import urlencode

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]


def download_image(url):
    print('Downloading:' + url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except ConnectionError:
        print('下载失败！')
        return None


def save_image(content):
    file_path = os.path.join(os.getcwd(), 'images', '{0}.{1}'.format(md5(content).hexdigest(), 'jpg'))
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def get_page_index(offset, keyword):
    data = {'offset': offset,
            'format': 'json',
            'keyword': keyword,
            'autoload': 'true',
            'count': 20,
            'cur_tab': 3,
            'from': 'gallery', }
    params = urlencode(data)
    base_url = 'https://www.toutiao.com/search_content/'
    url = base_url + '?' + params
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        print('请求失败！url=' + url)
        return None


def parse_page_index(text):
    try:
        data = json.loads(text)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                yield item.get('article_url')
    except JSONDecodeError:
        print('JSON解析失败！')
        pass


def get_page_detail(url):
    try:
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36', }
        respone = requests.get(url, headers=header)
        if respone.status_code == 200:
            return respone.text
        return None
    except ConnectionError:
        print('请求失败！url=' + url)
        return None


def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')
    result_title = title[0].get_text if title else ''
    image_pattern = re.compile('gallery: JSON.parse\("(.*)"\)', re.S)
    result = re.search(image_pattern, html)
    if result:
        data = json.loads(result.group(1).replace('\\', ''))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images:
                download_image(image)
            return {
                'title': result_title,
                'url': url,
                'images': images
            }


def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('successful saved to mongo!')
        return True
    return None


def main(offset):
    text = get_page_index(offset, KEYWORD)
    urls = parse_page_index(text)
    for url in urls:
        html = get_page_detail(url)
        result = parse_page_detail(html, url)
        # if result:
        # save_to_mongo(result)


if __name__ == '__main__':
    '''
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END)])
    pool.map(main, groups)
    pool.close()
    pool.join()
    '''
    main(0)
