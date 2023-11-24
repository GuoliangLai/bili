from rss import biliRss
from rss import from_resource_get_img
from downloader import biliDownloader
from biliResource import biliResource
from webdav4.client import Client
from datetime import datetime
import configparser
import os
import schedule
import time
import threading
import asyncio
import json
import requests
import threading



def start_download_with_config_url():
    # 创建一个配置文件解析器对象
    config = configparser.RawConfigParser()

    # 读取配置文件
    config.read('./config/config.ini', encoding='utf-8')

    # 获取配置文件中的值
    cookie = config['base_cfg']['cookie']
    bili_rss = config['base_cfg']['bili_rss']
    dir = config['base_cfg']['dir']
    quality = config['base_cfg']['quality']
    up_name = config['base_cfg']['up']
    rss_link = biliRss(bili_rss, up_name)
    rss_link.parse_res()
    resource_list = rss_link.get_resource_list()
    try:
        from_resource_get_img(resource_list, dir)
    except Exception:
        print('下载封面片出错')
    index = 0
    for resource in resource_list:
        bili_resource = biliResource(resource['title'], resource['url'], resource['time'], resource['nfo'],
                                     resource['actors'])
        cookie = config['base_cfg']['cookie']
        bili_downloader = biliDownloader(bili_resource, cookie, dir, quality)
        index = index + 1
        try:
            bili_downloader.get_video()
        except Exception:
            print('下载', resource['title'], '出错')
            # 下载失败将从数据库中删除该条目
            bili_resource.remove_item_from_media_db_with_title(resource['title'])


def start_daily_download_with_up_id(up_name, up_id, attention_day=1):
    # 创建一个配置文件解析器对象
    config = configparser.RawConfigParser()
    # 读取配置文件
    config.read('./config/config.ini', encoding='utf-8')
    # 获取配置文件中的值
    bili_rss = 'https://rsshub.guolianghome.xyz/bilibili/user/video/{}'.format(up_id)
    dir = config['base_cfg']['dir']
    quality = config['base_cfg']['quality']
    rss_link = biliRss(bili_rss, up_name)
    rss_link.parse_res()
    resource_list = rss_link.get_resource_list()
    for resource in resource_list:
        current_date = datetime.now()
        up_time = resource['time']
        differ_time = current_date - up_time
        differ_time = differ_time.days
        if differ_time <= attention_day:
            tmp_list = [resource]
            try:
                from_resource_get_img(tmp_list, dir)
            except Exception:
                print(Exception)
                print('下载封面照片出错')
            bili_resource = biliResource(resource['title'], resource['url'], resource['time'], resource['nfo'],
                                         resource['actors'])
            cookie = config['base_cfg']['cookie']
            bili_downloader = biliDownloader(bili_resource, cookie, dir, quality)
            try:
                bili_downloader.generate_nfo_file()
                bili_downloader.get_video()
            except Exception:
                print(Exception)
                print('下载', resource['title'], '出错')
                # 下载失败将从数据库中删除该条目
                bili_resource.remove_item_from_media_db_with_title(resource['title'])
        # else:
        #     print(resource['title'], '视频未在设定时间：', attention_day, '天内，不下载！')


def start_subscribe_follow_users_up(attention_day=1):
    # 创建一个 ConfigParser 对象
    up_config = configparser.ConfigParser()
    # 读取文件
    up_config.read('./config/user.ini', encoding='utf-8')
    # 获取所有的 section
    sections = up_config.sections()
    # 创建一个空字典用于存储数据
    # 遍历每个 section
    for section in sections:
        # 获取 section 下的所有选项和值
        options = up_config.options(section)
        length = len(options) // 2
        for i in range(2, length):
            up_name = up_config[section]['user' + str(i)]
            up_id = up_config[section]['mid' + str(i)]
            print(up_name, ',', up_id)
            start_daily_download_with_up_id(up_name, up_id, attention_day)
    # 打印数据字典


# attention_day为设置只下载距离当前日期几天内的视频
def start_update_download(attention_day=1):
    # 创建一个配置文件解析器对象
    config = configparser.RawConfigParser()

    # 读取配置文件
    config.read('./config/config.ini', encoding='utf-8')
    current_date = datetime.now()
    # 获取配置文件中的值
    bili_rss = config['base_cfg']['bili_rss']
    dir = config['base_cfg']['dir']
    quality = config['base_cfg']['quality']
    up_name = config['base_cfg']['up']
    rss_link = biliRss(bili_rss, up_name)
    rss_link.parse_res()
    resource_list = rss_link.get_resource_list()
    for resource in resource_list:
        up_time = resource['time']
        differ_time = current_date - up_time
        differ_time = differ_time.days
        if differ_time <= attention_day:
            try:
                from_resource_get_img(resource, dir)
            except Exception:
                print('下载封面片出错')
            bili_resource = biliResource(resource['title'], resource['url'], resource['time'], resource['nfo'],
                                         resource['actors'])
            cookie = config['base_cfg']['cookie']
            bili_downloader = biliDownloader(bili_resource, cookie, dir, quality)
            try:
                bili_downloader.get_video()
            except Exception:
                print('下载', resource['title'], '出错')
                # 下载失败将从数据库中删除该条目
                bili_resource.remove_item_from_media_db_with_title(resource['title'])
        else:
            print(resource['title'], '视频未在设定时间：', attention_day, '天内，不下载！')


