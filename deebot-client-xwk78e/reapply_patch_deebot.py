#!/usr/bin/env python3
"""DEEBOT T80 (xwk78e) 支持补丁 — 重放脚本
用途: HA 升级后 deebot-client 会被重装, 运行本脚本重新打补丁。

适用: HA 2026.8 / deebot-client 18.5.1 (如升级到其他版本, 先核对
hardware/commands/messages 模块结构再跑, 锚点不匹配脚本会 assert 失败并停止)

来源: 基于 DeebotUniverse/client.py PR #1802 (被拒但代码正确, 适配到 18.5.1)
验证: 2026-09-14 实测 T80 实体上线, vacuum=docked, 电量 MQTT 实时刷新

用法:
  sudo docker cp <本目录>/deebot_xwk78e_pr1802 homeassistant:/tmp/pr1802
  sudo docker cp <本目录>/reapply_patch_deebot.py homeassistant:/tmp/
  sudo docker exec homeassistant python3 /tmp/reapply_patch_deebot.py
  sudo docker restart homeassistant

回滚: 解包 deebot-client-18.5.1.tar.gz 覆盖 /usr/local/lib/python3.14/site-packages/deebot_client
"""
import shutil, os, sys

D = '/usr/local/lib/python3.14/site-packages/deebot_client'
SRC = '/tmp/pr1802'

new_files = ['events/xwk78e.py', 'commands/json/xwk78e.py',
             'messages/json/xwk78e.py', 'hardware/xwk78e.py']
for rel in new_files:
    s, d = os.path.join(SRC, rel), os.path.join(D, rel)
    if not os.path.exists(s):
        sys.exit(f'缺少源文件 {s} (先 docker cp 到 /tmp/pr1802)')
    if os.path.exists(d):
        print(f'跳过(已存在) {rel}')
        continue
    shutil.copy(s, d)
    print(f'新增 {rel}')

p = os.path.join(D, 'messages/__init__.py')
txt = open(p).read()
if 'xwk78e' not in txt:
    anchor_imp = 'from .json import MESSAGES as JSON_MESSAGES, get_legacy_message\n'
    assert anchor_imp in txt, 'messages import 锚点不匹配(版本变了?)'
    txt = txt.replace(anchor_imp, anchor_imp + 'from .json.xwk78e import OnAutoEmptyT80, OnWashInfoT80\n', 1)
    anchor_block = '    if message_type := messages.get(message_name, None):\n        return message_type\n'
    assert anchor_block in txt, 'messages 注册锚点不匹配(版本变了?)'
    add = ('    if static.data_type == DataType.JSON and (\n'
           '        station := static.capabilities.station\n'
           '    ) is not None and getattr(station, "wash_mode", None) is not None:\n'
           '        messages = messages | {\n'
           '            "onAutoEmpty": OnAutoEmptyT80,\n'
           '            "onWashInfo": OnWashInfoT80,\n'
           '        }\n\n' + anchor_block)
    txt = txt.replace(anchor_block, add, 1)
    open(p, 'w').write(txt)
    print('messages/__init__.py 已插入')
else:
    print('messages/__init__.py 已打过')

p = os.path.join(D, 'mqtt_client.py')
txt = open(p).read()
if 'from .commands.json.xwk78e import' not in txt:
    anchor_imp = 'from .commands import COMMANDS_WITH_MQTT_P2P_HANDLING\n'
    assert anchor_imp in txt, 'mqtt import 锚点不匹配(版本变了?)'
    txt = txt.replace(anchor_imp, anchor_imp + 'from .commands.json.xwk78e import SetTrueDetectV2, SetWashInfoT80\n', 1)
    anchor_block = '''            command_name = topic_split[2]
            command_type = COMMANDS_WITH_MQTT_P2P_HANDLING.get(data_type, {}).get(
                command_name, None
            )
            if command_type is None:
                _LOGGER.debug(
                    "Command %s does not support p2p handling (yet)", command_name
                )
                return
'''
    assert anchor_block in txt, 'mqtt p2p 锚点不匹配(版本变了?)'
    add = '''            command_name = topic_split[2]
            command_type = COMMANDS_WITH_MQTT_P2P_HANDLING.get(data_type, {}).get(
                command_name, None
            )
            if command_type is None:
                if sub_info := self._subscriptions.get(topic_split[3]):
                    station = sub_info.device_info.static.capabilities.station
                    if station is not None and getattr(station, "wash_mode", None) is not None:
                        if command_name == "setTrueDetect":
                            command_type = SetTrueDetectV2
                        elif command_name == "setWashInfo":
                            command_type = SetWashInfoT80
            if command_type is None:
                _LOGGER.debug(
                    "Command %s does not support p2p handling (yet)", command_name
                )
                return
'''
    txt = txt.replace(anchor_block, add, 1)
    open(p, 'w').write(txt)
    print('mqtt_client.py 已插入')
else:
    print('mqtt_client.py 已打过')

n = 0
for root, dirs, files in os.walk(D):
    for f in files:
        if f.endswith('.pyc'):
            os.remove(os.path.join(root, f))
            n += 1
print(f'清理 pyc {n} 个')
print('=== 重放完成, 记得 sudo docker restart homeassistant ===')
