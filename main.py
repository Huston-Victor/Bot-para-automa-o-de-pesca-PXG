import time
import os
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
SHINY_ALTERNATIVO = "imagens/shiny(1).png"


# ============================================================
# CONFIANÇAS
# ============================================================

CONFIANCA_BOLHAS = 0.85

CONFIANCA_PEIXE = 0.80

CONFIANCA_ELIXIR_COOLDOWN = 0.75

ERRO_MAXIMO_SHINY = 0.15

PERCENTUAL_AMARELO_SHINY = 0.12


# ============================================================
# COORDENADA DA PESCA
# ============================================================

COORDENADA_PESCA = (
    416,
    532
)


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
# TEMPOS DO MINI-GAME
# ============================================================

TEMPO_DETECCAO_MINIGAME = 0.10

TEMPO_DESAPARECIMENTO_MINIGAME = 2.0

TEMPO_MAXIMO_MINIGAME = 30

TEMPO_ULTIMA_BARRA = 0.20


# ============================================================
# TEMPO ENTRE PUXAR E LANÇAR NOVAMENTE
# ============================================================

TEMPO_REPETIR_PESCA = 2.3


# ============================================================
# TEMPO MÁXIMO SEM DETECTAR BOLHAS
# ============================================================

TEMPO_SEM_BOLHAS = 15.0


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


# ============================================================
# ESCOLHER IMAGEM DO SHINY
# ============================================================

caminho_shiny = SHINY

if os.path.exists(
    SHINY_ALTERNATIVO
):

    caminho_shiny = (
        SHINY_ALTERNATIVO
    )


