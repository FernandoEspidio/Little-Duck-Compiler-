"""
Main - Little Duck.

Punto de entrada del compilador Little Duck. Llama a el lexer y el parser
para analizar un archivo .txt con codigo Little Duck.

El programa por default no imprime el token stream ni la traza del parseo paso a paso. Solo reporta si el codigo es valido
("ACEPTADO") o si hay errores, en cuyo caso lista cada error con su ubicacion y el token que se esperaba/recibio. Si se quisieran ver
estos detalles, se puede activar el modo debug en la función analyze, la cual si se pone en True, ademas de lo mencionado, imprime el token stream completo y la traza del parseo.

Se puede ejecutar el programa de dos formas ya sea de forma directa con un nombre de archivo, en este caso prueba.txt y se imprime
en consola SOLO si fue aceptado o rechazado, listando errores si los hubo. No se imprime el token stream ni el parser. Después también se llama a la función para procesar todos los archivos .txt del folder inputs/ 
y guarda la salida detallada con informacion del token stream y el seguimiento del parser de cada uno en outputs/
"""

import os
import sys
from contextlib import redirect_stdout

from lexer import Tokenizer, read_source, printTokens
from parser import Parser, print_errors


# Archivo que se ejecuta en consola por default
FILE_NAME = "prueba.txt"

# Carpetas para los casos de prueba
INPUTS_DIR = "inputs"
OUTPUTS_DIR = "outputs"


"""
Funcion que ejecuta el analisis de un archivo .txt.

Args:
    fileName: ruta al archivo a analizar.
    debug: si True, imprime el codigo fuente, el token stream y la traza
             del parseo. Si False (default), solo imprime ACEPTADO o los
             errores encontrados.
"""
def analyze_file(fileName, debug=False):
    # Se lee el archivo
    source_code = read_source(fileName)

    if debug:
        # Modo detallado: encabezado + codigo fuente + tokens
        print(f"=== Archivo: {fileName} ===\n")
        print("Codigo fuente:")
        print("-" * 60)
        print(source_code)
        print("-" * 60)

        # En modo debug, se hace una pasada de tokenizacion adicional
        # solo para mostrar el token stream al usuario
        tokenizer_preview = Tokenizer(keep_comments=True)
        tokenizer_preview.tokenize(source_code)
        print("\n--- Analisis lexico ---")
        printTokens(source_code, tokenizer_preview, debug=True)
        print("\n--- Analisis sintactico ---")

    # Parseo: se crea un tokenizer y parser nuevos para esta corrida
    tokenizer = Tokenizer(keep_comments=False)
    parser = Parser(tokenizer=tokenizer)
    ok = parser.parse(source_code)

    # Reporte final segun el resultado
    if ok:
        print(f"\n{fileName}: ACEPTADO")
    else:
        print(f"\n{fileName}: RECHAZADO")
        print_errors(parser)
        print(f"\nTotal: {len(tokenizer.errors)} error(es) lexico(s), "
              f"{len(parser.errors)} error(es) sintactico(s)")

    return ok


"""
Procesa todos los archivos .txt del folder inputs/ y escribe el resultado
detallado (con token stream y traza) en outputs/ con el mismo nombre.

Esta funcion siempre usa modo debug para que los archivos de output
sirvan como evidencia completa de cada caso de prueba en el reporte.
"""
def run_test_cases(inputs_dir=INPUTS_DIR, outputs_dir=OUTPUTS_DIR):
    # Se crea el folder de salida si no existe
    os.makedirs(outputs_dir, exist_ok=True)

    # Se listan los archivos .txt del folder de entrada, ordenados
    input_files = sorted(
        f for f in os.listdir(inputs_dir) if f.endswith(".txt")
    )

    if not input_files:
        print(f"No se encontraron archivos .txt en {inputs_dir}/")
        return

    print(f"Procesando {len(input_files)} caso(s) de prueba:\n")

    # Por cada archivo de entrada, se analiza en modo debug y se redirige
    # la salida al archivo correspondiente en outputs/
    for fname in input_files:
        input_path = os.path.join(inputs_dir, fname)
        output_path = os.path.join(outputs_dir, fname)

        with open(output_path, "w", encoding="utf-8") as out_file:
            with redirect_stdout(out_file):
                analyze_file(input_path, debug=True)

        print(f"  {input_path}  ->  {output_path}")


if __name__ == "__main__":
    # Primero se corre el archivo de consola default prueba.txt y se imprime el resultado de si fue aceptado o no, junto con los errores si los hubo
    if os.path.exists(FILE_NAME):
        analyze_file(FILE_NAME, debug=False)
    else:
        print(f"Aviso: no se encontro '{FILE_NAME}' en el directorio actual.")

    # Despues se procesan todos los casos de prueba del folder inputs/
    # y se guardan en outputs/. Esto no imprime nada al usuario, pero se imprime en caso de que se quiera analizar con más a detalle 
    # cada caso de prueba
    if os.path.isdir(INPUTS_DIR):
        print()
        run_test_cases()