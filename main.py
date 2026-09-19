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

CONFIANCA_BOLHAS = 0.85
CONFIANCA_PEIXE = 0.70

# Região onde o mini-game aparece
REGIAO_MINIGAME = (900, 430, 100, 420)

# Região aproximada da barra
BARRA_X = (948, 975)
BARRA_Y = (435, 842)

# Tempo máximo esperando o mini-game aparecer
TEMPO_DETECCAO_MINIGAME = 2

# Tempo sem detectar peixe/barra para considerar
# que o mini-game terminou
TEMPO_DESAPARECIMENTO_MINIGAME = 2.0

# Proteção contra ficar preso no mini-game
TEMPO_MAXIMO_MINIGAME = 30

# Estado do Space
SPACE_PRESSIONADO = False


# ============================================================
# CONFIGURAÇÃO
# ============================================================

py.useImageNotFoundException(False)


imagem_bolhas = cv2.imread(BOLHAS)

imagem_peixe = cv2.imread(
    PEIXE,
    cv2.IMREAD_GRAYSCALE
)

imagem_regiao = cv2.imread(
    REGIAO,
    cv2.IMREAD_GRAYSCALE
)


if imagem_bolhas is None:
    raise SystemExit("Imagem bolhas.png não encontrada.")

if imagem_peixe is None:
    raise SystemExit("Imagem peixe.png não encontrada.")

if imagem_regiao is None:
    raise SystemExit("Imagem regiao.png não encontrada.")


# ============================================================
# ATIVAR JANELA
# ============================================================

autoit.win_activate(JANELA)

py.moveTo(416, 532)


# ============================================================
# CAPTURA DA TELA
# ============================================================

def capturar_tela():

    return cv2.cvtColor(
        np.array(py.screenshot()),
        cv2.COLOR_RGB2BGR
    )


# ============================================================
# F1
# ============================================================

def verificar_f1():

    global SPACE_PRESSIONADO

    if keyboard.is_pressed("f1"):

        if SPACE_PRESSIONADO:

            keyboard.release("space")

            SPACE_PRESSIONADO = False

        raise SystemExit


# ============================================================
# LIBERAR SPACE
# ============================================================

def liberar_space():

    global SPACE_PRESSIONADO

    if SPACE_PRESSIONADO:

        keyboard.release("space")

        SPACE_PRESSIONADO = False


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

    confianca = cv2.minMaxLoc(resultado)[1]

    return confianca >= CONFIANCA_BOLHAS


# ============================================================
# ESPERAR BOLHAS
# ============================================================

def esperar_bolhas():

    # Dá tempo para a animação da pesca anterior terminar
    time.sleep(0.3)

    while True:

        verificar_f1()

        if detectar_bolhas():

            return True

        time.sleep(0.03)


# ============================================================
# DETECTAR PEIXE
# ============================================================

def detectar_peixe(imagem):

    x, y, largura, altura = REGIAO_MINIGAME

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

    _, confianca, _, posicao = cv2.minMaxLoc(
        resultado
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
        imagem[y1:y2, x1:x2],
        cv2.COLOR_BGR2GRAY
    )

    brilho = np.mean(
        regiao,
        axis=1
    )

    mascara = brilho > 80

    segmentos = []

    inicio = None

    for i, ativo in enumerate(mascara):

        if ativo and inicio is None:

            inicio = i

        elif not ativo and inicio is not None:

            if i - inicio >= 8:

                segmentos.append(
                    (inicio, i)
                )

            inicio = None

    if inicio is not None:

        segmentos.append(
            (inicio, len(mascara))
        )

    if not segmentos:

        return None

    topo, fundo = max(
        segmentos,
        key=lambda s: s[1] - s[0]
    )

    return (
        topo + y1,
        fundo + y1
    )


# ============================================================
# DETECTAR MINI-GAME
# ============================================================

def detectar_minigame(imagem):

    peixe_y = detectar_peixe(imagem)

    if peixe_y is not None:

        return True

    barra = detectar_barra(imagem)

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

        if detectar_minigame(imagem):

            return True

        if (
            time.time() - inicio
            >= TEMPO_DETECCAO_MINIGAME
        ):

            return False

        time.sleep(0.03)


# ============================================================
# CONTROLAR MINI-GAME
# ============================================================

def controlar_minigame(peixe_y, barra):

    global SPACE_PRESSIONADO

    topo, fundo = barra

    margem = 3

    # Peixe acima da barra
    if peixe_y < topo + margem:

        if not SPACE_PRESSIONADO:

            keyboard.press("space")

            SPACE_PRESSIONADO = True

    # Peixe abaixo da barra
    elif peixe_y > fundo - margem:

        if SPACE_PRESSIONADO:

            keyboard.release("space")

            SPACE_PRESSIONADO = False


# ============================================================
# RESOLVER MINI-GAME
# ============================================================

def resolver_minigame():

    inicio = time.time()

    detectado = False

    ultima_deteccao = time.time()

    while True:

        verificar_f1()

        # Proteção contra ficar preso
        if (
            time.time() - inicio
            >= TEMPO_MAXIMO_MINIGAME
        ):

            liberar_space()

            return


        imagem = capturar_tela()

        peixe_y = detectar_peixe(imagem)

        barra = detectar_barra(imagem)


        # ====================================================
        # PEIXE + BARRA ENCONTRADOS
        # ====================================================

        if (
            peixe_y is not None
            and barra is not None
        ):

            detectado = True

            ultima_deteccao = time.time()

            controlar_minigame(
                peixe_y,
                barra
            )


        # ====================================================
        # NÃO ENCONTROU PEIXE/BARRA
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


        time.sleep(0.01)


# ============================================================
# LOOT
# ============================================================

def fazer_loot():

    autoit.send("e")

    # Pequena pausa para o jogo processar o loot
    time.sleep(0.2)


# ============================================================
# LOOP PRINCIPAL
# ============================================================

while True:

    verificar_f1()


    # ========================================================
    # 1. LANÇA A VARA
    # ========================================================

    autoit.send("q")


    # ========================================================
    # 2. ESPERA AS BOLHAS
    # ========================================================

    esperar_bolhas()


    # ========================================================
    # 3. PUXA A VARA
    # ========================================================

    autoit.send("q")


    # ========================================================
    # 4. LOOTEIA A ÁREA
    # ========================================================

    fazer_loot()


    # ========================================================
    # 5. ESPERA O RESULTADO DA PESCA
    # ========================================================

    time.sleep(1)


    # ========================================================
    # 6. VERIFICA SE VEIO MINI-GAME
    # ========================================================

    if esperar_minigame():

        resolver_minigame()


    # ========================================================
    # 7. GARANTE QUE O SPACE ESTÁ SOLTO
    # ========================================================

    liberar_space()


    # ========================================================
    # 8. PEQUENO INTERVALO
    # ========================================================

    time.sleep(0.5)