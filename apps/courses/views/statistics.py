# -*- coding: utf-8 -*-
"""
apps.courses.views.statistics - 实验统计视图

提供实验的访问/练习统计，数据存储在 tb_record_info 表（汇总）和 tb_experiment_daily_stats 表（按天）。
"""

from datetime import datetime, date, timedelta

from django.db import connection
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

import uuid

from django.db.models import Sum

from apps.courses.models import TbExperiment, TbRecordInfo


def _get_or_create_daily(experiment_id, stat_date):
    """获取或创建当天的统计记录"""
    with connection.cursor() as cur:
        cur.execute(
            "SELECT id, visit_count, practice_count FROM tb_experiment_daily_stats WHERE experiment_id=%s AND stat_date=%s",
            [experiment_id, stat_date]
        )
        row = cur.fetchone()
        if row:
            return {'id': row[0], 'visit_count': row[1] or 0, 'practice_count': row[2] or 0}
        # 创建新记录
        import uuid
        new_id = uuid.uuid4().hex[:32]
        cur.execute(
            "INSERT INTO tb_experiment_daily_stats (id, experiment_id, stat_date, visit_count, practice_count, create_time, update_time) VALUES (%s,%s,%s,0,0,%s,%s)",
            [new_id, experiment_id, stat_date, now(), now()]
        )
        return {'id': new_id, 'visit_count': 0, 'practice_count': 0}


@api_view(['POST'])
@permission_classes([AllowAny])
def record_visit(request, pk):
    """
    POST /api/v1/experiments/<id>/record-visit/
    记录一次访问（点进实验详情页即算）
    """
    today = now().date()

    # 更新按天统计
    daily = _get_or_create_daily(pk, today)
    with connection.cursor() as cur:
        cur.execute(
            "UPDATE tb_experiment_daily_stats SET visit_count=%s, update_time=%s WHERE id=%s",
            [daily['visit_count'] + 1, now(), daily['id']]
        )

    # 更新汇总表 tb_record_info（处理多记录情况）
    records = TbRecordInfo.objects.filter(experimentId=pk)
    if records.exists():
        # 如果有多个记录，更新第一个
        record = records.first()
        record.browseNum = (record.browseNum or 0) + 1
        record.updateTime = now()
        record.save(update_fields=['browseNum', 'updateTime'])
    else:
        # 创建新记录
        TbRecordInfo.objects.create(
            experimentId=pk,
            browseNum=1,
            operateNum=0,
            createTime=now(),
            updateTime=now(),
        )

    return Response({'code': 0, 'message': '记录成功'})


@api_view(['POST'])
@permission_classes([AllowAny])
def record_practice(request, pk):
    """
    POST /api/v1/experiments/<id>/record-practice/
    记录一次练习（点击开始实验即算）
    """
    today = now().date()

    # 更新按天统计
    daily = _get_or_create_daily(pk, today)
    with connection.cursor() as cur:
        cur.execute(
            "UPDATE tb_experiment_daily_stats SET practice_count=%s, update_time=%s WHERE id=%s",
            [daily['practice_count'] + 1, now(), daily['id']]
        )

    # 更新汇总表 tb_record_info（处理多记录情况）
    records = TbRecordInfo.objects.filter(experimentId=pk)
    if records.exists():
        # 如果有多个记录，更新第一个
        record = records.first()
        record.operateNum = (record.operateNum or 0) + 1
        record.updateTime = now()
        record.save(update_fields=['operateNum', 'updateTime'])
    else:
        # 创建新记录
        TbRecordInfo.objects.create(
            experimentId=pk,
            browseNum=0,
            operateNum=1,
            createTime=now(),
            updateTime=now(),
        )

    # 写入 tb_experiment_record，标记用户已练习过该实验
    user_id = None
    if hasattr(request, 'user') and request.user and hasattr(request.user, 'id'):
        user_id = request.user.id

    if user_id:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT id FROM tb_experiment_record WHERE user_Id=%s AND experiment_Id=%s",
                [user_id, pk]
            )
            exist_row = cur.fetchone()
            if not exist_row:
                new_id = uuid.uuid4().hex[:32]
                cur.execute(
                    "INSERT INTO tb_experiment_record (id, user_Id, experiment_Id, record_num, browse_num, create_time, update_time) VALUES (%s,%s,%s,1,0,%s,%s)",
                    [new_id, user_id, pk, now(), now()]
                )
            else:
                cur.execute(
                    "UPDATE tb_experiment_record SET record_num=record_num+1, update_time=%s WHERE id=%s",
                    [now(), exist_row[0]]
                )

    return Response({'code': 0, 'message': '记录成功'})


