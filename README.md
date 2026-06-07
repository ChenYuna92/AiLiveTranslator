# AI 同声传译助手

## 项目简介

本项目用于观看英语演讲、技术分享、国际会议或网课时，将单向音频流实时翻译成中文，并用悬浮双语字幕展示。

字幕会直接覆盖更新为当前最合适的一版，不额外展示“原文/修正版”历史，满足题目要求中的自动修正能力。

## Demo 视频

点击观看 AI 同声传译助手演示视频  https://b23.tv/8MGtHfQ

## 功能

- 实时采集麦克风、系统混音或虚拟声卡音频。
- 使用 `faster-whisper` 识别英文语音。
- 使用腾讯云机器翻译将英文翻译为中文。
- 显示置顶悬浮双语字幕。
- 自动过滤静音幻觉、重复字幕和明显错误文本。
- 可选中文语音播报，默认关闭。

## 运行环境

- Windows 10 / Windows 11
- Python 3.9+

## 安装与启动

```powershell
cd D:\七牛云\AiLiveTranslator
.\env\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
python main.py
```

在 `.env` 中填写腾讯云翻译密钥：

```env
TENCENT_SECRET_ID=你的SecretId
TENCENT_SECRET_KEY=你的SecretKey
```

如果不填写密钥，程序可以启动，但不会得到真正的中文翻译。

## 使用方式

1. 启动后会出现控制窗口和悬浮字幕窗口。
2. 选择音频输入源。
3. 点击“开始传译”。
4. 点击“暂停”停止。
5. “字幕演示”可用于检查界面效果。

翻译电脑播放的视频时，建议使用系统混音或虚拟声卡，避免用麦克风收外放声音。

## 项目结构

```text
backend/      音频采集、语音识别、翻译、调度、TTS
frontend/     控制窗口和字幕窗口
config/       配置文件
utils/        日志和配置读取
docs/         PR 规划
main.py       启动入口
```

## 依赖说明

第三方依赖已写入 `requirements.txt`。核心原创部分包括实时调度、字幕更新、静音过滤、重复过滤和修正覆盖逻辑。


## 团队协作说明

本项目由本人账号完成代码提交。队友全程参与选题讨论、需求分析、效果测试、Demo 反馈和文档校对。由于开发环境和账号安排原因，代码提交统一由本人完成。