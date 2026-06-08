# -*- coding: utf-8 -*-
"""
Student Report - 学生实验报告查询 API
对应 Java: sybg.jsp 的 showStudentReport 接口
"""

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.accounts.models import TbUser


def _get_user_id(request):
    uid = request.GET.get('userId')
    if uid:
        return uid
    if request.method == 'POST':
        try:
            raw = request.read()
            if raw:
                import json
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


@csrf_exempt
def student_report_list(request):
    """
    GET/POST /api/v1/scores/student/reports/
    学生查看自己的实验报告列表
    对应 Java: sybg.jsp initReportInfo
    """
    user_id = _get_user_id(request)
    if not user_id:
        return JsonResponse({'flag': 0, 'msg': '未登录', 'list': {'rows': [], 'pageInfo': {}}})

    start_page = int(request.GET.get('startPage') or request.POST.get('startPage') or request.GET.get('page') or '1')
    page_size = int(request.GET.get('PageSize') or request.POST.get('PageSize') or request.GET.get('page_size') or '10')
    offset = (start_page - 1) * page_size

    with connection.cursor() as cur:
        # 统计总数
        cur.execute("""
            SELECT COUNT(*) FROM tb_experiment_score
            WHERE user_id=%s
        """, [user_id])
        total = cur.fetchone()[0]

        # 查询数据
        cur.execute("""
            SELECT s.id, s.id_card, s.experiment_id, s.curriculum_id, s.pdf_path,
                   s.operation_score, s.report_score, s.score_sum, s.experiment_num,
                   COALESCE(e.title, ''), COALESCE(c.curriculum_name, ''),
                   COALESCE(ci.class_card, ''),
                   CASE WHEN s.pdf_path IS NOT NULL AND s.pdf_path != '' THEN 1 ELSE 0 END
            FROM tb_experiment_score s
            LEFT JOIN tb_experiment e ON s.experiment_id = e.id
            LEFT JOIN tb_curriculum c ON s.curriculum_id = c.id
            LEFT JOIN tb_class_info ci ON s.class_Id = ci.id
            WHERE s.user_id=%s
            ORDER BY s.update_time DESC
            LIMIT %s OFFSET %s
        """, [user_id, page_size, offset])
        rows = cur.fetchall()

    results = []
    for r in rows:
        has_report = r[12]
        results.append({
            'id': r[0],
            'idCard': r[1] or '',
            'experimentId': r[2],
            'curriculumId': r[3],
            'pdfPath': r[4] or '',
            'operationScore': str(r[5]) if r[5] is not None else '',
            'reportScore': str(r[6]) if r[6] is not None else '',
            'scoreSum': str(r[7]) if r[7] is not None else '',
            'experimentNum': r[8] or 0,
            'experimentStr': r[9] or '未知实验',
            'curriculumStr': r[10] or '未知课程',
            'classStr': r[11] or '',
            'reportType': '查看' if has_report else '未上传',
            'flag': has_report,
        })

    pages = (total + page_size - 1) // page_size if total > 0 else 0
    pre_page = max(1, start_page - 1)
    next_page = min(pages, start_page + 1) if start_page < pages else pages
    nav_start = max(1, start_page - 2)
    nav_end = min(pages, start_page + 2)

    return JsonResponse({
        'flag': 1 if results else 0,
        'list': {
            'rows': results,
            'pageInfo': {
                'pageNum': start_page, 'pages': pages, 'total': total,
                'prePage': pre_page, 'nextPage': next_page,
                'navigatepageNums': list(range(nav_start, nav_end + 1)),
            }
        }
    })
