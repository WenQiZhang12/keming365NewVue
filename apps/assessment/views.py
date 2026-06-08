# -*- coding: utf-8 -*-
"""
Assessment App - Views
测评模块：为第三方考试系统提供数据查询接口
对应 Java: AssessmentController
使用 JWT 加密 token 做身份验证
"""

import json
from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from apps.assessment.services import AssessmentService
from apps.assessment.utils import encrypt_payload, decrypt_token

# 配置（对应 Java 中的静态常量）
SECRET = "8leFQSz"
AES_KEY = "n0BjS5mJhR2fw9z1ChhGi1lWt9ON6A5RHuqOJhIi9vh="
ISSUE_ID = 10025
ZIP_UPLOAD_URL = "http://58.56.66.167:8088/vrAppli/upload"


# ====== 内部辅助函数 ======

def _user_to_dict(user) -> dict:
    """将 TbUser 转为测评接口需要的字典格式"""
    return {
        'id': user.id,
        'name': user.name or '',
        'username': user.username or '',
        'type': user.type,
        'memberType': str(user.type),
        'schoolId': user.schoolId or '',
        'classId': user.classId or '',
        'telephone': user.telephone or '',
        'email': user.email or '',
        'userImg': user.userImg or '',
    }


def _make_key_response(data: dict):
    """
    用加密 Key 包装响应数据
    对应 Java 中的 visitPage / visitManage 返回格式
    """
    import json as j
    return JsonResponse([data], safe=False)


