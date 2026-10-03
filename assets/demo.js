/* 示例脚本：注入主窗口（defer，位于宿主脚本之后执行） */
console.log("[my-plugin] demo.js loaded");

/* 插件设置保存后宿主会推送该事件（detail.plugin_id 标识保存者），
   同时 /plugins/ 下的 <link> 会自动改 URL 重新拉取最新样式 */
window.addEventListener("omm-plugin-refresh", function (e) {
  if (e.detail && e.detail.plugin_id && e.detail.plugin_id !== "my-plugin") return;
  console.log("[my-plugin] 设置已保存，按需重新应用");
});
