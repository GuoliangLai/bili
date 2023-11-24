from flask import Flask, render_template, request, redirect, url_for
import configparser
from flask import render_template_string
from main import *
app = Flask(__name__)


@app.route('/')
def index():
    config = configparser.RawConfigParser()

    # 读取配置文件
    config.read('./config/config.ini', encoding='utf-8')
    # 获取配置文件中的值
    dir = config['base_cfg']['dir']
    quality = config['base_cfg']['quality']
    cookie = config['base_cfg']['cookie']
    user_id = config['base_cfg']['user_id']
    form_data = {
        'cookie': cookie,
        'user_id': user_id,
        'dir': dir,
        'quality': quality,
        'attention_day': 1,
        'get_time': 2
    }
    return render_template('index1.html', **form_data)


@app.route('/save', methods=['POST'])
def save():
    cookie = request.form['cookie']
    user_id = request.form['user_id']
    dir = request.form['dir']
    quality = request.form['quality']
    attention_day = int(request.form['attention_day'])
    get_time = int(request.form['get_time'])
    print('cookie', cookie, 'user_id', user_id, 'dir', dir, 'quality', quality, 'attention_day', attention_day, 'get_time', get_time)
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
    print("开始订阅！！")
    get_user_list()
    run_sub()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=722)
