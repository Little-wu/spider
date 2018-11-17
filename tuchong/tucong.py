import os
from hashlib import md5
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import time


# 以图集标题为文件名，有非法字符直接存在上一级
def create_path(path):
    try:
        # 如果路径不存在就创建
        if not os.path.exists(path):
            os.mkdir(path)
    except OSError:
        return os.path.join(os.getcwd(), 'images')
    return path


# 请求索引页，并把返回解析的json数据
def get_page_index(url, pagecount):
    # 构造请求参数
    param = {'page': pagecount,
             'count': 20,
             'order': 'weekly'}
    try:
        # 请求网页
        response = requests.get(url, params=param)
        if response.status_code == 200:
            return response.json()
        return None
    except ConnectionError:
        print('请求连接失败！')


# 获取图集的链接，使用生成器
def parse_page_index(json):
    if 'postList' in json.keys():
        for item in json.get('postList'):
            yield item.get('url')


# 请求图集的网页
def get_page_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        print('请求连接失败！')


# 获取图集中图片链接，并下载
def parse_page_detail(html):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].text.split(' ')[0]
    images = soup.select('article.post-content > img.multi-photo-image')
    for image in images:
        time.sleep(1)
        download_image(image.get('src'), create_path(os.path.join(os.getcwd(), 'images', title)))


# 下载图片
def download_image(url, path):
    print('Downloading:' + url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content, path)
        return None
    except ConnectionError:
        print('下载失败！')
        return None


# 保存图片
def save_image(content, path):
    file_path = os.path.join(path, '{0}.{1}'.format(md5(content).hexdigest(), 'jpg'))
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main(pagecount):
    URL = 'https://tuchong.com/rest/tags/私房/posts'
    json = get_page_index(URL, pagecount)
    urls = parse_page_index(json)
    for url in urls:
        html = get_page_detail(url)
        parse_page_detail(html)


if __name__ == '__main__':
    for i in range(1, 10):
        main(i)
