# -*- coding: utf-8 -*-
"""
Teacher Report - 教师实验报告管理 API
对应 Java: ExperimentScoreController 中的教师查询部分 + sybgforteacher.jsp
"""

import json
from datetime import datetime

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.accounts.models import TbUser


def _get_user_id(request):
    """从请求中提取 userId"""
    # 优先查 query 参数
    uid = request.GET.get('userId')
    if uid:
        return uid
    # POST JSON body
    if request.method == 'POST':
        try:
            raw = request.read()
            if raw:
                body = json.loads(raw)
                uid = body.get('userId')
                if uid:
                    return uid
        except Exception:
            pass
        uid = request.POST.get('userId')
        if uid:
            return uid
    return None


def _check_user(user_id):
    """验证用户并返回 (user, error_msg)"""
    if not user_id:
        return None, '未登录'
    try:
        user = TbUser.objects.get(pk=user_id)
    except TbUser.DoesNotExist:
        return None, '用户不存在'
    if user.type not in (1, 2):
        return None, '仅教师或管理员可操作'
    return user, None


@csrf_exempt
def teacher_class_list(request):
    """
    GET/POST /api/v1/scores/teacher/classes/
    获取教师管理的班级列表
    """
    if request.method not in ('GET', 'POST'):
        return JsonResponse({'flag': 0, 'msg': '不支持的请求方法'})
    user_id = _get_user_id(request)
    user, err = _check_user(user_id)
    if err:
        return JsonResponse({'flag': 0, 'msg': err})
    with connection.cursor() as cur:
        if user.type == 2:
            # 管理员查看所有班级
            cur.execute(
                "SELECT id, class_card, school_id FROM tb_class_info WHERE type!=%s ORDER BY create_time",
                ['0']
            )
        else:
            # 教师查看自己的班级
            cur.execute(
                "SELECT id, class_card, school_id FROM tb_class_info WHERE teacher_id=%s AND type!=%s ORDER BY create_time",
                [user.id, '0']
            )
        rows = cur.fetchall()
        results = [{'id': r[0], 'classCard': r[1], 'schoolId': r[2]} for r in rows]
    return JsonResponse({'flag': 1, 'list': results})


@csrf_exempt
def teacher_course_list(request):
    """课程列表"""
    if request.method not in ('GET', 'POST'):
        return JsonResponse({'flag': 0, 'msg': '不支持的请求方法'})
    user_id = _get_user_id(request)
    user, err = _check_user(user_id)
    if err:
        return JsonResponse({'flag': 0, 'msg': err})
    params = request.GET
    class_id = params.get('classId')
    if not class_id:
        return JsonResponse({'flag': 0, 'msg': '缺少 classId'})
    with connection.cursor() as cur:
        cur.execute("SELECT school_id FROM tb_class_info WHERE id=%s", [class_id])
        row = cur.fetchone()
        if not row:
            return JsonResponse({'flag': 0, 'list': []})
        school_id = row[0] or ''
        cur.execute("""
            SELECT DISTINCT s.curriculum_id, c.curriculum_name
            FROM tb_experiment_score s
            LEFT JOIN tb_curriculum c ON s.curriculum_id = c.id
            WHERE s.class_Id=%s AND s.curriculum_id IS NOT NULL
        """, [class_id])
        rows = cur.fetchall()
        if not rows:
            cur.execute("""
                SELECT DISTINCT sc.curriculum_id, c.curriculum_name
                FROM school_curriculum sc
                LEFT JOIN tb_curriculum c ON sc.curriculum_id = c.id
                WHERE sc.school_id=%s
            """, [school_id])
            rows = cur.fetchall()
        results = [{'curriculumId': r[0], 'curriculumStr': r[1] or '未知课程'} for r in rows]
    return JsonResponse({'flag': 1, 'list': results})


@csrf_exempt
def teacher_experiment_list(request):
    """实验列表"""
    if request.method not in ('GET', 'POST'):
        return JsonResponse({'flag': 0, 'msg': '不支持的请求方法'})
    user_id = _get_user_id(request)
    user, err = _check_user(user_id)
    if err:
        return JsonResponse({'flag': 0, 'msg': err})
    params = request.GET
    class_id = params.get('classId')
    curriculum_id = params.get('curriculumId')
    if not class_id:
        return JsonResponse({'flag': 0, 'msg': '缺少 classId'})
    with connection.cursor() as cur:
        if curriculum_id:
            cur.execute("""
                SELECT DISTINCT s.experiment_id, e.title
                FROM tb_experiment_score s
                LEFT JOIN tb_experiment e ON s.experiment_id = e.id
                WHERE s.class_Id=%s AND s.curriculum_id=%s AND s.experiment_id IS NOT NULL
            """, [class_id, curriculum_id])
        else:
            cur.execute("""
                SELECT DISTINCT s.experiment_id, e.title
                FROM tb_experiment_score s
                LEFT JOIN tb_experiment e ON s.experiment_id = e.id
                WHERE s.class_Id=%s AND s.experiment_id IS NOT NULL
            """, [class_id])
        rows = cur.fetchall()
        if not rows and curriculum_id:
            cur.execute("SELECT id, title FROM tb_experiment WHERE parent_id=%s", [curriculum_id])
            rows = cur.fetchall()
        results = [{'experimentId': r[0], 'experimentStr': r[1] or '未知实验'} for r in rows]
    return JsonResponse({'flag': 1, 'list': results})


