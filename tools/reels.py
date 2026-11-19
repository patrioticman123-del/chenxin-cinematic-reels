#!/usr/bin/env python3
"""Chenxin cinematic reels: topic-independent storyboard, prompts, voice and FFmpeg assembly."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "C:/Windows/Fonts/msjh.ttc",
    "C:/Windows/Fonts/msjhbd.ttc",
]

def run(args):
    p = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError("Command failed: " + " ".join(map(str,args)) + "\n" + p.stderr[-3500:])
    return p.stdout

def load(path):
    path = Path(path).resolve()
    return json.loads(path.read_text(encoding="utf-8")), path.parent

def resolve(base, path):
    if not path: return None
    p = Path(path)
    return p if p.is_absolute() else (base / p).resolve()

def validate(data, base, strict=False):
    errors, warnings = [], []
    if not isinstance(data,dict): return ["Project must be a JSON object"],warnings
    scenes = data.get("scenes",[])
    if not isinstance(scenes,list) or not scenes: return ["scenes must be nonempty list"],warnings
    duration_total=0.0
    for i,sc in enumerate(scenes,1):
        if not isinstance(sc,dict):
            errors.append(f"scene {i}: must be an object");continue
        duration=sc.get("duration")
        if isinstance(duration,bool) or not isinstance(duration,(int,float)) or not 0.3<=duration<=60:
            errors.append(f"scene {i}: invalid duration")
        else: duration_total+=duration
        media=resolve(base,sc.get("media"))
        if media is None or not media.is_file():
            errors.append(f"scene {i}: missing media")
        elif media.suffix.lower() not in {".jpg",".jpeg",".png",".webp",".mp4",".mov",".mkv",".webm"}:
            errors.append(f"scene {i}: unsupported media")
        voice=resolve(base,sc.get("voice"))
        if voice and not voice.is_file(): errors.append(f"scene {i}: missing voice")
        if len(sc.get("caption",""))>38: warnings.append(f"scene {i}: long caption")
    if not 60<=duration_total<=90:
        warnings.append(f"runtime {duration_total:g}s outside 60–90 seconds")
        if strict: errors.append("strict mode: runtime outside target")
    music=resolve(base,data.get("music"))
    if music and not music.is_file(): errors.append("missing music")
    return errors,warnings

def cjk_font(size):
    paths=[os.environ.get("REELS_FONT")]+FONTS
    for path in paths:
        if path and Path(path).is_file(): return ImageFont.truetype(path,size)
    raise RuntimeError("Chinese font not found; set REELS_FONT to a CJK font path")

def caption_png(path, caption, title, width, height):
    img=Image.new("RGBA",(width,height),(0,0,0,0))
    draw=ImageDraw.Draw(img)
    if title:
        f=cjk_font(max(22,int(width*0.045)))
        draw.rounded_rectangle((width*.08,height*.09,width*.92,height*.165),
                               radius=int(width*.02), fill=(12,35,55,174))
        draw.text((width/2,height*.12),title,font=f,anchor="mm",fill="white")
    if caption:
        f=cjk_font(max(24,int(width*.058)))
        lines=[]
        for original in caption.split("\n"):
            while original:
                lines.append(original[:13]); original=original[13:]
        lines=lines[:3]
        spacing=int(width*.09)
        blockheight=len(lines)*spacing+int(width*.07)
        y=int(height*.80-blockheight*.5)
        draw.rounded_rectangle((width*.065,y,width*.935,y+blockheight),
                               radius=int(width*.03),fill=(2,12,24,196))
        for idx,line in enumerate(lines):
            draw.text((width/2,y+int(width*.025)+idx*spacing),line,
                      font=f,anchor="mt",fill="white",stroke_width=2,stroke_fill="#081c2a")
    img.save(path)

def generate_prompts(data,output):
    style=(ROOT/"docs"/"style-bible.md").read_text(encoding="utf-8")
    doctor=(ROOT/"docs"/"character-bible.md").read_text(encoding="utf-8")
    lines=["# Cinematic video prompts", "Use doctor reference photograph only when rights cleared.","",style,doctor]
    for i,scene in enumerate(data["scenes"],1):
        lines += ["",f"## Shot {i:02} — {scene.get('title','')}",
                  f"Duration: {scene['duration']} seconds",
                  f"Visual: {scene.get('visual_prompt','TBD')}",
                  f"Motion: {scene.get('motion_prompt','Natural walk, gestures and tracking')}",
                  "Format: 9:16, photoreal cinematic 3D, continuous human motion; NO embedded text.",
                  f"Caption (post-production): {scene.get('caption','')}",
                  f"Voice (post-production): {scene.get('narration','')}",
                  "Avoid inaccurate anatomy, identity drift, extra fingers, floating feet and frame flicker."]
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("Saved prompts:",path)

def generate_voice(data,project,base,voice_name):
    if not shutil.which("edge-tts"):
        raise RuntimeError("Install optional TTS: pip install edge-tts (internet required)")
    for i,scene in enumerate(data["scenes"],1):
        if not scene.get("narration"):continue
        fname=f"narration_{i:02}.mp3"
        run(["edge-tts","--voice",voice_name,"--text",scene["narration"],
             "--write-media",base/fname])
        scene["voice"]=fname
    Path(project).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def render(data,base,output,size="1080x1920",fps=30,crf=19):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg and FFprobe must be on PATH")
    w,h=map(int,size.lower().split("x"))
    if w<=0 or h<=0 or w%2 or h%2: raise ValueError("size must contain even positive dimensions")
    errors,warnings=validate(data,base)
    for msg in warnings: print("WARNING:",msg,file=sys.stderr)
    if errors: raise ValueError("\n".join(errors))
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="chenxin_") as tmp:
        temp=Path(tmp)
        scene_videos=[]
        voices=[]
        for idx,sc in enumerate(data["scenes"],1):
            dur=float(sc["duration"])
            src=resolve(base,sc["media"])
            cap=temp/f"cap_{idx:02}.png"
            caption_png(cap,sc.get("caption",""),sc.get("title",""),w,h)
            video=temp/f"scene_{idx:02}.mp4"
            still=src.suffix.lower() in {".jpg",".jpeg",".png",".webp"}
            cmd=["ffmpeg","-hide_banner","-loglevel","error","-y"]
            cmd+=["-loop","1","-framerate",str(fps),"-i",src] if still else ["-stream_loop","-1","-i",src]
            cmd+=["-loop","1","-i",cap,
                  "-filter_complex",f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps},format=yuv420p[bg];[bg][1:v]overlay=0:0:shortest=1,format=yuv420p[v]",
                  "-map","[v]","-t",dur,"-c:v","libx264","-preset","medium",
                  "-crf",crf,"-pix_fmt","yuv420p","-an","-movflags","+faststart",video]
            run(cmd);scene_videos.append(video)
            aud=temp/f"voice_{idx:02}.wav"
            voice=resolve(base,sc.get("voice"))
            if voice:
                run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",voice,
                     "-af","apad","-t",dur,"-ar","48000","-ac","2",aud])
            else:
                run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi",
                     "-i","anullsrc=r=48000:cl=stereo","-t",dur,aud])
            voices.append(aud)
        vlist=temp/"videos.txt"
        vlist.write_text("".join(f"file '{s}'\n" for s in scene_videos),encoding="utf-8")
        joined=temp/"joined.mp4"
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
             "-i",vlist,"-c","copy",joined])
        alist=temp/"audios.txt"
        alist.write_text("".join(f"file '{s}'\n" for s in voices),encoding="utf-8")
        joined_audio=temp/"joined.wav"
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
             "-i",alist,"-c:a","pcm_s16le",joined_audio])
        music=resolve(base,data.get("music"))
        if music:
            args=["ffmpeg","-hide_banner","-loglevel","error","-y","-i",joined,
                  "-i",joined_audio,"-stream_loop","-1","-i",music,
                  "-filter_complex","[2:a]volume=0.12[m];[1:a][m]amix=inputs=2:duration=first[a]",
                  "-map","0:v","-map","[a]"]
        else:
            args=["ffmpeg","-hide_banner","-loglevel","error","-y","-i",joined,
                  "-i",joined_audio,"-map","0:v","-map","1:a"]
        run(args+["-c:v","copy","-c:a","aac","-b:a","192k","-shortest",
                  "-movflags","+faststart",output])
    print("Rendered:",output)

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="command",required=True)
    p=sub.add_parser("init");p.add_argument("directory")
    p=sub.add_parser("validate");p.add_argument("project");p.add_argument("--strict",action="store_true")
    p=sub.add_parser("prompts");p.add_argument("project");p.add_argument("--out",default="scene-prompts.md")
    p=sub.add_parser("voice");p.add_argument("project");p.add_argument("--voice",default="zh-TW-YunJheNeural")
    p=sub.add_parser("render");p.add_argument("project");p.add_argument("--out",default="output.mp4")
    p.add_argument("--size",default="1080x1920");p.add_argument("--fps",type=int,default=30)
    p.add_argument("--crf",type=int,default=19)
    args=ap.parse_args()
    try:
        if args.command=="init":
            dest=Path(args.directory).resolve()
            dest.mkdir(parents=True,exist_ok=True)
            project=dest/"project.json"
            if project.exists():raise RuntimeError(f"Already exists: {project}")
            shutil.copyfile(ROOT/"templates"/"project.blank.json",project)
            (dest/"media").mkdir(exist_ok=True)
            print("Created:",project);return
        data,base=load(args.project)
        if args.command=="validate":
            errors,warnings=validate(data,base,args.strict)
            for msg in warnings:print("WARNING",msg)
            for msg in errors:print("ERROR",msg)
            if errors:sys.exit(1)
            print("PASS:",sum(s["duration"] for s in data["scenes"]),"seconds")
        elif args.command=="prompts":generate_prompts(data,args.out)
        elif args.command=="voice":generate_voice(data,args.project,base,args.voice)
        elif args.command=="render":render(data,base,args.out,args.size,args.fps,args.crf)
    except (RuntimeError,ValueError,FileNotFoundError) as exc:
        print("ERROR:",exc,file=sys.stderr)
        sys.exit(1)
if __name__=="__main__":
    main()
