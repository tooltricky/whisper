# Whisper Web 界面

这是一个基于 Streamlit 的用户友好的 Web 界面，用于 OpenAI 的 Whisper 语音识别模型。

## 功能特性

- 🎙️ **多格式支持**: 支持 MP3、WAV、M4A、FLAC、OGG、WebM 等多种音频格式
- 🌍 **多语言识别**: 支持 99 种语言的自动检测和转录
- 🔄 **翻译功能**: 可将非英语语音翻译成英文
- 🎯 **多模型选择**: 从 tiny 到 large，根据需求选择不同大小的模型
- ⚡ **实时处理**: 快速转录音频文件
- 📊 **详细分段**: 显示带时间戳的详细转录分段
- 💾 **结果导出**: 支持下载转录文本和SRT字幕文件
- 📝 **SRT字幕生成**: 自动生成带时间戳的标准SRT字幕文件，支持智能分段
- 🎨 **友好界面**: 简洁直观的用户界面

## 安装步骤

### 1. 系统要求

- Python 3.8-3.11
- ffmpeg（音频处理必需）

### 2. 安装 ffmpeg

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows (使用 Chocolatey):**
```bash
choco install ffmpeg
```

**Windows (使用 Scoop):**
```bash
scoop install ffmpeg
```

### 3. 安装 Python 依赖

在 `webui` 目录下运行：

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install streamlit openai-whisper torch torchaudio ffmpeg-python numpy
```

## 使用方法

### 启动应用

在 `webui` 目录下运行：

```bash
streamlit run app.py
```

应用将自动在浏览器中打开，默认地址为 `http://localhost:8501`

### 使用步骤

1. **选择模型**: 在左侧边栏选择合适的 Whisper 模型
   - 推荐使用 `turbo` 模型（速度快且准确）
   - 英语识别可使用 `.en` 后缀的模型

2. **选择任务**:
   - `transcribe`: 转录为原语言文本
   - `translate`: 翻译成英文（注意：turbo 模型不支持）

3. **指定语言**: 选择音频的语言，或使用自动检测

4. **上传文件**: 点击上传按钮选择音频文件

5. **开始转录**: 点击"开始转录"按钮

6. **查看结果**: 转录完成后可以:
   - 查看完整文本
   - 查看带时间戳的详细分段
   - 下载文本文件
   - 下载SRT字幕文件（带精确时间戳，适用于视频字幕）

### 高级选项

在左侧边栏的"高级选项"中可以调整：

- **Temperature**: 采样温度，控制输出的随机性
- **Beam Size**: 束搜索大小，影响准确度和速度
- **Best Of**: 候选数量，从多个候选中选择最佳结果
- **字幕每行最大字符数**: 控制SRT字幕每行显示的最大字符数（20-80字符，默认40），适合不同显示需求

## 模型说明

| 模型 | 参数量 | 所需显存 | 相对速度 | 适用场景 |
|------|--------|---------|---------|---------|
| tiny | 39M | ~1 GB | ~10x | 快速测试，对准确度要求不高 |
| base | 74M | ~1 GB | ~7x | 轻量级应用 |
| small | 244M | ~2 GB | ~4x | 速度和准确度的良好平衡 |
| medium | 769M | ~5 GB | ~2x | 高准确度需求，支持翻译 |
| large | 1550M | ~10 GB | 1x | 最高准确度 |
| turbo | 809M | ~6 GB | ~8x | **推荐**：最佳的速度和准确度平衡 |

**注意事项:**
- `.en` 后缀的模型仅支持英语，但在英语识别上表现更好
- `turbo` 模型不支持翻译任务
- 进行翻译时请使用 `medium` 或 `large` 模型

## 支持的语言

Whisper 支持包括但不限于以下语言：

中文、英语、日语、韩语、西班牙语、法语、德语、俄语、阿拉伯语、葡萄牙语、意大利语、荷兰语、波兰语、土耳其语、越南语、泰语、印地语、印尼语等 99 种语言。

完整语言列表请查看：[tokenizer.py](https://github.com/openai/whisper/blob/main/whisper/tokenizer.py)

## 故障排除

### 问题: 模型下载失败

**解决方法**: Whisper 会在首次使用时自动下载模型，请确保网络连接正常。模型文件较大，可能需要一些时间。

### 问题: ffmpeg 未找到

**解决方法**: 确保已正确安装 ffmpeg，并且在系统 PATH 中可用。运行 `ffmpeg -version` 检查安装。

### 问题: CUDA/GPU 相关错误

**解决方法**:
- 如果有 NVIDIA GPU，安装对应版本的 PyTorch with CUDA
- 如果没有 GPU，Whisper 会自动使用 CPU（速度会较慢）

### 问题: 内存不足

**解决方法**:
- 使用较小的模型（如 tiny 或 base）
- 关闭其他占用内存的程序
- 处理较短的音频片段

## 技术细节

### 工作原理

1. 用户上传音频文件
2. 音频被保存到临时文件
3. Whisper 模型加载（首次使用会自动下载）
4. 使用 30 秒滑动窗口处理音频
5. 返回转录结果和详细分段信息
6. 自动生成SRT字幕文件，智能分割长文本并分配时间戳

### 性能优化

- 模型使用 `@st.cache_resource` 缓存，避免重复加载
- 临时文件在处理完成后自动清理
- 支持进度显示，提供更好的用户体验

### SRT字幕功能详解

**SRT字幕生成特性：**

- **标准格式**: 生成符合SubRip标准的SRT字幕文件
- **精确时间戳**: 时间戳精确到毫秒（格式：HH:MM:SS,mmm）
- **智能分段**:
  - 自动识别中英文标点符号进行分段
  - 根据字符长度智能分割过长字幕
  - 按字符数比例分配时间戳
- **可自定义**: 通过"字幕每行最大字符数"参数控制字幕长度
- **即时下载**: 转录完成后可直接下载SRT文件

**适用场景：**
- 为视频添加字幕
- 会议记录配字幕
- 教学视频制作
- 多媒体内容本地化

## 参考资料

- [Whisper GitHub](https://github.com/openai/whisper)
- [Whisper 论文](https://arxiv.org/abs/2212.04356)
- [OpenAI 博客](https://openai.com/blog/whisper)
- [Streamlit 文档](https://docs.streamlit.io)

## 许可证

本项目遵循 Whisper 的 MIT 许可证。

## 贡献

欢迎提交问题和改进建议！
