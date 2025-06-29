from flask import Flask, render_template, jsonify
import sqlite3
import pandas as pd
import json
from datetime import datetime
import os

app = Flask(__name__)

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('sichuan_university_zhihu.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    """主仪表板页面"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """获取基础统计数据"""
    conn = get_db_connection()
    
    stats = {}
    tables = ['topics', 'questions', 'users', 'answers', 'topic_details']
    
    for table in tables:
        try:
            cursor = conn.execute(f'SELECT COUNT(*) as count FROM {table}')
            stats[table] = cursor.fetchone()['count']
        except:
            stats[table] = 0
    
    conn.close()
    return jsonify(stats)

@app.route('/api/top-topics')
def get_top_topics():
    """获取热门话题"""
    conn = get_db_connection()
    
    try:
        cursor = conn.execute('''
            SELECT name, followers_count, questions_count 
            FROM topics 
            ORDER BY followers_count DESC 
            LIMIT 10
        ''')
        
        topics = []
        for row in cursor.fetchall():
            topics.append({
                'name': row['name'],
                'followers_count': row['followers_count'],
                'questions_count': row['questions_count']
            })
        
        conn.close()
        return jsonify(topics)
    except Exception as e:
        conn.close()
        return jsonify([])

@app.route('/api/top-users')
def get_top_users():
    """获取活跃用户"""
    conn = get_db_connection()
    
    try:
        cursor = conn.execute('''
            SELECT name, follower_count, answer_count 
            FROM users 
            ORDER BY follower_count DESC 
            LIMIT 10
        ''')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'name': row['name'],
                'follower_count': row['follower_count'],
                'answer_count': row['answer_count']
            })
        
        conn.close()
        return jsonify(users)
    except:
        conn.close()
        return jsonify([])

@app.route('/api/top-questions')
def get_top_questions():
    """获取热门问题"""
    conn = get_db_connection()
    
    try:
        cursor = conn.execute('''
            SELECT title, answer_count, follower_count 
            FROM questions 
            ORDER BY answer_count DESC 
            LIMIT 10
        ''')
        
        questions = []
        for row in cursor.fetchall():
            questions.append({
                'title': row['title'][:50] + ('...' if len(row['title']) > 50 else ''),
                'answer_count': row['answer_count'],
                'follower_count': row['follower_count']
            })
        
        conn.close()
        return jsonify(questions)
    except:
        conn.close()
        return jsonify([])

@app.route('/api/chart-data')
def get_chart_data():
    """获取图表数据"""
    conn = get_db_connection()
    
    data = {
        'follower_distribution': [],
        'answer_distribution': [],
        'topic_distribution': []
    }
    
    try:
        # 话题关注者分布
        cursor = conn.execute('''
            SELECT 
                CASE 
                    WHEN followers_count < 100 THEN '<100'
                    WHEN followers_count < 1000 THEN '100-1K'
                    WHEN followers_count < 10000 THEN '1K-10K'
                    WHEN followers_count < 100000 THEN '10K-100K'
                    ELSE '>100K'
                END as range,
                COUNT(*) as count
            FROM topics 
            WHERE followers_count > 0
            GROUP BY range
        ''')
        
        for row in cursor.fetchall():
            data['follower_distribution'].append({
                'range': row['range'],
                'count': row['count']
            })
        
        # 回答数分布
        cursor = conn.execute('''
            SELECT 
                CASE 
                    WHEN answer_count < 5 THEN '<5'
                    WHEN answer_count < 20 THEN '5-20'
                    WHEN answer_count < 100 THEN '20-100'
                    ELSE '>100'
                END as range,
                COUNT(*) as count
            FROM questions 
            WHERE answer_count > 0
            GROUP BY range
        ''')
        
        for row in cursor.fetchall():
            data['answer_distribution'].append({
                'range': row['range'],
                'count': row['count']
            })
            
    except Exception as e:
        print(f"Error: {e}")
    
    conn.close()
    return jsonify(data)

if __name__ == '__main__':
    # 确保templates文件夹存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=True, host='localhost', port=5000)