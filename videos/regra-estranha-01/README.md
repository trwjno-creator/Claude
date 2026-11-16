# Regra Estranha #1: "Nesse mundo, sua nuca esquenta quando alguém pensa em você"

- `regra_estranha_01.mp4`: vídeo final, 60s, 1080x1920, com voz, legendas, música e efeitos.
- `src/`: código da animação, que pode ser renderizado de novo.
  - `lines.json`: falas do roteiro, com as tags de emoção da voz.
  - `tts.py`: gera as vozes no ElevenLabs (a chave é injetada pelo proxy, não fica no código).
  - `build_timeline.py`: calcula o tempo das falas, das palavras e das bocas a partir do áudio.
  - `anim.html`: animação em canvas (personagens, cenários, sincronia labial, legendas).
  - `music.py`: trilha e efeitos sonoros gerados por código.
  - `make.sh`: renderiza os quadros com Playwright e monta o mp4 com ffmpeg.

Para renderizar de novo: sirva `src/` em `http://127.0.0.1:8765` (`python3 -m http.server 8765`), rode `python3 build_timeline.py`, monte o `voice.wav` e execute `./make.sh`.
