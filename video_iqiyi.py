# -*- coding: utf-8 -*-
#!/usr/bin/env python
#抓取爱奇艺搜索结果
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

class IQiYiVideo(BaseVideo):
    def __init__(self):
        BaseVideo.__init__(self)
        self.engine = '爱奇艺'
        self.album_url = 'http://so.iqiyi.com/so/q_key' #专辑的url
        self.general_url = 'http://so.iqiyi.com/so/q_key_ctg__t_tid_page_pid_p_1_qc_0_rd__site__m_1_bitrate_' #普通搜索的url
        self.filePath = './data/iqiyi_video.xlsx'

    def run(self, keys):

        for key in keys:
            # 初始化
            self.items = []

            #搜索
            self.search(key)

            #过滤
            #self.filter_short_video()

            #创建dataframe
            self.create_data(key)
            break


        #存入excel
        self.data_to_excel()

    def search(self, key):

        # 专辑
        album_url = self.album_url.replace('key',key)
        r = requests.get(album_url)
        self.parse_data_album(r.text)

        print '*'*20, '暂停10s', '*'*20
        print '\n'
        time.sleep(10)


        # 普通
        cf = ConfigParser.ConfigParser()
        cf.read("config.ini")
        lengthtypes = cf.get("iqiyi","lengthtype")
        lengthtypes = lengthtypes.strip('[').strip(']').split(',')
        for lengthtype in lengthtypes:

            for i in range(self.pagecount):
                url = self.general_url.replace('tid', lengthtype)
                url = url.replace('pid', str(i+1))
                url = url.replace('key',key)

                r = requests.get(url)
                self.parse_data(r.text)

                print '\n'
                print '*'*20, '暂停10s, key:%s, Page %d, 时长Type:%s' % (key, i+1, lengthtype), '*'*20
                print '\n'
                time.sleep(10)


    # 专辑
    def parse_data_album(self, text):
        try:
            soup = bs(text)

            #视频链接-专辑
            dramaList = soup.findAll('a', attrs={'class':'album_link'})
            for drama in dramaList:

                item = DataItem()

                print '标题:',drama['title']
                print '链接:',drama['href']
                item.title = drama['title']
                item.href = drama['href']

                self.items.append(item)
        except Exception, e:
                print str(e)


    # 普通
    def parse_data(self, text):
        soup = bs(text)

        #视频链接-全部结果
        dramaList = soup.findAll('a', attrs={'class':'figure  figure-180101 '})
        for drama in dramaList:

            item = DataItem()

            titleAndLink = drama.find('img')
            if titleAndLink:
                print '标题:',titleAndLink['title']
                print '链接:',drama['href']#titleAndLink['href']
                item.title = titleAndLink['title']
                item.href = drama['href']
            durationTag = drama.find('span', attrs={'class':'v_name'})
            if durationTag:
                item.duration = durationTag.text

            self.items.append(item)



if __name__=='__main__':
    #key = raw_input('输入搜索关键字:')

    data = pd.read_excel('keys.xlsx', 'Sheet1', index_col=None, na_values=['NA'])
    print data

    youkuVideo = IQiYiVideo()
    youkuVideo.run(data['key'].get_values())

    #key = '快乐大本营'
    #key = urllib.quote(key.decode(sys.stdin.encoding).encode('gbk'))

