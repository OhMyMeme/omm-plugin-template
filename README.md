# OhMyMeme 插件模板

复制本仓库即可开始编写 [OhMyMeme](https://github.com/OhMyMeme/OhMyMeme) 插件（宿主插件 API 版本 `api_version: 1`，OhMyMeme ≥ 0.7.0）。

## 快速开始

1. 复制本仓库，改名/改 `plugin.json` 的 `id`（小写字母、数字、`-`、`_`，≤64 字符），并同步 `main.py` 中出现的 id（`_section`、事件过滤、按钮 handler 等）。
2. 安装插件（二选一）：
   - 把整个文件夹放入**插件目录**（设置 → 插件 → 「打开插件目录」），即 `<数据目录>/plugins/<你的插件目录>/plugin.json`；**推荐文件夹名与 `id` 一致**，插件设置文件 `settings.json` 按 id 存放时就会保存在该文件夹内；
   - 开发期把本仓库路径加入 `config.json` 的 `plugin_dirs` 数组，免复制直连。
3. 重启 OhMyMeme，设置 → 插件中应看到你的插件且状态为「已启用」。
4. 修改代码后再次重启生效（插件在进程启动时加载）。

## 目录结构

```
plugin.json   # manifest（必须）
main.py       # 入口（entry 可指向其他文件，但必须位于插件目录内）
assets/       # 任意静态资源（css/js/图片/字体/视频），按 windows 注入
```

## plugin.json 字段

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `id` | 是 | 插件唯一标识，`^[a-z0-9][a-z0-9_-]{0,63}$`，与目录名保持一致 |
| `name` / `version` | 是 | 显示名 / 版本号，缺任一插件不注册 |
| `repo` | 否 | 仓库地址；填写时必须是 `https://` / `git@` / `ssh://` 开头 |
| `api_version` | 是 | 必须等于宿主的 `1`，否则拒绝加载 |
| `entry` | 否 | 入口文件相对路径；留空为纯资产插件（仅注入 CSS/JS/区块） |
| `windows` | 否 | 资产注入到哪些窗口：`main`（主窗口）/ `settings`（设置窗口），默认 `["main"]` |
| `permissions` | 否 | 权限声明，见下表；未声明的调用会在 `on_load` 中抛 `PermissionError` 导致本插件加载失败 |
| `description` / `author` | 否 | 展示信息 |
| `dependencies` | 否 | pip 包名列表，宿主用 `find_spec` 检测，缺失则跳过加载 |
| `sandbox` | 否 | `true` 表示沙箱运行（v0.8 提供），当前版本会跳过加载 |

## 权限

| 权限 | 说明 |
| --- | --- |
| `route` | 自定义 HTTP 路由 |
| `main_api` | 主窗口 JS API（`pywebview.api.plugin_call`） |
| `settings_api` | 设置窗口 JS API（`pywebview.api.plugin_call`） |
| `assets:serve` | 注入 CSS/JS 资产（`/plugins/<id>/<path>` 静态服务对已启用插件开放，`data/<path>` 前缀解析到 `ctx.data_dir`） |
| `settings:section` | 设置页「插件」分组内的 HTML 区块 |
| `buttons` | 主窗口顶栏按钮 + 核心按钮布局约束 |
| `startup` | 覆盖启动动画视频/底色 |
| `window` | 覆盖主窗口初始尺寸 |
| `host:evaluate_js` | `ctx.evaluate_js` 向主窗口推送脚本 |

## on_load(ctx) 能力

| API | 说明 |
| --- | --- |
| `ctx.id` / `ctx.settings` | 插件 id / 已保存设置快照（dict） |
| `ctx.data_dir` | 插件私有数据目录 `<数据目录>/plugins_data/<id>/`（自动创建） |
| `ctx.log(msg, level)` | 写宿主日志，带 `[plugin:<id>]` 前缀 |
| `ctx.save_settings(dict)` | 合并保存插件设置，落盘 `<配置目录>/plugins/<id>/settings.json`（`%APPDATA%`，与设置页 `pluginSaveSection` 同一存储） |
| `ctx.register_route(rule, fn)` | 自定义路由，`fn(params_dict)` 返回 `str` 或 `dict`（dict → JSON） |
| `ctx.register_main_api(name, fn)` | 主窗口 API，`fn(*args)` 返回可 JSON 序列化值 |
| `ctx.register_settings_api(name, fn)` | 设置窗口 API，同上 |
| `ctx.register_css/register_js(window, relpath)` | 注入资产，路径必须在插件目录内 |
| `ctx.register_settings_section(html)` | 设置页区块，见下文约定 |
| `ctx.register_button(dict)` | 顶栏按钮 `{key, label, icon?, order?}`（`icon` 为插件内相对路径） |
| `ctx.register_button_handler(fn)` | 按钮点击处理 `fn(key)`（一个插件一个） |
| `ctx.register_button_constraints(hide=[...], order={...})` | 隐藏/重排核心按钮；核心 key：`sort` `select` `upload` `download` `import` `refresh` `settings` `close` |
| `ctx.set_startup_override(video_src, bg_color, duration_ms=0, media_type="")` | 启动动画覆盖，重启生效；多插件按 id 排序后者生效；`duration_ms`（>0）供图片/GIF 类型按时长收起、`media_type` 为 `image` 时前端按 `<img>` 只播一遍 |
| `ctx.set_window_params(width, height)` | 主窗口初始尺寸覆盖，重启生效，优先于持久化的窗口尺寸 |
| `ctx.evaluate_js(code)` | 向主窗口推送脚本 |

## 生命周期

```python
def on_load(ctx): ...                 # 必须（entry 存在时）
def on_unload(): ...                  # 退出/禁用时调用
def on_settings_changed(delta): ...   # 设置页保存后调用（delta 为本次保存的增量）
```

- `on_load` 超时 15s / 普通回调超时 10s / JS API 调用超时 120s，超时或抛异常会把插件置为「已停用」熔断（下次重启恢复），单个插件故障不影响其余插件与宿主。
- 禁用立即生效（注册项清空、vendor 移除），启用需重启加载。

## 设置页区块约定

```html
<div class="section" data-group="plugin" data-plugin="my-plugin">
  <h3>标题</h3>
  <div class="check-row"><label><input type="checkbox"
    data-plugin="my-plugin" data-key="flag"> 开关</label></div>
  <input type="text" data-plugin="my-plugin" data-key="text_key" placeholder="文本">
  <button class="btn" onclick="pluginSaveSection('my-plugin')">保存插件设置</button>
</div>
```

- 宿主启动时自动把 `plugin_get_settings(id)` 的值回填到 `data-plugin` + `data-key` 元素（checkbox → `checked`，其余 → `value`）。
- `pluginSaveSection(id)` 收集本 id 全部输入（checkbox → bool，其余 → 字符串）合并保存，并自动触发 `on_settings_changed` 与主窗口 `omm-plugin-refresh` 事件。
- 区块内输入不计入设置页「有未保存的更改」提示。
- 设置 → 插件列表为折叠栏：**点击插件名**展开/收起该插件的区块与信息，右侧开关启用/停用；宿主会自动把区块移入对应插件的折叠栏内（`section` 必须带 `data-plugin="<id>"`）。

## 前端调用

```js
// 主窗口（JsApi）
const r = await pywebview.api.plugin_call('my-plugin', 'greet', ['世界']);
const b = await pywebview.api.plugin_button_click('my-plugin', 'demo');

// 设置窗口（SettingsApi）
await pywebview.api.plugin_call('my-plugin', 'some_method', []);

// 监听插件设置保存（主窗口脚本）
window.addEventListener('omm-plugin-refresh', (e) => {
  if (e.detail.plugin_id === 'my-plugin') { /* 重新应用 */ }
});

// 设置窗口：宿主回填完插件区块后派发（下拉/颜色等非 data-key 控件在此同步）
window.addEventListener('omm-plugin-section-filled', (e) => {
  if (e.detail.plugin_id === 'my-plugin') { /* 读 plugin_get_settings 同步控件 */ }
});

// 设置窗口：文件选择（media: 'video' | 'image' | 'any'，需 settings_api 权限；插件须处于已启用）
const r = await pywebview.api.plugin_pick_file('my-plugin', 'image');
// r = {ok: true, path} 或 {cancelled: true}
```

顶栏插件按钮由宿主渲染：`icon` 非空渲染为图标按钮，否则为文字按钮，按 `order` 排序（默认 100，插件按钮位于核心按钮 `settings`(70) 与 `close`(1000) 之间更自然时可设 80）。

## 自定义路由

```python
ctx.register_route("/omm-my-plugin/hello", lambda p: {"hello": p.get("name")})
```

- GET/POST 均注册，参数为 query + 表单合并的 dict；返回 `dict` → JSON，`str` → 按扩展名推断 Content-Type（`.css`/`.js`/`.html`/`.svg`/`.woff2`/`.mp4` 等）。
- 插件停用/异常时路由返回 404。

## 依赖

- 零依赖优先；`dependencies` 中的包用 `importlib.util.find_spec` 检测（**不安装**，缺失即拒绝加载并显示原因）。
- 需要随插件分发的纯 Python 依赖放入 `vendor/`，宿主会把该目录追加到 `sys.path` 末尾（禁用时移除）。

## 调试

- 设置 → 插件列表点击插件名展开后可见状态与失败原因（`reason`）。
- `ctx.log(...)` 输出到宿主日志（帮助 → 日志分组可打开日志目录）。
- 前端错误看主窗口控制台（`Ctrl+Shift+I`，源码运行时）。
