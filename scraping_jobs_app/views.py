#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Thread
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from scraping_jobs_app.crawl import *
import scraping_jobs_app.filter as f

p = None


def index(request):
    """
    进入主页
    :param request:
    :return:
    """
    return render(request, 'list.html')


def start_crawl(request):
    """
    开启爬虫进程
    :param request:
    :return:
    """
    if daemon_is_running():
        return JsonResponse({'mess': '爬虫进程不能重复启动!'})
    elif already_scraped():
        return JsonResponse({'mess': '今日已执行过爬虫!'})
    else:
        global p
        Thread(target=crawl_timing_process).start()
        ProcessRecord.objects.filter(process='crawl').update(is_started=True)
        print('爬虫进程启动...')
        return JsonResponse({'mess': '爬虫进程已经启动'})


def reset_thread_status(request):
    """
    强制恢复线程状态
    :param request:
    :return:
    """
    ProcessRecord.objects.filter(process='crawl').update(is_started=False)
    cdt_today = datetime.date.today().__str__()
    ScrapingRecord.objects.filter(scraping_date__range=[cdt_today + u' 0:00:00', cdt_today + u' 23:59:59']).delete()
    return JsonResponse({'mess': '线程和记录已重置！'})


def filter_job(request):
    """
    根据关键字列表查询职位
    :param request:
    :return:
    """
    if 'keywords' in request.GET:
        origin = request.GET['keywords']
        keywords = origin.split(',')
        r = f.filter_job(keywords)
        return render(request, 'list.html', {'list': r})
