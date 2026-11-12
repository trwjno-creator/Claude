# GRAPH_REPORT — repo dos vídeos (mentalista/, supernatural/, dexter/)

**256 nós · 872 arestas** (847 pares únicos) · 6 comunidades
Confiança: 867 EXTRACTED · 5 INFERRED · 0 AMBIGUOUS

## Resumo
Três projetos com o mesmo pipeline: roteiro (`script.py`) → narração TTS → `timeline.json` → cenas 3D no Blender (`lib.py` personagens/primitivas, `props.py` cenários, `shots.py` câmeras/animação) → quadros PNG → compositor (`compose.py` + `overlays.py`) → música/SFX (`music.py`) → `make_final.sh` → MP4. Funções de mesmo nome entre projetos foram fundidas num nó (ex.: `lib.Char`), com todas as fontes listadas. Dexter trocou narração frase a frase por contínua e adicionou redução de ruído.

## God nodes — grau
- `dexter/blender/shots.py` — grau 79
- `mentalista/blender/shots.py` — grau 69
- `dexter/blender/props.py` — grau 68
- `supernatural/blender/shots.py` — grau 65
- `dexter/blender/lib.py` — grau 57
- `supernatural/blender/props.py` — grau 54
- `supernatural/blender/lib.py` — grau 46
- `mentalista/blender/props.py` — grau 42
- `mentalista/blender/lib.py` — grau 41
- `dexter/post/compose.py` — grau 36

## God nodes — betweenness (por onde tudo passa)
- `dexter` — 0.246
- `dexter/blender/shots.py` — 0.195
- `supernatural` — 0.169
- `dexter/blender/props.py` — 0.132
- `supernatural/blender/shots.py` — 0.117
- `mentalista` — 0.107
- `dexter/blender/lib.py` — 0.104
- `dexter/post/compose.py` — 0.094
- `mentalista/blender/shots.py` — 0.094
- `dexter/audio/music.py` — 0.070

## Comunidades
- **0. Cenas 3D Mentalista/Supernatural + primitivas** (71 nós): `mentalista/blender/shots.py`, `dexter/blender/props.py`, `supernatural/blender/shots.py`, `supernatural/blender/props.py`, `mentalista/blender/props.py`, `lib.empty`, `lib.cyl`, `lib.mat`
- **1. Narração, timeline e capas** (50 nós): `supernatural`, `dexter`, `dexter/audio/gen_tts_cont.py`, `mentalista`, `timeline.json`, `ffmpeg`, `narration.wav`, `supernatural/capa/gerar_capa.py`
- **2. Núcleo Blender (lib, render, animação)** (40 nós): `dexter/blender/lib.py`, `supernatural/blender/lib.py`, `mentalista/blender/lib.py`, `Blender (bpy)`, `mentalista/blender/render_shot.py`, `supernatural/blender/render_shot.py`, `dexter/blender/render_shot.py`, `lib.cone`
- **3. Música, SFX e montagem final** (32 nós): `dexter/audio/music.py`, `mentalista/audio/music.py`, `supernatural/audio/music.py`, `supernatural/make_final.sh`, `dexter/make_final.sh`, `mentalista/make_final.sh`, `sfx_events.json`, `final_mix.wav`
- **4. Cenas e props do Dexter** (32 nós): `dexter/blender/shots.py`, `lib.kid`, `lib.harry`, `lib.dexter_kill`, `props.pine`, `lib.rita`, `props.blood_pool`, `lib.trinity`
- **5. Compositor (legendas, overlays, transições)** (31 nós): `dexter/post/compose.py`, `mentalista/post/compose.py`, `supernatural/post/compose.py`, `frames/<shot>/*.png`, `Pillow`, `compose.ease_pop`, `compose.bar_img`, `compose.disp_word`

## Órfãos (grau ≤ 1): 24
`Dexter_2m30_9x16.mp4`, `Narração contínua (1 passada TTS)`, `O_Mentalista_2m30_9x16.mp4`, `Supernatural_2m30_9x16.mp4`, `dexter/capa/template.html`, `gen_tts_cont.ntok`, `gen_tts_cont.remap`, `narr_raw.mp3`, `narr_raw.wav`, `shots.barn_set`, `shots.bathroom`, `shots.bridge_set`, `shots.cbi_office`, `shots.forest_set`, `shots.ghost`, `shots.ghostify`, `shots.little_dean`, `shots.miami_set`, `shots.park_set`, `shots.road`, `shots.smile`, `shots.station`, `shots.tv_set`, `supernatural/capa/template.html`

## Surpresas (INFERRED ligando comunidades)
Nenhuma: as 5 arestas INFERRED (cópia do pipeline entre projetos, `gen_tts_cont` substitui `gen_tts`, deriva de sincronia) ficam dentro da mesma comunidade.

## 5 perguntas que o grafo responde
1. Quais funções de `lib.py`/`props.py` cada `shots.py` usa, e o que muda se eu alterar `lib.Char`?
2. Que arquivos leem/escrevem `timeline.json` e `narration.wav` (cadeia da sincronia)?
3. O que o Dexter tem que os outros não têm (narração contínua, denoise, props novos)?
4. Qual é o caminho de `script.py` até o MP4 final em cada projeto?
5. Quais ferramentas externas (Blender, edge-tts, OpenCV, ffmpeg, Playwright) cada etapa usa?

## Limites
Extração por leitura de código (AST de Python + regex em .sh/.json), sem tree-sitter. Arestas de leitura/escrita detectadas por nome de arquivo na linha. Funções `sNN` de cena agregadas no módulo (`shots` = nº de cenas).