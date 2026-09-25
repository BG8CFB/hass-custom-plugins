# hass-custom-plugins

Home Assistant 定制插件仓库——**全量独立分发**，安装/升级不依赖上游仓库。

## gree_cloud/ （完整 HA 自定义集成）

来源 `davo22/homeassistant-gree-cloud` v1.3.2 全量 + 本地两处补丁。

**安装**：整个 `gree_cloud/` 拷到 `<ha-config>/custom_components/gree_cloud/`，重启 HA。

**本地补丁**：
1. `coordinator.py` — 格力 V3.x 固件（V3.4.M/V3.5.M）对 MQTT `request/` 轮询应答全 0（云端脱敏），补丁让全 0 应答不覆盖 `status/` 推送的真实状态。上游 PR：https://github.com/davo22/homeassistant-gree-cloud/pull/30
2. `manifest.json` — requirements 由 git 依赖改为 `greeclimate>=2.1.4`，消除 HA 启动联网装包卡死。

## deebot_client/ （完整 Python 包，360 个文件）

来源 `deebot-client` 18.5.1 全量 + xwk78e（DEEBOT T80 水箱版）支持补丁，从生产容器原样抽出。

**安装/升级后重打补丁**：直接覆盖容器内包目录：
```
sudo docker cp deebot_client homeassistant:/tmp/deebot_client_new
sudo docker exec homeassistant rm -rf /usr/local/lib/python3.14/site-packages/deebot_client
sudo docker exec homeassistant mv /tmp/deebot_client_new /usr/local/lib/python3.14/site-packages/deebot_client
sudo docker restart homeassistant
```
或用 `tools/reapply_patch_deebot.py`（只补 xwk78e 差异，带版本锚点检查）。

**补丁内容**（相对上游 18.5.1 的新增）：`hardware/xwk78e.py`、`commands/json/xwk78e.py`、`events/xwk78e.py`、`messages/json/xwk78e.py`。来源为上游被拒 PR #1802，规范方案 PR #1840 合并后可直接升级官方新版。

## 验证基线（2026-09-25 生产实测）

- gree_cloud：次卧/主卧空调（V3.5.M/V3.4.M）开关/模式/调温/风速/扫风全通，面板状态真实
- deebot_client：DEEBOT T80 上线，电量/固件/状态 MQTT 实时刷新
