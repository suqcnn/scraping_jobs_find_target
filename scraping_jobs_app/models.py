#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
import uuid


class Job(models.Model):
    """
    职位信息
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # 主键
    co_name = models.CharField(max_length=100)  # 公司名称
    co_link = models.TextField(default='none')  # 公司链接
    job_name = models.CharField(max_length=100)  # 招聘职位
    co_type = models.CharField(max_length=20, default='none')  # 公司性质
    co_scale = models.CharField(max_length=20, default='none')  # 公司规模
    job_experience = models.CharField(max_length=20, default='none')  # 工作经验
    education = models.CharField(max_length=10, default='none')  # 学历
    salary = models.CharField(max_length=20, default='none')  # 职位月薪
    duty = models.TextField(default='none')  # 岗位职责
    scraping_time = models.DateTimeField('最后修改日期', auto_now=True)  # 数据抓取日期


class ScrapingRecord(models.Model):
    """
    爬虫记录
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # 主键
    scraping_date = models.DateTimeField(auto_now=True)  # 抓取日期
    total = models.IntegerField()  # 抓取条数


class ProcessRecord(models.Model):
    """
    记录进程启动情况
    """
    process = models.CharField(max_length=100)  # 进程名
    is_started = models.BooleanField()
