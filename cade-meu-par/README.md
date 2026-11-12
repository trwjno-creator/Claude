# Cadê Meu Par? 🧦

Animação 2D curta (9:16, 40 s, loop perfeito) para TikTok, Reels e Shorts.
Uma meia é esquecida na máquina de lavar, cai no **Reino das Meias Perdidas**, foge de forma épica,
reencontra o seu par... e descobre que ele já está com outra. No fim, é jogada de volta na máquina
e o vídeo emenda no primeiro quadro.

**Vídeo final:** `CadeMeuPar_40s_9x16.mp4` (1080×1920, 30 fps, H.264 + AAC, -14 LUFS)

## Narração (estilo trailer de cinema)
Legendas animadas palavra por palavra (a palavra falada acende em amarelo), para quem assiste sem som.

| Tempo | Fala |
|---|---|
| 0,0 s | Toda semana, uma meia desaparece. |
| 2,2 s | E ninguém nunca perguntou pra onde elas vão. |
| 6,9 s | Bem-vinda ao Reino das Meias Perdidas. |
| 9,5 s | Tampas, elásticos... e o seu fone sem fio. |
| 14,1 s | Mas ela tinha um plano. |
| 16,1 s | Escalar o impossível. |
| 18,1 s | Enfrentar o terror. |
| 20,1 s | E voar... |
| 22,1 s | ...de volta pro grande amor. |
| 25,3 s | Até que... ela encontrou seu par. |
| 28,1 s | *(o par, sem graça)* Faz três semanas... |
| 30,4 s | Tem história que não tem final feliz. |
| 32,4 s | E sabe o pior? |
| 35,9 s | Ela não foi a primeira. |
| 38,0 s | E não vai ser a última. → *(loop)* Toda semana, uma meia desaparece. |

A última fala emenda na primeira, então a narração também fecha em loop.

## Cenas
| Tempo | Cena |
|---|---|
| 0–2 s | **Gancho:** a meia esmagada no vidro da máquina — "POV: você é a meia que sumiu" |
| 2–6 s | A máquina para, a mão tira as roupas, a meia fica presa na borracha e cai na fresta (BLOP...) |
| 6–14 s | O Reino das Meias Perdidas: casas com telhado de tampa de pote, ponte de elásticos, poste de caneta, cartaz "PROCURADO desde 2023" (fone sem fio) e a placa "BEM-VINDO. NINGUÉM VOLTA." |
| 14–24 s | A fuga: plano no papel de bala → escalar a mangueira → monstro de fiapos → estilingue de elástico → voo em câmera lenta |
| 24–32 s | O reencontro em câmera lenta com corações... arranhão de disco: o par está enrolado com uma meia de bolinhas. "faz 3 semanas…" → raio e choro |
| 32–40 s | A mão pega a meia, dá de ombros 🤷 e joga de volta na máquina → zoom na janela = primeiro quadro (loop) |

## Como gerar de novo
```bash
./make_video.sh            # renderiza os quadros (Playwright/Chromium), sintetiza o áudio e codifica
SKIP_RENDER=1 ./make_video.sh   # só refaz o áudio e o encode, reaproveitando os quadros
NEW_VOICE=1 ./make_video.sh     # também regera a narração (edge-tts, precisa de internet)
```
- `anim.js`: toda a animação em canvas 2D; `draw(t)` é determinístico, então cada quadro é reproduzível.
- `index.html`: abra no navegador para ver a prévia em tempo real (sem som).
- `render.js`: exporta os quadros JPEG 1080×1920.
- `audio/gen_narration.py`: narração (edge-tts pt-BR) encaixada nas janelas de cada cena; gera `audio/narration.wav` e `subs.js` (tempo de cada palavra).
- `audio/audio.py`: trilha e efeitos sintetizados (numpy/scipy), tratamento da voz e ducking da trilha sob a narração.

## Para postar
**Legenda:** Agora você sabe pra onde elas vão 🧦💔 Já perdeu quantas?

**Hashtags:** #animação #meiaperdida #relatable #pov #animation2d #humor #fyp
