import os
import time
import random
import json
from urllib.parse import urlencode
from util.net.net import get

# 在当前目录创建下载文件夹
current_dir = os.path.dirname(os.path.abspath(__file__))
warehouse = os.path.join(current_dir, "downloads")

if not os.path.exists(warehouse):
    os.makedirs(warehouse)

# 原有的单个爬取功能保留
make_as_book = True
answer_id = ''
column_id = ''
article_id = ''
question_id = ''
topic_id = ''
user_id_for_answers = ''
user_id_for_articles = ''
collection_id = ''

def search_topics(keyword, max_results=1000):
    """搜索相关话题"""
    topics = []
    offset = 0
    consecutive_empty = 0
    
    print(f"开始搜索话题: {keyword}")
    
    while len(topics) < max_results:
        try:
            base_url = 'https://www.zhihu.com/api/v4/search_v3'
            params = {
                'q': keyword,
                't': 'topic',
                'correction': '1',
                'offset': offset,
                'limit': 20
            }
            url = f"{base_url}?{urlencode(params)}"
            
            response = get(url)
            
            if response is None or response.status_code != 200:
                print("搜索失败，停止")
                break
                
            data = response.json()
            search_results = data.get('data', [])
            
            new_topics = []
            for item in search_results:
                if item.get('object', {}).get('type') == 'topic':
                    topic_info = item['object']
                    topic_id = topic_info.get('id')
                    # 避免重复
                    if not any(t.get('id') == topic_id for t in topics):
                        new_topics.append({
                            'id': topic_id,
                            'name': topic_info.get('name'),
                            'excerpt': topic_info.get('excerpt', ''),
                            'followers_count': topic_info.get('followers_count', 0),
                            'questions_count': topic_info.get('questions_count', 0),
                            'best_answers_count': topic_info.get('best_answers_count', 0)
                        })
            
            if not new_topics:
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    break
            else:
                consecutive_empty = 0
                topics.extend(new_topics)
                print(f"已获取 {len(topics)} 个话题")
            
            # 检查是否到底
            paging = data.get('paging', {})
            if paging.get('is_end', False):
                break
            
            offset += 20
            if offset > 500:  # 话题数量通常较少
                break
            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"解析搜索结果失败: {e}")
            break
    
    return topics[:max_results]

def search_questions(keyword, max_results=5000):
    """搜索相关问题 - 改为从回答中提取问题"""
    questions = []
    questions_dict = {}
    offset = 0
    consecutive_empty = 0
    
    print(f"开始搜索问题: {keyword} (通过回答提取)")
    
    while len(questions) < max_results:
        try:
            base_url = 'https://www.zhihu.com/api/v4/search_v3'
            params = {
                'q': keyword,
                't': 'general',
                'correction': '1',
                'offset': offset,
                'limit': 20
            }
            url = f"{base_url}?{urlencode(params)}"
            
            print(f"请求 offset={offset}, 已有问题: {len(questions)}")
            response = get(url)
            
            if response is None or response.status_code != 200:
                print("搜索失败")
                break
                
            data = response.json()
            search_results = data.get('data', [])
            
            new_questions_count = 0
            for item in search_results:
                obj = item.get('object', {})
                obj_type = obj.get('type')
                
                if obj_type == 'answer':
                    question_info = obj.get('question', {})
                    if question_info:
                        question_id = question_info.get('id')
                        if question_id and question_id not in questions_dict:
                            question_data = {
                                'id': question_id,
                                'title': question_info.get('title', ''),
                                'excerpt': question_info.get('excerpt', ''),
                                'answer_count': question_info.get('answer_count', 0),
                                'follower_count': question_info.get('follower_count', 0),
                                'visit_count': question_info.get('visit_count', 0),
                                'created': question_info.get('created'),
                                'updated_time': question_info.get('updated_time')
                            }
                            questions_dict[question_id] = question_data
                            questions.append(question_data)
                            new_questions_count += 1
            
            if new_questions_count == 0:
                consecutive_empty += 1
                print(f"本次无新问题，连续空结果: {consecutive_empty}")
                
                if consecutive_empty >= 5:
                    print("✓ 连续多次无新数据，搜索完成")
                    break
                    
            else:
                consecutive_empty = 0
                print(f"✓ 已获取 {len(questions)} 个问题 (本次新增: {new_questions_count})")
            
            paging = data.get('paging', {})
            if paging.get('is_end', False):
                print("✓ API返回已到末页，搜索完成")
                break
            
            offset += 20
            
            if offset > 2000:  # 从1000增加到2000
                print("✓ 达到搜索深度限制，停止搜索")
                break
            
            time.sleep(random.uniform(1, 2))
            
        except KeyboardInterrupt:
            print("✓ 用户中断，保存已获取的数据")
            break
        except Exception as e:
            print(f"搜索出错: {e}")
            break
    
    print(f"问题搜索完成，共获取 {len(questions)} 个问题")
    return questions[:max_results]