# ====== API 接口 ======


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def visit_page(request):
    """
    GET/POST /api/v1/assessment/visit-page/
    进入考试 - 返回加密 Key
    参数: userId, classId(可选), experimentId(可选), curricullumId(可选)
    """
    user_id = request.GET.get('userId') or request.POST.get('userId')
    if not user_id:
        return JsonResponse({'code': 400, 'message': '缺少 userId'}, status=400)

    # 构建加密 payload
    payload = {
        'timestamp': str(int(datetime.now().timestamp() * 1000)),
        'userId': user_id,
    }
    try:
        key = encrypt_payload(
            json.dumps(payload),
            SECRET, AES_KEY, ISSUE_ID,
            60 * 60 * 1000  # 1 小时有效期
        )
        return JsonResponse([{'Key': key}], safe=False)
    except Exception as e:
        return JsonResponse([{'code': 500, 'message': str(e)}], safe=False)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def visit_manage(request):
    """
    GET/POST /api/v1/assessment/visit-manage/
    考试管理 - 返回加密 Key
    参数: userId, userType(可选), classId(可选)
    """
    user_id = request.GET.get('userId') or request.POST.get('userId')
    if not user_id:
        return JsonResponse({'code': 400, 'message': '缺少 userId'}, status=400)

    payload = {
        'timestamp': str(int(datetime.now().timestamp() * 1000)),
        'userId': user_id,
    }
    try:
        key = encrypt_payload(
            json.dumps(payload),
            SECRET, AES_KEY, ISSUE_ID,
            60 * 60 * 1000
        )
        return JsonResponse([{'Key': key}], safe=False)
    except Exception as e:
        return JsonResponse([{'code': 500, 'message': str(e)}], safe=False)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def auth_member(request):
    """
    GET/POST /api/v1/assessment/auth-member/
    验证用户身份 - 解密 Token 并对比 userId
    参数: MemberID, Token（加密 token）
    """
    member_id = request.GET.get('MemberID') or request.POST.get('MemberID')
    token = request.GET.get('Token') or request.POST.get('Token')

    if not member_id or not token:
        return HttpResponse(status=400)

    try:
        decrypted = decrypt_token(token, SECRET, AES_KEY, ISSUE_ID)
        payload = json.loads(decrypted)
        send_user_id = payload.get('userId')
        if send_user_id == member_id:
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
    except Exception:
        return HttpResponse(status=400)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def member_info(request):
    """
    GET/POST /api/v1/assessment/member-info/
    获取用户信息 - 支持批量（多个 userId 用逗号分隔）
    参数: userId / userId1,userId2,...
    """
    raw = request.GET.get('userId') or request.POST.get('userId') or ''
    user_ids = [uid.strip() for uid in raw.split(',') if uid.strip()]

    results = []
    for uid in user_ids:
        user = AssessmentService.site_member(uid)
        if user:
            d = _user_to_dict(user)
            results.append(d)

    return JsonResponse(results, safe=False)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def class_info(request):
    """
    GET/POST /api/v1/assessment/class-info/
    获取班级信息 - 支持批量
    参数: classId / classId1,classId2,...
    """
    raw = request.GET.get('classId') or request.POST.get('classId') or ''
    class_ids = [cid.strip() for cid in raw.split(',') if cid.strip()]

    results = []
    for cid in class_ids:
        info = AssessmentService.site_class(cid)
        if info:
            results.append(info)

    return JsonResponse(results, safe=False)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def course_info(request):
    """
    GET/POST /api/v1/assessment/course-info/
    获取课程信息 - 支持批量
    参数: courseId / courseId1,courseId2,...
    """
    raw = request.GET.get('courseId') or request.POST.get('courseId') or ''
    course_ids = [cid.strip() for cid in raw.split(',') if cid.strip()]

    results = []
    for cid in course_ids:
        course = AssessmentService.site_course(cid)
        if course:
            results.append({
                'id': course.id,
                'name': course.curriculumName or '',
                'curriculumName': course.curriculumName or '',
            })

    return JsonResponse(results, safe=False)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def section_info(request):
    """
    GET/POST /api/v1/assessment/section-info/
    获取实验信息 - 支持批量
    参数: experimentId / experimentId1,experimentId2,...
    """
    raw = request.GET.get('experimentId') or request.POST.get('experimentId') or ''
    exp_ids = [eid.strip() for eid in raw.split(',') if eid.strip()]

    results = []
    for eid in exp_ids:
        exp = AssessmentService.site_section(eid)
        if exp:
            results.append({
                'id': exp.id,
                'name': exp.title or '',
                'title': exp.title or '',
            })

    return JsonResponse(results, safe=False)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def course_index(request):
    """
    GET/POST /api/v1/assessment/course-index/
    获取分类/班级下的课程列表
    参数: MajorID, MemberID(通过用户查学校), ClassID(通过班级查学校)
    """
    major_id = request.GET.get('MajorID') or request.POST.get('MajorID')
    member_id = request.GET.get('MemberID') or request.POST.get('MemberID')
    class_id = request.GET.get('ClassID') or request.POST.get('ClassID')

    if not major_id:
        return JsonResponse([], safe=False)

    if member_id:
        results = AssessmentService.course_index(major_id, member_id, 1)
    elif class_id:
        results = AssessmentService.course_index(major_id, class_id, 2)
    else:
        results = []

    return JsonResponse(results, safe=False)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def section_index(request):
    """
    GET/POST /api/v1/assessment/section-index/
    获取课程下的实验列表
    参数: CourseID
    """
    course_id = request.GET.get('CourseID') or request.POST.get('CourseID')
    if not course_id:
        return JsonResponse([], safe=False)

    results = AssessmentService.section_index(course_id)
    return JsonResponse(results, safe=False)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def class_index(request):
    """
    GET/POST /api/v1/assessment/class-index/
    获取用户所有班级信息
    参数: MemberID
    """
    member_id = request.GET.get('MemberID') or request.POST.get('MemberID')
    if not member_id:
        return JsonResponse([], safe=False)

    results = AssessmentService.class_index(member_id)
    return JsonResponse(results, safe=False)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def major_index(request):
    """
    GET/POST /api/v1/assessment/major-index/
    获取分类列表（按学校授权）
    参数: MemberID
    """
    member_id = request.GET.get('MemberID') or request.POST.get('MemberID')
    if not member_id:
        return JsonResponse([], safe=False)

    results = AssessmentService.classify_index(member_id)
    return JsonResponse(results, safe=False)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def major_info(request):
    """
    GET/POST /api/v1/assessment/major-info/
    获取分类信息 - 支持批量
    参数: classifyId / classifyId1,classifyId2,...
    """
    raw = request.GET.get('classifyId') or request.POST.get('classifyId') or ''
    ids = [cid.strip() for cid in raw.split(',') if cid.strip()]

    results = []
    for cid in ids:
        info = AssessmentService.major_info(cid)
        if info:
            results.append(info)

    return JsonResponse(results, safe=False)
