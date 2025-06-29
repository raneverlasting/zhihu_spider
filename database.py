import sqlite3
import os
from datetime import datetime

class ZhihuDatabase:
    def __init__(self, db_name="sichuan_university_zhihu.db"):
        self.db_path = os.path.join(os.getcwd(), db_name)
        self.init_database()
        print("数据库初始化完成")
    
    def init_database(self):
        """初始化完整的数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. 话题表（扩展字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id TEXT PRIMARY KEY,
                name TEXT,
                excerpt TEXT,
                introduction TEXT,
                followers_count INTEGER,
                questions_count INTEGER,
                best_answers_count INTEGER,
                view_count INTEGER,
                avatar_url TEXT,
                collected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. 用户表（完整用户信息）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                url_token TEXT,
                name TEXT,
                headline TEXT,
                description TEXT,
                avatar_url TEXT,
                gender INTEGER,
                follower_count INTEGER,
                following_count INTEGER,
                answer_count INTEGER,
                question_count INTEGER,
                articles_count INTEGER,
                voteup_count INTEGER,
                thanked_count INTEGER,
                favorited_count INTEGER,
                hosted_live_count INTEGER,
                participated_live_count INTEGER,
                locations TEXT,
                business TEXT,
                employments TEXT,
                educations TEXT,
                collected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 3. 问题表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                excerpt TEXT,
                author_id TEXT,
                author_name TEXT,
                answer_count INTEGER,
                follower_count INTEGER,
                visit_count INTEGER,
                comment_count INTEGER,
                created_time INTEGER,
                updated_time INTEGER,
                collected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 4. 回答表（扩展字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id TEXT PRIMARY KEY,
                question_id TEXT,
                author_id TEXT,
                author_name TEXT,
                content TEXT,
                excerpt TEXT,
                voteup_count INTEGER,
                comment_count INTEGER,
                thanks_count INTEGER,
                created_time INTEGER,
                updated_time INTEGER,
                is_copyable BOOLEAN,
                reward_info TEXT,
                collected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 5. 评论表（新增）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY,
                content_type TEXT,
                content_id TEXT,
                author_id TEXT,
                author_name TEXT,
                content TEXT,
                like_count INTEGER,
                dislike_count INTEGER,
                reply_to_author_id TEXT,
                reply_to_author_name TEXT,
                created_time INTEGER,
                collected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 6. 文章表（新增）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                excerpt TEXT,
                author_id TEXT,
                author_name TEXT,
                voteup_count INTEGER,
                comment_count INTEGER,
                created_time INTEGER,
                updated_time INTEGER,
                collected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 7. 用户关注关系表（新增）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_follows (
                follower_id TEXT,
                followee_id TEXT,
                followee_name TEXT,
                followee_headline TEXT,
                follow_time INTEGER,
                collected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (follower_id, followee_id)
            )
        ''')
        
        # 8. 用户动态表（新增）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activities (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                user_name TEXT,
                activity_type TEXT,
                target_type TEXT,
                target_id TEXT,
                target_title TEXT,
                created_time INTEGER,
                collected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 9. 话题详情表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topic_details (
                topic_id TEXT PRIMARY KEY,
                introduction TEXT,
                avatar_url TEXT,
                best_answerers TEXT,
                unanswered_count INTEGER,
                collected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_topics(self, topics):
        """插入话题数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for topic in topics:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO topics 
                    (id, name, excerpt, followers_count, questions_count, best_answers_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    str(topic.get('id')),
                    topic.get('name'),
                    topic.get('excerpt'),
                    topic.get('followers_count', 0),
                    topic.get('questions_count', 0),
                    topic.get('best_answers_count', 0)
                ))
            except Exception as e:
                print(f"插入话题失败: {e}")
                continue
        
        conn.commit()
        conn.close()
        print(f"插入 {len(topics)} 条话题数据")
    
    def insert_questions(self, questions):
        """插入问题数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for question in questions:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO questions 
                    (id, title, excerpt, answer_count, follower_count, visit_count, created_time, updated_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(question.get('id')),
                    question.get('title'),
                    question.get('excerpt'),
                    question.get('answer_count', 0),
                    question.get('follower_count', 0),
                    question.get('visit_count', 0),
                    question.get('created'),
                    question.get('updated_time')
                ))
            except Exception as e:
                print(f"插入问题失败: {e}")
                continue
        
        conn.commit()
        conn.close()
        print(f"插入 {len(questions)} 条问题数据")
    
    def insert_users(self, users):
        """插入用户数据（扩展版）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for user in users:
            try:
                # 处理复杂字段
                locations = str(user.get('locations', []))
                employments = str(user.get('employments', []))
                educations = str(user.get('educations', []))
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (id, url_token, name, headline, description, avatar_url, gender,
                     follower_count, following_count, answer_count, question_count, articles_count,
                     voteup_count, thanked_count, favorited_count, locations, business, employments, educations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(user.get('id')),
                    user.get('url_token'),
                    user.get('name'),
                    user.get('headline'),
                    user.get('description'),
                    user.get('avatar_url'),
                    user.get('gender', -1),
                    user.get('follower_count', 0),
                    user.get('following_count', 0),
                    user.get('answer_count', 0),
                    user.get('question_count', 0),
                    user.get('articles_count', 0),
                    user.get('voteup_count', 0),
                    user.get('thanked_count', 0),
                    user.get('favorited_count', 0),
                    locations,
                    user.get('business', ''),
                    employments,
                    educations
                ))
            except Exception as e:
                print(f"插入用户失败: {e}")
                continue
        
        conn.commit()
        conn.close()
        print(f"插入 {len(users)} 条用户数据")
    
    def insert_answers(self, answers):
        """插入回答数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for answer in answers:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO answers 
                    (id, question_id, author_id, author_name, content, voteup_count, comment_count, created_time, updated_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(answer.get('id')),
                    str(answer.get('question_id', '')),
                    str(answer.get('author_id', '')),
                    answer.get('author_name'),
                    answer.get('content'),
                    answer.get('voteup_count', 0),
                    answer.get('comment_count', 0),
                    answer.get('created_time'),
                    answer.get('updated_time')
                ))
            except Exception as e:
                print(f"插入回答失败: {e}")
                continue
        
        conn.commit()
        conn.close()
        print(f"插入 {len(answers)} 条回答数据")
    
    def insert_topic_details(self, topic_details):
        """插入话题详情数据（修改为兼容版本）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for detail in topic_details:
            try:
                # 修改：移除avatar_url字段，避免数据库错误
                cursor.execute('''
                    INSERT OR REPLACE INTO topic_details 
                    (topic_id, introduction, best_answerers, unanswered_count)
                    VALUES (?, ?, ?, ?)
                ''', (
                    str(detail.get('topic_id')),
                    detail.get('introduction'),
                    detail.get('best_answerers'),
                    detail.get('unanswered_count', 0)
                ))
            except Exception as e:
                print(f"插入话题详情失败: {e}")
                continue
        
        conn.commit()
        conn.close()
        print(f"插入 {len(topic_details)} 条话题详情数据")
    
    def insert_comments(self, comments):
        """插入评论数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for comment in comments:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO comments 
                    (id, content_type, content_id, author_id, author_name, content, 
                     like_count, dislike_count, reply_to_author_id, reply_to_author_name, created_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(comment.get('id')),
                    comment.get('content_type'),
                    str(comment.get('content_id')),
                    str(comment.get('author_id', '')),
                    comment.get('author_name'),
                    comment.get('content'),
                    comment.get('like_count', 0),
                    comment.get('dislike_count', 0),
                    str(comment.get('reply_to_author_id', '')),
                    comment.get('reply_to_author_name'),
                    comment.get('created_time')
                ))
            except Exception as e:
                print(f"插入评论失败: {e}")
                continue
        
        conn.commit()
        conn.close()
        print(f"插入 {len(comments)} 条评论数据")
    
    def insert_user_follows(self, follows):
        """插入用户关注关系数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for follow in follows:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO user_follows 
                    (follower_id, followee_id, followee_name, followee_headline, follow_time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    str(follow.get('follower_id')),
                    str(follow.get('followee_id')),
                    follow.get('followee_name'),
                    follow.get('followee_headline'),
                    follow.get('follow_time')
                ))
            except Exception as e:
                print(f"插入关注关系失败: {e}")
                continue
        
        conn.commit()
        conn.close()
        print(f"插入 {len(follows)} 条关注关系数据")
    
    def insert_user_activities(self, activities):
        """插入用户动态数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for activity in activities:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO user_activities 
                    (id, user_id, user_name, activity_type, target_type, target_id, target_title, created_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(activity.get('id')),
                    str(activity.get('user_id')),
                    activity.get('user_name'),
                    activity.get('activity_type'),
                    activity.get('target_type'),
                    str(activity.get('target_id', '')),
                    activity.get('target_title'),
                    activity.get('created_time')
                ))
            except Exception as e:
                print(f"插入用户动态失败: {e}")
                continue
        
        conn.commit()
        conn.close()
        print(f"插入 {len(activities)} 条用户动态数据")
    
    def get_statistics(self):
        """获取完整统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        tables = ['topics', 'questions', 'users', 'answers', 'comments', 
                 'articles', 'user_follows', 'user_activities', 'topic_details']
        
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = 0
        
        conn.close()
        return stats