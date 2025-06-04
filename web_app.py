import os
import configparser
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from database.db_manager import DatabaseManager
from models.diary import Diary

# 导入运行时配置
try:
    from runtime_config import RUNTIME_PATHS
    # 使用运行时配置中的路径
    templates_path = RUNTIME_PATHS['templates_path']
    static_path = RUNTIME_PATHS['static_path']
    settings_ini_path = RUNTIME_PATHS['settings_path']
    print(f"使用运行时配置路径: {RUNTIME_PATHS}")
except ImportError:
    # 如果无法导入运行时配置，则使用默认路径
    print("无法导入运行时配置，使用默认路径")
    if getattr(sys, 'frozen', False):
        # 如果是打包后的应用
        application_path = os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        application_path = os.path.dirname(os.path.abspath(__file__))

    # 模板和静态文件的路径
    templates_path = os.path.join(application_path, 'templates')
    static_path = os.path.join(application_path, 'static')
    settings_ini_path = os.path.join(application_path, 'settings.ini')

# 初始化Flask应用，指定模板和静态文件路径
app = Flask(__name__, 
            template_folder=templates_path,
            static_folder=static_path)
app.config['SECRET_KEY'] = 'diary_pro_secret_key'

# 打印应用程序的路径信息，帮助调试
print(f"应用程序路径信息:")
print(f"  - 工作目录: {os.getcwd()}")
print(f"  - 模板路径: {templates_path}")
print(f"  - 静态文件路径: {static_path}")
print(f"  - 设置文件路径: {settings_ini_path}")
print(f"  - 模板文件夹是否存在: {os.path.exists(templates_path)}")
print(f"  - 模板文件列表: {os.listdir(templates_path) if os.path.exists(templates_path) else '路径不存在'}")

# 数据库连接
db_manager = None

def get_absolute_path(path):
    """获取绝对路径，并确保路径分隔符正确"""
    if path:
        # 转换路径分隔符为操作系统对应的格式
        path = os.path.normpath(path)
        # 如果不是绝对路径，则转换为绝对路径
        if not os.path.isabs(path):
            path = os.path.abspath(path)
    return path

def init_db_connection(db_path):
    """初始化数据库连接"""
    global db_manager
    try:
        if db_manager:
            db_manager.close()
        
        db_path = get_absolute_path(db_path)
        if not os.path.exists(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
        db_manager = DatabaseManager(db_path)
        db_manager.init_db()
        return True
    except Exception as e:
        print(f"初始化数据库连接失败: {e}")
        return False

def init_app():
    """初始化应用程序"""
    try:
        # 使用运行时配置中的settings.ini路径
        settings_path = settings_ini_path
        print(f"尝试加载配置文件: {settings_path}")  # 添加日志
        
        # 加载上次使用的数据库路径
        last_db_path = None
        
        if os.path.exists(settings_path):
            config = configparser.ConfigParser()
            config.read(settings_path)
            # 从配置文件中读取数据库路径，如果不存在则返回None
            db_path = config.get('Database', 'path', fallback=None)
            print(f"从配置文件读取数据库路径: {db_path}")  # 添加日志
            
            if db_path:
                # 检查数据库路径是否存在
                if os.path.exists(db_path):
                    print(f"找到数据库文件: {db_path}")  # 添加日志
                    # 初始化数据库连接
                    return init_db_connection(db_path)
                else:
                    print(f"数据库路径不存在: {db_path}")  # 添加日志
                    last_db_path = db_path  # 记住上次的路径以便后续使用
        else:
            print(f"配置文件不存在，将在首次设置后创建")  # 添加日志
        # 如果没有找到有效的数据库连接，则继续执行后续的默认数据库查找逻辑            
        # 如果未找到配置文件或配置的数据库不存在，尝试在当前目录查找默认数据库
        if getattr(sys, 'frozen', False):
            # 打包环境下使用可执行文件目录
            app_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境使用脚本目录
            app_dir = os.path.dirname(os.path.abspath(__file__))
            
        default_db_path = os.path.join(app_dir, 'diary.db')
        if os.path.exists(default_db_path):
            print(f"找到默认数据库文件: {default_db_path}")  # 添加日志
            # 自动创建配置文件
            config = configparser.ConfigParser()
            config['Database'] = {'path': default_db_path}
            with open(settings_path, 'w') as f:
                config.write(f)
            return init_db_connection(default_db_path)
        elif last_db_path:
            # 尝试创建上次使用的数据库文件所在的目录
            try:
                os.makedirs(os.path.dirname(last_db_path), exist_ok=True)
                print(f"尝试创建上次数据库目录: {os.path.dirname(last_db_path)}")  # 添加日志
                return init_db_connection(last_db_path)
            except Exception as e:
                print(f"创建上次数据库目录失败: {e}")  # 添加日志
    except Exception as e:
        print(f"初始化应用程序失败: {e}")
    return False

# 初始化应用
init_app()

# 添加自定义模板函数
@app.context_processor
def utility_processor():
    def current_date():
        return Diary.get_current_date()
    return dict(current_date=current_date)

def get_db_manager():
    """获取数据库管理器实例"""
    global db_manager
    print("获取数据库管理器")  # 添加日志
    if db_manager is None:
        print("数据库管理器为空，尝试初始化")  # 添加日志
        if not init_app():
            print("初始化应用失败")  # 添加日志
            return None
    print(f"数据库管理器状态: {'已连接' if db_manager else '未连接'}")  # 添加日志
    return db_manager

@app.route('/')
def index():
    """主页，显示日记列表和编辑界面"""
    print("访问首页")  # 添加日志
    db = get_db_manager()
    if not db:
        print("数据库未连接，重定向到设置页面")  # 添加日志
        return redirect(url_for('setup'))
    try:
        print("尝试获取所有日记")  # 添加日志
        diaries = db.get_all_diaries()
        print(f"成功获取日记列表，数量：{len(diaries)}")  # 添加日志
        return render_template('index.html', diaries=diaries)
    except Exception as e:
        print(f"加载日记列表失败: {str(e)}")  # 添加日志
        flash(f'加载日记列表失败: {str(e)}', 'error')
        return redirect(url_for('setup'))

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """数据库设置页面"""
    if request.method == 'POST':
        db_path = request.form.get('db_path')
        db_type = request.form.get('db_type', 'new')  # 默认为新数据库
        
        if not db_path:
            flash('请选择数据库文件', 'error')
            return redirect(url_for('setup'))
        
        try:
            # 获取规范化的绝对路径
            db_path = get_absolute_path(db_path)
            print(f"处理的数据库路径: {db_path}")  # 添加日志
            
            # 如果是现有数据库，检查文件是否存在
            if db_type == 'existing':
                if not os.path.exists(db_path):
                    print(f"数据库文件不存在: {db_path}")  # 添加日志
                    
                    # 尝试在当前目录查找
                    base_name = os.path.basename(db_path)
                    current_dir_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) 
                                                  else os.path.dirname(os.path.abspath(__file__)), base_name)
                    print(f"尝试在当前目录查找: {current_dir_path}")  # 添加日志
                    
                    if os.path.exists(current_dir_path):
                        db_path = current_dir_path
                        print(f"在当前目录找到数据库: {db_path}")  # 添加日志
                    else:
                        flash('选择的数据库文件不存在', 'error')
                        return redirect(url_for('setup'))
                print(f"使用现有数据库: {db_path}")  # 添加日志
            else:
                # 确保目录存在
                try:
                    os.makedirs(os.path.dirname(db_path), exist_ok=True)
                except Exception as e:
                    print(f"创建目录失败: {e}")  # 添加日志
                    # 使用当前目录
                    base_name = os.path.basename(db_path)
                    app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                    db_path = os.path.join(app_dir, base_name)
                    print(f"改用当前目录: {db_path}")  # 添加日志
                    
                print(f"创建新数据库: {db_path}")  # 添加日志
            
            # 初始化数据库连接
            if init_db_connection(db_path):
                # 保存数据库路径到配置文件
                config = configparser.ConfigParser()
                config['Database'] = {'path': db_path}
                with open(settings_ini_path, 'w') as f:
                    config.write(f)
                
                print(f"数据库设置成功，保存路径: {db_path}")  # 添加日志
                flash('数据库设置成功！', 'success')
                return redirect(url_for('index'))
            else:
                flash('数据库初始化失败', 'error')
                return redirect(url_for('setup'))
        except Exception as e:
            print(f"设置数据库出错: {str(e)}")  # 添加日志
            flash(f'设置数据库失败: {str(e)}', 'error')
            return redirect(url_for('setup'))
    
    return render_template('setup.html')

