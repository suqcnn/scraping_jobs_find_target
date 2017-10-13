#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import time
from bs4 import BeautifulSoup
from scraping_jobs_app.models import *
import datetime

# 智联招聘的搜索接口
zl_interface = 'http://sou.zhaopin.com/jobs/searchresult.ashx'


def get_html_text(page=1, **kwargs):
    """
    根据接口拼装的URL下载网页

    :param page: 当前页码
    :param jl: 地址位置
    :param sm: 视图模式 0:简略 1:详细
    :return: response对象
    """
    try:
        # 模拟浏览器的header
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://www.baidu.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        }

        params = kwargs
        params['p'] = page
        params['jl'] = kwargs['jl'] if 'jl' in kwargs else '南京'  # 地理位置
        params['sm'] = kwargs['sm'] if 'sm' in kwargs else '1'  # 默认搜索视图为详细模式
        print(params)

        r = requests.get(zl_interface, timeout=30, headers=headers, params=params)
        r.raise_for_status()  # 如果状态不是200，引发HTTPError异常
        r.encoding = r.apparent_encoding  # 根据内容猜测的编码
        print('已下载网页【%s】' % r.request.url)
        return r.text
    except Exception as e:
        raise e


def get_job_items():
    """
    用BeautifulSoup4抓取职位条目

    :return:
    """
    # 当前页码
    crt_page = 0
    # 条目计数
    item_cnt = 0
    while True:
        crt_page += 1
        soup = BeautifulSoup(get_html_text(crt_page, kw='紫东创意园'), "lxml")
        job_list = soup.find('div', attrs={'id': 'newlist_list_content_table'})
        print(len(job_list))
        # 无内容时候退出循环
        if len(job_list) == 1:
            break
        jobs = job_list.find_all('div', attrs={'class', 'newlist_detail newlist'})
        for job in jobs:
            # 职位名称
            job_name = job.find('li', attrs={'class', 'newlist_deatil_first clearfix zwmc'}).div.a.text
            # 公司名称
            co_name = job.find('li', attrs={'class', 'newlist_deatil_three gsmc'}).a.text
            # 公司链接（二级页面）
            co_link = job.find('li', attrs={'class', 'newlist_deatil_three gsmc'}).a['href']
            # 不确定数目的项目（包括地点、公司性质、公司规模等，需要单独处理）
            uncertain_items = job.find('li', attrs={'class', 'newlist_deatil_two'}).find_all('span')
            result = filter_uncertain_items(uncertain_items)
            # 岗位职责
            duty = job.find('li', attrs={'class', 'newlist_deatil_last'}).text

            # 将爬取的数据存入数据库
            j = Job()
            j.job_name = job_name
            j.co_name = co_name
            j.co_link = co_link
            j.duty = duty

            if result.get('co_type'):
                j.co_type = result['co_type']
            if result.get('co_scale'):
                j.co_scale = result['co_scale']
            if result.get('job_experience'):
                j.job_experience = result['job_experience']
            if result.get('education'):
                j.education = result['education']
            if result.get('salary'):
                j.salary = result['salary']

            j.save()
            item_cnt += 1
            print('【%s】的"%s"职位已保存' % (co_name, job_name))

    record = ScrapingRecord()
    record.total = item_cnt
    record.save()
    print('爬虫记录已保存')
    # 写入线程记录
    ProcessRecord.objects.filter(process='crawl').update(is_started=False)
    print('线程记录已更改')


def filter_uncertain_items(items):
    """
    根据不确定列表筛选已知的项目

    :param items:
    :return:
    """
    known_items = dict()
    known_list = {'地点': 'job_location', '公司性质': 'co_type',
                  '经验': 'job_experience', '公司规模': 'co_scale',
                  '学历': 'education',
                  '职位月薪': 'salary'}
    for i in items:
        item = i.text
        for j in known_list:
            if j in item:
                index = item.find('：')
                known_items[known_list[j]] = item[index + 1:]
    return known_items


def already_scraped():
    """
    检查今天是否执行过爬虫
    :return:
    """
    cdt_today = datetime.date.today().__str__()
    result = ScrapingRecord.objects.filter(scraping_date__range=[cdt_today + u' 0:00:00', cdt_today + u' 23:59:59'])
    if result:
        return True
    return False


def crawl_timing_process():
    """
    用定时执行爬虫的进程
    :return:
    """
    while True:
        print('daemon运行中...')
        if already_scraped():
            print('今天已经执行过爬虫...')
        else:
            print('开始执行爬虫')
            get_job_items()
            print('爬虫执行完毕')
        time.sleep(1)


def daemon_is_running():
    """
    判断爬虫进程是否已经执行
    :return:
    """
    p = ProcessRecord.objects.get(process='crawl')
    return p.is_started
