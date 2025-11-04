import streamlit as st
import whisper
import os
import tempfile
from pathlib import Path
import time

# Page configuration
st.set_page_config(
    page_title="Whisper 语音转文字",
    page_icon="🎙️",
    layout="wide"
)

# Title and description
st.title("🎙️ Whisper 语音转文字 Web 界面")
st.markdown("""
这是一个基于 OpenAI Whisper 的语音识别 Web 应用。支持多语言语音转录和翻译功能。
""")

# Sidebar for settings
st.sidebar.header("⚙️ 设置")

# Model selection
model_options = ["tiny", "base", "small", "medium", "large", "turbo",
                 "tiny.en", "base.en", "small.en", "medium.en"]
selected_model = st.sidebar.selectbox(
    "选择模型",
    model_options,
    index=5,  # Default to turbo
    help="较大的模型更准确但速度较慢。'turbo' 模型提供最佳的速度和准确性平衡。"
)

# Task selection
task_options = ["transcribe", "translate"]
selected_task = st.sidebar.selectbox(
    "选择任务",
    task_options,
    help="transcribe: 转录原语言\ntranslate: 翻译成英文（注意：turbo 模型不支持翻译）"
)

# Language selection
languages = {
    "自动检测": None,
    "中文": "Chinese",
    "英文": "English",
    "日语": "Japanese",
    "韩语": "Korean",
    "西班牙语": "Spanish",
    "法语": "French",
    "德语": "German",
    "俄语": "Russian",
    "阿拉伯语": "Arabic",
    "葡萄牙语": "Portuguese",
    "意大利语": "Italian"
}

selected_language = st.sidebar.selectbox(
    "语言",
    list(languages.keys()),
    help="指定音频的语言，或选择'自动检测'"
)

# Advanced options
with st.sidebar.expander("🔧 高级选项"):
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1,
                           help="采样温度，较高的值会增加随机性")
    beam_size = st.number_input("Beam Size", 1, 10, 5,
                                help="束搜索的大小，较大的值可能提高准确性但速度较慢")
    best_of = st.number_input("Best Of", 1, 10, 5,
                              help="从多少个候选中选择最佳结果")

# Warning for turbo model and translation
if selected_model == "turbo" and selected_task == "translate":
    st.sidebar.warning("⚠️ 'turbo' 模型不支持翻译任务。请选择其他模型（如 medium 或 large）以进行翻译。")

# Model loading status
@st.cache_resource
def load_whisper_model(model_name):
    """Load and cache the Whisper model"""
    with st.spinner(f"正在加载 {model_name} 模型..."):
        model = whisper.load_model(model_name)
    return model

# Main content area
st.header("📤 上传音频文件")

# File uploader
uploaded_file = st.file_uploader(
    "选择音频文件",
    type=["mp3", "mp4", "wav", "m4a", "flac", "ogg", "webm"],
    help="支持常见的音频和视频格式"
)

# Audio recording option
st.markdown("---")
st.subheader("🎤 或者录制音频")
st.info("浏览器录音功能需要 HTTPS 或 localhost 环境。")

# Process button
if uploaded_file is not None:
    # Display audio player
    st.audio(uploaded_file)

    # Show file info
    file_details = {
        "文件名": uploaded_file.name,
        "文件大小": f"{uploaded_file.size / 1024:.2f} KB",
        "文件类型": uploaded_file.type
    }

    with st.expander("📋 文件信息"):
        for key, value in file_details.items():
            st.write(f"**{key}:** {value}")

    st.markdown("---")

    # Process button
    if st.button("🚀 开始转录", type="primary", use_container_width=True):
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Load model
            model = load_whisper_model(selected_model)

            # Prepare transcription options
            transcribe_options = {
                "task": selected_task,
                "temperature": temperature,
                "beam_size": beam_size,
                "best_of": best_of
            }

            # Add language if specified
            if languages[selected_language] is not None:
                transcribe_options["language"] = languages[selected_language]

            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Start transcription
            status_text.text("正在处理音频文件...")
            progress_bar.progress(30)

            start_time = time.time()
            result = model.transcribe(tmp_file_path, **transcribe_options)
            end_time = time.time()

            progress_bar.progress(100)
            status_text.text("转录完成！")

            # Display results
            st.success(f"✅ 转录完成！用时: {end_time - start_time:.2f} 秒")

            # Detected language
            if "language" in result:
                st.info(f"🌐 检测到的语言: {result['language'].upper()}")

            # Transcription text
            st.subheader("📝 转录结果")
            st.text_area(
                "文本内容",
                result["text"],
                height=300,
                help="您可以复制此文本"
            )

            # Download button for text
            st.download_button(
                label="📥 下载文本文件",
                data=result["text"],
                file_name=f"{Path(uploaded_file.name).stem}_transcription.txt",
                mime="text/plain"
            )

            # Show segments if available
            if "segments" in result and len(result["segments"]) > 0:
                with st.expander("🔍 查看详细分段"):
                    for i, segment in enumerate(result["segments"]):
                        st.markdown(f"""
                        **分段 {i+1}**
                        - 时间: {segment['start']:.2f}s - {segment['end']:.2f}s
                        - 文本: {segment['text']}
                        """)

            # Clean up temporary file
            os.unlink(tmp_file_path)

        except Exception as e:
            st.error(f"❌ 处理过程中出错: {str(e)}")
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

else:
    st.info("👆 请上传音频文件开始使用")

# Footer with information
st.markdown("---")
with st.expander("ℹ️ 关于 Whisper 模型"):
    st.markdown("""
    ### 可用模型

    | 模型 | 参数 | 所需显存 | 相对速度 | 说明 |
    |------|------|---------|---------|------|
    | tiny | 39M | ~1 GB | ~10x | 最快但准确度较低 |
    | base | 74M | ~1 GB | ~7x | 快速且轻量 |
    | small | 244M | ~2 GB | ~4x | 良好的速度和准确度平衡 |
    | medium | 769M | ~5 GB | ~2x | 较高准确度 |
    | large | 1550M | ~10 GB | 1x | 最高准确度 |
    | turbo | 809M | ~6 GB | ~8x | 推荐：速度快且准确度高 |

    **注意:**
    - `.en` 后缀的模型仅支持英语，但在英语识别上表现更好
    - `turbo` 模型不支持翻译任务
    - 翻译任务请使用 `medium` 或 `large` 模型

    ### 支持的语言
    Whisper 支持 99 种语言的转录和翻译。

    ### 了解更多
    - [Whisper 项目主页](https://github.com/openai/whisper)
    - [技术论文](https://arxiv.org/abs/2212.04356)
    - [OpenAI 博客](https://openai.com/blog/whisper)
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Powered by <a href='https://github.com/openai/whisper'>OpenAI Whisper</a> | Built with <a href='https://streamlit.io'>Streamlit</a></p>
</div>
""", unsafe_allow_html=True)
