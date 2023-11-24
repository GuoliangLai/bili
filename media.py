import sqlite3
import datetime
media_data_path = './database/media.db'

def generate_nfo_xml(title, src, uptime, nfo, actors):
    nfo_content = f'''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<movie>
  <plot><![CDATA[{nfo}]]></plot>
  <outline><![CDATA[发行日期 {uptime}]]></outline>
  <customrating>{actors}</customrating>
  <lockdata>false</lockdata>
  <dateadded> {uptime}</dateadded>
  <title>{title}</title>
  <actor>
    <name>{actors}</name>
    <type>Actor</type>
  </actor>
  <director>{actors}</director>
  <premiered>{uptime}</premiered>
  <releasedate>{uptime}</releasedate>
  <tagline>发行日期 {uptime}</tagline>
  <genre>{actors}</genre>
  <website>{src}</website>
</movie>
        '''
    return nfo_content


class baseMedia:
    # 媒体由基本的三部分组成，即媒体标题、媒体的资源文件（可能是文件也可能是链接，也可能是路径）、媒体的nfo内容（媒体简介）
    def __init__(self, title, src, uptime, nfo, actors):
        self.title = title
        self.src = src
        self.uptime = uptime
        self.nfo = generate_nfo_xml(title, src, uptime, nfo, actors)
        self.actors = actors
        conn = sqlite3.connect('./database/media.db')
        # 创建一个游标对象，用于执行SQL语句
        cursor = conn.cursor()
        # 创建一个表格
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS media(title TEXT, src TEXT, uptime Datetime, nfo TEXT, actors TEXT)''')
        cursor.execute("INSERT INTO media VALUES (?, ?, ?, ?, ?)",
                       (self.title, self.src, self.uptime, self.nfo, self.actors))
        # 提交事务并关闭连接
        conn.commit()
        conn.close()

    def get_title(self):
        return self.title

    def get_src(self):
        return self.src

    def get_nfo(self):
        return self.nfo

    def get_time(self):
        return self.uptime

    def get_actors(self):
        return self.actors

    def form_title_get_src(self, title):
        # 连接到数据库
        conn = sqlite3.connect('./database/media.db')
        cursor = conn.cursor()

        # 执行SELECT语句
        cursor.execute("SELECT src FROM media WHERE title = ?", (title,))

        # 获取所有匹配的数据
        rows = cursor.fetchall()
        result = ""
        # 遍历结果并打印
        for row in rows:
            title, src, time, summary = row
            result = src
            print("标题:", title)
            print("文件路径:", src)
            print("时间:", time)
            print("简介:", summary)
            print()
        # 关闭连接
        conn.close()
        return result

    def from_src_get_title(self, src):
        # 连接到数据库
        conn = sqlite3.connect('./database/media.db')
        cursor = conn.cursor()

        # 执行SELECT语句
        cursor.execute("SELECT title FROM media WHERE src = ?", (src,))

        # 获取所有匹配的数据
        rows = cursor.fetchall()
        result = ""
        # 遍历结果并打印
        for row in rows:
            title, src, time, summary = row
            result = title
            print("标题:", title)
            print("文件路径:", src)
            print("时间:", time)
            print("简介:", summary)
            print()
        # 关闭连接
        conn.close()
        return result

    def from_title_get_media_is_saved(self, title):
        # 连接到数据库
        conn = sqlite3.connect('./database/media.db')
        cursor = conn.cursor()
        # 执行SELECT语句
        cursor.execute("SELECT * FROM media WHERE title = ?", (title,))

        # 获取查询结果
        result = cursor.fetchone()
        # 关闭数据库连接
        conn.close()
        # 检查结果是否存在
        if result is not None:
            print("数据已存在")
            return False
        else:
            print("数据不存在")
            return True

    def remove_item_from_media_db_with_title(self, title):
        conn = sqlite3.connect('./database/media.db')
        # 创建一个游标对象，用于执行SQL语句
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM media WHERE title = ?",
                       (title,))
        result = cursor.fetchone()
        if result:
            # 数据存在，执行删除操作
            cursor.execute("DELETE FROM media WHERE title = ?", (title,))
            conn.commit()
            print("数据已删除")
        else:
            # 数据不存在
            print("数据不存在")
        # 提交事务并关闭连接
        conn.commit()
        conn.close()
