# hass-custom-plugins

Home Assistant 定制插件仓库——**全量独立分发**，安装/升级不依赖上游仓库。

本仓库专门针对以下两款设备做适配（官方集成不支持或支持不完整）：

| 设备 | 型号/固件 | 官方集成的问题 | 本仓库方案 |
|---|---|---|---|
| **科沃斯扫地机器人** | DEEBOT T80 水箱版（硬件代码 xwk78e） | deebot-client 官方无此型号支持，上游 PR #1802 被拒 | 完整 `deebot_client` 包 + xwk78e 补丁 |
| **格力云空调** | Gree 云空调 V3.x 固件（实测 V3.4.M / V3.5.M） | gree_cloud 面板状态被云端全 0 脱敏应答覆盖成假数据 | 完整 `gree_cloud` 集成 + 全 0 应答过滤补丁 |

## gree_cloud/ （格力云空调，完整 HA 自定义集成）

来源 `davo22/homeassistant-gree-cloud` v1.3.2 全量 + 本地两处补丁。

**适配问题**：V3.x 固件对 MQTT `request/` 轮询应答全 0（云端对第三方客户端脱敏），真实状态只在 `status/` 推送里。原版集成会把全 0 应答写进设备状态，导致 HA 面板显示温度 0/假状态，命令虽然能执行但状态错乱。

**本地补丁**：
1. `coordinator.py` — 轮询应答全 0 时跳过状态更新，只信 `status/` 推送的真实值
2. `manifest.json` — requirements 由 git 依赖改为 `greeclimate>=2.1.4`，消除 HA 启动联网装包卡死

**安装**：整个 `gree_cloud/` 拷到 `<ha-config>/custom_components/gree_cloud/`，重启 HA。

上游 PR：https://github.com/davo22/homeassistant-gree-cloud/pull/30

## deebot_client/ （科沃斯 DEEBOT T80，完整 Python 包 360 文件）

来源 `deebot-client` 18.5.1 全量 + xwk78e 支持补丁，从生产容器原样抽出。

**适配问题**：T80 水箱版不在官方支持列表，上游规范方案 PR #1840（symlink 到 9eamof family）尚未合并。本仓库用的是 PR #1802 的完整实现（被 maintainer 以"AI 生成不符仓库结构"拒收，但代码经生产验证正确）。

**安装/HA 升级后重打补丁**：
```
sudo docker cp deebot_client homeassistant:/tmp/deebot_client_new
sudo docker exec homeassistant rm -rf /usr/local/lib/python3.14/site-packages/deebot_client
sudo docker exec homeassistant mv /tmp/deebot_client_new /usr/local/lib/python3.14/site-packages/deebot_client
sudo docker restart homeassistant
```
或用 `tools/reapply_patch_deebot.py`（只补差异，带版本锚点检查）。

**补丁内容**（相对上游 18.5.1 的新增）：`hardware/xwk78e.py`、`commands/json/xwk78e.py`、`events/xwk78e.py`、`messages/json/xwk78e.py`。

## 验证基线（2026-09-25 生产实测）

- 格力空调（次卧 V3.5.M / 主卧 V3.4.M）：开关/制冷/制热/除湿/送风/调温/风速/上下扫风/左右扫风全部实测通过，HA 面板显示真实状态
- DEEBOT T80：上线正常，电量/固件/状态 MQTT 实时刷新，清扫指令可下发

## 说明

本仓库为个人生产环境自用的定制分发，补丁针对特定型号/固件验证。其他型号未经测试，使用前请自行核对设备型号。
