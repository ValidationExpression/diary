import os
import sys
import shutil
from cx_Freeze import setup, Executable

# 删除之前的构建文件
if os.path.exists("build"):
    shutil.rmtree("build")
if os.path.exists("dist"):
    shutil.rmtree("dist")

# 应用基本信息
APP_NAME = "每日反思日记"
VERSION = "1.0.0"

# 依赖包 - 根据requirements.txt更新
packages = ["flask", "jinja2", "werkzeug", "markupsafe", "itsdangerous", "click", 
            "sqlite3", "configparser"]

# 额外文件 - 添加模板和静态文件夹，配置文件和数据库文件
include_files = [
    ("templates", "templates"),
    ("static", "static"),
    ("settings.ini", "settings.ini"),
    ("database", "database"),
    ("models", "models")
]

# 构建选项
build_options = {
    "packages": packages,
    "include_files": include_files,
    "include_msvcr": True,
    "excludes": [],
}

# 创建可执行文件
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 使用Windows GUI子系统

executables = [
    Executable(
        script="web_app.py",  # 主入口文件修改为web_app.py
        base=None,     # 修改为None以便在控制台显示输出
        target_name=f"{APP_NAME}.exe",
        icon=None,  # 可以添加图标路径
        shortcut_name=APP_NAME,
        shortcut_dir="DesktopFolder",
        copyright="Copyright © 2025"
    )
]

# 使用新版cx_Freeze的命令行格式执行打包
if __name__ == "__main__":
    sys.argv.append("build")
    setup(
        name=APP_NAME,
        version=VERSION,
        description="一款简单的日记反思软件",
        author="AI助手",
        options={"build_exe": build_options},
        executables=executables
    )

    print(f"\n打包完成！可执行文件位于 dist 目录。") 