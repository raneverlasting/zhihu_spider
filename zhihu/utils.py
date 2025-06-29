import requests
import time
import random

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.zhihu.com/',
        'Cookie': '_zap=8011985a-542c-4f1b-86cf-c64506e393a4; _xsrf=EKYdN1Fw8ihMAlYePVVZO1wZItVWlVxb; d_c0=ARCS-VKwWhmPTu3QiltDvK3ZXI2AcHoGDIU=|1728362749; q_c1=24a4a167a9fd45049cef12fecefeb9d3|1737654258000|1737654258000; edu_user_uuid=edu-v1|3523570c-df26-4d48-9500-fd1a2f4ae670; z_c0=2|1:0|10:1749197536|4:z_c0|80:MS4xMVJRYk9nQUFBQUFtQUFBQVlBSlZUZUR3TDJtNFdQY0EydkV1QmlKTndpRWZSZng2cEFfSFBRPT0=|8e60970e031e5b3e723a30e3345c066710f89ba0f138a3f280f0038717155faf; __zse_ck=004_q3dn94INyIxO2EKZBxWWIc2TQK9wDqXDdGZWkyB/2Y=NohKGZL2JewV7cGaLpmFDTHGFtftjztqB8VQqwHB3iUHr6bVW5mHFMtrEDx20kb==F4vmY2d8yUjtH1H3eGjB-EPk+u6lAXnhxcMfL44U1rAnrYNHm4W3edXpPozqAvhZmScw/u36Elw9QPSHCmeluYDdJyumptaMkR0aDGffPzwhy/SGkAH0kaKfmOjukTuUL0zt8eL2LCl3qF3tEL4mq; cap_id="ZDU5MWFkYjM5M2NmNDk2MTgxMjgzMDhmNzgzMWM3Y2U=|1750058336|c4b05e887b769f7949b02bf6c596ca3df675679f"; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1749791327,1750044307,1750054049,1750059883; HMACCOUNT=6745494431B8B726; tst=r; BEC=d6322fc1daba6406210e61eaa4ec5a7a; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1750060107'
    }

# 创建全局session
session = requests.Session()
session.headers.update(get_headers())

def safe_request(url, max_retries=3):
    """统一的网络请求函数"""
    for attempt in range(max_retries):
        try:
            # 添加随机延时
            time.sleep(random.uniform(1, 3))
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
    return None