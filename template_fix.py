import os
import sys

# 获取应用程序所在目录
if getattr(sys, 'frozen', False):
    # 如果是打包后的应用
    application_path = os.path.dirname(sys.executable)
else:
    # 如果是开发环境
    application_path = os.path.dirname(os.path.abspath(__file__))

# 模板和静态文件的路径
templates_path = os.path.join(application_path, 'templates')
static_path = os.path.join(application_path, 'static')

# 用于Flask应用程序的配置
template_folder = templates_path
static_folder = static_path 