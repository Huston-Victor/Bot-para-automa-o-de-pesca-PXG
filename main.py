import time
import cv2
import numpy as np
import pyautogui as py
import autoit
import keyboard


# ============================================================
# CONFIGURAÇÕES
# ============================================================

JANELA = "PokeXGames"

BOLHAS = "imagens/bolhas.png"
PEIXE = "imagens/peixe.png"
REGIAO = "imagens/regiao.png"

ELIXIR_COOLDOWN = "imagens/elixir_cooldown.png"

SHINY = "imagens/shiny.png"


CONFIANCA_BOLHAS = 0.85
CONFIANCA_PEIXE = 0.70

CONFIANCA_ELIXIR_COOLDOWN = 0.75

CONFIANCA_SHINY = 0.80


# ============================================================
# COORDENADA DA PESCA
# ============================================================

COORDENADA_PESCA = (416, 532)


# ============================================================
# COORDENADA DA BALL
# ============================================================

COORDENADA_BALL = (825, 998)


# ============================================================
# REGIÃO DO ELIXIR
# ============================================================

REGIAO_ELIXIR = (
    800,
    950,
    120,
    120
)


# ============================================================
# REGIÃO DE BUSCA DO SHINY
# ============================================================

REGIAO_BUSCA_SHINY = (
    0,
    20,
    1475,
    850
)


# ============================================================
# REGIÃO DO MINI-GAME
# ============================================================

REGIAO_MINIGAME = (
    900,
    430,
    100,
    420
)


# ============================================================
# REGIÃO DA BARRA
# ============================================================

BARRA_X = (
    948,
    975
)

BARRA_Y = (
    435,
    842
)


# ============================================================
# TEMPOS
# ============================================================

TEMPO_DETECCAO_MINIGAME = 0.10

TEMPO_DESAPARECIMENTO_MINIGAME = 2.0

TEMPO_MAXIMO_MINIGAME = 30

TEMPO_ULTIMA_BARRA = 0.20


# ============================================================
# ESTADO DO SPACE
# ============================================================

SPACE_PRESSIONADO = False


# ============================================================
# CONFIGURAÇÃO
# ============================================================

py.useImageNotFoundException(False)


# ============================================================
# CARREGAR IMAGENS
# ============================================================

imagem_bolhas = cv2.imread(
    BOLHAS
)

imagem_peixe = cv2.imread(
    PEIXE,
    cv2.IMREAD_GRAYSCALE
)

imagem_regiao = cv2.imread(
    REGIAO,
    cv2.IMREAD_GRAYSCALE
)

imagem_elixir_cooldown = cv2.imread(
    ELIXIR_COOLDOWN,
    cv2.IMREAD_GRAYSCALE
)

imagem_shiny = cv2.imread(
    SHINY,
    cv2.IMREAD_GRAYSCALE
)


# ============================================================
# VERIFICAR IMAGENS
# ============================================================

if imagem_bolhas is None:
    raise SystemExit(
        "Imagem bolhas.png não encontrada."
    )

if imagem_peixe is None:
    raise SystemExit(
        "Imagem peixe.png não encontrada."
    )

if imagem_regiao is None:
    raise SystemExit(
        "Imagem regiao.png não encontrada."
    )

if imagem_elixir_cooldown is None:
    raise SystemExit(
        "Imagem elixir_cooldown.png não encontrada."
    )

if imagem_shiny is None:
    raise SystemExit(
        "Imagem shiny.png não encontrada."
    )


# ============================================================
# DIMENSÕES DO SHINY
# ============================================================

ALTURA_SHINY, LARGURA_SHINY = (
    imagem_shiny.shape
)


# ============================================================
# ATIVAR JANELA
# ============================================================

autoit.win_activate(
    JANELA
)


# ============================================================
# CAPTURA DA TELA
# ============================================================

def capturar_tela():

    return cv2.cvtColor(
        np.array(
            py.screenshot()
        ),
        cv2.COLOR_RGB2BGR
    )


# ============================================================
# F1
# ============================================================

def verificar_f1():

    global SPACE_PRESSIONADO

    if keyboard.is_pressed("f1"):

        if SPACE_PRESSIONADO:

            keyboard.release(
                "space"
            )

            SPACE_PRESSIONADO = False

        raise SystemExit


# ============================================================
# LIBERAR SPACE
# ============================================================

def liberar_space():

    global SPACE_PRESSIONADO

    if SPACE_PRESSIONADO:

        keyboard.release(
            "space"
        )

        SPACE_PRESSIONADO = False


# ============================================================
# DETECTAR COOLDOWN DO ELIXIR
# ============================================================

