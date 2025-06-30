import requests
from requests import HTTPError
import time
import random
import hashlib

# 尝试导入 brotli
try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False

from util.const import *
from .api import *

# 用户代理池
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def get_random_headers():
    """获取随机请求头"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br' if BROTLI_AVAILABLE else 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Referer': 'https://www.zhihu.com/',
        'X-Requested-With': 'XMLHttpRequest',
        # 使用自己的cookie，同时需要确保cookie是最新的，过期的cookie会导致请求失败
        'Cookie': 'Your_Cookie_Here',  # 替换为你的cookie
    }

# 创建Session池
sessions = [requests.Session() for _ in range(3)]
current_session_index = 0

def get_session():
    """轮换Session"""
    global current_session_index
    current_session_index = (current_session_index + 1) % len(sessions)
    return sessions[current_session_index]

def get(url, headers=None, max_retries=5):
    """增强的GET请求函数"""
    # 增加随机延时（更长）
    time.sleep(random.uniform(5, 15))
    
    for attempt in range(max_retries):
        try:
            # 使用随机请求头
            request_headers = get_random_headers()
            if headers:
                request_headers.update(headers)
            
            # 轮换session
            session = get_session()
            
            # 添加随机延时
            if attempt > 0:
                delay = random.uniform(10, 30)  # 更长的重试延时
                print(f"等待 {delay:.1f} 秒后重试...")
                time.sleep(delay)
            
            response = session.get(url, headers=request_headers, timeout=30)
            
            print(f"请求URL: {url}")
            print(f"状态码: {response.status_code}")
            
            # 如果是403，立即休息更长时间
            if response.status_code == 403:
                print("⚠️ 遇到403错误，休息60秒...")
                time.sleep(60)
                continue
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            print(f'请求错误 (尝试 {attempt + 1}/{max_retries})：', e)
            
            # 指数退避，但时间更长
            if attempt < max_retries - 1:
                backoff_time = (2 ** attempt) * 10  # 10, 20, 40, 80秒
                print(f"等待 {backoff_time} 秒后重试...")
                time.sleep(backoff_time)
    
    print(f"❌ 请求最终失败: {url}")
    return None

def get_html(url):
    return get(url)

def get_json(url):
    return get(url)

def answer_spider(answer_id):
    url = answer_api(answer_id)
    return get_json(url)

def answers_spider(question_id, offset, sort_by, limit=LIMIT_SIZE):
    url = all_answers_api(question_id, limit, offset, sort_by)
    return get_json(url)

def user_answers_spider(user_id, offset, sort_by, limit=LIMIT_SIZE):
    url = user_answers_api(user_id, limit, offset, sort_by)
    return get_json(url)

def article_spider(article_id):
    url = article_api(article_id)
    return get_html(url)

def column_spider(column_id, offset, limit=LIMIT_SIZE):
    url = columns_article_api(column_id, limit, offset)
    return get_html(url)

def user_articles_spider(user_id, offset, sort_by, limit=LIMIT_SIZE):
    url = user_articles_api(user_id, offset, limit, sort_by)
    return get_json(url)

def user_column_spider():
    pass

def user_msg_spider(user_id):
    url = user_msg_api(user_id)
    return get_json(url)

def column_msg_spider(column_id):
    url = columns_msg_api(column_id)
    return get_json(url)

def question_msg_spider(question_id):
    url = question_msg_api(question_id)
    return get_json(url)

def article_spider_url(article_id):
    return article_api(article_id)

def topic_essence_spider(topic_id, offset, limit=LIMIT_SIZE):
    url = topic_essence_api(topic_id, offset, limit)
    return get_json(url)

def topic_msg_spider(topic_id):
    url = topic_msg_api(topic_id)
    return get_json(url)

def collection_msg_spider(collection_id):
    url = collection_msg_api(collection_id)
    return get(url)

def collection_spider(collection_id, page):
    url = collection_html_api(collection_id, page)
    return get_html(url)

"""
说明：
    这里定义了用于不同api的网络请求函数，函数统一返回response对象，如果发生网络请求错误会给出可能的错误类型，不会引发
错误。当出错时返回的是None。
"""
