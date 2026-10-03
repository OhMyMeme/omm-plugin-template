"""OhMyMeme 插件入口模板。

宿主加载流程：
 1. 读取并校验 plugin.json（id 非法 / api_version 不匹配 / 依赖缺失 => 插件加载失败，不影响其他插件）
 2. 导入本文件，调用 on_load(ctx)——异常会导致本插件加载失败
 3. 应用退出或插件被禁用时调用 on_unload()
 4. 设置页保存本插件设置后调用 on_settings_changed(本次保存的数据)
"""


def on_load(ctx):
    """注册插件提供的全部能力（需在 plugin.json 的 permissions 中声明对应权限）"""
    ctx.log("加载成功")

    # 设置页区块（权限 settings:section）：注入设置窗口左栏「插件」分组。
    # 输入元素带 data-plugin=<id> data-key=<键名>，宿主自动回填已保存值；
    # 保存按钮调用 pluginSaveSection('<id>') 即可收集本区块全部输入。
    ctx.register_settings_section(_section(ctx.id))

    # 主窗口 API（权限 main_api）：前端经 pywebview.api.plugin_call('<id>', 'greet', ['世界'])
    ctx.register_main_api("greet", lambda name="世界": greet(ctx, name))

    # 静态资产（权限 assets:serve）：按 manifest windows 注入对应窗口，
    # URL 带版本号参数，插件设置变化时自动改 URL 防缓存。
    ctx.register_css("main", "assets/style.css")
    ctx.register_js("main", "assets/demo.js")

    # 自定义路由（权限 route）：GET/POST 均可，规则为以 / 开头的完整路径。
    # 处理器收一个 dict（query + 表单参数），返回 str 或 dict（dict 自动 JSON）。
    ctx.register_route("/omm-my-plugin/hello", hello_route)

    # --- 以下能力按需打开（取消注释并同步声明 manifest 权限）---

    # 顶栏按钮（权限 buttons）：{key, label, icon?, order?}
    # ctx.register_button({"key": "demo", "label": "演示", "icon": "assets/icon.svg", "order": 65})
    # ctx.register_button_handler(on_button_click)  # fn(key) -> 任意可序列化返回值
    # 约束核心按钮：hide 隐藏，order 调整位置（默认 sort10/select20/upload30/
    # download40/import50/refresh60/settings70/close1000）
    # ctx.register_button_constraints(hide=["import"], order={"settings": 90})

    # 启动动画覆盖（权限 startup，重启生效，多插件按 id 排序后者生效）
    # ctx.set_startup_override(video_src="/plugins/my-plugin/media/intro.mp4", bg_color="#000000")

    # 主窗口初始尺寸覆盖（权限 window，重启生效；插件优先于持久化的窗口尺寸）
    # ctx.set_window_params(width=1280, height=800)

    # 设置窗口 API（权限 settings_api）：设置窗口前端经
    # pywebview.api.plugin_call('<id>', 'method', args) 分发
    # ctx.register_settings_api("do_something", do_something)

    # 向主窗口推送 JS（权限 host:evaluate_js）
    # ctx.evaluate_js("console.log('hello from plugin')")

    # 插件私有数据目录（LOCALAPPDATA/OhMyMeme/plugins_data/<id>/），读写文件用
    # data_dir = ctx.data_dir


def _section(pid):
    """设置页区块 HTML（class=section + data-group=plugin 才会出现在「插件」分组）"""
    return (
        '<div class="section" data-group="plugin" data-plugin="%s">'
        '<h3>我的插件</h3>'
        '<div class="check-row"><label><input type="checkbox" '
        'data-plugin="%s" data-key="demo_flag"> 示例开关</label></div>'
        '<input type="text" data-plugin="%s" data-key="greeting" '
        'placeholder="问候语" style="width:100%%;margin:6px 0">'
        '<button class="btn" onclick="pluginSaveSection(\'%s\')">保存插件设置</button>'
        "</div>"
    ) % (pid, pid, pid, pid)


def greet(ctx, name="世界"):
    """主窗口 API 示例：ctx.settings 可读到本插件已保存的设置"""
    saved = ctx.settings.get("greeting", "")
    return {"ok": True, "msg": (saved or "你好") + "，" + str(name)}


def hello_route(params):
    """自定义路由示例：GET /omm-my-plugin/hello?name=xx"""
    return {"hello": params.get("name", "world")}


def on_settings_changed(data):
    """设置页保存后调用（独立线程，data 为本次保存的增量）"""


def on_unload():
    """应用退出/插件禁用时调用：释放线程、关闭文件等"""
