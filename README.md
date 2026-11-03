# MP3Downloader for Windows

独立的 Windows MP3 音频提取与转换工具。它使用内置浏览器识别网页公开媒体请求，可将支持的音频或视频来源提取音轨并保存为 MP3。

## 功能
- 内置 Chromium 浏览器。
- 识别 MP3、M4A、AAC、WAV、FLAC、OGG、OPUS 等音频资源。
- 识别 MP4 等常见视频资源，以及 HLS M3U8、DASH MPD 播放列表。
- 扫描网页 HTML 中公开的媒体直链。
- 在公开 API 允许时尝试解析 Bilibili 视频 MP4 地址。
- 选择媒体候选项后，保存为 MP3 文件。
- 通过 imageio-ffmpeg 携带 FFmpeg，无需单独安装 FFmpeg。
- 本项目只负责 MP3 提取与转换，不包含独立的视频链接复制版功能。

## Windows 运行
需要 Windows 10/11 64 位与 Python 3.11。

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## 说明与限制
转换需要媒体 URL 可访问且包含音轨。部分网站需要登录 Cookie、授权、特殊请求头或反爬验证，软件可能无法访问。仅有 blob 地址或受 DRM 保护的流可能无法转换。本软件不会绕过 DRM、付费墙、登录要求或其他访问控制。请只保存你有权下载的媒体。