imagem_shiny_original = cv2.imread(
    caminho_shiny,
    cv2.IMREAD_UNCHANGED
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


if imagem_shiny_original is None:

    raise SystemExit(
        "Imagem shiny não encontrada."
    )


# ============================================================
# PREPARAR SHINY
# ============================================================

if (
    len(imagem_shiny_original.shape) == 3
    and
    imagem_shiny_original.shape[2] == 4
):

    imagem_shiny_bgr = (
        imagem_shiny_original[:, :, :3]
    )

    alpha_shiny = (
        imagem_shiny_original[:, :, 3]
    )

else:

    imagem_shiny_bgr = (
        imagem_shiny_original
    )

    alpha_shiny = (
        np.ones(
            imagem_shiny_bgr.shape[:2],
            dtype=np.uint8
        )
        * 255
    )


# ============================================================
# RECORTAR ÁREA VISÍVEL DO SHINY
# ============================================================

pixels_validos = (
    alpha_shiny > 10
)


ys, xs = np.where(
    pixels_validos
)


if len(xs) == 0:

    raise SystemExit(
        "A imagem do shiny não possui área visível."
    )


x_min = xs.min()

x_max = xs.max() + 1

y_min = ys.min()

y_max = ys.max() + 1


imagem_shiny_bgr = (
    imagem_shiny_bgr[
        y_min:y_max,
        x_min:x_max
    ]
)


alpha_shiny = (
    alpha_shiny[
        y_min:y_max,
        x_min:x_max
    ]
)


# ============================================================
# SHINY EM CINZA
# ============================================================

imagem_shiny_cinza = cv2.cvtColor(
    imagem_shiny_bgr,
    cv2.COLOR_BGR2GRAY
)


# ============================================================
# MÁSCARA DO SHINY
# ============================================================

mascara_shiny = (
    alpha_shiny > 10
).astype(
    np.uint8
)

mascara_shiny = (
    mascara_shiny * 255
).astype(
    np.uint8
)


# ============================================================
# MÁSCARA AMARELA DO TEMPLATE
# ============================================================

shiny_hsv = cv2.cvtColor(
    imagem_shiny_bgr,
    cv2.COLOR_BGR2HSV
)

hue = shiny_hsv[:, :, 0]

saturacao = shiny_hsv[:, :, 1]

brilho = shiny_hsv[:, :, 2]


mascara_amarela_template = (
    (hue >= 15)
    &
    (hue <= 40)
    &
    (saturacao >= 100)
    &
    (brilho >= 100)
    &
    (mascara_shiny > 0)
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
# F11
# ============================================================

def verificar_f11():

    global SPACE_PRESSIONADO

    if keyboard.is_pressed("f11"):

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

        return False

    autoit.send(
        "+5"
    )

    time.sleep(
        0.2
    )

    return True


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

    inicio = time.monotonic()

    while True:

        verificar_f11()

        # ====================================================
        # DETECTOU BOLHAS
        # ====================================================

        if detectar_bolhas():

            return True


        # ====================================================
        # CALCULAR TEMPO SEM BOLHAS
        # ====================================================

        tempo_sem_bolhas = (
            time.monotonic()
            - inicio
        )


        # ====================================================
        # TIMEOUT DE 15 SEGUNDOS
        # ====================================================

        if (
            tempo_sem_bolhas
            >= TEMPO_SEM_BOLHAS
        ):

            # ------------------------------------------------
            # REPOSICIONAR MOUSE
            # ------------------------------------------------

            py.moveTo(
                *COORDENADA_PESCA
            )


            # ------------------------------------------------
            # PEQUENO DELAY
            # ------------------------------------------------

            time.sleep(
                0.1
            )


            # ------------------------------------------------
            # TENTAR LANÇAR NOVAMENTE
            # ------------------------------------------------

            autoit.send(
                "q"
            )


            # ------------------------------------------------
            # REINICIAR CONTADOR
            # ------------------------------------------------

            inicio = time.monotonic()


            # ------------------------------------------------
            # DAR TEMPO PARA O JOGO PROCESSAR
            # ------------------------------------------------

            time.sleep(
                0.2
            )

            continue


        # ====================================================
        # INTERVALO NORMAL
        # ====================================================

        time.sleep(
            0.03
        )


# ============================================================
# VALIDAR COR AMARELA DO SHINY
# ============================================================

def validar_shiny_amarelo(
    regiao,
    mascara_shape
):

    if regiao.size == 0:

        return False

    hsv = cv2.cvtColor(
        regiao,
        cv2.COLOR_BGR2HSV
    )

    h = hsv[:, :, 0]

    s = hsv[:, :, 1]

    v = hsv[:, :, 2]

    mascara_amarela = (
        (h >= 12)
        &
        (h <= 40)
        &
        (s >= 100)
        &
        (v >= 100)
        &
        (mascara_shape > 0)
    )

    pixels_shape = np.count_nonzero(
        mascara_shape
    )

    if pixels_shape == 0:

        return False

    pixels_amarelos = np.count_nonzero(
        mascara_amarela
    )

    percentual = (
        pixels_amarelos
        / pixels_shape
    )

    return (
        percentual
        >= PERCENTUAL_AMARELO_SHINY
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

    melhor_erro = float("inf")

    melhor_posicao = None

    melhor_tamanho = None

    melhor_mascara = None


    # ========================================================
    # ESCALAS
    # ========================================================

    escalas = [
        0.75,
        0.80,
        0.85,
        0.90,
        0.95,
        1.00,
        1.05,
        1.10,
        1.15,
        1.20,
        1.25
    ]


    # ========================================================
    # PROCURAR SHINY
    # ========================================================

    for escala in escalas:

        nova_largura = int(
            imagem_shiny_cinza.shape[1]
            * escala
        )

        nova_altura = int(
            imagem_shiny_cinza.shape[0]
            * escala
        )

        if (
            nova_largura < 20
            or
            nova_altura < 15
        ):

            continue

        if (
            nova_largura
            > regiao_cinza.shape[1]
            or
            nova_altura
            > regiao_cinza.shape[0]
        ):

            continue

        template = cv2.resize(
            imagem_shiny_cinza,
            (
                nova_largura,
                nova_altura
            ),
            interpolation=cv2.INTER_CUBIC
        )

        mascara = cv2.resize(
            mascara_shiny,
            (
                nova_largura,
                nova_altura
            ),
            interpolation=cv2.INTER_NEAREST
        )

        mascara = (
            mascara * 255
        ).astype(
            np.uint8
        )

        resultado = cv2.matchTemplate(
            regiao_cinza,
            template,
            cv2.TM_SQDIFF_NORMED,
            mask=mascara
        )

        erro, _, posicao, _ = (
            cv2.minMaxLoc(
                resultado
            )
        )

        if erro < melhor_erro:

            melhor_erro = erro

            melhor_posicao = posicao

            melhor_tamanho = (
                nova_largura,
                nova_altura
            )

            melhor_mascara = mascara


    # ========================================================
    # VALIDAR RESULTADO
    # ========================================================

    if (
        melhor_posicao is None
        or
        melhor_tamanho is None
        or
        melhor_mascara is None
    ):

        return None

    if (
        melhor_erro
        > ERRO_MAXIMO_SHINY
    ):

        return None


    # ========================================================
    # POSIÇÃO DO CANDIDATO
    # ========================================================

    px = melhor_posicao[0]

    py_ = melhor_posicao[1]

    largura_shiny = (
        melhor_tamanho[0]
    )

    altura_shiny = (
        melhor_tamanho[1]
    )


    # ========================================================
    # RECORTAR CANDIDATO
    # ========================================================

    candidato = regiao[
        py_:
        py_ + altura_shiny,
        px:
        px + largura_shiny
    ]


    if (
        candidato.shape[1]
        != largura_shiny
        or
        candidato.shape[0]
        != altura_shiny
    ):

        return None


    # ========================================================
    # VALIDAR AMARELO
    # ========================================================

    if not validar_shiny_amarelo(
        candidato,
        melhor_mascara
    ):

        return None


    # ========================================================
    # CENTRO DO SHINY
    # ========================================================

    centro_x = (
        x
        + px
        + largura_shiny // 2
    )

    centro_y = (
        y
        + py_
        + altura_shiny // 2
    )

    return (
        centro_x,
        centro_y
    )


# ============================================================
# USAR BALL
# ============================================================

def usar_ball():

    keyboard.send(
        "shift+4"
    )


# ============================================================
# PEGAR SHINY
# ============================================================

def pegar_shiny():

    coordenada = detectar_shiny()

    if coordenada is None:

        return False

    x, y = coordenada

    py.moveTo(
        x,
        y,
        duration=0.05
    )

    time.sleep(
        0.05
    )

    py.click(
        button="right"
    )

    time.sleep(
        0.70
    )

    usar_ball()

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
            and
            inicio is not None
        ):

            tamanho = (
                i - inicio
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

    return False


# ============================================================
# ESPERAR MINI-GAME
# ============================================================

def esperar_minigame():

    inicio = time.time()

    while True:

        verificar_f11()

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

        verificar_f11()


        # ====================================================
        # TEMPO MÁXIMO
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
        # PEIXE
        # ====================================================

        peixe_y = detectar_peixe(
            imagem
        )


        # ====================================================
        # BARRA
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
# INÍCIO
# ============================================================

verificar_f11()


# ============================================================
# SHINY INICIAL
# ============================================================

pegar_shiny()


# ============================================================
# ELIXIR INICIAL
# ============================================================

usar_elixir()


# ============================================================
# POSICIONAR MOUSE
# ============================================================

py.moveTo(
    *COORDENADA_PESCA
)


# ============================================================
# PRIMEIRO LANÇAMENTO
# ============================================================

autoit.send(
    "q"
)


# ============================================================
# LOOP PRINCIPAL
# ============================================================

while True:

    verificar_f11()


    # ========================================================
    # ESPERA AS BOLHAS
    # ========================================================

    esperar_bolhas()


    # ========================================================
    # PUXA IMEDIATAMENTE
    # ========================================================

    autoit.send(
        "q"
    )


    # ========================================================
    # ESPERA 2.3 SEGUNDOS
    # ========================================================

    time.sleep(
        TEMPO_REPETIR_PESCA
    )


    # ========================================================
    # VERIFICA MINI-GAME
    # ========================================================

    if esperar_minigame():

        resolver_minigame()


    # ========================================================
    # LANÇA NOVAMENTE
    # ========================================================

    autoit.send(
        "q"
    )


    # ========================================================
    # LOOT
    # ========================================================

    fazer_loot()


    # ========================================================
    # SHINY
    # ========================================================

    pegar_shiny()


    # ========================================================
    # ELIXIR
    # ========================================================

    usar_elixir()


    # ========================================================
    # GARANTE SPACE SOLTO
    # ========================================================

    liberar_space()