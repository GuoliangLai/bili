from biliResource import biliResource
import feedparser
import requests
from media import media_data_path
from datetime import datetime
# 解析RSS订阅的XML文件
import os
import sqlite3



class biliRss():
    def __init__(self, rss, actors):
        self.rss = rss
        self.actors = actors
        self.resource_list = []

    def parse_res(self):
        feed = feedparser.parse(self.rss)
        # 检查是否成功解析
        if feed.bozo == 0:
            print(self.rss, "解析成功")
        else:
            print(self.rss, "解析失败")
        # 输出标题和链接
        for entry in feed.entries:
            # print("标题:", entry.title)
            # print("链接:", entry.link)
            # print("时间:", entry.published)
            nfo = entry.summary.split("<br />")[0]
            img_url_start_index = entry.summary.find('http://')
            img_url_end_index = entry.summary.find('.jpg') + len('.jpg')
            img_url = entry.summary[img_url_start_index:img_url_end_index]
            # 记录视频标题、链接、时间、简介、图像链接
            datetime_obj = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
            title_date = datetime_obj.date().strftime("%Y-%m-%d")
            video_resource = {'title': 'none', 'url': 'none', 'time': '1970-01-01', 'nfo': 'none', 'img_url': 'none', 'actors': 'none'}
            video_resource['title'] = title_date + entry.title.replace(" ", "").replace("|", "").replace("'", "").replace(":", "").replace("?", "").replace("/", "")#删除空格和|'
            video_resource['url'] = entry.link
            video_resource['time'] = datetime_obj
            video_resource['nfo'] = nfo
            video_resource['img_url'] = img_url
            video_resource['actors'] = self.actors
            self.resource_list.append(video_resource)
            # print("简介:", nfo)
            # print("图像链接:", img_url)

    def get_resource_list(self):
        return self.resource_list



def from_resource_get_img(resource_list, base_path):
    if len(resource_list) <= 0:
        print("无资源列表，不下载任何图像！")
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
        #先检查是否存在该路径，不存在则会递归创建
        os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
        print(image_save_path)
        # 检查请求是否成功
        print(filename)
        # 发送HTTP请求获取图片内容
        response = requests.get(img_url, headers=headers)
        if response.status_code == 200:
            # 将图片内容保存到文件
            with open(image_save_path, 'wb') as file:
                file.write(response.content)
            print(filename, '图片下载成功:', filename)
        else:
            print(filename, '图片下载失败')

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