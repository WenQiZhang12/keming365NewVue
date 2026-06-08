# -*- coding: utf-8 -*-
"""
Pushlet - 推送/云雀实验进入服务
对应 Java: PushletController + ExperimentPushletController
提供第三方 VR 平台的入口跳转：检查预约状态 → SHA-1 签名 → 获取进入 URL
"""

import hashlib
import time
import json
from datetime import datetime, timedelta

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# ====== 配置（对应 Java 常量） ======
ACCESS_KEY = "Jx3wQMD1"
PULLET_SECRET = "d8aefb52b9534d0cad19b33be8d190b2"        # PushletController
EXPERIMENT_SECRET = "ea6cfae932a94a5aad7c7b8cf24f5b85"   # ExperimentPushletController
TOKEN_URL = "getEnterAppliURL"  # 云雀进入验证路径


def _sha1_sign(secret: str, timestamp: int) -> str:
    """SHA-1 签名（accessKey, secret, timestamp 排序后拼接）"""
    arr = sorted([ACCESS_KEY, secret, str(timestamp)])
    raw = ''.join(arr)
    return hashlib.sha1(raw.encode('utf-8')).hexdigest().upper()


def _date_to_timestamp(date_str: str) -> int:
    """将 yyyy-MM-dd HH:mm:ss 格式转换为13位时间戳"""
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp() * 1000)