@csrf_exempt
def teacher_report_list(request):
    """
    GET/POST /api/v1/scores/teacher/reports/
    获取教师管理的实验报告列表
    """
    if request.method not in ('GET', 'POST'):
        return JsonResponse({'flag': 0, 'msg': '不支持的请求方法'})
    user_id = _get_user_id(request)
    user, err = _check_user(user_id)
    if err:
        return JsonResponse({'flag': 0, 'msg': err})
    params = request.GET
    class_id = params.get('classId')
    curriculum_id = params.get('curriculumId')
    experiment_id = params.get('experimentId')
    start_page = int(params.get('startPage', '1'))
    page_size = int(params.get('PageSize', '10'))

    if not class_id or not curriculum_id or not experiment_id:
        return JsonResponse({
            'flag': 0, 'msg': '缺少参数',
            'list': {'rows': [], 'pageInfo': {'pageNum': start_page, 'pages': 0, 'total': 0, 'prePage': 0, 'nextPage': 0, 'navigatepageNums': []}}
        })

    offset = (start_page - 1) * page_size
    with connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM tb_experiment_score s
            WHERE s.class_Id=%s AND s.curriculum_id=%s AND s.experiment_id=%s
        """, [class_id, curriculum_id, experiment_id])
        total = cur.fetchone()[0]
        cur.execute("""
            SELECT s.id, s.id_card, s.user_id, s.class_Id, s.curriculum_id, s.experiment_id,
                   COALESCE(u.name, ''), COALESCE(u.class_name, ''),
                   COALESCE(c.curriculum_name, ''), COALESCE(e.title, ''),
                   s.operation_score, s.report_score, s.score_sum, s.pdf_path, s.experiment_num,
                   CASE WHEN s.pdf_path IS NOT NULL AND s.pdf_path != '' THEN 1 ELSE 0 END
            FROM tb_experiment_score s
            LEFT JOIN tb_user u ON s.user_id = u.id
            LEFT JOIN tb_curriculum c ON s.curriculum_id = c.id
            LEFT JOIN tb_experiment e ON s.experiment_id = e.id
            WHERE s.class_Id=%s AND s.curriculum_id=%s AND s.experiment_id=%s
            ORDER BY u.name LIMIT %s OFFSET %s
        """, [class_id, curriculum_id, experiment_id, page_size, offset])
        rows = cur.fetchall()

    results = []
    for r in rows:
        has_report = r[15]
        results.append({
            'id': r[0], 'idCard': r[1] or '', 'userId': r[2], 'classId': r[3],
            'studentName': r[6] or '', 'classStr': r[7] or '',
            'curriculumStr': r[8] or '', 'experimentStr': r[9] or '',
            'operationScore': str(r[10]) if r[10] is not None else '',
            'reportScore': str(r[11]) if r[11] is not None else '',
            'scoreSum': str(r[12]) if r[12] is not None else '',
            'pdfPath': r[13] or '', 'experimentNum': r[14] or 0,
            'reportType': '已上传' if has_report else '未上传', 'flag': has_report,
        })

    pages = (total + page_size - 1) // page_size if total > 0 else 0
    pre_page = start_page - 1 if start_page > 1 else 1
    next_page = start_page + 1 if start_page < pages else pages
    nav_start = max(1, start_page - 2)
    nav_end = min(pages, start_page + 2)
    if nav_end - nav_start < 4:
        nav_end = min(pages, nav_start + 4) if nav_start == 1 else max(1, nav_end - 4)
    navigatepage_nums = list(range(nav_start, nav_end + 1))

    return JsonResponse({
        'flag': 1 if results else 0,
        'list': {
            'rows': results,
            'pageInfo': {'pageNum': start_page, 'pages': pages, 'total': total,
                         'prePage': pre_page, 'nextPage': next_page, 'navigatepageNums': navigatepage_nums},
        }
    })


@csrf_exempt
def teacher_report_detail(request, report_id):
    """查询实验报告详情"""
    with connection.cursor() as cur:
        cur.execute("""
            SELECT s.id, s.pdf_path, s.operation_score, s.report_score, s.score_sum,
                   s.experiment_id, s.curriculum_id, s.class_Id, s.user_id,
                   COALESCE(u.name, ''), COALESCE(e.title, ''), COALESCE(c.curriculum_name, '')
            FROM tb_experiment_score s
            LEFT JOIN tb_user u ON s.user_id = u.id
            LEFT JOIN tb_experiment e ON s.experiment_id = e.id
            LEFT JOIN tb_curriculum c ON s.curriculum_id = c.id
            WHERE s.id=%s
        """, [report_id])
        row = cur.fetchone()
    if not row:
        return JsonResponse({'flag': 0, 'msg': '报告不存在'})
    return JsonResponse({
        'flag': 1, 'id': row[0], 'pdfPath': row[1] or '',
        'operationScore': str(row[2]) if row[2] is not None else '',
        'reportScore': str(row[3]) if row[3] is not None else '',
        'scoreSum': str(row[4]) if row[4] is not None else '',
        'experimentId': row[5], 'curriculumId': row[6],
        'classId': row[7], 'userId': row[8],
        'studentName': row[9], 'experimentName': row[10], 'curriculumName': row[11],
    })


@csrf_exempt
def teacher_submit_score(request, report_id):
    """教师提交批阅分数"""
    if request.method not in ('POST', 'GET'):
        return JsonResponse({'flag': 0, 'msg': '仅支持 POST 或 GET'})
    score_sum = request.GET.get('scoreSum')
    now = datetime.now()
    with connection.cursor() as cur:
        cur.execute("SELECT id FROM tb_experiment_score WHERE id=%s", [report_id])
        if not cur.fetchone():
            return JsonResponse({'flag': 0, 'msg': '记录不存在'})
        if score_sum:
            cur.execute(
                "UPDATE tb_experiment_score SET report_score=%s, score_sum=%s, update_time=%s WHERE id=%s",
                [score_sum, score_sum, now, report_id]
            )
    return JsonResponse({'flag': 1, 'msg': '提交成功'})
