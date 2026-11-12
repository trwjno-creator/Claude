# -*- coding: utf-8 -*-
# Roteiro: Game of Thrones (2011-2019) - gancho forte (0-5s) + loop aberto + POV do Ned + CTA no fim.
# Nomes escritos foneticamente para o TTS (pt-BR); a legenda mostra a grafia real (FIX / MERGE em post/compose.py).

SHOW = {}

HIGHLIGHT = {"protagonista", "1milhão", "cabeça", "literalmente", "final", "milhão", "néd", "stárk", "uínterfél", "inverno",
             "kétlin", "róbi", "sânsa", "ária", "brân", "ríkon", "djón", "isnôu", "róbert", "baratiôn", "mão",
             "cérsei", "lânister", "djáime", "torre", "dainéris", "targárien", "cál", "drôgo", "segredo", "djófri",
             "mindinho", "dragões", "patrulha", "muralha", "caminhantes", "tírion", "verde", "vermelho", "uólder",
             "frei", "envenenado", "táiuen", "rãmzei", "bôlton", "melisândre", "bastardos", "templo", "tia",
             "noite", "sam", "istânis", "cão", "caça", "feiticeira", "facada", "capital", "trono", "ferro", "rei", "comenta", "rainha", "vida", "banheiro", "ninguém", "missão", "tradicional", "oito", "sério", "merecia", "nada"}

LINES = [
    ("s01", "O protagonista dessa série perde a cabeça na primeira temporada. Literalmente."),
    ("s02", "E o final foi tão odiado que mais de um milhão de fãs pediram pra refazer."),
    ("s03", "Póve: você é o Néd Stárk, senhor de Uínterfél, no norte, onde o inverno está chegando."),
    ("s04", "Com a sua esposa Kétlin, você tem cinco filhos: Róbi, Sânsa, Ária, Brân e Ríkon. E cria o bastardo Djón Isnôu."),
    ("s05", "O seu amigo, o rei Róbert Baratiôn, te chama pra ser a Mão do Rei."),
    ("s06", "Mas a rainha Cérsei Lânister tem um caso com o próprio irmão gêmeo, Djáime."),
    ("s07", "O Brân vê os dois juntos, e o Djáime empurra ele da torre."),
    ("s08", "Do outro lado do mar, a Dainéris Targárien é obrigada a casar com o Cál Drôgo."),
    ("s09", "Na capital, você descobre o segredo: os filhos da rainha não são do rei."),
    ("s10", "O rei morre numa caçada, e o cruel Djófri assume o trono."),
    ("s11", "O Mindinho te trai, e o Djófri manda cortar a sua cabeça."),
    ("s12", "Você morreu, mas a guerra só começou. A Dainéris entra numa fogueira e sai viva, com três dragões."),
    ("s13", "No norte, o Djón entra na Patrulha da Noite, ao lado do amigo Sam, pra proteger a Muralha dos Caminhantes Brancos."),
    ("s14", "O Róbi vira Rei do Norte, e o Tírion, irmão anão da Cérsei, salva a capital do ataque do Istânis com fogo verde."),
    ("s15", "Até que vem o Casamento Vermelho: o Róbi e a Kétlin são mortos na festa do Uólder Frei. Moral da história: se o Uólder Frei te chamar pra um casamento, não vai."),
    ("s16", "Mas o Djófri também morre, envenenado no próprio casamento. E sinceramente? Ninguém chorou."),
    ("s17", "O Tírion é acusado, mata o próprio pai, Táiuen, no banheiro, e foge."),
    ("s18", "A Ária foge com o Cão de Caça e vira assassina, e a Sânsa cai nas mãos do cruel Rãmzei Bôlton."),
    ("s19", "O Djón é traído pela Patrulha, mas a feiticeira Melisândre traz ele de volta à vida. Mas ele continua não sabendo de nada, Djón Isnôu."),
    ("s20", "Na Batalha dos Bastardos, o Djón vence o Rãmzei e vira Rei do Norte."),
    ("s21", "A Cérsei explode um templo inteiro com fogo verde e vira rainha."),
    ("s22", "A Dainéris chega com dragões, um exército e o Tírion como conselheiro."),
    ("s23", "Ela e o Djón se apaixonam. Só tem um problema: ela é tia dele. Família tradicional de Uésteros."),
    ("s24", "Porque o Djón, na verdade, é um Targárien, com mais direito ao trono que ela."),
    ("s25", "O Rei da Noite ataca com um exército de mortos, mas a Ária salta do nada e mata ele com uma facada. Oito temporadas de ameaça, resolvidas em um segundo."),
    ("s26", "Aí a Dainéris perde a cabeça e queima a capital inteira. A Cérsei e o Djáime morrem nos escombros."),
    ("s27", "O Djón mata a mulher que ama, e o dragão derrete o Trono de Ferro. Esse aí entendeu a missão."),
    ("s28", "E quem vira rei? O Brân, o menino que caiu da torre lá no começo. Sim, é sério. Pra você, quem merecia o trono? Comenta aí. E se você chegou até aqui, segue o perfil, que a próxima série já tá vindo."),
]
