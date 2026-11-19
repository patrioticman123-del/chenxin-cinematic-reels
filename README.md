# 宸新復健科 — Cinematic Doctor Reels Kit (方案 B)

一套**無預設疾病主題**、可反覆引用的醫療科普短影音 GitHub Skill。每次在 Codex 指定主題與文章即可產生分鏡、旁白、字幕及影片模型提示詞，取得素材後交由 FFmpeg 合成為直式 MP4。

**影片預設：**60–90 秒（72 秒起始模板）、9:16、1080×1920、30 FPS、繁體中文、台灣中文男聲。角色是穿白袍、淺藍襯衫、深藍領帶的醫師，在巨大的人體解剖場景帶領民眾走路、指向構造，搭配電影感跟拍。

> **請注意：** 這是 storyboard / prompt / 剪輯流程專案，不是內建 Veo 或 Sora 的一鍵 3D 影片生成器。真正人物運動必須由外部影片模型生成的連續影片提供；提供圖片的話只能做動態運鏡。醫師照片與 V4 示範素材在原始交付 ZIP 中，若未出現在 GitHub 請自行補齊；腳本與模板仍可使用。

## 快速開始

安裝 Python 3.10+、FFmpeg 與 ffprobe：

```bash
python -m pip install -r requirements.txt
python tools/reels.py init projects/my-topic
```

修改 `projects/my-topic/project.json`，填入本集的主題、來源、旁白、字幕、鏡頭描述和媒體路徑。

```bash
python tools/reels.py prompts projects/my-topic/project.json --out projects/my-topic/prompts.md
python tools/reels.py validate projects/my-topic/project.json
python tools/reels.py render projects/my-topic/project.json --out projects/my-topic/output.mp4
```

第三步需各幕有實際媒體素材。若已有授權音檔，填入每幕 `voice`；可選擇另行安裝 `edge-tts` 生成台灣中文配音。

## 每次用在 Codex 的提示詞

```text
請先閱讀本 Repository 的 SKILL.md、README.md、
docs/style-bible.md、docs/character-bible.md 和 prompt-templates/。

主題：【在這裡填】
衛教內容或來源：【貼文章／重點／網址】
觀眾：【在這裡填】
最重要的觀念：【在這裡填】

請依照固定醫師角色與電影感 3D 導覽風格，做 75 秒、9:16
繁中 Reels。先輸出有秒數的分鏡、旁白、字幕、每鏡生成
Prompt，建立獨立 projects/<slug>/project.json；取得真實
連續動作鏡頭後合成 MP4。若無法使用影片模型，請明確
說明，不能以靜態縮放宣稱完成真正的 3D 角色動畫。
```

## 專案目錄

- `SKILL.md` — 固定角色、分鏡、醫療審核和輸出原則
- `docs/` — 美術設計、醫師角色、分鏡和驗收清單
- `templates/project.blank.json` — 無主題預設影片
- `prompt-templates/` — 每次新增主題的輸入格式、影片生成、配音、封面及社群文案
- `tools/reels.py` — 初始化、驗證、提示詞和 FFmpeg 合成
- `tests/` — 基本驗證
- `assets/character/` — 使用者照片與角色設定（如已提供）
- `projects/` — 每支影片獨立資料夾

原始靈感參考 [Summerhuang585/card-reels-kit](https://github.com/Summerhuang585/card-reels-kit)，但本專案獨立實作；前者是**無人物、無配音的 HTML 圖卡影片**，不是本專案的 3D 影片引擎。

## 授權提醒
公開專案並不等於第三方參考影片、音樂、真人影像都可任意再利用。避免放入未經授權素材、病患資料或 API 金鑰。