def detectar_cooldown_elixir():

    imagem = capturar_tela()

    x, y, largura, altura = (
        REGIAO_ELIXIR
    )

    regiao = cv2.cvtColor(
        imagem[
            y:y + altura,
            x:x + largura
        ],
        cv2.COLOR_BGR2GRAY
    )

    resultado = cv2.matchTemplate(
        regiao,
        imagem_elixir_cooldown,
        cv2.TM_CCOEFF_NORMED
    )

    confianca = cv2.minMaxLoc(
        resultado
    )[1]

    return (
        confianca
        >= CONFIANCA_ELIXIR_COOLDOWN
    )


# ============================================================
# USAR ELIXIR
# ============================================================

def usar_elixir():

    if detectar_cooldown_elixir():

        return

    autoit.send(
        "+5"
    )

    time.sleep(
        0.2
    )


# ============================================================
# DETECTAR BOLHAS
# ============================================================

def detectar_bolhas():

    imagem = capturar_tela()

    resultado = cv2.matchTemplate(
        imagem,
        imagem_bolhas,
        cv2.TM_CCOEFF_NORMED
    )

    confianca = cv2.minMaxLoc(
        resultado
    )[1]

    return (
        confianca
        >= CONFIANCA_BOLHAS
    )


# ============================================================
# ESPERAR BOLHAS
# ============================================================

def esperar_bolhas():

    time.sleep(
        0.3
    )

    while True:

        verificar_f1()

        if detectar_bolhas():

            return True

        time.sleep(
            0.03
        )


# ============================================================
# DETECTAR SHINY
# ============================================================

def detectar_shiny():

    imagem = capturar_tela()

    x, y, largura, altura = (
        REGIAO_BUSCA_SHINY
    )

    regiao = imagem[
        y:y + altura,
        x:x + largura
    ]

    regiao_cinza = cv2.cvtColor(
        regiao,
        cv2.COLOR_BGR2GRAY
    )

    resultado = cv2.matchTemplate(
        regiao_cinza,
        imagem_shiny,
        cv2.TM_CCOEFF_NORMED
    )

    _, confianca, _, posicao = (
        cv2.minMaxLoc(
            resultado
        )
    )

    if confianca < CONFIANCA_SHINY:

        return None

    esquerda = (
        posicao[0]
        + x
    )

    topo = (
        posicao[1]
        + y
    )

    centro_x = (
        esquerda
        + LARGURA_SHINY // 2
    )

    centro_y = (
        topo
        + ALTURA_SHINY // 2
    )

    return (
        centro_x,
        centro_y
    )


# ============================================================
# PEGAR SHINY
# ============================================================

def pegar_shiny():

    coordenada = detectar_shiny()

    if coordenada is None:

        return False

    x, y = coordenada


    # ========================================================
    # 1. BOTÃO DIREITO DIRETAMENTE NO SHINY
    # ========================================================

    py.click(
        x=x,
        y=y,
        button="right"
    )


    time.sleep(
        0.15
    )


    # ========================================================
    # 2. CLIQUE DIRETO NA BALL
    # ========================================================

    py.click(
        x=COORDENADA_BALL[0],
        y=COORDENADA_BALL[1],
        button="left"
    )


    time.sleep(
        0.15
    )


    # ========================================================
    # 3. CLIQUE DIRETO NOVAMENTE NO SHINY
    # ========================================================

    py.click(
        x=x,
        y=y,
        button="left"
    )


    time.sleep(
        0.20
    )


    return True


# ============================================================
# DETECTAR PEIXE
# ============================================================

def detectar_peixe(imagem):

    x, y, largura, altura = (
        REGIAO_MINIGAME
    )

    regiao = cv2.cvtColor(
        imagem[
            y:y + altura,
            x:x + largura
        ],
        cv2.COLOR_BGR2GRAY
    )

    resultado = cv2.matchTemplate(
        regiao,
        imagem_peixe,
        cv2.TM_CCOEFF_NORMED
    )

    _, confianca, _, posicao = (
        cv2.minMaxLoc(
            resultado
        )
    )

    if confianca < CONFIANCA_PEIXE:

        return None

    return (
        posicao[1]
        + imagem_peixe.shape[0] // 2
        + y
    )


# ============================================================
# DETECTAR BARRA
# ============================================================

def detectar_barra(imagem):

    x1, x2 = BARRA_X

    y1, y2 = BARRA_Y

    regiao = cv2.cvtColor(
        imagem[
            y1:y2,
            x1:x2
        ],
        cv2.COLOR_BGR2GRAY
    )

    brilho = np.mean(
        regiao,
        axis=1
    )

    mascara = brilho > 65

    segmentos = []

    inicio = None

    for i, ativo in enumerate(mascara):

        if ativo and inicio is None:

            inicio = i

        elif (
            not ativo
            and inicio is not None
        ):

            tamanho = (
                i
                - inicio
            )

            if tamanho >= 5:

                segmentos.append(
                    (
                        inicio,
                        i
                    )
                )

            inicio = None

    if inicio is not None:

        tamanho = (
            len(mascara)
            - inicio
        )

        if tamanho >= 5:

            segmentos.append(
                (
                    inicio,
                    len(mascara)
                )
            )

    if not segmentos:

        return None

    topo, fundo = max(
        segmentos,
        key=lambda s:
        s[1] - s[0]
    )

    return (
        topo + y1,
        fundo + y1
    )


