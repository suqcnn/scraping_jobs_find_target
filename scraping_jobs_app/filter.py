#!/usr/bin/env python
# -*- coding: utf-8 -*-
import operator
from functools import reduce

from django.db.models import Q

from scraping_jobs_app.models import Job
import datetime


def filter_job(kw=None):
    """
    根据字段和关键字列表筛选数据
    :return:
    """
    new_kw = []
    for k in kw:
        q_k = Q(job_name__contains=k)
        new_kw.append(q_k)
    cdt_today = datetime.date.today().__str__()
    result = Job.objects.filter(
        reduce(operator.or_, new_kw) & Q(scraping_time__range=[cdt_today + ' 0:00:00', cdt_today + ' 23:59:59']))
    return result


if __name__ == '__main__':
    kw = ['name', 'age', 'city']
    filter_job('test_field', *kw)