def search_users(keyword, max_results=2000):
    """搜索相关用户"""
    users = []
    offset = 0
    consecutive_empty = 0
    
    print(f"开始搜索用户: {keyword}")
    
    while len(users) < max_results:
        try:
            base_url = 'https://www.zhihu.com/api/v4/search_v3'
            params = {
                'q': keyword,
                't': 'people',
                'correction': '1',
                'offset': offset,
                'limit': 20
            }
            url = f"{base_url}?{urlencode(params)}"
            
            response = get(url)
            
            if response is None or response.status_code != 200:
                print("搜索用户失败")
                break
                
            data = response.json()
            search_results = data.get('data', [])
            
            new_users = []
            for item in search_results:
                obj = item.get('object', {})
                if obj.get('type') == 'people':
                    user_id = obj.get('id')
                    if not any(u.get('id') == user_id for u in users):
                        new_users.append({
                            'id': user_id,
                            'url_token': obj.get('url_token'),
                            'name': obj.get('name'),
                            'headline': obj.get('headline', ''),
                            'description': obj.get('description', ''),
                            'follower_count': obj.get('follower_count', 0),
                            'following_count': obj.get('following_count', 0),
                            'answer_count': obj.get('answer_count', 0),
                            'question_count': obj.get('question_count', 0),
                            'articles_count': obj.get('articles_count', 0)
                        })
            
            if not new_users:
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    break
            else:
                consecutive_empty = 0
                users.extend(new_users)
                print(f"已获取 {len(users)} 个用户")
            
            paging = data.get('paging', {})
            if paging.get('is_end', False):
                break
                
            offset += 20
            if offset > 1500:  # 从800增加到1500
                break
            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"搜索用户失败: {e}")
            break
    
    return users

def search_answers(keyword, max_results=2000):
    """搜索相关回答"""
    answers = []
    offset = 0
    consecutive_empty = 0
    
    print(f"开始搜索回答: {keyword}")
    
    while len(answers) < max_results:
        try:
            base_url = 'https://www.zhihu.com/api/v4/search_v3'
            params = {
                'q': keyword,
                't': 'general',
                'correction': '1',
                'offset': offset,
                'limit': 20
            }
            url = f"{base_url}?{urlencode(params)}"
            
            response = get(url)
            
            if response is None or response.status_code != 200:
                break
                
            data = response.json()
            search_results = data.get('data', [])
            
            new_answers = []
            for item in search_results:
                obj = item.get('object', {})
                if obj.get('type') == 'answer':
                    answer_info = {
                        'id': obj.get('id'),
                        'question_id': obj.get('question', {}).get('id'),
                        'author_id': obj.get('author', {}).get('id'),
                        'author_name': obj.get('author', {}).get('name'),
                        'content': obj.get('content', ''),
                        'voteup_count': obj.get('voteup_count', 0),
                        'comment_count': obj.get('comment_count', 0),
                        'created_time': obj.get('created_time'),
                        'updated_time': obj.get('updated_time')
                    }
                    
                    if not any(a.get('id') == answer_info['id'] for a in answers):
                        new_answers.append(answer_info)
            
            if not new_answers:
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    break
            else:
                consecutive_empty = 0
                answers.extend(new_answers)
                print(f"已获取 {len(answers)} 个回答")
            
            paging = data.get('paging', {})
            if paging.get('is_end', False):
                break
                
            offset += 20
            if offset > 1000:
                break
            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"搜索回答失败: {e}")
            break
    
    return answers[:max_results]

