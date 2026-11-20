# 宸新復健科｜Codex × Google Flow：30 秒 Reels Skill

**通用、無預設疾病主題。** 每集由 Codex 根據使用者提供的內容產生分鏡稿、4 組 Google Flow 英文 Prompt、繁體中文旁白與字幕；使用者在 Google Flow 生成影片，下載後用 Flow Scenebuilder 或本專案 FFmpeg 合成。

## 正式工作流程

1. Codex 閱讀 `SKILL.md`、`docs/`、`templates/project.blank.json` 和 `prompt-templates/`。
2. 輸入主題、衛教內容、受眾、最重要的觀念。Codex 產出四幕、影片生成提示詞、參考圖使用方案和獨立 `projects/<slug>/project.json`。
3. 在 [Google Flow](https://labs.google/fx/tools/flow) 選 Video、9:16（portrait）、可用的 8 秒模式；在支援的模型中加入相同的醫師參考照和前一幕的保存畫格，建立**4 段各 8 秒**動態片段。
4. 下載影片命名 `shot_01.mp4` 至 `shot_04.mp4`；**最終剪輯使用 8+8+8+6 = 30 秒**。最後一段生成 8 秒但只取前 6 秒。
5. 預設後製另加台灣中文男聲旁白及繁體字幕，避免跨段原生語音聲線不一致。實際音檔放入 `media/` 並設定各幕 `voice`。
6. 醫師確認解剖與醫療敘述、角色一致性、音量、成片長度再發布。

**重要：** 這不是 Codex 直接連線 Flow 一鍵生成工具。Flow 的模式、片長、參考圖片與音訊依所選模型及帳戶實際功能而定；不可宣稱尚未產生的素材已完成。不要把靜態照片縮放當作真正 3D 人物行走。

## 標準設定
- 成片 **30.0 秒**，1080×1920 目標，9:16，30 fps，繁體中文字幕。
- 醫師：固定白袍、淺藍襯衫、深藍領帶，與參考照片相近的輕微動畫化 3D 人物。
- Hook 約 0–8s；巨大人體結構 8–16s；醫學機制 16–24s；結論與品牌 24–30s。
- 選模型時以 Google Flow 介面為準；若不能生成 8s，Codex 要改用該模型允許的 4/6/8s 素材排列，維持成片總長。

## 每次給 Codex 的通用提示詞

```text
請閱讀本 Repository 的 SKILL.md、README.md、docs/、templates/、prompt-templates/。
主題：【填寫】
衛教內容／來源：【貼文章或重點】
觀眾：【填寫】
核心觀念：【一句話】
先做 30 秒分鏡：4 段 Google Flow 影片素材各生成 8 秒，成片使用 8+8+8+6 秒。產生四組可以直接貼到 Google Flow 的英文提示詞、醫師照片與畫格引用說明、逐段台灣中文男聲旁白、繁體字幕、連續性及醫學驗收表。
建立新的 projects/<slug>/project.json，不要修改通用 SKILL.md。只有已取得真實影片素材才進行 MP4 合成；不能假稱已在 Flow 完成生成。
```

## 已有媒體的合成工具

安裝 Python 3.10+、FFmpeg／FFprobe 與中文字體：

```bash
python -m pip install -r requirements.txt
python tools/reels.py init projects/my-topic
python tools/reels.py prompts projects/my-topic/project.json --out projects/my-topic/flow-prompts.md
python tools/reels.py validate projects/my-topic/project.json --strict
python tools/reels.py render projects/my-topic/project.json --out projects/my-topic/final-30s.mp4
```

Flow 各幕影片與旁白若尚未下載，`validate` 會報 missing media，屬正常狀況。既有 `examples/knee-pain/` 是舊長版展示，不是新版 30 秒預設。

## 參考
- [Google Flow 生成影片](https://support.google.com/flow/answer/16353334)
- [Flow 模型功能](https://support.google.com/flow/answer/16352836)
- [Flow Scenebuilder／剪輯](https://support.google.com/flow/answer/16935718)

> 公開專案可供引用，但應遵守本人肖像、患者隱私、第三方素材與台灣醫療廣告相關規範。
