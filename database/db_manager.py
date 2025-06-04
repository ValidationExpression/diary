import sqlite3
import os
from datetime import datetime
from models.diary import Diary


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """连接到数据库"""
        try:
            # 确保目录存在
            db_dir = os.path.dirname(os.path.abspath(self.db_path))
            print(f"数据库目录: {db_dir}")  # 添加日志
            os.makedirs(db_dir, exist_ok=True)
            
            # 连接数据库
            print(f"尝试连接数据库: {self.db_path}")  # 添加日志
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # 允许通过列名访问数据
            self.cursor = self.conn.cursor()
            print("数据库连接成功")  # 添加日志
            return True
        except sqlite3.Error as e:
            print(f"数据库连接错误: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.cursor = None
        self.conn = None
    
    def ensure_connected(self):
        """确保数据库已连接"""
        if not self.conn or not self.cursor:
            self.connect()
    
    def init_db(self):
        """初始化数据库表结构"""
        try:
            self.ensure_connected()
            
            # 检查表是否存在
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='diaries'")
            table_exists = self.cursor.fetchone()
            
            if not table_exists:
                print("创建新的日记表")  # 添加日志
                # 表不存在，创建新表
                self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS diaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    date TEXT NOT NULL,
                    weather TEXT NOT NULL DEFAULT '',
                    mood TEXT NOT NULL DEFAULT '',
                    quote TEXT NOT NULL DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                self.conn.commit()
                print("日记表创建成功")  # 添加日志
            else:
                print("日记表已存在，检查列结构")  # 添加日志
                # 表已存在，检查并添加缺失的列
                self._check_and_update_columns()
                
            return True
        except sqlite3.Error as e:
            print(f"初始化数据库错误: {e}")
            raise
    
    def _check_and_update_columns(self):
        """检查并更新数据库表结构，添加缺失的列"""
        try:
            # 获取表的当前结构
            self.cursor.execute("PRAGMA table_info(diaries)")
            columns = self.cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            # 检查并添加缺失的列
            required_columns = {
                'weather': 'TEXT',
                'mood': 'TEXT',
                'quote': 'TEXT'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in column_names:
                    self.cursor.execute(f"ALTER TABLE diaries ADD COLUMN {col_name} {col_type}")
                    print(f"已添加{col_name}列")
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"更新数据库结构错误: {e}")
            raise
    
    def save_diary(self, diary):
        """保存日记"""
        try:
            self.ensure_connected()
            self.cursor.execute(
                "INSERT INTO diaries (title, content, date, weather, mood, quote) VALUES (?, ?, ?, ?, ?, ?)",
                (diary.title, diary.content, diary.date, diary.weather, diary.mood, diary.quote)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"保存日记错误: {e}")
            raise
    
    def get_all_diaries(self):
        """获取所有日记"""
        try:
            self.ensure_connected()
            self.cursor.execute("SELECT * FROM diaries ORDER BY created_at DESC")
            rows = self.cursor.fetchall()
            return [self._row_to_diary(row) for row in rows]
        except sqlite3.Error as e:
            print(f"获取日记列表错误: {e}")
            raise
    
    def get_diary_by_id(self, diary_id):
        """根据ID获取日记"""
        try:
            self.ensure_connected()
            self.cursor.execute("SELECT * FROM diaries WHERE id = ?", (diary_id,))
            row = self.cursor.fetchone()
            return self._row_to_diary(row) if row else None
        except sqlite3.Error as e:
            print(f"根据ID获取日记错误: {e}")
            raise
    
    def update_diary(self, diary):
        """更新日记"""
        try:
            self.ensure_connected()
            self.cursor.execute(
                "UPDATE diaries SET title = ?, content = ?, weather = ?, mood = ?, quote = ? WHERE id = ?",
                (diary.title, diary.content, diary.weather, diary.mood, diary.quote, diary.id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新日记错误: {e}")
            raise
    
    def delete_diary(self, diary_id):
        """删除日记"""
        try:
            self.ensure_connected()
            self.cursor.execute("DELETE FROM diaries WHERE id = ?", (diary_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"删除日记错误: {e}")
            raise
    
    def _row_to_diary(self, row):
        """将数据库行转换为Diary对象"""
        if not row:
            return None
            
        return Diary(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            date=row['date'],
            weather=row['weather'] if 'weather' in row.keys() else '',
            mood=row['mood'] if 'mood' in row.keys() else '',
            quote=row['quote'] if 'quote' in row.keys() else ''
        ) 