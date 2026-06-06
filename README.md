# AI实时同声传译助手
## 演示视频
> B站演示地址：视频链接

## 一、项目简介
本项目使用 **Python + Visual Studio** 开发，针对英文网课、国际会议、外文直播场景实现AI实时同声翻译。
实现链路：**实时音频采集 → 流式语音识别 → 云端机器翻译 → 文本自动纠错去重 → 桌面置顶悬浮双语字幕 + 可选语音播报**。
项目完成需求规定的**译文自动纠错**功能，通过文本相似度校验+短句缓存聚合优化识别碎片化、错词、重复字幕问题。

## 二、运行环境
- 开发IDE：Visual Studio
- Python版本：Python3.9+
- 系统：Windows 10 / Windows11

## 三、技术组成
### 1. 第三方依赖库（全部在requirements.txt声明）
1. `faster-whisper`：轻量化语音识别模型，实现英文实时ASR
2. `sounddevice + numpy`：硬件麦克风音频采集、音频切片处理
3. `tencentcloud-sdk-python`：腾讯云机器翻译API（英→中）
4. `pyttsx3`：本地离线中文语音播报（默认关闭）
5. `python-dotenv`：密钥环境变量管理

### 2. 自研原创模块（项目核心自研内容）
1. 通用工具库：配置文件加载、环境变量解析、全局日志封装
2. 音频采集模块：自定义缓冲区，自动枚举本机音频输入设备
3. 文本纠错引擎：基于序列相似度算法实现重复过滤、识别内容修正（题目要求核心功能）
4. 任务调度中心：多线程+消息队列解耦全业务链路，避免UI阻塞
5. Tkinter自研GUI：主控设置窗口、半透明置顶悬浮字幕

> 本项目全程自主编码开发，无抄袭，未直接复用过往项目代码，第三方组件全部在文档标注。

## 四、项目目录结构
```
AiLiveTranslator/
├─ backend/            # 音频/识别/翻译/纠错/调度/TTS核心后端
├─ frontend/           # 控制窗口、悬浮字幕前端代码
├─ config/             # 项目全局配置json
├─ utils/              # 配置读取、日志、公共工具函数
├─ docs/               # PR开发规划文档
├─ main.py             # 程序启动入口
├─ requirements.txt    # 项目依赖清单
├─ .env.example        # 密钥配置模板
├─ AiLiveTranslator.pyproj
└─ AiLiveTranslator.slnx
```

## 五、Windows CMD部署步骤
```cmd
#1.进入项目根目录
cd /d 七牛云\AiLiveTranslator

#2.激活本地虚拟环境
env\Scripts\activate.bat

#3.安装全部依赖
pip install -r requirements.txt

#4.生成密钥配置文件
copy .env.example .env

#5.填写腾讯云翻译密钥
notepad .env
```
打开.env填入：
```env
TENCENT_SECRET_ID=腾讯云密钥ID
TENCENT_SECRET_KEY=腾讯云密钥KEY
```
```cmd
#6.启动程序
python main.py
```

## 六、软件使用说明
1. 运行`main.py`自动弹出**主控面板**+**置顶悬浮双语字幕窗口**；
2. 在下拉栏选择需要使用的麦克风设备，点击【开始传译】；
3. 对着麦克风朗读英文，上方展示识别原文，下方展示经过纠错后的中文译文；
4. 字幕自动聚合短句，过滤重复识别内容，减少字幕频繁闪烁；
5. 【暂停】终止采集，【字幕演示】快速预览界面效果；
6. 语音播报功能默认关闭，如需开启可修改配置。

## 七、优化方向
1. 提升Whisper识别beam_size参数、切换base模型、开启上下文联动，优化单词错位识别不准问题；
2. 音频切片由2s调整至2.5s，优化短句割裂；
3. 新增文本缓存聚合逻辑，凑够指定字符再输出字幕，解决零碎单词刷屏；
4. 优化UI尺寸、字体、配色，优化主控窗口与悬浮字幕视觉效果。

## 八、组队分工
- **陈宇娜**：负责后端全模块+utils工具类开发（音频采集、语音识别、翻译接口、纠错算法、任务调度），负责后端相关PR提交与代码维护。
- **刘千渝**：负责前端GUI开发、项目入口main、依赖整理、README编写、演示视频录制、项目文档编写，前端相关PR提交。

> 仓库所有Commit、PR由两位开发者独立账号分别提交，开发记录分布在项目全周期，无最后突击提交。


## 九、依赖清单 requirements.txt
```txt
faster-whisper
sounddevice
numpy
tencentcloud-sdk-python
pyttsx3
python-dotenv
```