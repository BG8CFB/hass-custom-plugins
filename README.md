# hass-custom-plugins

Home Assistant 定制插件仓库（FNOS NAS 生产自用 + 上游 PR 备用份）。

## gree_cloud/

来源：`davo22/homeassistant-gree-cloud` v1.3.2，本地打补丁。

**改动 1：coordinator.py — V3.x 固件全 0 应答修复**
- 格力 V3.x 固件（V3.4.M/V3.5.M）对 MQTT `request/` 轮询应答全 0（云端对第三方脱敏），真实状态只在 `status/` 推送里
- 补丁：轮询应答全 0 时跳过 `handle_state_update()`，不覆盖推送的真实值
- 已提上游 PR：https://github.com/davo22/homeassistant-gree-cloud/pull/30

**改动 2：manifest.json — requirements 改版本约束**
- 原 `git+https://github.com/davo22/greeclimate.git` → `greeclimate>=2.1.4`
- 消除 HA 启动时联网 git clone 的卡死隐患

## deebot-client-xwk78e/

来源：deebot-client 上游被拒的 PR #1802（AI 生成不符仓库结构），生产自用补丁。

- DEEBOT T80 水箱版（xwk78e）硬件 profile + commands/events
- 上游规范方案是 PR #1840（symlink 到 9eamof family），合并后升级 deebot-client 18.6.0+ 可弃用本补丁
- 部署位置：容器内 `deebot_client/hardware/xwk78e.py`、`commands/json/xwk78e.py`、`events/xwk78e.py`