@api_view(['GET'])
@permission_classes([AllowAny])
def experiment_stats(request, pk):
    """
    GET /api/v1/experiments/<id>/stats/
    获取实验统计数据（全部真实，从数据库读取）
    """
    # 汇总数据从 tb_record_info 取（按 experiment_id 汇总所有记录）
    agg = TbRecordInfo.objects.filter(experimentId=pk).aggregate(
        total_browse=Sum('browseNum'),
        total_operate=Sum('operateNum')
    )
    total_visits = agg['total_browse'] or 0
    total_practice = agg['total_operate'] or 0

    # 今日数据（使用date.today()确保日期一致）
    today = date.today()
    tomorrow = today + timedelta(days=1)

    with connection.cursor() as cur:
        # 今日新增
        cur.execute(
            "SELECT COALESCE(SUM(visit_count),0), COALESCE(SUM(practice_count),0) FROM tb_experiment_daily_stats WHERE experiment_id=%s AND stat_date>=%s AND stat_date<%s",
            [pk, today, tomorrow]
        )
        row = cur.fetchone()
        new_visits = int(row[0]) if row else 0
        new_practice = int(row[1]) if row else 0

        # 近7天趋势
        seven_days_ago = today - timedelta(days=6)
        cur.execute(
            "SELECT stat_date, COALESCE(SUM(visit_count),0), COALESCE(SUM(practice_count),0) FROM tb_experiment_daily_stats WHERE experiment_id=%s AND stat_date>=%s GROUP BY stat_date ORDER BY stat_date ASC",
            [pk, seven_days_ago]
        )
        rows = cur.fetchall()
        daily_map = {r[0].isoformat(): (int(r[1]), int(r[2])) for r in rows}

    # 补齐7天（没数据的填0）
    daily_visits = []
    daily_practice = []
    for i in range(7):
        d = (seven_days_ago + timedelta(days=i))
        ds = d.isoformat()
        v, p = daily_map.get(ds, (0, 0))
        daily_visits.append({'date': ds, 'count': v})
        daily_practice.append({'date': ds, 'count': p})

    # 计算7天前的基数，用于生成累计趋势
    seven_days_total_v = sum(d['count'] for d in daily_visits)
    seven_days_total_p = sum(d['count'] for d in daily_practice)
    base_visits = max(0, total_visits - seven_days_total_v)
    base_practice = max(0, total_practice - seven_days_total_p)

    # 累计趋势：每天的累计总量
    cumulative_visits = []
    cumulative_practice = []
    running_v = base_visits
    running_p = base_practice
    for i in range(7):
        running_v += daily_visits[i]['count']
        running_p += daily_practice[i]['count']
        cumulative_visits.append({'date': daily_visits[i]['date'], 'count': running_v})
        cumulative_practice.append({'date': daily_practice[i]['date'], 'count': running_p})

    return Response({
        'totalVisits': total_visits,
        'totalPractice': total_practice,
        'newVisits': new_visits,
        'newPractice': new_practice,
        'dailyVisits': daily_visits,
        'dailyPractice': daily_practice,
        'cumulativeVisits': cumulative_visits,
        'cumulativePractice': cumulative_practice,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def experiment_record_info(request):
    """
    POST /api/v1/record/experimentRecordInfo
    兼容旧Java接口，返回访问总量、练习总次数等统计数据（最近7天）
    参数: cId (课程ID), eId (实验ID)
    返回: flag, tbRecordInfo (数组)
    """
    c_id = request.data.get('cId') or request.POST.get('cId')
    e_id = request.data.get('eId') or request.POST.get('eId')

    if not e_id:
        return Response({'flag': 0, 'msg': '页面过期'})

    # 获取汇总数据（按 experiment_id 汇总所有记录）
    agg = TbRecordInfo.objects.filter(experimentId=e_id).aggregate(
        total_browse=Sum('browseNum'),
        total_operate=Sum('operateNum')
    )
    total_visits = agg['total_browse'] or 0
    total_practice = agg['total_operate'] or 0

    # 查询最近7天的按天统计数据
    today = now().date()
    seven_days_ago = today - timedelta(days=6)

    with connection.cursor() as cur:
        cur.execute(
            "SELECT stat_date, COALESCE(SUM(visit_count),0), COALESCE(SUM(practice_count),0) "
            "FROM tb_experiment_daily_stats WHERE experiment_id=%s AND stat_date>=%s "
            "GROUP BY stat_date ORDER BY stat_date ASC",
            [e_id, seven_days_ago]
        )
        rows = cur.fetchall()
        daily_map = {r[0].isoformat(): (int(r[1]), int(r[2])) for r in rows}

    # 构建7天数据（从旧到新）
    tb_record_info = []
    running_browse = max(0, total_visits)
    running_operate = max(0, total_practice)

    # 先计算7天内总量，用于推算7天前的基数
    seven_v = 0
    seven_p = 0
    for i in range(7):
        d = (seven_days_ago + timedelta(days=i))
        ds = str(d)
        v, p = daily_map.get(ds, (0, 0))
        seven_v += v
        seven_p += p

    base_browse = max(0, total_visits - seven_v)
    base_operate = max(0, total_practice - seven_p)

    running_browse = base_browse
    running_operate = base_operate

    for i in range(7):
        d = (seven_days_ago + timedelta(days=i))
        ds = str(d)
        v, p = daily_map.get(ds, (0, 0))
        running_browse += v
        running_operate += p

        # 格式化日期为 MM-dd
        mm_dd = d.strftime('%m-%d')

        tb_record_info.append({
            'browseNum': v,           # 当天新增访问量
            'operateNum': p,          # 当天新增练习次数
            'browseCount': running_browse,   # 访问总量（累计到当天）
            'operateCount': running_operate, # 练习总次数（累计到当天）
            'highchartsDate': mm_dd,  # 日期 MM-dd
        })

    return Response({
        'flag': 1,
        'tbRecordInfo': tb_record_info,
    })
