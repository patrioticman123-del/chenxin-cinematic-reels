# V4 風格與合成示範

這是一支約 13.5 秒的短測試片，而不是正式 60–90 秒衛教片。此目錄的 `project.json` 對應 `shot_01.jpg` 至 `shot_03.jpg`、`narration_01.wav` 至 `narration_03.wav`。

若 GitHub 只有文字檔，請將原交付 ZIP 的相應二進位素材一次上傳到本資料夾。`v4-style-reference.mp4` 僅作為風格校準；畫面中的 3D 視覺與動態不代表具有完整 3D 模型生成能力，醫學內容發布前需醫師審核。

合成測試：
```bash
python tools/reels.py render examples/knee-pain/project.json --size 360x640 --out output/test.mp4
```