@app.route('/diary/new')
def new_diary():
    """新建日记页面"""
    return render_template('diary_form.html', diary=None)

@app.route('/diary/edit/<int:diary_id>')
def edit_diary(diary_id):
    """编辑日记页面"""
    db = get_db_manager()
    if not db:
        return redirect(url_for('setup'))
    
    diary = db.get_diary_by_id(diary_id)
    if not diary:
        return redirect(url_for('index'))
    
    return render_template('diary_form.html', diary=diary)

@app.route('/diary/save', methods=['POST'])
def save_diary():
    """保存日记"""
    db = get_db_manager()
    if not db:
        print("保存日记失败：数据库未连接")  # 添加日志
        return jsonify({'success': False, 'message': '未连接数据库'})
    
    try:
        # 获取表单数据
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        weather = request.form.get('weather', '').strip()
        mood = request.form.get('mood', '').strip()
        quote = request.form.get('quote', '').strip()
        diary_id = request.form.get('diary_id', '')
        
        print(f"接收到的表单数据: title={title}, weather={weather}, mood={mood}")  # 添加日志
        
        if not title:
            return jsonify({'success': False, 'message': '标题不能为空'})
        
        if not content:
            return jsonify({'success': False, 'message': '内容不能为空'})
        
        # 创建日记对象
        diary = Diary(
            title=title,
            content=content,
            weather=weather,
            mood=mood,
            quote=quote
        )
        
        # 根据是否有ID决定是新增还是更新
        if diary_id and diary_id.isdigit():
            diary.id = int(diary_id)
            diary.date = request.form.get('date', diary.date)
            db.update_diary(diary)
            message = '日记更新成功'
        else:
            db.save_diary(diary)
            message = '日记保存成功'
        
        print(f"日记保存成功: {message}")  # 添加日志
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        print(f"保存日记失败: {e}")  # 添加错误日志
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'})

@app.route('/diary/view/<int:diary_id>')
def view_diary(diary_id):
    """查看日记详情"""
    db = get_db_manager()
    if not db:
        return redirect(url_for('setup'))
    
    diary = db.get_diary_by_id(diary_id)
    if not diary:
        return redirect(url_for('index'))
    
    return render_template('diary_view.html', diary=diary)

@app.route('/diary/delete/<int:diary_id>', methods=['POST'])
def delete_diary(diary_id):
    """删除日记"""
    db = get_db_manager()
    if not db:
        return jsonify({'success': False, 'message': '未连接数据库'})
    
    try:
        db.delete_diary(diary_id)
        return jsonify({'success': True, 'message': '日记删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 