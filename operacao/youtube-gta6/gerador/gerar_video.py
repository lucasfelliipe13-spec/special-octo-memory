#!/usr/bin/env python3
"""Gera um YouTube Short (1080x1920) a partir de um roteiro JSON, 100% grátis e offline.

- Narração: voz pt-BR Piper (sherpa-onnx), roda no próprio computador, sem chave de API.
- Fundo: clipes seus em assets/gameplay/*.mp4 (gameplay gravado por você) ou, se não houver,
  um fundo animado em degradê neon (nada de material de terceiros = sem risco de direitos).
- Legenda grande, palavra-chave em destaque, gancho no topo nos primeiros segundos.

Uso:
  python3 gerar_video.py roteiro.json saida.mp4

Formato do roteiro.json:
{
  "titulo": "...",
  "gancho_tela": "TEXTO CURTO NO TOPO",
  "cenas": [ {"fala": "frase narrada", "tela": "texto opcional na tela"}, ... ]
}
"""
import json
import os
import random
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VOZ_DIR = Path(os.environ.get("GTA6_VOZ_DIR", Path.home() / ".cache/gta6-voz/vits-piper-pt_BR-faber-medium"))
VOZ_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-pt_BR-faber-medium.tar.bz2"
GAMEPLAY_DIR = Path(os.environ.get("GTA6_GAMEPLAY_DIR", AQUI.parent / "assets/gameplay"))
W, H = 1080, 1920


def garantir_voz():
    if (VOZ_DIR / "pt_BR-faber-medium.onnx").exists():
        return
    VOZ_DIR.parent.mkdir(parents=True, exist_ok=True)
    tar = VOZ_DIR.parent / "voz.tar.bz2"
    subprocess.run(["curl", "-sL", "-m", "300", "-o", str(tar), VOZ_URL], check=True)
    subprocess.run(["tar", "xjf", str(tar), "-C", str(VOZ_DIR.parent)], check=True)
    tar.unlink()


def sintetizar(frases, pasta):
    import sherpa_onnx

    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=str(VOZ_DIR / "pt_BR-faber-medium.onnx"),
                tokens=str(VOZ_DIR / "tokens.txt"),
                data_dir=str(VOZ_DIR / "espeak-ng-data"),
            ),
            num_threads=2,
        )
    )
    tts = sherpa_onnx.OfflineTts(cfg)
    arquivos, duracoes = [], []
    for i, frase in enumerate(frases):
        audio = tts.generate(frase, sid=0, speed=1.12)
        caminho = pasta / f"fala_{i:02d}.wav"
        import numpy as np

        pcm = (np.clip(np.array(audio.samples), -1, 1) * 32767).astype("<i2")
        pcm = np.concatenate([pcm, np.zeros(int(0.15 * audio.sample_rate), dtype="<i2")])  # pausa curta
        with wave.open(str(caminho), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(audio.sample_rate)
            f.writeframes(pcm.tobytes())
        arquivos.append(caminho)
        duracoes.append(len(pcm) / audio.sample_rate)
    return arquivos, duracoes


def ts(seg):
    h, r = divmod(seg, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def esc(t):
    return t.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def montar_ass(roteiro, duracoes, caminho):
    linhas = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Fala,DejaVu Sans,74,&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,6,3,5,80,80,0,1",
        "Style: Gancho,DejaVu Sans,82,&H0000F0FF,&H00FFFFFF,&H00000000,&HA0000000,1,0,0,0,100,100,0,0,3,4,0,8,60,60,180,1",
        "Style: Tela,DejaVu Sans,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0B000B0,1,0,0,0,100,100,0,0,3,4,0,2,70,70,260,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    t = 0.0
    gancho = roteiro.get("gancho_tela")
    if gancho:
        linhas.append(f"Dialogue: 1,{ts(0)},{ts(min(3.0, sum(duracoes)))},Gancho,,0,0,0,,{esc(gancho)}")
    for cena, d in zip(roteiro["cenas"], duracoes):
        palavras = cena["fala"].split()
        # blocos de até 3 palavras, como legenda de Reels/Shorts
        blocos = [" ".join(palavras[i:i + 3]) for i in range(0, len(palavras), 3)] or [""]
        passo = d / len(blocos)
        for j, b in enumerate(blocos):
            ini, fim = t + j * passo, t + (j + 1) * passo
            linhas.append(f"Dialogue: 0,{ts(ini)},{ts(fim)},Fala,,0,0,0,,{{\\fscx115\\fscy115\\t(0,120,\\fscx100\\fscy100)}}{esc(b).upper()}")
        if cena.get("tela"):
            linhas.append(f"Dialogue: 0,{ts(t)},{ts(t + d)},Tela,,0,0,0,,{esc(cena['tela'])}")
        t += d
    caminho.write_text("\n".join(linhas), encoding="utf-8")


def fundo(duracao, pasta):
    clipes = sorted(GAMEPLAY_DIR.glob("*.mp4")) if GAMEPLAY_DIR.exists() else []
    saida = pasta / "fundo.mp4"
    if clipes:
        clipe = random.choice(clipes)
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", str(clipe), "-t", f"{duracao:.2f}",
            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},eq=brightness=-0.08",
            "-an", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", str(saida)], check=True)
    else:
        # degradê neon animado (estética Vice City), gerado do zero
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
            "-i", f"gradients=s={W}x{H}:c0=0xff2fa3:c1=0x2b0a5c:c2=0x00e5ff:c3=0x120024:nb_colors=4:speed=0.012:d={duracao:.2f}:r=30",
            "-vf", "noise=alls=6:allf=t,vignette", "-c:v", "libx264", "-preset", "veryfast", str(saida)], check=True)
    return saida


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    roteiro = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    saida = Path(sys.argv[2]).resolve()
    garantir_voz()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        falas, duracoes = sintetizar([c["fala"] for c in roteiro["cenas"]], tmp)
        lista = tmp / "lista.txt"
        lista.write_text("".join(f"file '{f}'\n" for f in falas))
        audio = tmp / "voz.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lista),
                        str(audio)], check=True)
        total = sum(duracoes) + 0.4
        bg = fundo(total, tmp)
        ass = tmp / "legenda.ass"
        montar_ass(roteiro, duracoes, ass)
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(bg), "-i", str(audio),
            "-vf", f"ass={ass}", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
            "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(saida)], check=True)
    print(f"ok {saida} ({total:.1f}s)")


if __name__ == "__main__":
    main()
