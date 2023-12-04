from biliResource import biliResource
import feedparser
import requests
import hashlib
from media import media_data_path
from datetime import datetime
# 解析RSS订阅的XML文件
import os
import sqlite3
import time
import configparser
from biliResource import log

class biliRss():
    def __init__(self, u_id, actors):
        self.u_id = u_id
        self.actors = actors
        self.resource_list = []

    def parse_res(self):
        config = configparser.RawConfigParser()
        # 读取配置文件
        config.read('./config/config.ini', encoding='utf-8')
        cookie = config['base_cfg']['cookie']
        # 模拟浏览器
        cookies = {
            "SESSDATA": cookie + ";"
        }
        headers = {
            # 用户代理 表示浏览器基本身份信息
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        string = f'keyword=&mid={self.u_id}&order=pubdate&order_avoided=true&platform=web&pn=1&ps=30&tid=0&web_location=1550101&wts={int(time.time())}6eff17696695c344b67618ac7b114f92'
        # 实例化对象
        md5_hash = hashlib.md5()
        md5_hash.update(string.encode('utf-8'))
        # 请求链接
        url = 'https://api.bilibili.com/x/space/wbi/arc/search'
        # 请求参数
        data = {
            'mid': self.u_id,
            'ps': '30',
            'tid': '0',
            'pn': '1',
            'keyword': '',
            'order': 'pubdate',
            'platform': 'web',
            'web_location': '1550101',
            'order_avoided': 'true',
            'w_rid': md5_hash.hexdigest(),
            'wts': int(time.time()),
        }
        # 发送请求 <Response [200]> 响应对象 表示请求成功
        response = requests.get(url=url, params=data, headers=headers, cookies=cookies)
        for index in response.json()['data']['list']['vlist']:
            video_resource = {'title': 'none', 'url': 'none', 'time': '1970-01-01', 'nfo': 'none', 'img_url': 'none',
                              'actors': 'none'}
            # 时间戳 时间节点 --> 上传视频时间点
            date = index['created']
            if None != index['meta']:
                dt = datetime.fromtimestamp(date)
                dt_time = dt.strftime('%Y-%m-%d')
                video_resource['title'] = dt_time + index['title'].replace(" ", "").replace("|", "").replace("'",
                                                                                                             "").replace(
                    ":", "").replace("?", "").replace("/", "").replace(".", "")  # 删除空格和|'
                video_resource['url'] = 'https://www.bilibili.com/video/{}'.format(index['bvid'])
                video_resource['time'] = dt
                video_resource['nfo'] = index['description']
                video_resource['img_url'] = index['pic']
                video_resource['actors'] = self.actors
                video_resource['meta'] = index['meta']['title']
                video_resource['flag'] = index['meta']['title']
                self.resource_list.append(video_resource)
            else:
                dt = datetime.fromtimestamp(date)
                dt_time = dt.strftime('%Y-%m-%d')
                video_resource['title'] = dt_time + index['title'].replace(" ", "").replace("|", "").replace("'",
                                                                                                             "").replace(
                    ":", "").replace("?", "").replace("/", "").replace(".", "")  # 删除空格和|'
                video_resource['url'] = 'https://www.bilibili.com/video/{}'.format(index['bvid'])
                video_resource['time'] = dt
                video_resource['nfo'] = index['description']
                video_resource['img_url'] = index['pic']
                video_resource['actors'] = self.actors
                video_resource['meta'] = None
                video_resource['flag'] = None
                self.resource_list.append(video_resource)
        log.info('开始订阅：%s', self.actors)
    def get_resource_list(self):
        return self.resource_list


def from_resource_get_img(resource_list, base_path):
    if len(resource_list) <= 0:
        log.warn("无资源列表，不下载任何图像！")
        return 0
    for resource in resource_list:
        filename = '{}.jpg'.format(resource['title'])
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Host': 'i1.hdslb.com',
            'If-Modified-Since': 'Sat, 11 Dec 2021 06:47: 14GMT',
            'If-None-Match': '5db79f9686f2e00c7f6905c6f8b2edc4',
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'

        }
        img_url = resource['img_url']
        # 先判断文件是否已下载，下载则不重复下载
        image_save_path = os.path.join(base_path, resource['actors'])
        image_save_path = os.path.join(image_save_path, resource['title'])
        image_save_path = os.path.join(image_save_path, filename)
        if os.path.exists(image_save_path):
            continue
        # 先检查是否存在该路径，不存在则会递归创建
        os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
        log.info('image_save_path%s', image_save_path)
        # 检查请求是否成功
        log.info('image_save_path filename%s', filename)
        # 发送HTTP请求获取图片内容
        response = requests.get(img_url, headers=headers)
        if response.status_code == 200:
            # 将图片内容保存到文件
            with open(image_save_path, 'wb') as file:
                file.write(response.content)
            log.info('图片下载成功:%s', filename)
        else:
            log.error('图片下载失败%s', filename)


def add_media_item_to_db(item):
    conn = sqlite3.connect('./database/media.db')
    # 创建一个游标对象，用于执行SQL语句
    cursor = conn.cursor()
    # 创建一个表格
    title = item['title']
    src = item['url']
    uptime = item['time']
    nfo = item['nfo']
    actors = item['actors']
    cursor.execute('''CREATE TABLE IF NOT EXISTS media(title TEXT, src TEXT, uptime Datetime, nfo TEXT, actors TEXT)''')
    cursor.execute("INSERT INTO articles VALUES (?, ?, ?, ?, ?)",
                   (title, src, uptime, nfo, actors))
    # 提交事务并关闭连接
    conn.commit()
    conn.close()
