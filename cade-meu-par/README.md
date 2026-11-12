# Cadê Meu Par? 🧦

Animação 2D curta (9:16, 40 s, loop perfeito) para TikTok, Reels e Shorts.
Uma meia é esquecida na máquina de lavar, cai no **Reino das Meias Perdidas**, foge de forma épica,
reencontra o seu par... e descobre que ele já está com outra. No fim, é jogada de volta na máquina
e o vídeo emenda no primeiro quadro.

**Vídeo final:** `CadeMeuPar_40s_9x16.mp4` (1080×1920, 30 fps, H.264 + AAC, -14 LUFS)

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
```
- `anim.js`: toda a animação em canvas 2D; `draw(t)` é determinístico, então cada quadro é reproduzível.
- `index.html`: abra no navegador para ver a prévia em tempo real (sem som).
- `render.js`: exporta os quadros JPEG 1080×1920.
- `audio/audio.py`: trilha e efeitos 100% sintetizados (numpy/scipy), sem samples externos.

## Para postar
**Legenda:** Agora você sabe pra onde elas vão 🧦💔 Já perdeu quantas?

**Hashtags:** #animação #meiaperdida #relatable #pov #animation2d #humor #fyp