async def upload_local_dir_to_webdav():
    config = configparser.RawConfigParser()
    # 读取配置文件
    config.read('./config/config.ini', encoding='utf-8')
    # 获取配置文件中的值
    local_folder = config['web_dav']['local_folder']
    remote_folder = config['web_dav']['remote_folder']
    webdav_url = config['web_dav']['webdav_url']
    username = config['web_dav']['username']
    password = config['web_dav']['password']
    # 创建 WebDAV 客户端
    client = Client(base_url=webdav_url, auth=(username, password))
    client.ls("", detail=False)
    # 递归上传文件夹及其内容
    for root, dirs, files in os.walk(local_folder):
        # 创建远程文件夹
        remote_path = os.path.join(remote_folder, os.path.relpath(root, local_folder))
        remote_path = remote_path.replace('\\', '/')
        print('remote_path:', remote_path)
        client.mkdir(remote_path)

        # 上传文件
        for file in files:
            local_path = os.path.join(root, file)
            remote_path = os.path.join(remote_folder, os.path.relpath(local_path, local_folder))
            remote_path = remote_path.replace('\\', '/')
            print('local_path:', local_path, 'remote_path', remote_path)
            client.upload_file(from_path=local_path, to_path=remote_path)

    print("文件夹上传完成")


async def schedule_job():
    date_length = 2
    while True:
        await asyncio.sleep(60)  # 每隔 60 秒执行一次
        await start_update_download(date_length)


def get_user_list():
    config = configparser.RawConfigParser()
    user_config = configparser.RawConfigParser()
    # 读取配置文件
    config.read('./config/config.ini', encoding='utf-8')
    # 获取配置文件中的值
    user_id = config['base_cfg']['user_id']
    cookie = config['base_cfg']['cookie']
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        # 'Cookie' : "buvid3=585F0101-1550-21AA-8718-7083AC3187D800634infoc; i-wanna-go-back=-1; _uuid=BD15D439-6A10E-B5AB-FB98-31C6710E399E701029infoc; FEED_LIVE_VERSION=V8; DedeUserID=110733082; DedeUserID__ckMd5=c3d1c2455fc66dca; header_theme_version=CLOSE; rpdid=|(u)mmYkuYmm0J\"uY)llJ|J~J; buvid_fp_plain=undefined; LIVE_BUVID=AUTO1016869948257729; b_nut=1689995196; is-2022-channel=1; b_ut=5; hit-new-style-dyn=1; hit-dyn-v2=1; buvid4=C830D299-E316-CB53-9E74-DA6C997398DC02356-023053118-KDrPtUOg+Krl4Ze6Y8KACw%3D%3D; fingerprint=e1d948067fe32241f2cb7796d645e96c; buvid_fp=ea40f3f5fb51714869ade4cabfc41aa1; enable_web_push=DISABLE; CURRENT_BLACKGAP=0; CURRENT_FNVAL=4048; CURRENT_QUALITY=120; PVID=1; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDA3NDk0MTAsImlhdCI6MTcwMDQ5MDE1MCwicGx0IjotMX0.30GKg3zqfOH-vbv0zHWkQwAqKOOk-COah_zcxfyeK-8; bili_ticket_expires=1700749350; SESSDATA=37201990%2C1716044394%2C05e99%2Ab2CjA_fcEjZBEpruLPRnlV8UIM5wRS0syfdkCqrz72DHlsakOeJaeSMNtlR2v050GJ3mASVkg1NE1nYXhOTHhXeG9FNU5ycW94LWk4ZDVGc3N4bzVRQWkxQ2pqdXE0ajBsMGc3U09sSjNVSGdVQTdjLU9NVmRrbjhESDVVWTFta1FzOV94cWoxdmxnIIEC; bili_jct=a7ed49f68388c12722f39db796a5a7c0; home_feed_column=5; browser_resolution=1632-888; sid=4y5mku4c; bp_article_offset_110733082=866305765579685908; bp_video_offset_110733082=866452988469706770; b_lsid=1101E9CDC_18BF2602C87"
    }
    cookies = {
        "SESSDATA": cookie + ";"
    }
    user_api_url = 'https://api.bilibili.com/x/relation/followings?vmid={}&pn=1&ps=50&order=desc&order_type=attention'.format(
        user_id)
    response = requests.get(user_api_url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        print("GET ERROR!")
        return 0
    user_list_response = response.text
    # 解析 JSON 数据
    parsed_data = json.loads(user_list_response)

    # 获取 list
    data_list = parsed_data['data']['list']
    user_list = []
    # 遍历 list 中的每个元素
    index = 1
    user_config[user_id] = {
        'user1': '',
        'mid1': '',
    }
    for item in data_list:
        uname = item['uname']
        mid = item['mid']
        item = {"name": uname, "mid": mid}
        user_list.append(item)
        user_uname = 'user' + str(index)
        up_id = 'mid' + str(index)
        user_config[user_id][user_uname] = str(uname)
        user_config[user_id][up_id] = str(mid)
        index = index + 1
        print("uname:", uname)
        print("mid:", mid)
        print()  # 打印空行，用于分隔不同元素的输出
    with open('./config/user.ini', 'w', encoding='utf-8') as configfile:
        user_config.write(configfile)
    return user_list


def run_sub(cancel_flag=False):
    config = configparser.RawConfigParser()
    # 读取配置文件
    config.read('./config/config.ini', encoding='utf-8')
    # 获取配置文件中的值
    attention_day = int(config['base_cfg']['attention_day'])
    get_time = int(config['base_cfg']['get_time'])
    print("开始订阅！！", 'attention_day', attention_day, 'get_time', get_time)
    start_subscribe_follow_users_up(attention_day)
    timer = threading.Timer(get_time * 60, run_sub)
    timer.start()
    if cancel_flag:
        timer.cancel()  # 取消定时器的执行
    print("订阅完成！！")

if __name__ == '__main__':
    run_sub()