def _check_experiment_status(school_name: str, resource_name: str, is_experiment: bool = False):
    """
    调用外部接口检查实验/课程状态
    Java 中：Pushlet = youerxiaoxuetang.com:11002/check
          ExperimentPushlet = youerxiaoxuetang.com:11005/check
    """
    port = "11005" if is_experiment else "11002"
    url = f"http://www.youerxiaoxuetang.com:{port}/check"
    try:
        resp = requests.post(url, data={
            "schoolName": school_name,
            "resourceName": resource_name,
        }, timeout=10)
        return resp.json()
    except Exception:
        return None


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def get_pull_event(request):
    """
    GET/POST /api/v1/assessment/pushlet/pull-event/
    对应 Java PushletController.getPullEvent
    
    参数:
        schoolId, userType, useTimeUrl, downTime, yunqUrl,
        schoolName, curriculumName, appliId, curriculumId,
        experimentId, userId, postUrl, gxPostUrl
    """
    if request.method == 'POST' and request.body:
        try:
            import json as j
            data = j.loads(request.body)
        except Exception:
            data = {}
    else:
        data = {}

    school_name = data.get('schoolName') or request.GET.get('schoolName') or request.POST.get('schoolName')
    curriculum_name = data.get('curriculumName') or request.GET.get('curriculumName') or request.POST.get('curriculumName')
    yunq_url = data.get('yunqUrl') or request.GET.get('yunqUrl') or request.POST.get('yunqUrl')
    appli_id = data.get('appliId') or request.GET.get('appliId') or request.POST.get('appliId')
    curriculum_id = data.get('curriculumId') or request.GET.get('curriculumId') or request.POST.get('curriculumId')
    experiment_id = data.get('experimentId') or request.GET.get('experimentId') or request.POST.get('experimentId')
    user_id = data.get('userId') or request.GET.get('userId') or request.POST.get('userId')
    post_url = data.get('postUrl') or request.GET.get('postUrl') or request.POST.get('postUrl')
    gx_post_url = data.get('gxPostUrl') or request.GET.get('gxPostUrl') or request.POST.get('gxPostUrl')
    use_time_url = data.get('useTimeUrl') or request.GET.get('useTimeUrl') or request.POST.get('useTimeUrl')
    user_type = data.get('userType') or request.GET.get('userType') or request.POST.get('userType')
    school_id = data.get('schoolId') or request.GET.get('schoolId') or request.POST.get('schoolId')
    down_time = data.get('downTime') or request.GET.get('downTime') or request.POST.get('downTime')

    if not all([school_name, curriculum_name, yunq_url, appli_id, user_id]):
        return JsonResponse({'code': 400, 'msg': '缺少必填参数'})

    # 1. 检查状态
    status_data = _check_experiment_status(school_name, curriculum_name)
    if not status_data:
        return JsonResponse({'code': 500, 'msg': '检查预约状态失败'})

    state = status_data.get('state', '')
    if state == '':
        return JsonResponse({'code': 500, 'msg': '系统异常'})

    experiment_flag = state.lower() == 'true'

    if not experiment_flag:
        code = status_data.get('code', '500')
        msg_map = {
            '201': '请按学校预约时间上课',
            '202': '请按学校预约的资源进行上课',
            '203': '人数已达上限，请选择其他预约时间进行上课',
            '204': '人数已达上限，请选择其他时间进行上课',
        }
        return JsonResponse({
            'code': int(code) if code.isdigit() else 500,
            'msg': msg_map.get(code, '系统异常')
        })

    # 2. 计算结束时间
    reservated = status_data.get('reservated', '').lower() == 'true'

    if down_time:
        down_time_ms = int(down_time)
    elif reservated:
        timeline = status_data.get('timeline', '')
        if timeline:
            down_time_ms = _date_to_timestamp(timeline)
        else:
            down_time_ms = int((datetime.now() + timedelta(hours=1)).timestamp() * 1000)
    else:
        # 无预约，1小时后
        next_hour = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        down_time_ms = int(next_hour.timestamp() * 1000)

    # 3. SHA-1 签名获取进入 URL
    timestamp = int(time.time() * 1000)
    token = _sha1_sign(PULLET_SECRET, timestamp)

    try:
        params = (
            f"appliId={appli_id}"
            f"&extraParam.downtime={down_time_ms}"
            f"&extraParam.userId={user_id}"
            f"&extraParam.curriculumId={curriculum_id}"
            f"&extraParam.experimentId={experiment_id}"
            f"&extraParam.baseUrl={post_url}"
            f"&extraParam.experimentOperationType={gx_post_url}"
            f"&codeRate=3000&frameRate=30"
            f"&appKey={ACCESS_KEY}&timestamp={timestamp}&signature={token}"
            f"&extraParam.useTimeUrl={use_time_url}"
            f"&extraParam.userType={user_type}"
            f"&extraParam.schoolId={school_id}"
            f"&extraParam.appliId={appli_id}"
        )
        full_url = f"{yunq_url}{TOKEN_URL}?{params}"
        resp = requests.get(full_url, timeout=15)
        resp.encoding = 'utf-8'
        result = resp.json()
        result_url = result.get('result', '')

        return JsonResponse({
            'code': 101,
            'resultUrl': result_url,
            'msg': '成功'
        })
    except Exception as e:
        return JsonResponse({'code': 500, 'msg': f'系统异常: {str(e)}'})


