"""共享 HTTP 客户端：带自动重试与连接池，用于缓解偶发的 SSL / 网络抖动。

所有模块统一从这里导入 get / post，避免在每个调用点各自处理重试。
核心收益：服务端偶发重置 TLS 连接（SSLEOFError / UNEXPECTED_EOF_WHILE_READING）
会在退避后自动重试，不再直接抛异常导致界面崩溃。
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 单次请求默认超时（秒）。具体调用仍可显式覆盖。
DEFAULT_TIMEOUT = 30


def _build_session():
    session = requests.Session()

    # 连接错误、读取错误（含 SSL 中途 EOF）、以及 5xx / 429 都会重试。
    # 注意 allowed_methods 必须包含 POST，否则 urllib3 默认不对 POST 重试。
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(
            ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
        ),
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=10,
        pool_maxsize=10,
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


session = _build_session()


def get(url, **kwargs):
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    return session.get(url, **kwargs)


def post(url, **kwargs):
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    return session.post(url, **kwargs)
