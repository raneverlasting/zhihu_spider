import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import jieba

plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False

def analyze_zhihu_data():
    """分析知乎数据并生成可视化图表"""
    
    # 连接数据库
    conn = sqlite3.connect('sichuan_university_zhihu.db')
    
    print("📊 数据库概览")
    print("=" * 50)
    
    # 1. 基础统计
    tables = ['topics', 'questions', 'users', 'answers', 'topic_details']
    stats = {}
    
    for table in tables:
        try:
            count = pd.read_sql(f'SELECT COUNT(*) as count FROM {table}', conn)['count'].iloc[0]
            stats[table] = count
            print(f"{table:15}: {count:,}")
        except:
            stats[table] = 0
            print(f"{table:15}: 表不存在")
    
    total = sum(stats.values())
    print(f"{'总记录数':15}: {total:,}")
    
    # 2. 话题分析
    if stats['topics'] > 0:
        print("\n🏷️ 热门话题 TOP 10")
        print("-" * 30)
        topics_df = pd.read_sql('''
            SELECT name, followers_count, questions_count 
            FROM topics 
            ORDER BY followers_count DESC 
            LIMIT 10
        ''', conn)
        
        for idx, row in topics_df.iterrows():
            print(f"{idx+1:2}. {row['name'][:30]:30} (关注: {row['followers_count']:,})")
    
    # 3. 用户分析
    if stats['users'] > 0:
        print("\n👥 活跃用户 TOP 10")
        print("-" * 30)
        users_df = pd.read_sql('''
            SELECT name, follower_count, answer_count 
            FROM users 
            ORDER BY follower_count DESC 
            LIMIT 10
        ''', conn)
        
        for idx, row in users_df.iterrows():
            print(f"{idx+1:2}. {row['name'][:20]:20} (粉丝: {row['follower_count']:,}, 回答: {row['answer_count']:,})")
    
    # 4. 问题分析
    if stats['questions'] > 0:
        print("\n❓ 热门问题 TOP 10")
        print("-" * 30)
        questions_df = pd.read_sql('''
            SELECT title, answer_count, follower_count 
            FROM questions 
            ORDER BY answer_count DESC 
            LIMIT 10
        ''', conn)
        
        for idx, row in questions_df.iterrows():
            print(f"{idx+1:2}. {row['title'][:40]:40} (回答: {row['answer_count']:,})")
    
    # 5. 生成可视化图表
    create_visualizations(conn, stats)
    
    conn.close()
    print(f"\n✅ 分析完成！图表已保存到当前目录")

def create_visualizations(conn, stats):
    """创建可视化图表"""
    
    # 1. 数据分布饼图
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    labels = [k for k, v in stats.items() if v > 0]
    sizes = [v for v in stats.values() if v > 0]
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors[:len(sizes)])
    plt.title('数据分布')
    
    # 2. 话题关注者分布
    if stats['topics'] > 0:
        plt.subplot(2, 2, 2)
        topics_df = pd.read_sql('SELECT followers_count FROM topics WHERE followers_count > 0', conn)
        plt.hist(topics_df['followers_count'], bins=20, alpha=0.7, color='skyblue')
        plt.title('话题关注者数量分布')
        plt.xlabel('关注者数量')
        plt.ylabel('话题数量')
    
    # 3. 用户粉丝分布
    if stats['users'] > 0:
        plt.subplot(2, 2, 3)
        users_df = pd.read_sql('SELECT follower_count FROM users WHERE follower_count > 0', conn)
        plt.hist(users_df['follower_count'], bins=20, alpha=0.7, color='lightgreen')
        plt.title('用户粉丝数量分布')
        plt.xlabel('粉丝数量')
        plt.ylabel('用户数量')
    
    # 4. 问题回答数分布
    if stats['questions'] > 0:
        plt.subplot(2, 2, 4)
        questions_df = pd.read_sql('SELECT answer_count FROM questions WHERE answer_count > 0', conn)
        plt.hist(questions_df['answer_count'], bins=20, alpha=0.7, color='orange')
        plt.title('问题回答数量分布')
        plt.xlabel('回答数量')
        plt.ylabel('问题数量')
    
    plt.tight_layout()
    plt.savefig('zhihu_data_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 5. 词云图
    create_wordcloud(conn)

def create_wordcloud(conn):
    """生成词云图"""
    try:
        # 收集所有文本内容
        texts = []
        
        # 话题名称
        topics_df = pd.read_sql('SELECT name FROM topics', conn)
        texts.extend(topics_df['name'].tolist())
        
        # 问题标题
        questions_df = pd.read_sql('SELECT title FROM questions', conn)
        texts.extend(questions_df['title'].tolist())
        
        # 用户简介
        users_df = pd.read_sql('SELECT headline FROM users WHERE headline IS NOT NULL', conn)
        texts.extend(users_df['headline'].tolist())
        
        if texts:
            # 分词处理
            all_text = ' '.join(texts)
            words = jieba.cut(all_text)
            word_text = ' '.join(words)
            
            # 生成词云
            wordcloud = WordCloud(
                font_path='simhei.ttf',  # 如果有中文字体文件
                width=800, 
                height=400,
                background_color='white',
                max_words=100
            ).generate(word_text)
            
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('四川大学相关内容词云图')
            plt.savefig('wordcloud.png', dpi=300, bbox_inches='tight')
            plt.show()
            
    except Exception as e:
        print(f"词云生成失败: {e}")

def export_to_excel():
    """导出数据到Excel"""
    conn = sqlite3.connect('sichuan_university_zhihu.db')
    
    with pd.ExcelWriter('zhihu_data.xlsx') as writer:
        # 导出各个表到不同的工作表
        tables = ['topics', 'questions', 'users', 'answers']
        
        for table in tables:
            try:
                df = pd.read_sql(f'SELECT * FROM {table}', conn)
                df.to_excel(writer, sheet_name=table, index=False)
                print(f"✅ {table} 表已导出")
            except Exception as e:
                print(f"❌ {table} 表导出失败: {e}")
    
    conn.close()
    print("📁 数据已导出到 zhihu_data.xlsx")

if __name__ == "__main__":
    # 先安装必要的库
    print("安装必要的库...")
    import subprocess
    import sys
    
    packages = ['pandas', 'matplotlib', 'seaborn', 'wordcloud', 'jieba', 'openpyxl']
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"安装 {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    
    # 运行分析
    analyze_zhihu_data()
    
    # 导出Excel
    export_to_excel()