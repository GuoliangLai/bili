from biliResource import biliResource
import feedparser
import requests
from media import media_data_path
from datetime import datetime
# 解析RSS订阅的XML文件
import os
import subprocess
import re
import random
import glob
from rss import add_media_item_to_db



class biliDownloader():
    def __init__(self, bili_resource, cookie, dir, quality):
        self.bili_resource = bili_resource
        self.cookie = cookie
        self.dir = dir
        self.quality = quality

    def get_video(self):
        actors = self.bili_resource.get_actors().replace(" ", "").replace("|", "").replace("'", "").replace(":", "").replace("?", "").replace("/", "")#删除空格和|'
        title = self.bili_resource.get_title().replace(" ", "").replace("|", "").replace("'", "").replace(":", "").replace("?", "").replace("/", "")#删除空格和|'
        media_save_path = os.path.join(self.dir, actors)
        media_save_path = os.path.join(media_save_path, title)
        #先检查是否存在该路径，不存在则会递归创建
        os.makedirs(os.path.dirname(media_save_path), exist_ok=True)
        # 使用 glob 模块匹配目录下的所有 .mp4 文件
        mp4_files = glob.glob(os.path.join(media_save_path, '*.mp4'))
        # 提取文件名部分
        file_names = [os.path.basename(file) for file in mp4_files]
        # 打印文件名
        for file_name in file_names:
            file_name = file_name.replace(" ", "").replace("|", "").replace("'", "").replace(":", "").replace("?", "").replace("/", "")#删除空格和|'
            print(file_name)
            if os.path.exists(os.path.join(media_save_path, file_name)):
                print('已下载该视频', file_name, '跳过！')
                return 0
        print(media_save_path)
        pattern = r"^(127|126|125|120|116|112|80|74|64|32|16)$"
        if re.match(pattern, self.quality):
            print("选择清晰度", self.quality)
        else:
            self.quality = "127"
        # 执行系统命令，下载到指定的文件夹中
        url = self.bili_resource.get_src()
        command = 'yutto -c "{}" -q {} -d {} {}'.format(self.cookie, self.quality, media_save_path, url)
        print(command)
        status = subprocess.call(command, shell=True)
        if status == 0:
            print(url, "下载成功！！")
            download_mp4_files = glob.glob(os.path.join(media_save_path, '*.mp4'))
            download_ass_files = glob.glob(os.path.join(media_save_path, '*.ass'))
            download_srt_files = glob.glob(os.path.join(media_save_path, '*.srt'))
            print(download_mp4_files)
            print(download_ass_files)
            print(download_srt_files)
            # 打印文件名
            for download_mp4_file in download_mp4_files:
                rename = os.path.join(media_save_path, self.bili_resource.get_title() + '.mp4')
                os.rename(download_mp4_file, rename)
                print(rename)
            for download_ass_file in download_ass_files:
                rename = os.path.join(media_save_path, self.bili_resource.get_title() + '.ass')
                os.rename(download_ass_file, rename)
                print(rename)
            for download_srt_files in download_ass_files:
                rename = os.path.join(media_save_path, self.bili_resource.get_title() + '.srt')
                os.rename(download_srt_files, rename)
                print(rename)
        else:
            print(url, "下载失败！！")
        subprocess.run(['timeout', '/t', '{}'.format(random.randint(15, 60))], shell=True)  # 以5秒为例，可以根据需要调整等待时间

    def generate_nfo_file(self):
        actors = self.bili_resource.get_actors().replace(" ", "").replace("|", "").replace("'", "").replace(":", "").replace("?", "").replace("/", "")#删除空格和|'
        title = self.bili_resource.get_title().replace(" ", "").replace("|", "").replace("'", "").replace(":", "").replace("?", "").replace("/", "")#删除空格和|'
        nfo_save_path = os.path.join(self.dir, actors)
        nfo_save_path = os.path.join(nfo_save_path, title)
        # 先检查是否存在该路径，不存在则会递归创建
        os.makedirs(os.path.dirname(nfo_save_path), exist_ok=True)
        # 使用 glob 模块匹配目录下的所有 .mp4 文件
        nfo_files = glob.glob(os.path.join(nfo_save_path, '*.nfo'))
        # 提取文件名部分
        file_names = [os.path.basename(file) for file in nfo_files]
        # 打印文件名
        for file_name in file_names:
            file_name = file_name.replace(" ", "").replace("|", "").replace("'", "").replace(":", "").replace("?", "").replace("/", "")  # 删除空格和|'
            print(file_name)
            if os.path.exists(os.path.join(nfo_save_path, file_name)):
                print('已生成过该nfo', file_name, '跳过！')
                return 0
        nfo_save_path = os.path.join(nfo_save_path, self.bili_resource.get_title() + '.nfo')
        print(nfo_save_path)
        with open(nfo_save_path, 'w', encoding='utf-8') as file:
            file.write(self.bili_resource.get_nfo())
        print(nfo_save_path)