# ============================================================
# DETECTAR MINI-GAME
# ============================================================

def detectar_minigame(imagem):

    peixe_y = detectar_peixe(
        imagem
    )

    if peixe_y is not None:

        return True

    barra = detectar_barra(
        imagem
    )

    if barra is not None:

        return True

    return False


# ============================================================
# ESPERAR MINI-GAME
# ============================================================

def esperar_minigame():

    inicio = time.time()

    while True:

        verificar_f1()

        imagem = capturar_tela()

        if detectar_minigame(
            imagem
        ):

            return True

        if (
            time.time()
            - inicio
            >= TEMPO_DETECCAO_MINIGAME
        ):

            return False

        time.sleep(
            0.005
        )


# ============================================================
# CONTROLAR MINI-GAME
# ============================================================

def controlar_minigame(
    peixe_y,
    barra
):

    global SPACE_PRESSIONADO

    topo, fundo = barra

    margem = 3

    if peixe_y < topo + margem:

        if not SPACE_PRESSIONADO:

            keyboard.press(
                "space"
            )

            SPACE_PRESSIONADO = True

    elif peixe_y > fundo - margem:

        if SPACE_PRESSIONADO:

            keyboard.release(
                "space"
            )

            SPACE_PRESSIONADO = False


# ============================================================
# RESOLVER MINI-GAME
# ============================================================

def resolver_minigame():

    inicio = time.time()

    detectado = False

    ultima_deteccao = time.time()

    ultima_barra = None

    momento_ultima_barra = 0


    while True:

        verificar_f1()


        # ====================================================
        # PROTEÇÃO
        # ====================================================

        if (
            time.time()
            - inicio
            >= TEMPO_MAXIMO_MINIGAME
        ):

            liberar_space()

            return


        imagem = capturar_tela()


        # ====================================================
        # DETECTAR PEIXE
        # ====================================================

        peixe_y = detectar_peixe(
            imagem
        )


        # ====================================================
        # DETECTAR BARRA
        # ====================================================

        barra = detectar_barra(
            imagem
        )


        # ====================================================
        # SALVAR ÚLTIMA BARRA
        # ====================================================

        if barra is not None:

            ultima_barra = barra

            momento_ultima_barra = (
                time.time()
            )


        # ====================================================
        # RECUPERAR ÚLTIMA BARRA
        # ====================================================

        if (
            barra is None
            and
            ultima_barra is not None
        ):

            tempo_desde_barra = (
                time.time()
                - momento_ultima_barra
            )


            if (
                tempo_desde_barra
                <= TEMPO_ULTIMA_BARRA
            ):

                barra = ultima_barra


        # ====================================================
        # PEIXE + BARRA
        # ====================================================

        if (
            peixe_y is not None
            and
            barra is not None
        ):

            detectado = True

            ultima_deteccao = (
                time.time()
            )


            controlar_minigame(
                peixe_y,
                barra
            )


        # ====================================================
        # PERDEU A DETECÇÃO
        # ====================================================

        else:

            if detectado:

                tempo_sem_detectar = (
                    time.time()
                    - ultima_deteccao
                )


                if (
                    tempo_sem_detectar
                    >= TEMPO_DESAPARECIMENTO_MINIGAME
                ):

                    liberar_space()

                    return


        time.sleep(
            0.005
        )


# ============================================================
# LOOT
# ============================================================

def fazer_loot():

    autoit.send(
        "e"
    )


# ============================================================
# LOOP PRINCIPAL
# ============================================================

while True:

    verificar_f1()


    # ========================================================
    # 1. ELIXIR
    # ========================================================

    usar_elixir()


    # ========================================================
    # 2. POSICIONA MOUSE PARA PESCA
    # ========================================================

    py.moveTo(
        *COORDENADA_PESCA
    )


    # ========================================================
    # 3. LANÇA A VARA
    # ========================================================

    autoit.send(
        "q"
    )


    # ========================================================
    # 4. ESPERA BOLHAS
    # ========================================================

    esperar_bolhas()


    # ========================================================
    # 5. PUXA A VARA
    # ========================================================

    autoit.send(
        "q"
    )


    # ========================================================
    # 6. LOOT
    # ========================================================

    fazer_loot()


    # ========================================================
    # 7. PROCURA SHINY
    # ========================================================

    pegar_shiny()


    # ========================================================
    # 8. VERIFICA MINI-GAME
    # ========================================================

    if esperar_minigame():

        resolver_minigame()


    # ========================================================
    # 9. GARANTE SPACE SOLTO
    # ========================================================

    liberar_space()


    # ========================================================
    # 10. PRÓXIMA PESCADA
    # ========================================================

    time.sleep(
        0.05
    )