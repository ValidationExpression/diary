# 每日反思日记

一款简单的桌面应用程序，用于记录和保存每日反思日记。

## 功能特点

- 创建和保存日记
- 查看历史日记
- 自定义数据库位置
- 简洁直观的用户界面

## 安装说明

### 方法一：直接使用可执行文件

1. 下载最新的发布版本
2. 双击运行 `每日反思日记.exe`
3. 首次使用时，需要选择或创建一个数据库文件

### 方法二：从源代码运行

1. 确保已安装 Python 3.7 或更高版本
2. 安装依赖库：
   ```
   pip install -r requirements.txt
   ```
3. 运行主程序：
   ```
   python web_app.py
   ```

## 打包为可执行文件

要将项目打包为独立的可执行文件，请运行：
打包前可以先执行启动脚本：run_web.py
```
python build.py
```

打包完成后，可执行文件将位于 `build` 目录中。

## 数据库配置

本应用使用 SQLite 数据库存储日记数据。首次启动时，您需要选择数据库文件的位置：

1. 单击菜单中的"连接数据库"
2. 选择现有的数据库文件或创建新的数据库文件
3. 数据库连接成功后，您可以开始添加和查看日记

## 使用方法

1. 在右侧面板中输入日记标题和内容
2. 点击"保存"按钮保存日记
3. 左侧面板显示所有已保存的日记，点击可查看详情
4. 使用"清空"按钮清除当前编辑区域

## 许可证

MIT 许可证
