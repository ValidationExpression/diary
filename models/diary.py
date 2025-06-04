from datetime import datetime


class Diary:
    def __init__(self, title="", content="", date=None, id=None, weather="", mood="", quote=""):
        self.id = id
        self.title = title
        self.content = content
        self.date = date if date else self.get_current_date()
        self.weather = weather
        self.mood = mood
        self.quote = quote
    
    @staticmethod
    def get_current_date():
        """获取当前日期，格式为YYYY-MM-DD"""
        return datetime.now().strftime("%Y-%m-%d")
    
    def __str__(self):
        return f"日记 [{self.date}] {self.title}" 