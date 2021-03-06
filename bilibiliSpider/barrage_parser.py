#!/usr/bin/env python 
# -*- coding:utf-8 -*-
'''
获取弹幕的模块。
1.根据视频地址中的#link2获取到视频的oid
2.根据这个oid获取弹幕的url
3.据此url进行爬取
'''
import os
import time
import re

import jieba
from lxml import etree
import requests
from wordcloud import WordCloud

# 根据av号获取弹幕
class Barrage_parser(object):
    def __init__(self):
        self.headers_content = {
            'Host': 'api.bilibili.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': '_uuid=1967957A-B14A-5DE9-D441-41A92ED1AB2677559infoc; buvid3=481164A8-7E71-4AA7-87EA-CA73EF70C7DA40775infoc; LIVE_BUVID=AUTO5115561659814664; sid=cattb7cv; DedeUserID=13271717; DedeUserID__ckMd5=1f5367f5a29d5cb4; SESSDATA=d2bc012d%2C1558758034%2Cbc1be341; bili_jct=5957a9e9f713185654a6e10305ed7a2b; fts=1556166036; CURRENT_FNVAL=16; UM_distinctid=16a53a3f6514c4-069dcf04f8b778-f353163-130980-16a53a3f652621; rpdid=|(YuJ~m~|km0J\'ullYu)u~Ju; stardustvideo=-1; _dfcaptcha=506677d4de56c186778ba95c24d21756; bp_t_offset_13271717=256704517340171097'
        }
        self.headers_xml = {
            'Host': 'api.bilibili.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': '_uuid=1967957A-B14A-5DE9-D441-41A92ED1AB2677559infoc; buvid3=481164A8-7E71-4AA7-87EA-CA73EF70C7DA40775infoc; LIVE_BUVID=AUTO5115561659814664; sid=cattb7cv; DedeUserID=13271717; DedeUserID__ckMd5=1f5367f5a29d5cb4; SESSDATA=d2bc012d%2C1558758034%2Cbc1be341; bili_jct=5957a9e9f713185654a6e10305ed7a2b; fts=1556166036; CURRENT_FNVAL=16; UM_distinctid=16a53a3f6514c4-069dcf04f8b778-f353163-130980-16a53a3f652621; rpdid=|(YuJ~m~|km0J\'ullYu)u~Ju; stardustvideo=-1; _dfcaptcha=506677d4de56c186778ba95c24d21756; bp_t_offset_13271717=256704517340171097'
        }
        self.headers_videopage = {
            'Host': 'www.bilibili.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cookie': 'fts=1508229812; pgv_pvi=7374468096; rpdid=oqqwsmxwqpdoswqiilmqw; LIVE_BUVID=2988c862a6b9d72a34c05e964228b6bb; LIVE_BUVID__ckMd5=d11b8d00613fdb72; im_notify_type_13271717=2; sid=7etdt55i; UM_distinctid=1669ae067512bb-028802226e476e-8383268-144000-1669ae067524cc; _uuid=9797E404-709C-2013-055F-4E300C6854A405039infoc; CURRENT_QUALITY=80; CURRENT_FNVAL=16; stardustvideo=-1; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1546704889,1546777512,1549280995; arrange=matrix; DedeUserID=13271717; DedeUserID__ckMd5=1f5367f5a29d5cb4; SESSDATA=d2d20cb4%2C1553782962%2Cabc9c221; bili_jct=c10b992cadf74d778ed51d07e36c99ca; buvid3=71B33620-4962-4564-AD05-F8CED0AFA73447161infoc; _dfcaptcha=fa5b271726a7f59603b02bdfb18ef722; bp_t_offset_13271717=228899710812017602'
        }

    ####################################################
    # ** 获取指定x年x月x日的历史弹幕
    ####################################################
    # 历史弹幕文件url的获取需要两个信息：
    #   1.视频的oid，表示要爬取哪个视频
    #   2.日期字符串：yyyy-mm-dd，表示要获取哪天的弹幕
    #
    # 返回的list的元素为长度为2的touple，第一个元素是字符串内容，第二个是弹幕的p属性
    # P.S.查看B站的历史弹幕需要用户登录，这里也不例外
    ####################################################
    def get_history_barrage_by_av(self, av, date):
        # 获取oid
        oid = self.get_oid(av)

        # 构造目标url
        barrage_url = 'https://api.bilibili.com/x/v2/dm/history?type=1&oid=' + oid + '&date=' + date
        print(barrage_url)

        # 通过url下载xml文件到本地
        filepath, isSaturated = self.get_page(barrage_url, av, date)

        if filepath:
            # 通过下载的xml文件获取弹幕和p属性touple列表
            barrages_p = self.xml_parse(filepath)

        print(av+':实际爬取了'+str(len(barrages_p))+'条弹幕。')
        return barrages_p
        #self.count_and_wordcloud(barrages, av)

    ####################################################
    # ** 根据av获取弹幕列表（包括弹幕和弹幕ID）
    ####################################################
    def get_current_barrage_from_av(self, av):
        #print('获取oid...')
        oid = self.get_oid(av)
        if oid:
            # 最近弹幕，保存在一个XML文件中
            barrage_url = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + oid

            #print('下载xml到本地...')
            filepath, isSaturated = self.get_page(barrage_url, av, 'today')
            barrages_p = []
            if filepath:
                print('获取弹幕内容...')
                # get barrage text by xml file
                barrages_p = self.xml_parse(filepath)

            print(av + ':实际爬取了' + str(len(barrages_p)) + '条弹幕。')
            return barrages_p
        else:
            return []

    # 根据av字符串（avxxxxxxx）获取视频网页的oid
    def get_oid(self, av):
        aid = av[2:]     # 截取av的数字部分，作为aid
        src_url = 'https://www.bilibili.com/video/av' + aid
        middle_link = 'https://api.bilibili.com/x/player/pagelist?aid=' + aid
        try:
            time.sleep(0.5)
            #('获取oid页面内容...')
            res = requests.get(middle_link, headers=self.headers_content, timeout=30)
        except Exception as e:
            #print('获取内容失败,%s' % e)
            return False
        else:
            #print('成功')
            if res.status_code == 200:
                pattern = '\"cid\":\d+'
                mat = re.search(pattern, str(res.content, encoding='utf-8'))
                return mat.group(0)[6:]

    # 将oid标识的网页保存为本地xml
    def get_page(self, oid_url, av, time_str):
        try:
            time.sleep(0.5)
            response = requests.get(oid_url, headers=self.headers_xml, timeout=30)
        except Exception as e:
            print('获取xml内容失败, %s' % e)
            return '', False
        else:
            if response.status_code == 200:
                # 保存xml文件
                if not os.path.exists('./xml'): os.mkdir('./xml')

                filepath = './xml/'+av+'_'+time_str+'.xml'
                with open(filepath, 'wb') as f:
                    f.write(response.content)

                barrages_num = len(re.compile(b'</d>').findall(response.content))
                maxlimit = int(re.search(b'\d+', re.search(b'<maxlimit>\d+</maxlimit>', response.content).group(0)).group(0))

                isSaturated = True if barrages_num >= maxlimit else False

                #print(av+'弹幕xml文件('+time_str+')下载成功。原地址：', oid_url)
                return filepath, isSaturated
            else:
                print('打开失败, %s' % oid_url)
                return '', False

    # 将目标xml文件中的弹幕以touple形式保存在list中
    def xml_parse(self, filepath):
        time.sleep(0.5)
        html = etree.parse(filepath, etree.HTMLParser())

        barrage_list = html.xpath('//d//text()')    # 弹幕文本list
        p_list = html.xpath('//d//@p')              # 弹幕p属性list

        # 合并
        barrage_p_list = []          # list内元素为touple，每个代表一条弹幕，包含弹幕文本和弹幕的p属性（unique）
        for i in range(0, len(p_list)): barrage_p_list.append((barrage_list[i], p_list[i]))

        return barrage_p_list

    # 对获取到的弹幕list去重、划分
    def _devide_and_remove(self, barrage_list):
        single_text = []
        redundant_text = []
        redundant_category = set()

        for text in barrage_list:
            if text not in single_text:     # 第一次出现
                single_text.append(text)
            else:                           # 重复的弹幕
                redundant_text.append(text)
                redundant_category.add(text)
        return single_text, redundant_text, redundant_category

    # 弹幕计数和词云合成
    def count_and_wordcloud(self, barrage_list, av):
        single_text, redundant_text, redundant_category = self._devide_and_remove(barrage_list)

        with open('temp.txt', 'w') as fhandle:
            for barrage in redundant_category:
                #print('当前处理弹幕:', barrage)
                amount = redundant_text.count(barrage)
                #fhandle.write(barrage + ':' + str(amount + 1) + '\n')

        stop_words = ['【', '】', ',', '.', '?', '!', '。']
        words = []

        for text in single_text:
            for stop in stop_words:
                text = ''.join(text.split(stop))
            words.append(text)

        words = ''.join(words)
        words = jieba.cut(words)
        words = ''.join(words)

        #img = numpy.array(Image.open('wordCloud.jpg'))

        if len(words) > 30:
            print('构建词云:', words)
            wc = WordCloud(
                font_path='./fonts/microsoft-yahei.ttc',
                background_color='white',
                width=3000,
                height=3000,
                max_words=2000
            )
            wc.generate(words)
            print('写入文件...')
            filename = './wordcloud/av'+av+'.jpg'
            wc.to_file(filename)

            print('完毕。')
            print('==============')
        else:
            print('av'+av+'弹幕太少了(不足30个)，下一个。')

# if __name__ == '__main__':
#     print(Barrage_parser().get_history_barrage_by_av('av15900788', '2019-04-11'))