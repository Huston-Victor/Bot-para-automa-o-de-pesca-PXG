import time
import keyboard


print("Você tem 3 segundos para clicar no PXG...")
time.sleep(3)

print("Enviando Shift + 4...")

keyboard.send("shift+4")

print("Enviado.")