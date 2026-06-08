# -*- coding: utf-8 -*-
"""
ShowPPT - PPT/VR 资源展示入口
对应 Java: ShowPPTController
提供云雀 VR 资源的 URL 跳转（SHA-1 签名 + 多组密钥 Fallback）
"""

import hashlib
import time
from urllib.parse import quote

import requests
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.accounts.models import TbUser

# ====== 配置 ======
TOKEN_URL_TEMPLATE = "{yunq_url}/appli/getStartURL"
ACCESS_KEYS = [
    ("Jx3wQMD1", "6cdf1d37d5fb4d46a117b399c092cd24"),       # 默认密钥
    ("VUuNRF8L", "e7ab133dda24473da613c8927269166b"),       # 备份密钥1
    ("DrcnSVZZ", "aadb5f80872c4f6286217b952781d559"),       # 备份密钥2
]
DEFAULT_YUNQ_URL = "http://58.56.66.170:8181"
PROD_YUNQ_URL = "https://yq.keming365.com:8181"


def _sha1_sign(access_key: str, secret: str, timestamp: int) -> str:
    """SHA-1 签名"""
    arr = sorted([access_key, secret, str(timestamp)])
    raw = ''.join(arr)
    return hashlib.sha1(raw.encode('utf-8')).hexdigest().upper()


def _request_start_url(yunq_url: str, appli_id: str, access_key: str, secret: str) -> dict:
    """向云雀 API 请求资源启动 URL"""
    timestamp = int(time.time() * 1000)
    token = _sha1_sign(access_key, secret, timestamp)

    url = f"{yunq_url}/appli/getStartURL"
    params = (
        f"appliId={appli_id}"
        f"&codeRate=3000&frameRate=30"
        f"&appKey={access_key}&timestamp={timestamp}&signature={token}"
    )
    try:
        resp = requests.get(f"{url}?{params}", timeout=15)
        resp.encoding = 'utf-8'
        data = resp.json()
        return {
            'success': data.get('code') != '500',
            'data': data,
            'access_key': access_key,
            'secret': secret,
            'timestamp': timestamp,
            'token': token,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _try_start_url(appli_id: str, yunq_url: str = DEFAULT_YUNQ_URL) -> dict:
    """依次尝试多组密钥，直到成功"""
    for access_key, secret in ACCESS_KEYS:
        result = _request_start_url(yunq_url, appli_id, access_key, secret)
        if result['success']:
            return result
        # 检查错误消息是否包含 appKey（需要切换密钥）
        data = result.get('data', {})
        message = data.get('message', '')
        if 'appKey' not in message:
            return result  # 非 appKey 错误，直接返回
    # 全部失败
    return result


def _build_redirect_url(result: dict, prod_domain: str = None) -> str:
    """构建跳转 URL（替换内网地址为公网域名）"""
    data = result['data']
    result_url = data.get('result', '').strip('"')

    # 替换内网地址
    if prod_domain:
        result_url = result_url.replace("58.56.66.170", prod_domain)
        result_url = f"{prod_domain}{result_url}" if result_url.startswith(':') else result_url

    # 追加签名参数
    result_url += f"&appKey={result['access_key']}&timestamp={result['timestamp']}&signature={result['token']}"
    return result_url


@csrf_exempt
@require_http_methods(['GET'])
def show_ppt(request):
    """
    GET /api/v1/assessment/show-ppt/
    打开云雀资源（PPT/VR）
    对应 Java: /user/showPPT
    
    参数: appliId, curriculumId(可选), experimentId(可选), userId(可选)
    """
    appli_id = request.GET.get('appliId')
    if not appli_id:
        return JsonResponse({'code': 400, 'msg': '缺少 appliId'})

    result = _try_start_url(appli_id)
    if not result['success']:
        return JsonResponse({'msg': result.get('data', {}).get('message', '获取资源地址失败')})

    redirect_url = _build_redirect_url(result, prod_domain="yq.keming365.com")
    return HttpResponseRedirect(redirect_url)


@csrf_exempt
@require_http_methods(['GET'])
def show_ppt_by_qrcode(request):
    """
    GET /api/v1/assessment/show-ppt/qrcode/
    用户扫码打开资源
    对应 Java: /user/showPPTByQRCODE
    
    参数: appliId
    """
    appli_id = request.GET.get('appliId')
    if not appli_id:
        return JsonResponse({'code': 400, 'msg': '缺少 appliId'})

    redirect_url = f"https://www.keming365.com/cgzt/api/materials/{appli_id}"
    return HttpResponseRedirect(redirect_url)


@csrf_exempt
@require_http_methods(['GET'])
def scan_qrcode(request):
    """
    GET /api/v1/assessment/show-ppt/scan-qrcode/
    扫码登录后打开资源
    对应 Java: /user/scanQRCode
    
    参数: appliId, type(1=PPT, other=VR)
    从 Cookie access_token 获取用户身份
    """
    appli_id = request.GET.get('appliId')
    scan_type = request.GET.get('type')

    if not appli_id or not scan_type:
        return JsonResponse({'code': 400, 'msg': '缺少参数'})

    # 从 Cookie 获取 access_token
    access_id = request.COOKIES.get('access_token')
    if not access_id:
        redirect_url = f"http://www.keming365.com/login?appliId={appli_id}&type={scan_type}"
        return HttpResponseRedirect(redirect_url)

    # 验证用户
    try:
        user = TbUser.objects.get(pk=access_id)
    except TbUser.DoesNotExist:
        redirect_url = f"http://www.keming365.com/login?appliId={appli_id}&type={scan_type}"
        return HttpResponseRedirect(redirect_url)

    account_type = user.accountType or 0

    if scan_type == '1':
        # PPT 类型 - 取云雀 URL 并跳转
        result = _try_start_url(appli_id)
        if result['success']:
            data = result['data']
            result_url = data.get('result', '').strip('"')
            result_url += f"&appKey={result['access_key']}&timestamp={result['timestamp']}&signature={result['token']}"
            result_url = f"http://58.56.66.170:8181{result_url}"
            return HttpResponseRedirect(result_url)
        else:
            # 显示错误消息页面
            message = result.get('data', {}).get('message', '获取资源失败')
            html = _error_page(message)
            return HttpResponse(html, content_type='text/html;charset=utf-8')
    else:
        # 非 PPT 类型
        if account_type == 3:
            html = _error_page('暂无权限')
            return HttpResponse(html, content_type='text/html;charset=utf-8')

        result = _try_start_url(appli_id)
        if result['success']:
            data = result['data']
            result_url = data.get('result', '').strip('"')
            result_url += f"&appKey={result['access_key']}&timestamp={result['timestamp']}&signature={result['token']}"
            result_url = result_url.replace("58.56.66.170", "yq.keming365.com")
            result_url = f"http://yq.keming365.com:8181{result_url}"
            return HttpResponseRedirect(result_url)
        else:
            message = result.get('data', {}).get('message', '获取资源失败')
            html = _error_page(message)
            return HttpResponse(html, content_type='text/html;charset=utf-8')


def _error_page(message: str) -> str:
    """生成显示错误消息的 HTML 页面"""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src='http://www.keming365.com/js/jquery-2.0.0.js'></script>
<link rel='stylesheet' type='text/css' href='http://www.keming365.com/js/layer/theme/default/layer.css'>
<script src='http://www.keming365.com/js/jquery.md5.js'></script>
<script src='http://www.keming365.com/js/layer/layer.js'></script>
</head>
<body>
<script language="javascript">
$(function () {{
    layer.msg("{message}", {{icon: 6}})
}})
</script>
</body>
</html>"""
