# -*- coding: utf-8 -*-
"""
BatchUpdateTotalScore - 批量更新总分
教师设置操作成绩权重和报告成绩权重，批量重新计算所有学生的总分
对应 Java: BatchUpdateTotalScoreController + BatchUpdateTotalScoreServiceImpl
"""

import json
import uuid
from decimal import Decimal
from datetime import datetime

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.accounts.models import TbUser


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def batch_update_score(request):
    """
    POST /api/v1/assessment/batch/update-score/
    教师设置操作/报告权重，批量重算总分

    参数:
        operationNum (str): 操作成绩权重（如 0.6）
        reportNum (str): 报告成绩权重（如 0.4）
        userId (str): 教师/创建者ID
        experimentId (str): 实验ID
        classId (str): 班级ID

    总分 = operationScore * operationNum + reportScore * reportNum
    """
    # 参数提取
    if request.method == 'POST' and request.body:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}

    operation_num = data.get('operationNum') or request.GET.get('operationNum') or request.POST.get('operationNum')
    report_num = data.get('reportNum') or request.GET.get('reportNum') or request.POST.get('reportNum')
    user_id = data.get('userId') or request.GET.get('userId') or request.POST.get('userId')
    experiment_id = data.get('experimentId') or request.GET.get('experimentId') or request.POST.get('experimentId')
    class_id = data.get('classId') or request.GET.get('classId') or request.POST.get('classId')

    if not all([operation_num, report_num, user_id, experiment_id, class_id]):
        return JsonResponse({'flag': 0, 'msg': '缺少必填参数'})

    try:
        operation_weight = Decimal(str(operation_num))
        report_weight = Decimal(str(report_num))
    except Exception:
        return JsonResponse({'flag': 0, 'msg': '权重参数格式错误'})

    now = datetime.now()

    with connection.cursor() as cur:
        # 1. 检查是否已有权重记录
        cur.execute(
            "SELECT id FROM tb_weight_info WHERE experiment_Id=%s AND create_id=%s AND class_Id=%s",
            [experiment_id, user_id, class_id]
        )
        existing = cur.fetchone()

        if existing:
            cur.execute(
                "UPDATE tb_weight_info SET operation=%s, report=%s, update_time=%s, update_id=%s WHERE id=%s",
                [operation_weight, report_weight, now, user_id, existing[0]]
            )
        else:
            try:
                user = TbUser.objects.get(pk=user_id)
                if user.type not in (1, 2):
                    return JsonResponse({'flag': 0, 'msg': '仅教师或管理员可设置权重'})
                school_id = user.schoolId or ''
            except TbUser.DoesNotExist:
                return JsonResponse({'flag': 0, 'msg': '用户不存在'})

            new_id = uuid.uuid4().hex[:32]
            cur.execute(
                "INSERT INTO tb_weight_info (id, school_Id, class_Id, experiment_Id, operation, report, create_id, create_time, update_id, update_time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [new_id, school_id, class_id, experiment_id, operation_weight, report_weight, user_id, now, user_id, now]
            )

        # 2. 查询该实验+班级的所有成绩记录
        cur.execute(
            "SELECT id, operation_score, report_score FROM tb_experiment_score WHERE experiment_id=%s AND class_Id=%s",
            [experiment_id, class_id]
        )
        scores = cur.fetchall()

        if not scores:
            return JsonResponse({'flag': 1, 'msg': '权重信息设置成功（无成绩记录可更新）'})

        # 3. 逐条重算总分
        updated_count = 0
        for row in scores:
            score_id, op_score, rp_score = row
            op_val = Decimal(str(op_score)) if op_score is not None else Decimal('0')
            rp_val = Decimal(str(rp_score)) if rp_score is not None else Decimal('0')
            new_sum = op_val * operation_weight + rp_val * report_weight
            cur.execute(
                "UPDATE tb_experiment_score SET score_sum=%s, update_time=%s WHERE id=%s",
                [new_sum, now, score_id]
            )
            updated_count += 1

    return JsonResponse({
        'flag': 1,
        'msg': '权重信息设置成功',
        'updatedCount': updated_count
    })
