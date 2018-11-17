import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from hashlib import md5
import os
import time


def create_dir(path):
    try:
        # 如果路径不存在就创建
        if not os.path.exists(path):
            os.mkdir(path)
    except OSError:
        return os.path.join(os.getcwd(), 'user2')
    return path


def get_user(url, pagecount, timemap):
    param = {
        'count': 20,
        'page': pagecount,
        'before_timestamp': timemap
    }
    try:
        response = requests.get(url, params=param)
        if response.status_code == 200:
            return response.json()
        return None
    except ConnectionError:
        print('请求失败：' + url)


def parse_user(text):
    if text.get('post_list'):
        for item in text.get('post_list'):
            yield item


# 返回图集中每个图片地址
def get_image_urls(text):
    base_url = 'https://photo.tuchong.com/{0}/f/{1}.jpg'
    if text.get('images'):
        for image in text.get('images'):
            yield base_url.format(image.get('user_id'), image.get('img_id'))


def download_image(url, path):
    print('download:' + url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content, os.path.join(path, os.path.basename(url)))
        else:
            print('download failed:' + url)
    except ConnectionError:
        print("请求下载失败！")


def save_image(content, path):
    if not os.path.exists(path):
        with open(path, 'wb') as f:
            f.write(content)
            f.close()


def main():
    star_urls = ['https://mixmico.tuchong.com/rest/2/sites/2574940/posts',
                 'https://ronnie.tuchong.com/rest/2/sites/476401/posts',
                 'https://tuchong.com/rest/2/sites/1653292/posts',
                 'https://heikki.tuchong.com/rest/2/sites/1184254/posts',
                 'https://tuchong.com/rest/2/sites/3313267/posts',
                 'https://zhaojie.tuchong.com/rest/2/sites/2346568/posts',
                 'https://tuchong.com/rest/2/sites/1745920/posts',
                 'https://tuchong.com/rest/2/sites/2728584/posts',
                 'https://tuchong.com/rest/2/sites/3262232/posts',
                 'https://tuchong.com/rest/2/sites/1297735/posts',
                 'https://tuchong.com/rest/2/sites/384710/posts',
                 'https://qihua.tuchong.com/rest/2/sites/1076705/posts',
                 'https://tuchong.com/rest/2/sites/2551155/posts',
                 'https://tuchong.com/rest/2/sites/2898141/posts',
                 'https://tuchong.com/rest/2/sites/1139905/posts',
                 'https://tuchong.com/rest/2/sites/1107944/posts',
                 'https://tuchong.com/rest/2/sites/1160908/posts']
    for url in star_urls:
        print('start:' + url)
        count = 1
        js = get_user(url, 1, 0)
        # 创建用户文件夹
        if os.path.exists(os.path.join(os.getcwd(), 'user2', js.get('post_list')[0].get('author_id'))):
            continue
        create_dir(os.path.join(os.getcwd(), 'user2', js.get('post_list')[0].get('author_id')))
        while True:
            post_list = parse_user(js)
            for item in post_list:
                for image_url in get_image_urls(item):
                    time.sleep(0.5)
                    download_image(image_url,
                                   os.path.join(os.getcwd(), 'user2', js.get('post_list')[0].get('author_id')))
            if js.get('more'):
                count = count + 1
                js = get_user(url, count, js.get('before_timestamp'))
            else:
                break
        print('finsh:' + url)
    print('finsh')


if __name__ == "__main__":
    main()
