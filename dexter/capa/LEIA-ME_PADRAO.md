# Padrão de Capa · Grande Resumo

Capa TikTok: **1080 × 1920 px (9:16)**, PNG/JPG.
**Tudo fica no quadrado central y 430 → 1500 (1080×1080).** Assim aparece inteiro no feed, no grid 3:4 e no grid 1:1. Fora dele: só fundo e moldura.

## Estrutura fixa (de cima pra baixo)

| # | Bloco | Posição (y) | O que muda por vídeo |
|---|-------|-------------|----------------------|
| 1 | Logo + "GRANDE RESUMO" + Nº | 432 | só o número (001, 002…) |
| 2 | Título em 2 cores (branco + dourado) | 505 | nome da série, dividido em 2 partes |
| 3 | 3 chips: gênero, gênero, anos | ~640 | gêneros e anos da série |
| 4 | Card herói (borda dourada + glow) | 705–1105 | frame principal do vídeo |
| 5 | 3 polaroids numeradas com rótulo | 1060–1300 | 3 cenas-chave + rótulos curtos |
| 6 | Gancho (pílula com "?") | 1318 | pergunta que gera curiosidade |
| 7 | 3 stats em linha | 1428 | temporadas, episódios, duração |

Elementos fixos de fundo: frame herói desfocado, raios de luz, listras diagonais, pontilhado nos cantos, grão, moldura com cantos dourados.

## Cores

- `cor` (destaque): muda por série, e é ela que dá a identidade a cada vídeo.
  - Suspense/terror: `#E5172F` (vermelho)
  - Drama: `#7B3FE4` (roxo)
  - Comédia: `#FF7A00` (laranja)
  - Ficção científica: `#1E88E5` (azul)
  - Fantasia: `#12A150` (verde)
- `cor2` (dourado da marca): **sempre `#FFC93C`**
- `escuro` (base): `#12030A` ou um tom bem escuro da cor de destaque

## Fonte

Inter Display Black (900) nos títulos e Inter SemiBold/Bold nos textos pequenos. No Canva/CapCut, use **Inter** ou **Montserrat Black**.

## Regras de conteúdo

- **Herói**: frame com personagem principal + elemento icônico, **sem spoiler**.
- **Cenas**: 3 momentos do começo/meio. Rótulo de 1–2 palavras.
- **Gancho**: pergunta curta (até ~22 caracteres) que o vídeo responde.
- Nunca usar o frame da revelação final na capa.

## Gerar automaticamente

```
python3 gerar_capa.py o_mentalista.json
```

Para outro vídeo, copie o JSON e troque: `video`, `numero`, `cor`, `titulo`, `chips`, `heroi.t`, `cenas[].t` + `rotulo`, `gancho`, `stats`.
`t` = segundo do vídeo. `crop` = recorte [x0, y0, x1, y1] em pixels do vídeo 1080×1920 (opcional).

Requisitos: Python 3, ffmpeg, Pillow, Playwright (`pip install pillow playwright && playwright install chromium`).
