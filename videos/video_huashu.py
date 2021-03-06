# -*- coding: utf-8 -*-
#!/usr/bin/env python
#抓取华数搜索结果
import sys
import time
import requests
from pandas import Series, DataFrame

reload(sys)
sys.setdefaultencoding("utf-8")

from bs4 import BeautifulSoup as bs
import pandas as pd
from pandas import Series, DataFrame
from video_base import *

class HuashuVideo(BaseVideo):
    def __init__(self):
        BaseVideo.__init__(self)
        self.engine = '华数'
        self.site = 'huashu'
        self.pre_url = "http://www.wasu.cn"
        self.album_url = 'http://www.wasu.cn/Search/show/k/key/type/album' #专辑的url
        self.general_url = 'http://www.wasu.cn/Search/show/k/key/duration/tid?&p=pid#Top05' #普通搜索的url
        self.filePath = 'huashu_video'

        self.timelengthDict = {0:'不限', 1:'0-10分钟', 2:'10-30分钟', 3:'30-60分钟', 4:'60分钟以上'} #时长类型对应网页中的按钮文字

        #self.infoLogger = Logger(logname=dir_log+'info_huashu(' + GetNowDate()+ ').log', logger='I')
        #self.errorLogger = Logger(logname=dir_log+'error_huashu(' + GetNowDate()+ ').log', logger='E')

    @fn_timer_
    def run(self, keys):

        cf = ConfigParser.ConfigParser()
        cf.read(config_file_path)
        lengthtypes = cf.get("huashu","lengthtype")
        if len(lengthtypes.strip('[').strip(']')) == 0:
            print encode_wrap('配置为不运行')
            return

        start_time = GetNowTime()
        self.run_keys_multithreading(keys)

        #重试运行三次
        # for _ in range(0, 3):
        #     self.run_unfinished_keys(keys, start_time)


    def search(self, key):

        items_all = []

        # 专辑
        album_url = self.album_url.replace('key',key)
        r = requests.get(album_url)
        items = self.parse_data_album(r.text, key)
        items_all.extend(items)

        # 普通
        cf = ConfigParser.ConfigParser()
        cf.read(config_file_path)
        lengthtypes = cf.get("huashu","lengthtype")
        lengthtypes = lengthtypes.strip('[').strip(']').split(',')
        for lengthtype in lengthtypes:

            for i in range(self.pagecount):
                url = self.general_url.replace('tid', lengthtype)
                url = url.replace('pid', str(i+1))
                url = url.replace('key',key)

                #r = requests.get(url)
                r = self.get_requests(url)
                items = self.parse_data(r.text, i+1, lengthtype)

                items_all.extend(items)

        return items_all


    # 专辑
    def parse_data_album(self, text, key):

        items = []

        try:
            soup = bs(text, 'lxml')

            #视频链接-专辑
            sourceList = soup.findAll('div', attrs={'class':'special_item'})
            for source in sourceList:

                try:
                    item = DataItem()

                    div_title = source.find('div',{'class':'s_item_head'})
                    if div_title:
                        item.title = div_title.get_text()

                    a = source.find('a', {'class':'join'})
                    if a:
                        item.href = self.pre_url + a['href']

                    item.page = 1
                    item.durationType = '专辑'
                    items.append(item)
                except Exception,e:
                    errorLogger.logger.error('%s:%s:专辑解析出错' % (self.site, key))

        except Exception, e:
            errorLogger.logger.error('%s:%s:专辑解析出错' % (self.site, key))

        return items

    # 普通
    def parse_data(self, text, page, lengthType):

        items = []

        soup = bs(text, 'lxml')

        #视频链接-全部结果
        source = soup.find('div', {'class':'list_body'})
        dramaList = soup.findAll('a', href=re.compile('^/Play/show/id/'), text=re.compile('.+'))
        for drama in dramaList:

            if not drama.get_text():
                continue

            item = DataItem()

            item.title = drama.get_text()
            item.href = self.pre_url + drama['href']

            item.page = page
            try:
                item.durationType = self.timelengthDict[int(lengthType)]
            except Exception,e:
                print encode_wrap('未找到对应的时长类型!')

            items.append(item)

        return items


if __name__=='__main__':
    #key = raw_input('输入搜索关键字:')

    data = pd.read_excel('keys.xlsx', '华数', index_col=None, na_values=['NA'])
    print data

    youkuVideo = HuashuVideo()
    youkuVideo.run(data['key'].get_values()[:100])

    #key = '快乐大本营'
    #key = urllib.quote(key.decode(sys.stdin.encoding).encode('gbk'))


