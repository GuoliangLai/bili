import time

from flask import Flask, render_template, request, redirect, url_for
import configparser
from flask import render_template_string
from main import *
import asyncio
import aiohttp
import threading
from flask import Flask, request, redirect, url_for, render_template, make_response
from flask_socketio import SocketIO
import sys
from simple_logger import red_logs
import sqlite3
import datetime

app = Flask(__name__, static_folder='./templates/ui/static')

line_number = [0]  # 存放当前日志行数
quality_dic = {'8k': '127', '4k': '125', '1080p 60': '116', '1080p': '112', '1080p high': '112', '720p 60': '74',
               '480p': '32', '360p': '16'}


def run_subscribe():
    log.info("开始订阅！！")
    get_user_list()
    start_subscribe_follow_users_up()


run_flag = False


def schedule_thread(get_time):
    log.info('按照时间每隔%dh进行订阅', int(get_time))
    if run_flag:
        log.info('订阅线程已启动。')
        return 0
    # 创建一个线程
    # 循环执行线程
    while True:
        sub_thread = threading.Thread(target=run_subscribe)
        # 执行线程
        sub_thread.start()
        # 等待线程执行完毕
        sub_thread.join()
        log.info('订阅线程结束！！')
        print("线程执行完毕")
        # 等待两个小时
        time.sleep(int(get_time) * 60 * 60)


# 定义接口把处理日志并返回到前端
@app.route('/get_log', methods=['GET', 'POST'])
def get_log():
    log_data = red_logs('./log.log')  # 获取日志
    # 判断如果此次获取日志行数减去上一次获取日志行数大于0，代表获取到新的日志
    if len(log_data) - line_number[0] > 0:
        log_type = 2  # 当前获取到日志
        log_difference = len(log_data) - line_number[0]  # 计算获取到少行新日志
        log_list = []  # 存放获取到的新日志
        # 遍历获取到的新日志存放到log_list中
        for i in range(log_difference):
            log_i = log_data[-(i + 1)].decode('utf-8')  # 遍历每一条日志并解码
            log_list.insert(0, log_i)  # 将获取的日志存放log_list中
    else:
        log_type = 3
        log_list = ''
    # 已字典形式返回前端
    _log = {
        'log_type': log_type,
        'log_list': log_list
    }
    line_number.pop()  # 删除上一次获取行数
    line_number.append(len(log_data))  # 添加此次获取行数
    return _log


@app.route('/')
def index():
    return render_template('./ui/login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    name = request.form.get('user')
    pwd = request.form.get('pwd')
    remember_me = request.form.get('remember_me')

    config = configparser.RawConfigParser()
    # 读取配置文件
    config.read('./config/config.ini', encoding='utf-8')
    # 获取配置文件中的值
    dir = config['base_cfg']['dir']
    quality = config['base_cfg']['quality']
    cookie = config['base_cfg']['cookie']
    user_id = config['base_cfg']['user_id']
    attention_day = config['base_cfg']['attention_day']
    get_time = config['base_cfg']['get_time']
    form_data = {
        'cookie': cookie,
        'user_id': user_id,
        'dir': dir,
        'quality': quality,
        'attention_day': attention_day,
        'get_time': get_time
    }
    # 连接到 SQLite 数据库
    conn = sqlite3.connect('./database/media.db')
    # 创建游标对象
    cursor = conn.cursor()
    # 获取今日日期
    today = datetime.date.today()

    # 执行查询
    query = "SELECT DISTINCT title, uptime, actors, src FROM  media WHERE DATE(uptime) = ?"
    cursor.execute(query, (str(today),))

    # 获取查询结果
    results = cursor.fetchall()
    dynamic_items = []
    # 输出结果
    show_length = 1
    single_dic = {'a': 0}
    for row in results:
        if show_length >= 10:
            break
        show_dict = {'image': 'static/image/face/2403047.jpg',
                     'title': 'xxxxdasdasdasd',
                     'time': '2分钟前',
                     'url': '#'}
        if row[2] in single_dic:
            single_dic[row[2]] = single_dic[row[2]] + 1
        else:
            single_dic[row[2]] = 0
        if single_dic[row[2]] >= 1:
            continue
        title = row[0]
        uptime = row[1]
        actors = row[2]
        url = row[3]
        show_dict['image'] = 'static/image/face/' + str(row[2]) + '.jpg'
        img_dir = './templates/ui/static/image/face/' + actors + '.jpg'
        if not os.path.exists(img_dir):
            show_dict['image'] = 'static/image/face/default.webp'
        show_dict['title'] = title[10:]
        show_dict['time'] = str(uptime)
        show_dict['url'] = url
        dynamic_items.append(show_dict)
        print("Title:", title)
        print("Uptime:", uptime)
        print("Actors:", actors)
        print(url)
        print(show_dict['image'])
        show_length = show_length + 1


    if name == "lai" and pwd == '123':
        return render_template('./ui/basic_elements.html', **form_data, dynamic_items=dynamic_items)
    else:
        return render_template('./ui/login.html')


@app.route('/save', methods=['POST'])
def save():
    cookie = request.form['cookie']
    user_id = request.form['user_id']
    dir = request.form['dir']
    quality = request.form['quality']
    attention_day = int(request.form['attention_day'])
    get_time = int(request.form['get_time'])
    print('cookie', cookie, 'user_id', user_id, 'dir', dir, 'quality', quality, 'attention_day', attention_day,
          'get_time', get_time)
    config = configparser.RawConfigParser()
    config.read('./config/config.ini', encoding='utf-8')
    config['base_cfg']['user_id'] = user_id
    config['base_cfg']['cookie'] = cookie
    config['base_cfg']['dir'] = dir
    config['base_cfg']['quality'] = quality
    config['base_cfg']['attention_day'] = str(attention_day)
    config['base_cfg']['get_time'] = str(get_time)
    # 打开INI文件并写入键值对
    with open('./config/config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    thread = threading.Thread(target=run_subscribe)
    thread.start()

    # Start the operation asynchronously
    # asyncio.create_task(make_async_request(attention_day))
    return redirect(url_for('index'))


@app.route('/api/save', methods=['GET', 'POST'])
def get_data():
    # 获取请求头信息
    Sessdata = request.headers.get('Sessdata')
    userId = request.headers.get('userId')
    filePath = request.headers.get('filePath')
    videoQuality = request.headers.get('videoQuality')
    attentionDay = request.headers.get('attentionDay')
    subscribeInterval = request.headers.get('subscribeInterval')
    print('cookie', Sessdata, 'user_id', userId, 'dir', filePath, 'quality', quality_dic[videoQuality], 'attention_day',
          attentionDay, 'get_time', subscribeInterval)
    config = configparser.RawConfigParser()
    config.read('./config/config.ini', encoding='utf-8')
    config['base_cfg']['user_id'] = userId
    config['base_cfg']['cookie'] = Sessdata
    config['base_cfg']['dir'] = filePath
    config['base_cfg']['quality'] = quality_dic[videoQuality]
    config['base_cfg']['attention_day'] = str(attentionDay)
    config['base_cfg']['get_time'] = str(subscribeInterval)
    # 打开INI文件并写入键值对
    with open('./config/config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    sc_thread = threading.Thread(target=schedule_thread, args=subscribeInterval)
    sc_thread.start()
    run_flag = True
    return 'Response'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=722)
