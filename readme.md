# 沉浸式英法网页翻译器

**沉浸式英法网页翻译器**主要实现一个插件功能，在英语/法语页面中自动实现如下功能：

1. 划词翻译：鼠标划线，选词之后调用百度的api进行翻译。
2. 动态翻译生僻词：动态识别并高亮生僻单词/词组，调用deepl的api进行翻译。翻译结果在侧边栏显示。

## 代码实现

该项目包含一个本地 Python 后端和一个 Chrome 浏览器插件。

### 1. 启动后端服务

插件依赖本地 Python 后端来调用翻译 API（以保护 API 密钥安全并解决跨域问题）。

```bash
# 设置环境变量
export BAIDU_APPID='你的APPID'
export BAIDU_SECRET='你的密钥'

# 安装依赖 (如果尚未安装)
pip install -r requirements.txt

# 启动服务
python3 main.py
```

服务默认运行在 `http://127.0.0.1:5000`。

### 2. 安装浏览器插件

1. 打开 Chrome 浏览器，访问 `chrome://extensions/`。
2. 开启右上角的“开发者模式” (Developer mode)。
3. 点击“加载已解压的扩展程序” (Load unpacked)。
4. 选择本项目目录下的 `extension` 文件夹。

### 3. 使用

安装完成后，在任意网页选中一段文本，鼠标附近会出现悬浮框显示翻译结果。