@csrf_exempt
@require_http_methods(['POST', 'GET'])
def get_experiment_pushlet(request):
    """
    GET/POST /api/v1/assessment/pushlet/experiment-pushlet/
    对应 Java ExperimentPushletController.getExperimentPushlet
    
    参数:
        experimentName, schoolId, userType, useTimeUrl, downTime, yunqUrl,
        schoolName, curriculumName, appliId, curriculumId,
        experimentId, userId, postUrl, gxPostUrl
    """
    if request.method == 'POST' and request.body:
        try:
            import json as j
            data = j.loads(request.body)
        except Exception:
            data = {}
    else:
        data = {}

    school_name = data.get('schoolName') or request.GET.get('schoolName') or request.POST.get('schoolName')
    experiment_name = data.get('experimentName') or request.GET.get('experimentName') or request.POST.get('experimentName')
    yunq_url = data.get('yunqUrl') or request.GET.get('yunqUrl') or request.POST.get('yunqUrl')
    appli_id = data.get('appliId') or request.GET.get('appliId') or request.POST.get('appliId')
    curriculum_id = data.get('curriculumId') or request.GET.get('curriculumId') or request.POST.get('curriculumId')
    experiment_id = data.get('experimentId') or request.GET.get('experimentId') or request.POST.get('experimentId')
    user_id = data.get('userId') or request.GET.get('userId') or request.POST.get('userId')
    post_url = data.get('postUrl') or request.GET.get('postUrl') or request.POST.get('postUrl')
    gx_post_url = data.get('gxPostUrl') or request.GET.get('gxPostUrl') or request.POST.get('gxPostUrl')
    use_time_url = data.get('useTimeUrl') or request.GET.get('useTimeUrl') or request.POST.get('useTimeUrl')
    user_type = data.get('userType') or request.GET.get('userType') or request.POST.get('userType')
    school_id = data.get('schoolId') or request.GET.get('schoolId') or request.POST.get('schoolId')
    down_time = data.get('downTime') or request.GET.get('downTime') or request.POST.get('downTime')

    if not all([school_name, experiment_name, yunq_url, appli_id, user_id]):
        return JsonResponse({'code': 400, 'msg': '缺少必填参数'})

    # 1. 检查实验状态
    status_data = _check_experiment_status(school_name, experiment_name, is_experiment=True)
    if not status_data:
        return JsonResponse({'code': 500, 'msg': '检查预约状态失败'})

    state = status_data.get('state', '')
    if state == '':
        return JsonResponse({'code': 500, 'msg': '系统异常'})

    experiment_flag = state.lower() == 'true'

    if not experiment_flag:
        code = status_data.get('code', '500')
        msg_map = {
            '201': '请按学校预约时间上课',
            '202': '请按学校预约的资源进行上课',
            '203': '人数已达上限，请选择其他预约时间进行上课',
            '204': '人数已达上限，请选择其他时间进行上课',
        }
        return JsonResponse({
            'code': int(code) if code.isdigit() else 500,
            'msg': msg_map.get(code, '系统异常')
        })

    # 2. 计算结束时间
    reservated = status_data.get('reservated', '').lower() == 'true'

    if down_time:
        down_time_ms = int(down_time)
    elif reservated:
        timeline = status_data.get('timeline', '')
        if timeline:
            down_time_ms = _date_to_timestamp(timeline)
        else:
            down_time_ms = int((datetime.now() + timedelta(hours=1)).timestamp() * 1000)
    else:
        next_hour = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        down_time_ms = int(next_hour.timestamp() * 1000)

    # 3. SHA-1 签名获取进入 URL
    timestamp = int(time.time() * 1000)
    token = _sha1_sign(EXPERIMENT_SECRET, timestamp)

    try:
        params = (
            f"appliId={appli_id}"
            f"&extraParam.downtime={down_time_ms}"
            f"&extraParam.userId={user_id}"
            f"&extraParam.curriculumId={curriculum_id}"
            f"&extraParam.experimentId={experiment_id}"
            f"&extraParam.baseUrl={post_url}"
            f"&extraParam.experimentOperationType={gx_post_url}"
            f"&codeRate=3000&frameRate=30"
            f"&appKey={ACCESS_KEY}&timestamp={timestamp}&signature={token}"
            f"&extraParam.useTimeUrl={use_time_url}"
            f"&extraParam.userType={user_type}"
            f"&extraParam.schoolId={school_id}"
            f"&extraParam.appliId={appli_id}"
        )
        full_url = f"{yunq_url}{TOKEN_URL}?{params}"
        resp = requests.get(full_url, timeout=15)
        resp.encoding = 'utf-8'
        result = resp.json()
        result_url = result.get('result', '')

        return JsonResponse({
            'code': 101,
            'resultUrl': result_url,
            'msg': '成功'
        })
    except Exception as e:
        return JsonResponse({'code': 500, 'msg': f'系统异常: {str(e)}'})
