# Lexer con PLY - Little Duck

import os
import sys
from collections import defaultdict
from contextlib import redirect_stdout

import ply.lex as lex

"""
Se implementa el tokenizer con PLY acorde con la documentación y definición de tokens en el reporte
Se hace la clase para mantener una estructura un poco más ordenada compuesta del lexer y el parser
"""
class Tokenizer:
    # Se define la lista de palabras reservadas
    reserved = {
        "print": "KEYWORD_PRINT",
        "program": "KEYWORD_PROGRAM",
        "main": "KEYWORD_MAIN",
        "end": "KEYWORD_END",
        "int": "KEYWORD_INT",
        "float": "KEYWORD_FLOAT",
        "string": "KEYWORD_STRING",
        "do": "KEYWORD_DO",
        "while": "KEYWORD_WHILE",
        "if": "KEYWORD_IF",
        "else": "KEYWORD_ELSE",
        "var": "KEYWORD_VAR",
        "void": "KEYWORD_VOID",
        "for": "KEYWORD_FOR",
        "switch": "KEYWORD_SWITCH",
        "case": "KEYWORD_CASE",
        "default": "KEYWORD_DEFAULT",
        "break": "KEYWORD_BREAK",
        "continue": "KEYWORD_CONTINUE",
        "return": "KEYWORD_RETURN",
    }

    # Lista de tokens que son aceptados para el lexer de PLY
    tokens = [
        # Delimitadores
        "LBRACE",
        "RBRACE",
        "LPAREN",
        "RPAREN",
        "LBRACKET",
        "RBRACKET",
        "COMMA",
        "SEMICOL",
        "COLON",
 
        # Operadores
        "OP_EQUAL",
        "OP_NOT_EQUAL",
        "OP_LESS_EQUAL",
        "OP_GREATER_EQUAL",
        "OP_LESS_THAN",
        "OP_GREATER_THAN",
        "OP_LOGICAL_AND",
        "OP_LOGICAL_OR",
        "OP_LOGICAL_NOT",
        "OP_INCREMENT",
        "OP_DECREMENT",
        "OP_PLUS_ASSIGN",
        "OP_MINUS_ASSIGN",
        "OP_MULT_ASSIGN",
        "OP_DIV_ASSIGN",
        "OP_MOD_ASSIGN",
        "OP_TERNARY",
        "OP_ASSIGN",
        "OP_PLUS",
        "OP_MINUS",
        "OP_MULT",
        "OP_DIV",
        "OP_MOD",
 
        # Constantes
        "CONST_FLOAT",
        "CONST_INT",
        "CONST_STR",
 
        # Identificadores
        "ID",
 
        # Comentarios
        "BLOCK_COMMENT",
        "COMMENT",
 
        # Errores lexicos controlados
        "ERROR_INCOMPLETE_BLOCK_COMMENT",
        "ERROR_INCOMPLETE_STRING",
    ] + list(reserved.values())

    # Se establecen las expresiones regulares para cada token bajo la forma de string, ya que 
    # son directas y no requieren validaciones adicionales
    # Delimitadores
    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_COMMA = r","
    t_SEMICOL = r";"
    t_COLON = r":"
 
    # Relacionales
    t_OP_EQUAL = r"=="
    t_OP_NOT_EQUAL = r"!="
    t_OP_LESS_EQUAL = r"<="
    t_OP_GREATER_EQUAL = r">="
    t_OP_LESS_THAN = r"<"
    t_OP_GREATER_THAN = r">"
 
    # Lógicos
    t_OP_LOGICAL_AND = r"&&"
    t_OP_LOGICAL_OR = r"\|\|"
    t_OP_LOGICAL_NOT = r"!"
 
    # Incremento / decremento
    t_OP_INCREMENT = r"\+\+"
    t_OP_DECREMENT = r"--"
 
    # Asignación compuesta
    t_OP_PLUS_ASSIGN = r"\+="
    t_OP_MINUS_ASSIGN = r"-="
    t_OP_MULT_ASSIGN = r"\*="
    t_OP_DIV_ASSIGN = r"/="
    t_OP_MOD_ASSIGN = r"%="
 
    # Ternario y asignación
    t_OP_TERNARY = r"\?"
    t_OP_ASSIGN = r"="
 
    # Aritméticos
    t_OP_PLUS = r"\+"
    t_OP_MINUS = r"-"
    t_OP_MULT = r"\*"
    t_OP_DIV = r"/"
    t_OP_MOD = r"%"
 
    # Caracteres ignorados por el lexer.
    # No se incluye \n porque las líneas se cuentan en t_newline.
    t_ignore = " \t\r"

    # Se definen como funciones los tokens que requieren validaciones adicionales

    # Función para reconocer comentarios de bloque, que pueden ser multilinea. Se cuentan las líneas que abarca el comentario.
    def t_BLOCK_COMMENT(self, t):
        r'"""[\s\S]*?"""'
        t.lexer.lineno += t.value.count("\n")

        # Si se quieren imprimir comentarios, se regresa el token. Si no, se ignora.
        if self.keep_comments:
            return t

        # Si no se quieren imprimir comentarios, se reconocen pero se ignoran.
        return None

    # Función para reconocer comentarios de bloque que no cierran correctamente. Se cuentan las líneas que abarca el comentario.
    def t_ERROR_INCOMPLETE_BLOCK_COMMENT(self, t):
        r'"""[\s\S]*'

        #  Se agrega un error léxico indicando que el comentario de bloque no se cerró correctamente.
        self.add_error("ERROR_INCOMPLETE_BLOCK_COMMENT", '"""', t.lexer.lineno, t.lexpos,)

        # Se cuentan las líneas que abarca el comentario, aunque no se regresa ningún token porque es un error.
        t.lexer.lineno += t.value.count("\n")
        return None

    # Función para reconocer comentarios de línea, que van desde # hasta el final de la línea.
    def t_COMMENT(self, t):
        r"\#[^\n]*"

        # Si se quieren imprimir comentarios, se regresa el token. Si no, se ignora.
        if self.keep_comments:
            return t

        return None

    # Función para reconocer constantes de tipo float
    def t_CONST_FLOAT(self, t):
        r"[0-9]+\.[0-9]+\b"
        return t

    # Función para reconocer constantes de tipo int
    def t_CONST_INT(self, t):
        r"[0-9]+\b"
        return t

    # Función para reconocer constantes de tipo string, que van entre comillas dobles
    # Se permiten caracteres escapados con \, incluyendo \" para comillas dentro del string.
    def t_CONST_STR(self, t):
        r'"[^"\n]*"'
        return t

    # Función para reconocer strings que no cierran correctamente
    # Se agrega un error léxico indicando que el string no se cerró correctamente
    def t_ERROR_INCOMPLETE_STRING(self, t):
        r'"[^\n]*'

        # Se agrega un error léxico indicando que el string no se cerró correctamente. 
        self.add_error(
            "ERROR_INCOMPLETE_STRING",
            t.value,
            t.lexer.lineno,
            t.lexpos,
        )
        return None

    # Función para reconocer identificadores, que empiezan con letra y pueden contener letras, dígitos o guiones bajos.
    def t_ID(self, t):
        r"[a-zA-Z]\w*\b"

        # Si el lexema es palabra reservada, se cambia el tipo del token.
        # Si no, se queda como id.
        t.type = self.reserved.get(t.value, "ID")
        return t

    # Función para contar líneas, se acepta una o más nuevas líneas y se incrementa el contador de líneas del lexer
    def t_newline(self, t):
        r"\n+"
        # Se cuentan las líneas que abarca la nueva línea
        t.lexer.lineno += len(t.value)

    # Función para manejar errores léxicos, como símbolos desconocidos. Se agrega un error léxico indicando el símbolo desconocido.
    def t_error(self, t):
        self.add_error(
            "ERROR_UNKNOWN_SYMBOL",
            t.value[0],
            t.lexer.lineno,
            t.lexpos,
        )
        t.lexer.skip(1)
    
    """
    El constructor del tokenizer recibe un parámetro opcional para indicar si se quieren conservar los comentarios como tokens o no
    Se inicializan las estructuras de datos para almacenar el código fuente, el stream de tokens, los tokens por línea y los errores léxicos
    También se crea el lexer de PLY usando la clase actual como módulo.
    """
    def __init__(self, keep_comments=True):
        self.keep_comments = keep_comments # Indica si se quieren conservar los comentarios como tokens o no
        self.source_code = "" # El código fuente que se va a tokenizar
        self.token_stream = [] # Lista de tokens generados por el lexer, cada token es un diccionario con tipo, valor, línea, posición y columna
        self.tokensByLine = defaultdict(list) # Diccionario que mapea cada número de línea a la lista de tokens que aparecen en esa línea
        self.errors = [] # Lista de errores léxicos encontrados durante la tokenización, cada error es un diccionario con tipo, valor, línea, posición y columna
        self.lexer = lex.lex(module=self) # Se crea el lexer de PLY usando la clase actual como módulo, lo que permite que PLY encuentre las definiciones de tokens y funciones en esta clase

    # Funciones adicionales para manejo de tokens y errores
    
    # Función para limpiar los tokens
    def clean_tokens(self):
        # Se reinician las estructuras de datos para almacenar el código fuente, el stream de tokens, los tokens por línea y los errores léxicos
        self.token_stream = []
        self.tokensByLine = defaultdict(list)
        self.errors = []

    # Función para calcular la columna 1-indexed usando la posición absoluta lexpos. Se busca la última nueva línea antes de lexpos y se calcula la diferencia.
    # NO se usa como tal en la implementación, pero venía recomendado en la investigación que se realizó
    def find_column(self, lexpos):
        """Calcula la columna 1-indexed usando la posición absoluta lexpos."""
        last_newline = self.source_code.rfind("\n", 0, lexpos)
        return lexpos - last_newline

    # Función para agregar un error léxico a la lista de errores, 
    # se añade el tipo de error, el valor del token o símbolo que causó el error, la línea y la posición absoluta lexpos
    def add_error(self, error_type, value, lineno, lexpos):
        self.errors.append({
            "type": error_type,
            "value": value,
            "lineno": lineno,
            "lexpos": lexpos,
        })

    # Función para convertir un token de PLY a un diccionario con tipo, valor, línea, posición absoluta y columna
    def token_to_dict(self, tok):
        return {
            "type": tok.type,
            "value": tok.value,
            "lineno": tok.lineno,
            "lexpos": tok.lexpos,
        }
    
    # Función principal para tokenizar una cadena de entrada. 
    def tokenize(self, input_string):
        self.clean_tokens() # Se limpian los tokens y errores anteriores antes de tokenizar una nueva cadena de entrada
        self.source_code = input_string # Se guarda el código fuente que se va a tokenizar, lo que permite calcular columnas y mostrar líneas completas en caso de errores

        # Se inicializa el lexer con la cadena de entrada y se establece el contador de líneas en 1
        self.lexer.lineno = 1
        self.lexer.input(input_string)

        # Se itera sobre los tokens generados por el lexer hasta que no haya más tokens (tok es None).
        while True:
            tok = self.lexer.token()

            if not tok:
                break

            # Se convierte el token de PLY a un diccionario con tipo, valor, línea, posición absoluta 
            # y se agrega al stream de tokens y al diccionario de tokens por línea.
            token_data = self.token_to_dict(tok)
            self.token_stream.append(token_data)
            self.tokensByLine[token_data["lineno"]].append(token_data)

        # Al finalizar la tokenización, se regresa el diccionario de tokens por línea, que mapea cada número de línea a la lista de tokens que aparecen en esa línea.
        return self.tokensByLine


    # Interfaz para el parser de PLY
    # El parser de PLY (yacc) espera que el lexer le pase tenga metodos input() y token().
    # input() recibe la cadena de entrada y token() devuelve el siguiente token o None cuando se acaba. 

    """ Función que pasa la cadena al lexer interno y limpia el estado."""
    def input(self, data):
        self.clean_tokens()
        self.source_code = data
        self.lexer.lineno = 1
        self.lexer.input(data)

    """
    Devuelve el siguiente token al parser, descartando comentarios. El parser no necesita saber sobre comentarios, ya que no afectan
    la estructura sintáctica del programa.
    """
    def token(self):
        while True:
            tok = self.lexer.token()
            if tok is None:
                return None
            if tok.type in ("COMMENT", "BLOCK_COMMENT"):
                continue
            return tok

    # PLY consulta lexer.lineno y lexer.lexpos directamente para rastrear
    # posicion cuando se usa tracking=True.
    def __getattr__(self, name):
        if name in ("lineno", "lexpos"):
            return getattr(self.__dict__["lexer"], name)
        raise AttributeError(name)

