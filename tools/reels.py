#!/usr/bin/env python3
"""CLI: init, validate, prompts, render. Assembles media; does NOT generate 3D footage."""
import argparse, json, shutil, subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[1]
W,H,FPS=1080,1920,30
def load(p):
    p=Path(p).resolve()
    return json.loads(p.read_text(encoding="utf-8")),p.parent
def path(base,p):
    if not p:return None
    x=Path(p)
    return x if x.is_absolute() else base/x
def validate(data,base,strict=False):
    errors,warnings=[],[]
    scenes=data.get("scenes",[])
    if not scenes:return ["scenes must not be empty"],[]
    total=0
    for i,s in enumerate(scenes,1):
        n=s.get("duration",0)
        if isinstance(n,bool) or not isinstance(n,(int,float)) or not .3<=n<=60:errors.append(f"scene {i}: invalid duration")
        else:total+=n
        media=path(base,s.get("media"))
        if not media or not media.is_file():errors.append(f"scene {i}: media missing ({s.get('media')})")
        voice=path(base,s.get("voice"))
        if voice and not voice.is_file():errors.append(f"scene {i}: voice missing")
        if len(s.get("caption",""))>38:warnings.append(f"scene {i}: caption long")
    if abs(total-30)>0.05:
        warnings.append(f"runtime {total:g}s differs from required 30s")
        if strict:errors.append("runtime must equal 30s")
    if data.get("platform")=="Google Flow":
        for i,s in enumerate(scenes,1):
            gen=s.get("flow_generation_seconds")
            if gen is None:warnings.append(f"scene {i}: missing flow_generation_seconds")
            elif gen<s.get("duration",0):errors.append(f"scene {i}: generation shorter than edited duration")
    music=path(base,data.get("music"))
    if music and not music.is_file():errors.append("music missing")
    return errors,warnings
def call(args):
    p=subprocess.run([str(x) for x in args],capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stderr[-2500:])
def caption_image(text,out):
    from PIL import Image,ImageDraw,ImageFont
    choices=["C:/Windows/Fonts/msjhbd.ttc","/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc","/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"]
    file=next((p for p in choices if Path(p).exists()),None)
    if not file:raise RuntimeError("Install Noto CJK font or set up a compatible font")
    f=ImageFont.truetype(file,60)
    im=Image.new("RGBA",(1080,340),(0,0,0,0));d=ImageDraw.Draw(im)
    rows=[];line=""
    for ch in text:
        if d.textbbox((0,0),line+ch,font=f)[2]>950 and line:rows.append(line);line=ch
        else:line+=ch
    if line:rows.append(line)
    if len(rows)>3:raise ValueError("Caption too long; shorten")
    for i,row in enumerate(rows):d.text((540,55+i*95),row,font=f,anchor="mt",fill="white",stroke_width=5,stroke_fill="#213644")
    im.save(out)
def make_prompts(data,out):
    lines=[f"# {data.get('title',data.get('topic','New Reels'))}","", "Cinematic realistic 3D; consistent doctor identity; natural walking, pointing and tracking shots. Do not generate Chinese text in video.",""]
    for i,s in enumerate(data["scenes"],1):
        lines.extend([f"## Flow Shot {i:02} (generate {s.get('flow_generation_seconds',8)}s; edit uses {s['duration']}s)",f"Scene: {s.get('title','')}",f"Visual: {s.get('visual_prompt','')}",f"Motion: {s.get('motion_prompt','')}",f"References: {s.get('reference_guidance','Reuse same doctor image and previous saved frame when supported')}",f"Voice: {s.get('narration','')}",f"Caption: {s.get('caption','')}",""])
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text("\n".join(lines),encoding="utf-8")
def render(data,base,out):
    if not shutil.which("ffmpeg"):raise RuntimeError("FFmpeg is required")
    errors,_=validate(data,base)
    if errors:raise ValueError("; ".join(errors))
    with TemporaryDirectory() as td:
        temp=Path(td);parts=[]
        for i,s in enumerate(data["scenes"],1):
            seconds=float(s["duration"]);src=path(base,s["media"]);voice=path(base,s.get("voice"));cap=s.get("caption","")
            image=src.suffix.lower() in (".jpg",".jpeg",".png",".webp")
            cmd=["ffmpeg","-y"]
            if image:cmd+=["-loop","1","-framerate",str(FPS)]
            cmd+=["-i",str(src)]
            if voice:cmd+=["-i",str(voice)]
            if cap:
                pic=temp/f"cap{i:02}.png";caption_image(cap,pic)
                cmd+=["-loop","1","-i",str(pic)]
            v=f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p[v]"
            if cap:
                index=2 if voice else 1
                v+=f";[v][{index}:v]overlay=(W-w)/2:H-h-210:shortest=0[vo]"
            cmd+=["-filter_complex",v,"-map","[vo]" if cap else "[v]"]
            if voice:
                cmd+=["-map","1:a:0","-af","apad"]
            else:
                # Add silent audio via a separate lavfi input.
                cmd+=["-f","lavfi","-i","anullsrc=channel_layout=stereo:sample_rate=44100"]
                cmd+=["-map",f"{2 if cap else 1}:a:0"]
            part=temp/f"part{i:02}.mp4"
            cmd+=["-t",str(seconds),"-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-r",str(FPS),"-c:a","aac","-b:a","160k","-ar","44100",str(part)]
            call(cmd);parts.append(part)
        manifest=temp/"list.txt"
        manifest.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts),encoding="utf-8")
        out=Path(out).resolve();out.parent.mkdir(parents=True,exist_ok=True)
        call(["ffmpeg","-y","-f","concat","-safe","0","-i",str(manifest),"-c","copy",str(out)])
        return out
def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="command",required=True)
    a=sub.add_parser("init");a.add_argument("directory")
    a=sub.add_parser("validate");a.add_argument("project");a.add_argument("--strict",action="store_true")
    a=sub.add_parser("prompts");a.add_argument("project");a.add_argument("--out",required=True)
    a=sub.add_parser("render");a.add_argument("project");a.add_argument("--out",required=True)
    q=ap.parse_args()
    if q.command=="init":
        dst=Path(q.directory);dst.mkdir(parents=True,exist_ok=True)
        target=dst/"project.json"
        if target.exists():raise FileExistsError(target)
        shutil.copyfile(ROOT/"templates"/"project.blank.json",target)
        (dst/"media").mkdir(exist_ok=True);print(target);return
    data,base=load(q.project)
    if q.command=="validate":
        errors,warnings=validate(data,base,q.strict)
        for x in warnings:print("WARNING:",x)
        for x in errors:print("ERROR:",x)
        if errors:raise SystemExit(1)
        print("Validation OK")
    elif q.command=="prompts":make_prompts(data,q.out);print(q.out)
    elif q.command=="render":print(render(data,base,q.out))
if __name__=="__main__":main()
