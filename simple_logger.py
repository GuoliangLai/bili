import logging
import os


class logging_:
    def __init__(self, path, delete=True):
        self.path = path  # 日志文件存放位置
        name = 'log.log'  # 日志文件名称
        self.log_ = self.path  # 进入文件目录
        if delete == True:
            open(path, "w").close  # 为True时清空文本
        # 创建一个日志处理器
        self.logger = logging.getLogger('logger')
        # 设置日志等级，低于设置等级的日志被丢弃
        self.logger.setLevel(logging.DEBUG)
        # 设置输出日志格式
        self.fmt = logging.Formatter("[%(asctime)s] - %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        # 创建一个文件处理器
        self.fh = logging.FileHandler(self.log_, encoding='utf-8')
        # 设置文件输出格式
        self.fh.setFormatter(self.fmt)
        # 将文件处理器添加到日志处理器中
        self.logger.addHandler(self.fh)
        # 创建一个控制台处理器
        self.sh = logging.StreamHandler()
        # 设置控制台输出格式
        self.sh.setFormatter(self.fmt)
        # 将控制台处理器添加到日志处理器中
        self.logger.addHandler(self.sh)
        # 关闭文件
        self.fh.close()


def red_logs(log_path):
    with open(log_path, 'rb') as f:
        log_size = os.path.getsize(log_path)  # 获取日志大小
        offset = -100
        # 如果文件大小为0时返回空
        if log_size == 0:
            return ''
        while True:
            # 判断offset是否大于文件字节数,是则读取所有行,并返回
            if (abs(offset) >= log_size):
                f.seek(-log_size, 2)
                data = f.readlines()
                return data
            # 游标移动倒数的字节数位置
            data = f.readlines()
            # 判断读取到的行数，如果大于1则返回最后一行，否则扩大offset
            if (len(data) > 1):
                return data
            else:
                offset *= 2


# 使用
if __name__ == '__main__':
    logging = logging_('./log.log').logger  # 实例化封装类
    logging.info('1111%s', 'asdsadas')
    logging.debug('2222')
    logging.error('33333')
    logging.warning('44444')
