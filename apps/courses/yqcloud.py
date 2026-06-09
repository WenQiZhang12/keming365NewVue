# -*- coding: utf-8 -*-
"""
apps.courses.yqcloud - 云渲染平台对接模块

翻译自 Java YQPathController，用于获取 Unity/3D 实验的运行 URL。

流程:
  1. 接收前端请求参数（experimentId, curriculumId, userId 等）
  2. 根据资源类型选择对应的 appKey/appSecret
  3. 生成 SHA-1 签名（appKey + appSecret + timestamp 排序后加密）
  4. 向云渲染平台 Token URL 发送 GET 请求
  5. 返回 resultUrl 给前端嵌入 iframe 或 window.open
"""

import hashlib
import logging
import time
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from django.conf import settings

logger = logging.getLogger(__name__)


def get_yq_path(
    token_url: str = None,
    app_key: str = None,
    app_secret: str = None,
    appli_id: str = None,
    curriculum_id: str = None,
    experiment_id: str = None,
    user_id: str = None,
    post_url: str = None,
    use_time_url: str = None,
    school_id: str = None,
    user_type: str = None,
    resource_type: str = 'experiment',
    code_rate: str = '8000',
) -> dict:
    """
    获取云渲染实验路径

    参数说明：
        token_url   - 云渲染平台 Token 接口地址
        app_key     - 应用 Key
        app_secret  - 应用 Secret
        appli_id    - 应用 ID（tb_experiment.appliId）
        curriculum_id - 课程 ID
        experiment_id - 实验 ID
        user_id     - 用户 ID
        post_url    - 成绩上报地址
        use_time_url - 使用时长上报地址
        school_id   - 学校 ID
        user_type   - 用户类型
        resource_type - 资源类型（experiment/fragment/training），用于选择密钥
        code_rate   - 码率（默认 6000）

    返回：
        {
            'code': 0,          # 0=成功, 1=缺少参数, 2=云平台错误
            'resultUrl': '...',  # 实验访问 URL
            'token': '...',      # 签名 token
            'timestamp': 123,    # 时间戳
            'msg': '...',        # 消息
        }
    """
    # 参数验证
    required_params = {
        'token_url': token_url,
        'app_key': app_key,
        'app_secret': app_secret,
        'appli_id': appli_id,
        'curriculum_id': curriculum_id,
        'experiment_id': experiment_id,
        'user_id': user_id,
        'post_url': post_url,
        'use_time_url': use_time_url,
        'school_id': school_id,
        'user_type': user_type,
    }

    for name, value in required_params.items():
        if not value:
            return _error(1, f'缺少必要参数: {name}')

    try:
        timestamp = int(time.time() * 1000)

        # SHA-1 签名: 对 appKey, appSecret, timestamp 排序后拼接加密
        sorted_params = sorted([app_key, app_secret, str(timestamp)])
        sign_str = ''.join(sorted_params)
        signature = hashlib.sha1(sign_str.encode('utf-8')).hexdigest().upper()

        # 构建请求参数
        public_ip = getattr(settings, 'YQ_PUBLIC_IP', '58.56.66.170')
        query_params = {
            'appliId': appli_id,
            'preferPublicIp': public_ip,
            'codeRate': code_rate,
            'frameRate': '30',
            'appKey': app_key,
            'timestamp': str(timestamp),
            'signature': signature,
            'extraParam.userId': user_id,
            'extraParam.curriculumId': curriculum_id,
            'extraParam.experimentId': experiment_id,
            'extraParam.baseUrl': post_url,
            'extraParam.useTimeUrl': use_time_url,
            'extraParam.schoolId': school_id,
            'extraParam.userType': user_type,
        }

        request_url = f'{token_url}/appli/getStartURL?{urlencode(query_params)}'
        logger.info(f'YQCloud request: {request_url[:200]}...')

        # 发送请求
        req = Request(request_url, headers={
            'Accept': '*/*',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
        })

        with urlopen(req, timeout=30) as response:
            result = response.read().decode('utf-8')

        logger.info(f'YQCloud response: {result[:300]}')

        # 解析 JSON 响应
        import json
        data = json.loads(result)
        code = str(data.get('code', ''))
        msg = data.get('message', '')

        if code == '500':
            return _error(2, msg)

        result_url = data.get('result', '')

        # 替换云雀平台内网 IP 为公网域名，确保前端可正常访问
        token_url_host = token_url.rstrip('/')
        YQ_INTERNAL_HOSTS = [
            token_url_host,
            f'http://{public_ip}:8181',
            f'https://{public_ip}:8181',
            f'http://{public_ip}',
            f'https://{public_ip}',
        ]
        for internal_host in YQ_INTERNAL_HOSTS:
            if result_url.startswith(internal_host):
                logger.info(f'Stripping internal host: {internal_host}')
                result_url = result_url[len(internal_host):]
                break

        logger.info(f'Final resultUrl path: {result_url[:200]}')

        return {
            'code': 0,
            'resultUrl': result_url,
            'token': signature,
            'timestamp': timestamp,
            'msg': msg,
        }

    except Exception as e:
        logger.error(f'YQCloud error: {e}', exc_info=True)
        return _error(2, f'云平台请求失败: {str(e)}')


def get_yq_path_from_experiment(experiment, user, request=None) -> dict:
    """
    根据实验对象和用户自动获取云渲染路径

    参数：
        experiment - TbExperiment 实例
        user       - TbUser 实例（当前用户）
        request    - HttpRequest（用于获取 base_url）

    返回：
        同 get_yq_path 的返回格式
    """
    from django.conf import settings

    # 确定资源类型和密钥
    resource_type = 'experiment'
    # 工训课程 ID 列表（从 Java 后端逻辑转换）
    training_curriculum_ids = {10, 11, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48}

    # 通过 TbExperimentReport 获取 curriculumId
    from apps.courses.models import TbExperimentReport
    report = TbExperimentReport.objects.filter(experimentId=experiment.id).first()
    curriculum_id = str(report.curriculumId) if report and report.curriculumId else ''

    # 兆底：直接从实验记录的 parentId 获取（即课程 ID）
    if not curriculum_id:
        curriculum_id = str(getattr(experiment, 'parentId', '') or '')

    if curriculum_id and curriculum_id.isdigit() and int(curriculum_id) in training_curriculum_ids:
        resource_type = 'training'
    elif getattr(experiment, 'type', 0) == 1:
        resource_type = 'fragment'

    config = settings.YQ_CLOUD_CONFIGS.get(resource_type, settings.YQ_CLOUD_CONFIGS['experiment'])

    # 构建 base_url（成绩上报地址）
    if request:
        base_url = f'{request.scheme}://{request.get_host()}'
    else:
        base_url = 'http://localhost:8000'

    result = get_yq_path(
        token_url=settings.YQ_TOKEN_URL,
        app_key=config['appKey'],
        app_secret=config['appSecret'],
        appli_id=experiment.appliId,
        curriculum_id=curriculum_id,
        experiment_id=experiment.id,
        user_id=user.id,
        post_url=settings.YQ_SCORE_URL,
        use_time_url=settings.YQ_USAGE_URL,
        school_id=str(getattr(user, 'schoolId', '') or ''),
        user_type=str(getattr(user, 'type', '0') or '0'),
        resource_type=resource_type,
    )
    # 将 appKey 一并返回给前端，用于拼接最终 URL
    if result['code'] == 0:
        result['appKey'] = config['appKey']
    return result


def _error(code: int, msg: str) -> dict:
    """生成错误返回"""
    return {
        'code': code,
        'resultUrl': '',
        'token': '',
        'timestamp': 0,
        'msg': msg,
    }
