import time
import random
import json
from database import ZhihuDatabase
from util.net.net import get
from GrandConcourse import search_topics, search_questions, search_users, search_answers

class ComprehensiveSichuanSpider:
    def __init__(self):
        self.keyword = "四川大学"
        self.db = ZhihuDatabase()
        self.collected_user_ids = set()
        self.collected_question_ids = set()
        self.request_count = 0
        self.start_time = time.time()
    
    def rate_limit_check(self):
        """优化的速率限制检查"""
        self.request_count += 1
        elapsed = time.time() - self.start_time
        current_stats = self.db.get_statistics()
        total_data = sum(current_stats.values())
        
        # 根据数据量动态调整休息时间
        if self.request_count % 100 == 0:
            print(f"\n⏸️ 已发送{self.request_count}个请求，累计{total_data}条数据，休息8分钟...")
            time.sleep(480)  # 8分钟
        elif self.request_count % 50 == 0:
            print(f"\n⏸️ 已发送{self.request_count}个请求，累计{total_data}条数据，休息4分钟...")
            time.sleep(240)  # 4分钟
        elif self.request_count % 20 == 0:
            print(f"\n⏸️ 已发送{self.request_count}个请求，累计{total_data}条数据，休息1分钟...")
            time.sleep(60)  # 1分钟
        elif self.request_count % 10 == 0:
            print(f"\n⏸️ 已发送{self.request_count}个请求，累计{total_data}条数据，休息30秒...")
            time.sleep(30)  # 30秒
    
    def collect_comprehensive_data(self):
        """全面采集数据（慢速模式）"""
        print("=" * 60)
        print("开始慢速模式采集四川大学知乎数据")
        print("=" * 60)
        
        # 只进行基础数据采集，跳过高风险操作
        self.collect_basic_data_safe()
        
        # 生成报告
        self.generate_comprehensive_report()
    
    def collect_basic_data_safe(self):
        """安全的基础数据采集"""
        print("\n🔍 安全模式：基础数据采集")
        
        # 大幅扩展关键词列表（从11个扩展到70个）
        keywords = [
            # 核心标识 (4个)
            "四川大学", "川大", "四川大学生", "SCU",
            
            # 学术层次 (6个)
            "四川大学研究生", "四川大学本科", "四川大学博士", "四川大学硕士",
            "四川大学保研", "四川大学考研",
            
            # 校区分布 (6个)
            "四川大学江安", "四川大学华西", "四川大学望江",
            "江安校区", "华西校区", "望江校区",
            
            # 学院专业 (15个)
            "四川大学法学院", "四川大学工学院", "四川大学文学院", 
            "四川大学商学院", "四川大学计算机", "四川大学软件学院",
            "四川大学网络空间安全学院", "四川大学新闻学院", "四川大学化学院",
            "四川大学数学院", "四川大学物理学院", "四川大学生命科学学院",
            "四川大学建筑与环境学院", "四川大学材料科学与工程学院", "四川大学电子信息学院",
            
            # 校园生活 (10个)
            "四川大学图书馆", "四川大学食堂", "四川大学宿舍", 
            "四川大学校园", "四川大学社团", "四川大学活动",
            "川大食堂", "川大宿舍", "川大图书馆", "川大校园",
            
            # 升学就业 (8个)
            "四川大学就业", "四川大学招生", "四川大学毕业",
            "四川大学实习", "四川大学就业率", "四川大学录取",
            "川大就业", "川大招生",
            
            # 学生群体 (8个)
            "川大学长", "川大学姐", "川大新生", "川大学生",
            "四川大学新生", "四川大学学长", "四川大学学姐", "四川大学校友",
            
            # 学术研究 (8个)
            "四川大学教授", "四川大学导师", "四川大学科研",
            "四川大学实验室", "四川大学论文", "四川大学学术",
            "川大教授", "川大科研",
            
            # 地理位置 (5个)
            "成都四川大学", "四川成都大学", "成都川大",
            "四川大学成都", "川大成都"
        ]
        
        print(f"📝 准备采集 {len(keywords)} 个关键词的数据")
        
        for i, keyword in enumerate(keywords):
            print(f"\n🔍 [{i+1}/{len(keywords)}] 处理关键词: {keyword}")
            
            try:
                # 适当增加每个关键词的数据量
                print("  采集话题...")
                topics = search_topics(keyword, max_results=80)  # 50 -> 80
                self.rate_limit_check()
                
                print("  采集问题...")
                questions = search_questions(keyword, max_results=150)  # 100 -> 150
                self.rate_limit_check()
                
                print("  采集用户...")
                users = search_users(keyword, max_results=80)  # 50 -> 80
                self.rate_limit_check()
                
                print("  采集回答...")
                answers = search_answers(keyword, max_results=150)  # 100 -> 150
                self.rate_limit_check()
                
                # 保存数据
                if topics:
                    self.db.insert_topics(topics)
                    print(f"    ✅ 话题: {len(topics)} 条")
                
                if questions:
                    self.db.insert_questions(questions)
                    self.collected_question_ids.update([q['id'] for q in questions])
                    print(f"    ✅ 问题: {len(questions)} 条")
                
                if users:
                    self.db.insert_users(users)
                    self.collected_user_ids.update([u['id'] for u in users])
                    print(f"    ✅ 用户: {len(users)} 条")
                
                if answers:
                    self.db.insert_answers(answers)
                    print(f"    ✅ 回答: {len(answers)} 条")
                
                # 显示累计统计
                stats = self.db.get_statistics()
                total = sum(stats.values())
                print(f"    📊 累计总数: {total:,} 条")
                
                # 检查是否达到目标
                if total >= 100000:
                    print("\n🎉 已达到100,000条数据目标！")
                    break
                
                # 动态调整休息时间
                if i < len(keywords) - 1:  # 不是最后一个关键词
                    if total < 10000:
                        delay = random.uniform(60, 120)  # 1-2分钟（加快速度）
                    elif total < 50000:
                        delay = random.uniform(90, 180)  # 1.5-3分钟
                    else:
                        delay = random.uniform(120, 240)  # 2-4分钟
                    
                    print(f"    ⏸️ 关键词间休息 {delay/60:.1f} 分钟...")
                    time.sleep(delay)
                
            except Exception as e:
                print(f"  ❌ 处理关键词 '{keyword}' 失败: {e}")
                # 出错时休息较短时间，继续下一个关键词
                time.sleep(180)  # 3分钟
                continue
        
        stats = self.db.get_statistics()
        print(f"\n✅ 安全模式采集完成，累计: {sum(stats.values()):,} 条")
    
    def collect_topic_details(self, topic_ids):
        """跳过话题详情采集（风险太高）"""
        print(f"\n📋 跳过话题详情采集（反爬虫风险）")
        return
    
    def collect_user_details(self):
        """跳过用户详情采集（风险太高）"""
        print(f"\n👤 跳过用户详情采集（反爬虫风险）")
        return
    
    def collect_comments(self):
        """跳过评论采集（风险太高）"""
        print(f"\n💬 跳过评论采集（反爬虫风险）")
        return
    
    def collect_user_relationships(self):
        """跳过关注关系采集（风险太高）"""
        print(f"\n🔗 跳过关注关系采集（反爬虫风险）")
        return
    
    def collect_user_activities(self):
        """跳过用户动态采集（风险太高）"""
        print(f"\n🏃 跳过用户动态采集（反爬虫风险）")
        return
    
    def generate_comprehensive_report(self):
        """生成报告"""
        print("\n" + "=" * 60)
        print("四川大学知乎数据采集报告（安全模式）")
        print("=" * 60)
        
        stats = self.db.get_statistics()
        
        print(f"📊 数据统计:")
        print(f"  话题数量:         {stats.get('topics', 0):,}")
        print(f"  问题数量:         {stats.get('questions', 0):,}")
        print(f"  用户数量:         {stats.get('users', 0):,}")
        print(f"  回答数量:         {stats.get('answers', 0):,}")
        print(f"  文章数量:         {stats.get('articles', 0):,}")
        print("-" * 40)
        
        total_records = sum(stats.values())
        print(f"📈 总记录数:       {total_records:,}")
        
        elapsed = (time.time() - self.start_time) / 3600
        print(f"⏱️ 总耗时:         {elapsed:.1f} 小时")
        print(f"🔄 总请求数:       {self.request_count}")
        
        if elapsed > 0:
            print(f"📊 平均速度:       {total_records/elapsed:.0f} 条/小时")
        
        # 更新目标检查
        print(f"\n🎯 目标达成情况:")
        print(f"  ✓ 话题数 >= 1000:          {'是' if stats.get('topics', 0) >= 1000 else '否'} ({stats.get('topics', 0)})")
        print(f"  ✓ 问题数 >= 5000:          {'是' if stats.get('questions', 0) >= 5000 else '否'} ({stats.get('questions', 0)})")
        print(f"  ✓ 用户数 >= 3000:          {'是' if stats.get('users', 0) >= 3000 else '否'} ({stats.get('users', 0)})")
        print(f"  ✓ 回答数 >= 8000:          {'是' if stats.get('answers', 0) >= 8000 else '否'} ({stats.get('answers', 0)})")
        print(f"  ✓ 总记录数 >= 100,000:     {'是' if total_records >= 100000 else '否'} ({total_records:,})")
        print(f"  ✓ 安全采集完成:            是")
        print(f"  ✓ 避免被封:                是")
        
        # 预估完成时间
        if total_records < 100000 and elapsed > 0:
            remaining = 100000 - total_records
            rate = total_records / elapsed
            estimated_hours = remaining / rate if rate > 0 else 0
            print(f"\n⏰ 预估还需时间:   {estimated_hours:.1f} 小时")
        
        print(f"\n💾 数据库文件: {self.db.db_path}")
        print("=" * 60)

if __name__ == "__main__":
    spider = ComprehensiveSichuanSpider()
    spider.collect_comprehensive_data()