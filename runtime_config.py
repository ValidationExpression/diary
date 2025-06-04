import os
import sys

def get_runtime_paths():
    """获取应用程序运行时的关键路径"""
    # 检测是否是打包后的应用
    if getattr(sys, 'frozen', False):
        # 如果是打包后的应用，使用可执行文件所在目录
        application_path = os.path.dirname(sys.executable)
    else:
        # 如果是开发环境，使用脚本所在目录
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # 返回应用程序关键路径
    return {
        'base_path': application_path,
        'templates_path': os.path.join(application_path, 'templates'),
        'static_path': os.path.join(application_path, 'static'),
        'database_path': os.path.join(application_path, 'database'),
        'settings_path': os.path.join(application_path, 'settings.ini')
    }

# 全局路径配置
RUNTIME_PATHS = get_runtime_paths() 