# Función para acortar el valor de un token o error léxico si es muy largo, mostrando solo los primeros y últimos caracteres con "(...)" en medio
#  Hace más legibles strings o comentarios largos
def shorten_value(value, limit=40):
    # Se convierte el valor a string y se reemplazan las nuevas líneas por \n para que se muestren como texto en lugar de saltos de línea reales
    text = str(value).replace("\n", "\\n")
    
    # Si el texto es menor o igual al límite, se regresa tal cual. Si es mayor, se muestra solo los primeros caracteres, luego "(...)" y luego los últimos caracteres.
    if len(text) <= limit:
        return text

    return text[:15] + " (...) " + text[-15:]

# Función para imprimir los tokens por línea en el formato que se pidió
def printTokens(source_code, patokenizer, verbose=True):
    if verbose:
        # Se divide el código fuente en líneas para poder mostrar la línea
        # completa junto con los tokens que aparecen en esa línea
        source_lines = source_code.splitlines()

        print("Token stream:")

        # Se itera sobre los números de línea en orden, y para cada línea se
        # muestra el número de línea, el texto completo de la línea y luego
        # los tokens que aparecen en esa línea con su tipo, valor acortado,
        # posición absoluta lexpos
        for line_num in sorted(patokenizer.tokensByLine.keys()):
            line_text = source_lines[line_num - 1] if line_num - 1 < len(source_lines) else ""
            print(f"\nLinea {line_num}: {line_text}")

            for tok in patokenizer.tokensByLine[line_num]:
                value = shorten_value(tok["value"])
                print(
                    f"{tok['type']:<28} "
                    f"value: {value:<25} "
                    f"lexpos: {tok['lexpos']:<5} "
                )

    # Los errores siempre se muestran, sin importar el modo verbose
    if patokenizer.errors:
        print("\nErrores lexicos:")

        for err in patokenizer.errors:
            value = shorten_value(err["value"])
            print(
                f"{err['type']:<35} "
                f"value: {value:<20} "
                f"linea: {err['lineno']:<3} "
                f"lexpos: {err['lexpos']:<5} "
            )
    
# Lee un archivo local
def read_source(fileName):
    with open(fileName, "r", encoding="utf-8") as file:
        return file.read()

# Función de prueba para tokenizar un archivo con PLY,
def test_tokenizer(fileName, patokenizer):
    textInput = read_source(fileName)

    patokenizer.tokenize(textInput)

    print(f"Resultados del tokenizer: {fileName}\n")
    printTokens(textInput, patokenizer)

    return patokenizer.token_stream