def search_articles(keyword, max_results=1000):
    """搜索相关文章"""
    articles = []
    offset = 0
    
    print(f"开始搜索文章: {keyword}")
    
    while len(articles) < max_results:
        try:
            base_url = 'https://www.zhihu.com/api/v4/search_v3'
            params = {
                'q': keyword,
                't': 'content',  # 搜索内容类型
                'correction': '1',
                'offset': offset,
                'limit': 20
            }
            url = f"{base_url}?{urlencode(params)}"
            
            response = get(url)
            if response is None or response.status_code != 200:
                break
                
            data = response.json()
            search_results = data.get('data', [])
            
            if not search_results:
                break
                
            for item in search_results:
                obj = item.get('object', {})
                if obj.get('type') == 'article':
                    articles.append({
                        'id': obj.get('id'),
                        'title': obj.get('title'),
                        'excerpt': obj.get('excerpt', ''),
                        'author_id': obj.get('author', {}).get('id'),
                        'author_name': obj.get('author', {}).get('name'),
                        'voteup_count': obj.get('voteup_count', 0),
                        'comment_count': obj.get('comment_count', 0)
                    })
            
            offset += 20
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"搜索文章失败: {e}")
            break
    
    return articles

def search_columns(keyword, max_results=500):
    """搜索相关专栏"""
    columns = []
    offset = 0
    
    print(f"开始搜索专栏: {keyword}")
    
    while len(columns) < max_results:
        try:
            base_url = 'https://www.zhihu.com/api/v4/search_v3'
            params = {
                'q': keyword,
                't': 'column',
                'correction': '1',
                'offset': offset,
                'limit': 20
            }
            url = f"{base_url}?{urlencode(params)}"
            
            response = get(url)
            if response is None or response.status_code != 200:
                break
                
            data = response.json()
            search_results = data.get('data', [])
            
            if not search_results:
                break
                
            for item in search_results:
                obj = item.get('object', {})
                if obj.get('type') == 'column':
                    columns.append({
                        'id': obj.get('id'),
                        'title': obj.get('title'),
                        'description': obj.get('description', ''),
                        'author_id': obj.get('author', {}).get('id'),
                        'author_name': obj.get('author', {}).get('name'),
                        'followers': obj.get('followers', 0),
                        'articles_count': obj.get('articles_count', 0)
                    })
            
            offset += 20
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"搜索专栏失败: {e}")
            break
    
    return columns

# 原有的单个爬取逻辑保留
if user_id_for_answers != '':
    from zhihu.user import user_answers
    user_answers(user_id_for_answers, warehouse)

if user_id_for_articles != '':
    from zhihu.user import user_articles
    user_articles(user_id_for_articles, warehouse)

if column_id != '':
    from zhihu.article import articles
    articles(column_id, warehouse)

if article_id != '':
    from zhihu.article import article
    a = article(article_id, warehouse)
    print(a)

if question_id != '':
    if not make_as_book:
        from zhihu.question import answers
        a = answers(question_id, warehouse)
    else:
        from zhihu.question import make_answers_as_book
        a = make_answers_as_book(question_id, warehouse)

if answer_id != '':
    from zhihu.question import answer
    a = answer(answer_id, warehouse)
    print(a)

if topic_id != '':
    from zhihu.topic import topic_essence
    topic_essence(topic_id, warehouse)

if collection_id != '':
    from zhihu.collection import collection
    collection(collection_id, warehouse)

# 搜索功能入口（仅在直接运行时启用）
if __name__ == "__main__":
    # 如果没有设置具体ID，则启动搜索模式
    if not any([user_id_for_answers, user_id_for_articles, column_id, 
                article_id, question_id, answer_id, topic_id, collection_id]):
        
        # 简单测试
        print("测试搜索功能...")
        topics = search_topics("四川大学", max_results=5)
        print(f"测试结果: 获取到 {len(topics)} 个话题")
        
        if topics:
            print("前3个话题:")
            for i, topic in enumerate(topics[:3]):
                print(f"  {i+1}. {topic.get('name')} (关注者: {topic.get('followers_count')})")


