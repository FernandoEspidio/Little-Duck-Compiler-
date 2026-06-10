# Little Duck
# Equipo 5

# Integrantes:
"""
Abdiel Fritsche Barajas A01234933
Luis Santiago Sauma Peñaloza A00836418
Fernando Espidio Santamaria A00837570
Saúl Emilio Delgado Garza A01285188
Michelle González Candanosa A00837313
"""

import os
import sys
from collections import defaultdict
from contextlib import redirect_stdout

import ply.lex as lex

"""
Implementación del tokenizer con PLY (Definición de tokens en el reporte Entrega 1)

Clase Tokenizer para estructurar de mejor manera el lexer y parser
"""
class Tokenizer:
    # Lista de palabras reservadas
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

    # Se establecen las expresiones regulares para cada token bajo la forma de string, ya que son directas y no requieren validaciones adicionales

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
 
    # Logicos
    t_OP_LOGICAL_AND = r"&&"
    t_OP_LOGICAL_OR = r"\|\|"
    t_OP_LOGICAL_NOT = r"!"
 
    # Incremento / decremento
    t_OP_INCREMENT = r"\+\+"
    t_OP_DECREMENT = r"--"
 
    # Asignacion compuesta
    t_OP_PLUS_ASSIGN = r"\+="
    t_OP_MINUS_ASSIGN = r"-="
    t_OP_MULT_ASSIGN = r"\*="
    t_OP_DIV_ASSIGN = r"/="
    t_OP_MOD_ASSIGN = r"%="
 
    # Ternario y asignacion
    t_OP_TERNARY = r"\?"
    t_OP_ASSIGN = r"="
 
    # Aritmeticos
    t_OP_PLUS = r"\+"
    t_OP_MINUS = r"-"
    t_OP_MULT = r"\*"
    t_OP_DIV = r"/"
    t_OP_MOD = r"%"
 
    # Caracteres ignorados por el lexer.
    # No se incluye \n porque las lineas se cuentan en t_newline.
    t_ignore = " \t\r"

    # Se definen como funciones los tokens que requieren validaciones adicionales

    # Funcion para reconocer comentarios de bloque, que pueden ser multilinea. Se cuentan las lineas que abarca el comentario.
    def t_BLOCK_COMMENT(self, t):
        r'"""[\s\S]*?"""'
        t.lexer.lineno += t.value.count("\n")

        # Si se quieren imprimir comentarios, se regresa el token. Si no, se ignora.
        if self.keep_comments:
            return t

        # Si no se quieren imprimir comentarios, se reconocen pero se ignoran.
        return None

    # Funcion para reconocer comentarios de bloque que no cierran correctamente. Se cuentan las lineas que abarca el comentario.
    def t_ERROR_INCOMPLETE_BLOCK_COMMENT(self, t):
        r'"""[\s\S]*'

        #  Se agrega un error lexico indicando que el comentario de bloque no se cerro correctamente.
        self.add_error("ERROR_INCOMPLETE_BLOCK_COMMENT", '"""', t.lexer.lineno, t.lexpos,)

        # Se cuentan las lineas que abarca el comentario, aunque no se regresa ningun token porque es un error.
        t.lexer.lineno += t.value.count("\n")
        return None

    # Funcion para reconocer comentarios de linea, que van desde # hasta el final de la linea.
    def t_COMMENT(self, t):
        r"\#[^\n]*"

        # Si se quieren imprimir comentarios, se regresa el token. Si no, se ignora.
        if self.keep_comments:
            return t

        return None

    # Funcion para reconocer constantes de tipo float
    def t_CONST_FLOAT(self, t):
        r"[0-9]+\.[0-9]+\b"
        return t

    # Funcion para reconocer constantes de tipo int
    def t_CONST_INT(self, t):
        r"[0-9]+\b"
        return t

    # Funcion para reconocer constantes de tipo string, que van entre comillas dobles
    # Se permiten caracteres escapados con \, incluyendo \" para comillas dentro del string.
    def t_CONST_STR(self, t):
        r'"[^"\n]*"'
        return t

    # Funcion para reconocer strings que no cierran correctamente
    # Se agrega un error lexico indicando que el string no se cerro correctamente
    def t_ERROR_INCOMPLETE_STRING(self, t):
        r'"[^\n]*'

        # Se agrega un error lexico indicando que el string no se cerro correctamente. 
        self.add_error(
            "ERROR_INCOMPLETE_STRING",
            t.value,
            t.lexer.lineno,
            t.lexpos,
        )
        return None

    # Funcion para reconocer identificadores, que empiezan con letra y pueden contener letras, digitos o guiones bajos.
    def t_ID(self, t):
        r"[a-zA-Z]\w*\b"

        # Si el lexema es palabra reservada, se cambia el tipo del token.
        # Si no, se queda como id.
        t.type = self.reserved.get(t.value, "ID")
        return t

    # Funcion para contar lineas, se acepta una o mas nuevas lineas y se incrementa el contador de lineas del lexer
    def t_newline(self, t):
        r"\n+"
        # Se cuentan las lineas que abarca la nueva linea
        t.lexer.lineno += len(t.value)

    # Funcion para manejar errores lexicos, como simbolos desconocidos. Se agrega un error lexico indicando el simbolo desconocido.
    def t_error(self, t):
        self.add_error(
            "ERROR_UNKNOWN_SYMBOL",
            t.value[0],
            t.lexer.lineno,
            t.lexpos,
        )
        t.lexer.skip(1)
    
    """
    El constructor del tokenizer recibe un parametro opcional para indicar si se quieren conservar los comentarios como tokens o no
    Se inicializan las estructuras de datos para almacenar el codigo fuente, el stream de tokens, los tokens por linea y los errores lexicos
    Tambien se crea el lexer de PLY usando la clase actual como modulo.
    """
    def __init__(self, keep_comments=True):
        self.keep_comments = keep_comments # Indica si se quieren conservar los comentarios como tokens o no
        self.source_code = "" # El codigo fuente que se va a tokenizar
        self.token_stream = [] # Lista de tokens generados por el lexer, cada token es un diccionario con tipo, valor, linea, posicion y columna
        self.tokensByLine = defaultdict(list) # Diccionario que mapea cada numero de linea a la lista de tokens que aparecen en esa linea
        self.errors = [] # Lista de errores lexicos encontrados durante la tokenizacion, cada error es un diccionario con tipo, valor, linea, posicion y columna
        self.lexer = lex.lex(module=self) # Se crea el lexer de PLY usando la clase actual como modulo, lo que permite que PLY encuentre las definiciones de tokens y funciones en esta clase

    # Funciones adicionales para manejo de tokens y errores
    
    # Funcion para limpiar los tokens
    def clean_tokens(self):
        # Se reinician las estructuras de datos para almacenar el codigo fuente, el stream de tokens, los tokens por linea y los errores lexicos
        self.token_stream = []
        self.tokensByLine = defaultdict(list)
        self.errors = []

    # Funcion para calcular la columna 1-indexed usando la posicion absoluta lexpos. Se busca la ultima nueva linea antes de lexpos y se calcula la diferencia.
    # NO se usa como tal en la implementacion, pero venia recomendado en la investigacion que se realizo
    def find_column(self, lexpos):
        last_newline = self.source_code.rfind("\n", 0, lexpos)
        return lexpos - last_newline

    # Funcion para agregar un error lexico a la lista de errores, 
    # se anade el tipo de error, el valor del token o simbolo que causo el error, la linea y la posicion absoluta lexpos
    def add_error(self, error_type, value, lineno, lexpos):
        self.errors.append({
            "type": error_type,
            "value": value,
            "lineno": lineno,
            "lexpos": lexpos,
        })

    # Funcion para convertir un token de PLY a un diccionario con tipo, valor, linea, posicion absoluta y columna
    def token_to_dict(self, tok):
        return {
            "type": tok.type,
            "value": tok.value,
            "lineno": tok.lineno,
            "lexpos": tok.lexpos,
        }
    
    # Funcion principal para tokenizar una cadena de entrada. 
    def tokenize(self, input_string):
        self.clean_tokens() # Se limpian los tokens y errores anteriores antes de tokenizar una nueva cadena de entrada
        self.source_code = input_string # Se guarda el codigo fuente que se va a tokenizar, lo que permite calcular columnas y mostrar lineas completas en caso de errores

        # Se inicializa el lexer con la cadena de entrada y se establece el contador de lineas en 1
        self.lexer.lineno = 1
        self.lexer.input(input_string)

        # Se itera sobre los tokens generados por el lexer hasta que no haya mas tokens (tok es None).
        while True:
            tok = self.lexer.token()

            if not tok:
                break

            # Se convierte el token de PLY a un diccionario con tipo, valor, linea, posicion absoluta 
            # y se agrega al stream de tokens y al diccionario de tokens por linea.
            token_data = self.token_to_dict(tok)
            self.token_stream.append(token_data)
            self.tokensByLine[token_data["lineno"]].append(token_data)

        # Al finalizar la tokenizacion, se regresa el diccionario de tokens por linea, que mapea cada numero de linea a la lista de tokens que aparecen en esa linea.
        return self.tokensByLine


    # Interfaz para el parser de PLY
    # El parser de PLY (yacc) espera que el lexer le pase tenga metodos input() y token().
    # input() recibe la cadena de entrada y token() devuelve el siguiente token o None cuando se acaba. 

    def input(self, data):
        self.clean_tokens()
        self.source_code = data
        self.last_token_line = 1
        self.lexer.lineno = 1
        self.lexer.input(data)

    # Devuelve el siguiente token al parser, descartando comentarios.
    def token(self):
        while True:
            tok = self.lexer.token()
            if tok is None:
                return None
            if tok.type in ("COMMENT", "BLOCK_COMMENT"):
                continue
            self.last_token_line = tok.lineno  # se recuerda para las reglas marcador
            return tok

    # PLY consulta lexer.lineno y lexer.lexpos directamente para rastrear posicion cuando se usa tracking=True.
    def __getattr__(self, name):
        if name in ("lineno", "lexpos"):
            return getattr(self.__dict__["lexer"], name)
        raise AttributeError(name)

# Funcion para acortar el valor de un token o error lexico si es muy largo, mostrando solo los primeros y ultimos caracteres con "(...)" en medio para mejor legibilidad
def shorten_value(value, limit=40):
    # Se convierte el valor a string y se reemplazan las nuevas lineas por \n para que se muestren como texto en lugar de saltos de linea reales
    text = str(value).replace("\n", "\\n")
    
    # Si el texto es menor o igual al limite, se regresa tal cual. Si es mayor, se muestra solo los primeros caracteres, luego "(...)" y luego los ultimos caracteres.
    if len(text) <= limit:
        return text

    return text[:15] + " (...) " + text[-15:]

# Funcion para imprimir los tokens por linea en el formato que se pidio
def printTokens(source_code, patokenizer, debug=True):
    if debug:
        # Se divide el codigo fuente en lineas para poder mostrar la linea
        # completa junto con los tokens que aparecen en esa linea
        source_lines = source_code.splitlines()

        print("Token stream:")

        # Se itera sobre los numeros de linea en orden, y para cada linea se
        # muestra el numero de linea, el texto completo de la linea y luego
        # los tokens que aparecen en esa linea con su tipo, valor acortado,
        # posicion absoluta lexpos
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

    # Los errores siempre se muestran, sin importar el modo debug
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

# Funcion de prueba para tokenizar un archivo con PLY,
def test_tokenizer(fileName, patokenizer):
    textInput = read_source(fileName)

    patokenizer.tokenize(textInput)

    print(f"Resultados del tokenizer: {fileName}\n")
    printTokens(textInput, patokenizer)

    return patokenizer.token_stream




# SEGUNDA ENTREGA: ANALISIS SEMANTICO Y REPRESENTACION INTERMEDIA (CUADRUPLOS)
#
# Las validaciones semánticas se hacen al mismo tiempo que se lee la estructura del código (parsing).
# Añadidos de esta entrega:
#   - directorio de funciones + tablas de variables por scope
#   - cubo semantico para coincidencia de tipos
#   - pila de operandos, pila de saltos, pila de scopes
#   - generacion de cuadruplos (three address code) para: expresiones,
#     asignaciones, if/else, while, do-while, for, switch, ternario,
#     llamadas a funciones (ERA/PARAM/GOSUB), return, print, break/continue

import ply.yacc as yacc


# CUBO SEMANTICO
# Estructura que considera los tipos, dados (tipo_izq, tipo_der, operador), devuelve el tipo del
# resultado o 'error' si la operacion no es valida. Maneja int, float, string y bool
class CuboSemantico:
    def __init__(self):
        self.cubo = {}

        # Aritmeticos + - * : enteros y flotantes, con promocion a float
        for op in ("+", "-", "*"):
            self.cubo[("int", "int", op)] = "int"
            self.cubo[("int", "float", op)] = "float"
            self.cubo[("float", "int", op)] = "float"
            self.cubo[("float", "float", op)] = "float"
        
        # Concatenacion de strings con +
        self.cubo[("string", "string", "+")] = "string"

        # Division / : siempre produce float entre datos numericso
        for l in ("int", "float"):
            for r in ("int", "float"):
                self.cubo[(l, r, "/")] = "float"

        # Modulo % : solo enteros
        self.cubo[("int", "int", "%")] = "int"

        # Relacionales < > <= >= : numericos a bool
        for op in ("<", ">", "<=", ">="):
            for l in ("int", "float"):
                for r in ("int", "float"):
                    self.cubo[(l, r, op)] = "bool"

        # Igualdad == != : numericos, strings y bools a bool
        for op in ("==", "!="):
            for l in ("int", "float"):
                for r in ("int", "float"):
                    self.cubo[(l, r, op)] = "bool"
            self.cubo[("string", "string", op)] = "bool"
            self.cubo[("bool", "bool", op)] = "bool"

        # Logicos && || : bool con bool a bool
        for op in ("&&", "||"):
            self.cubo[("bool", "bool", op)] = "bool"

    # Consulta el tipo resultante de una operacion binaria
    def resultado(self, izq, der, op):
        return self.cubo.get((izq, der, op), "error")


# Compatibilidad para asignacion target = value.
# Devuelve el tipo del target si es valido, o 'error' si no.
# Reglas aparte: float acepta int, pero int no float, los iguales son compatibles y bool no se puede asignar a variables.

def compatible_asignacion(tipo_target, tipo_valor):
    if tipo_target == tipo_valor:
        return tipo_target
    if tipo_target == "float" and tipo_valor == "int":
        return "float"
    return "error"


# Resultado de un operador unario (- + sobre numericos, ! sobre bool)
def resultado_unario(op, tipo):
    if op in ("-", "+"):
        return tipo if tipo in ("int", "float") else "error"
    if op == "!":
        return "bool" if tipo == "bool" else "error"
    return "error"


# Unifica el tipo de las dos ramas de un ternario
def unifica_tipos(t1, t2):
    if t1 == t2:
        return t1
    if {t1, t2} == {"int", "float"}:
        return "float"
    return "error"


# PARSER (IMPLEMENTADO CON ACCIONES SEMANTICAS)
# Se reutiliza la misma estructura de clase wrapper del parser de la entrega pasada.
# Se agrega el cuerpo de cada funcion con la accion semantica correspondiente y los marcadores (np_xxx) que insertan acciones a la mitad de una regla. 
# Pero se mantienen las reglas gramáticales de la entrega pasada

class Parser:
    # Tokens importados del lexer
    tokens = Tokenizer.tokens

    # BODY PRINCIPAL DEL PROGRAMA
    # PROGRAM ::= keyword_program id ';' VARS_OPT FUNCS_LIST keyword_main BODY keyword_end
    # np_program: registra el scope global y emite el goto inicial hacia main.
    # np_main: rellena ese goto con el inicio del cuerpo de main.
    def p_program(self, p):
        """program : KEYWORD_PROGRAM ID np_program SEMICOL vars_opt funcs_list np_main KEYWORD_MAIN body KEYWORD_END"""
        # Al terminar el programa (tras el cuerpo de main) se emite un quad de
        # fin de ejecucion para que la maquina virtual sepa donde detenerse.
        self.emit("end", "-", "-", "-")

    # Marcador: tras leer el id del programa, se registra como scope global en el directorio de funciones y se emite goto pendiente hacia main.
    def p_np_program(self, p):
        """np_program : empty"""
        name = p[-1]  # el ID del programa esta inmediatamente a la izquierda
        self.global_scope = name
        self.func_dir[name] = {
            "return_type": "void",
            "params": [],
            "n_params": 0,
            "var_table": {},
            "start_quad": None,
        }
        self.scope_stack = [name]
        # gotomain inicial: salta a main, se rellena en np_main
        q = self.emit("gotomain", "-", "-", None)
        self.jump_stack.append(q)

    # Marcador: tras las funciones, se rellena el goto inicial con el inicio de main y se asegura que el scope vuelva a ser global.
    def p_np_main(self, p):
        """np_main : empty"""
        pending = self.jump_stack.pop()
        self.backpatch(pending, self.quad_count + 1)
        self.scope_stack = [self.global_scope]

    # VARS_OPT ::= VARS | epsilon
    def p_vars_opt_vars(self, p):
        """vars_opt : vars"""
        pass

    def p_vars_opt_empty(self, p):
        """vars_opt : empty"""
        pass

    # FUNCS_LIST ::= FUNCS_LIST FUNCS | epsilon
    def p_funcs_list_multiple(self, p):
        """funcs_list : funcs_list funcs"""
        pass

    def p_funcs_list_empty(self, p):
        """funcs_list : empty"""
        pass

    # BODY ::= '{' STMT_LIST '}'
    def p_body(self, p):
        """body : LBRACE stmt_list RBRACE"""
        pass

    # STMT_LIST ::= STMT_LIST STATEMENT | epsilon
    def p_stmt_list_multiple(self, p):
        """stmt_list : stmt_list statement"""
        pass

    def p_stmt_list_empty(self, p):
        """stmt_list : empty"""
        pass

    # VARIABLES
    # VARS ::= keyword_var VAR_DECL_LIST
    def p_vars(self, p):
        """vars : KEYWORD_VAR var_decl_list"""
        pass

    # VAR_DECL_LIST ::= VAR_DECL_LIST VAR_DECL | VAR_DECL
    def p_var_decl_list_multiple(self, p):
        """var_decl_list : var_decl_list var_decl"""
        pass

    def p_var_decl_list_single(self, p):
        """var_decl_list : var_decl"""
        pass

    # VAR_DECL ::= ID_LIST ':' TYPE ';'
    # En este caso ya conocemos el tipo, asi que volcamos la lista temporal de ids (id_list) a la tabla de variables del scope actual.
    def p_var_decl(self, p):
        """var_decl : id_list COLON type SEMICOL"""
        base, is_array, size = p[3]
        scope = self.current_scope()
        tabla = self.func_dir[scope]["var_table"]
        for name in p[1]:
            if name in tabla:
                self.add_sem_error(
                    "variable '%s' ya declarada en el scope '%s'" % (name, scope),
                    p.lineno(2),
                )
            elif scope == self.global_scope and name in self.func_dir:
                # En el scope global, una variable no puede llamarse igual que
                # una funcion ya declarada ni que el propio programa (los
                # nombres globales son unicos).
                quien = "el programa" if name == self.global_scope else "una funcion"
                self.add_sem_error(
                    "el nombre '%s' ya esta usado por %s" % (name, quien),
                    p.lineno(2),
                )
            else:
                tabla[name] = {
                    "tipo": base,
                    "scope": scope,
                    "is_param": False,
                    "is_array": is_array,
                    "size": size,
                }

    # ID_LIST ::= ID_LIST ',' id | id
    # La lista temporal sostiene los ids hasta conocer su tipo.
    def p_id_list_multiple(self, p):
        """id_list : id_list COMMA ID"""
        if p[3] in p[1]:
            self.add_sem_error(
                "id '%s' repetido en la misma declaracion" % p[3], p.lineno(3)
            )
            p[0] = p[1]
        else:
            p[0] = p[1] + [p[3]]

    def p_id_list_single(self, p):
        """id_list : ID"""
        p[0] = [p[1]]

    # TYPE ::= keyword_int | keyword_float | keyword_string | TYPE '[' const_int ']'
    # El valor del nonterminal type es una tupla (base, is_array, size).
    def p_type_int(self, p):
        """type : KEYWORD_INT"""
        p[0] = ("int", False, None)

    def p_type_float(self, p):
        """type : KEYWORD_FLOAT"""
        p[0] = ("float", False, None)

    def p_type_string(self, p):
        """type : KEYWORD_STRING"""
        p[0] = ("string", False, None)

    def p_type_array(self, p):
        """type : type LBRACKET CONST_INT RBRACKET"""
        base = p[1][0]
        size = int(p[3])
        # El tamano de un arreglo debe ser un entero positivo (>= 1).
        if size <= 0:
            self.add_sem_error(
                "el tamano de un arreglo debe ser mayor que 0, se obtuvo %d" % size,
                p.lineno(2),
            )
            size = 1  # valor de recuperacion para no romper el resto del analisis
        p[0] = (base, True, size)

    # FUNCIONES

    # FUNCS ::= keyword_void id '(' PARAMS_OPT ')' '[' VARS_OPT BODY ']' ';'
    #        |  TYPE id '(' PARAMS_OPT ')' '[' VARS_OPT BODY ']' ';'

    # Marcadores:
    #   np_func_decl  : registra la funcion y abre su scope
    #   np_func_params: fija el numero de parametros
    #   np_func_body  : guarda el quad de inicio del cuerpo (para GOSUB)
    #   np_func_end   : emite endfun y cierra el scope
    def p_funcs_void(self, p):
        """funcs : KEYWORD_VOID ID np_func_decl LPAREN params_opt RPAREN np_func_params LBRACKET vars_opt np_func_body body RBRACKET np_func_end SEMICOL"""
        pass

    def p_funcs_typed(self, p):
        """funcs : type ID np_func_decl LPAREN params_opt RPAREN np_func_params LBRACKET vars_opt np_func_body body RBRACKET np_func_end SEMICOL"""
        pass

    def p_np_func_decl(self, p):
        """np_func_decl : empty"""
        name = p[-1] # el ID de la funcion
        rt = p[-2] # tipo de retorno: 'void' (token) o tupla type
        return_type = rt[0] if isinstance(rt, tuple) else rt
        gtabla = self.func_dir.get(self.global_scope, {}).get("var_table", {})
        if name in self.func_dir:
            self.add_sem_error("funcion '%s' ya declarada" % name, self._cur_line())
        elif name in gtabla:
            self.add_sem_error(
                "el nombre '%s' ya esta usado por una variable global" % name,
                self._cur_line()
            )
        # Se registra (o re-registra) el scope de la funcion aunque haya
        # colision, para que su cuerpo se siga analizando sin romper las
        # busquedas posteriores en el directorio de funciones.
        if name not in self.func_dir:
            self.func_dir[name] = {
                "return_type": return_type,
                "params": [],
                "n_params": 0,
                "var_table": {},
                "start_quad": None,
                "has_return": False, # se marca True al ver un return con valor
            }
        self.scope_stack.append(name)

    def p_np_func_params(self, p):
        """np_func_params : empty"""
        scope = self.current_scope()
        self.func_dir[scope]["n_params"] = len(self.func_dir[scope]["params"])

    def p_np_func_body(self, p):
        """np_func_body : empty"""
        scope = self.current_scope()
        self.func_dir[scope]["start_quad"] = self.quad_count + 1

    def p_np_func_end(self, p):
        """np_func_end : empty"""
        scope = self.current_scope()
        rec = self.func_dir.get(scope, {})
        if rec.get("return_type", "void") != "void" and not rec.get("has_return"):
            self.add_sem_error(
                "la funcion '%s' es de tipo %s y debe tener un 'return' con valor"
                % (scope, rec.get("return_type")),
                self._cur_line()
            )
        self.emit("endfun", "-", "-", "-")
        # se cierra el scope de la funcion (se vuelve al global)
        self.scope_stack.pop()

    # PARAMS_OPT ::= PARAM_LIST | epsilon
    def p_params_opt_list(self, p):
        """params_opt : param_list"""
        pass

    def p_params_opt_empty(self, p):
        """params_opt : empty"""
        pass

    # PARAM_LIST ::= PARAM_LIST ',' PARAM | PARAM
    def p_param_list_multiple(self, p):
        """param_list : param_list COMMA param"""
        pass

    def p_param_list_single(self, p):
        """param_list : param"""
        pass

    # PARAM ::= id ':' TYPE
    # Se guarda cada parametro en la tabla de variables de la funcion actual,
    # marcandolo como is_param, y se anexa su tipo a la lista ordenada de
    # parametros (para validar las llamadas).
    def p_param(self, p):
        """param : ID COLON type"""
        name = p[1]
        base, is_array, size = p[3]
        scope = self.current_scope()
        tabla = self.func_dir[scope]["var_table"]
        if is_array:
            self.add_sem_error(
                "los parametros de tipo arreglo no estan soportados ('%s' en '%s')"
                % (name, scope),
                p.lineno(1),
            )
        if name in tabla:
            self.add_sem_error(
                "parametro '%s' repetido en la funcion '%s'" % (name, scope),
                p.lineno(1),
            )
        else:
            tabla[name] = {
                "tipo": base,
                "scope": scope,
                "is_param": True,
                "is_array": is_array,
                "size": size,
            }
            self.func_dir[scope]["params"].append(base)


    # STATEMENTS

    # STATEMENT ::= ASSIGN | CONDITION | CYCLE | PRINT | F_CALL_STMT
    #            |  SWITCH_STMT | BREAK_STMT | CONTINUE_STMT | RETURN_STMT
    def p_statement_assign(self, p):
        """statement : assign"""
        pass

    def p_statement_condition(self, p):
        """statement : condition"""
        pass

    def p_statement_cycle(self, p):
        """statement : cycle"""
        pass

    def p_statement_print(self, p):
        """statement : print_stmt"""
        pass

    def p_statement_f_call(self, p):
        """statement : f_call_stmt"""
        pass

    def p_statement_switch(self, p):
        """statement : switch_stmt"""
        pass

    def p_statement_break(self, p):
        """statement : break_stmt"""
        pass

    def p_statement_continue(self, p):
        """statement : continue_stmt"""
        pass

    def p_statement_return(self, p):
        """statement : return_stmt"""
        pass

    def p_statement_inc_dec(self, p):
        """statement : inc_dec_stmt"""
        pass

    # INC_DEC_STMT ::= INC_DEC_NO_SEMI ';'
    def p_inc_dec_stmt(self, p):
        """inc_dec_stmt : inc_dec_no_semi SEMICOL"""
        pass

    # BREAK_STMT ::= keyword_break ';'
    # break genera un goto pendiente que se rellena al cerrar el ciclo/switch.
    def p_break_stmt(self, p):
        """break_stmt : KEYWORD_BREAK SEMICOL"""
        if self.break_stack:
            # Rompe la estructura mas cercana (ciclo o switch), que es el tope de la pila
            kind, ctx = self.break_stack[-1]
            q = self.emit("goto", "-", "-", None)
            if kind == "loop":
                ctx["breaks"].append(q)
            else:  # switch
                ctx["end_jumps"].append(q)
        else:
            self.add_sem_error("break fuera de un ciclo o switch", p.lineno(1))

    # CONTINUE_STMT ::= keyword_continue ';'
    def p_continue_stmt(self, p):
        """continue_stmt : KEYWORD_CONTINUE SEMICOL"""
        if self.loop_stack:
            q = self.emit("goto", "-", "-", None)
            self.loop_stack[-1]["continues"].append(q)
        else:
            self.add_sem_error("continue fuera de un ciclo", p.lineno(1))

    # RETURN_STMT ::= keyword_return ';' | keyword_return EXPRESION ';'
    def p_return_stmt_void(self, p):
        """return_stmt : KEYWORD_RETURN SEMICOL"""
        scope = self.current_scope()
        if scope == self.global_scope:
            self.add_sem_error(
                "no se puede usar 'return' en el programa principal; "
                "'return' solo es valido dentro de una funcion", p.lineno(1)
            )
            return
        rt = self.func_dir.get(scope, {}).get("return_type", "void")
        if rt != "void":
            self.add_sem_error(
                "la funcion '%s' debe retornar un valor de tipo %s" % (scope, rt),
                p.lineno(1),
            )
        self.emit("return", "-", "-", "-")

    def p_return_stmt_value(self, p):
        """return_stmt : KEYWORD_RETURN expresion SEMICOL"""
        val = self.pop_operand()
        scope = self.current_scope()
        if scope == self.global_scope:
            self.add_sem_error(
                "no se puede usar 'return' en el programa principal; "
                "'return' solo es valido dentro de una funcion", p.lineno(1)
            )
            return
        rt = self.func_dir.get(scope, {}).get("return_type", "void")
        if rt == "void":
            self.add_sem_error(
                "una funcion void no puede retornar un valor", p.lineno(1)
            )
        elif val[1] == "arreglo":
            self.add_sem_error(
                "no se puede retornar '%s': es un arreglo sin indexar" % val[0],
                p.lineno(1),
            )
        elif compatible_asignacion(rt, val[1]) == "error":
            self.add_sem_error(
                "el tipo de retorno (%s) no coincide con el declarado (%s)"
                % (val[1], rt),
                p.lineno(1),
            )
        self.emit("return", val[0], "-", "-")
        if scope in self.func_dir:
            self.func_dir[scope]["has_return"] = True

    # ASSIGN Y FUNCTION CALL

    # ASSIGN ::= ASSIGN_TARGET ASSIGN_OP EXPRESION ';'
    def p_assign(self, p):
        """assign : assign_target assign_op expresion SEMICOL"""
        self.do_assign(p[1], p[2], p.lineno(4) if len(p) > 4 else 0)

    # ASSIGN_TARGET ::= id | id '[' EXPRESION ']'
    # El target se devuelve como descriptor en p[0].
    def p_assign_target_id(self, p):
        """assign_target : ID"""
        rec = self.lookup_var(p[1])
        if rec is None:
            self.add_sem_error("variable '%s' no declarada" % p[1], p.lineno(1))
            p[0] = {"name": p[1], "type": "error", "is_array": False}
        else:
            # is_array=True aqui indica que se intenta asignar al arreglo completo (sin indice); do_assign lo rechaza.
            p[0] = {"name": p[1], "type": rec["tipo"], "is_array": rec["is_array"]}

    def p_assign_target_array(self, p):
        """assign_target : ID LBRACKET expresion RBRACKET"""
        rec = self.lookup_var(p[1])
        idx = self.pop_operand()  # resultado del indice
        if rec is None:
            self.add_sem_error("variable '%s' no declarada" % p[1], p.lineno(1))
            p[0] = {"name": p[1], "type": "error", "is_array": False}
            return
        if not rec["is_array"]:
            self.add_sem_error("'%s' no es un arreglo" % p[1], p.lineno(1))
        if idx[1] != "int":
            self.add_sem_error(
                "el indice de '%s' debe ser int, no %s" % (p[1], idx[1]),
                p.lineno(1),
            )
        # cuadruplo de verificacion de limites (0 .. size-1)
        if rec["size"] is not None:
            self.emit("ver", idx[0], 0, rec["size"] - 1)
        p[0] = {
            "name": "%s[%s]" % (p[1], idx[0]),
            "type": rec["tipo"],
            "is_array": False,
        }

    # ASSIGN_OP ::= '=' | '+=' | '-=' | '*=' | '/=' | '%='
    # Cada alternativa devuelve el operador como string en p[0].
    def p_assign_op_assign(self, p):
        """assign_op : OP_ASSIGN"""
        p[0] = "="

    def p_assign_op_plus(self, p):
        """assign_op : OP_PLUS_ASSIGN"""
        p[0] = "+="

    def p_assign_op_minus(self, p):
        """assign_op : OP_MINUS_ASSIGN"""
        p[0] = "-="

    def p_assign_op_mult(self, p):
        """assign_op : OP_MULT_ASSIGN"""
        p[0] = "*="

    def p_assign_op_div(self, p):
        """assign_op : OP_DIV_ASSIGN"""
        p[0] = "/="

    def p_assign_op_mod(self, p):
        """assign_op : OP_MOD_ASSIGN"""
        p[0] = "%="

    # F_CALL_STMT ::= id '(' ARGS_OPT ')' ';'
    # np_call_start abre el contexto de llamada (emite ERA y valida que la
    # funcion exista). Al terminar (RPAREN) se valida el numero de argumentos
    # y se emite GOSUB.
    def p_f_call_stmt(self, p):
        """f_call_stmt : ID LPAREN np_call_start args_opt RPAREN SEMICOL"""
        self.end_call(p[1], expr_context=False, lineno=p.lineno(1))

    # F_CALL_EXPR ::= id '(' ARGS_OPT ')'
    def p_f_call_expr(self, p):
        """f_call_expr : ID LPAREN np_call_start args_opt RPAREN"""
        self.end_call(p[1], expr_context=True, lineno=p.lineno(1))

    # Marcador: al ver 'id (' se prepara el contexto de la llamada.
    def p_np_call_start(self, p):
        """np_call_start : empty"""
        name = p[-2]  # el ID de la funcion (id LPAREN np_call_start)
        if name not in self.func_dir or name == self.global_scope:
            self.add_sem_error("funcion '%s' no declarada" % name, self._cur_line())
            self.call_stack.append({"name": name, "idx": 0, "params": [], "valid": False})
        else:
            # Quad de encabezado de la llamada: indica a la maquina virtual a
            # cual funcion pertenecen los siguientes 'param'. Se emite antes de
            # los parametros y guarda el nombre de la funcion a invocar.
            self.emit("sub", name, "-", "-")
            self.call_stack.append({
                "name": name,
                "idx": 0,
                "params": self.func_dir[name]["params"],
                "valid": True,
            })

    # ARGS_OPT ::= ARG_LIST | epsilon
    def p_args_opt_list(self, p):
        """args_opt : arg_list"""
        pass

    def p_args_opt_empty(self, p):
        """args_opt : empty"""
        pass

    # ARG_LIST ::= ARG_LIST ',' EXPRESION | EXPRESION
    # Cada argumento se valida contra el parametro correspondiente y se emite
    # un cuadruplo PARAM en orden.
    def p_arg_list_multiple(self, p):
        """arg_list : arg_list COMMA expresion"""
        self.process_argument()

    def p_arg_list_single(self, p):
        """arg_list : expresion"""
        self.process_argument()

    # CONDITION Y CYCLE

    # CONDITION ::= keyword_if '(' EXPRESION ')' BODY ELSE_OPT ';'
    # np_gotof: tras la condicion, valida bool y emite gotof pendiente.
    # else_opt maneja el relleno del gotof (con o sin else).
    def p_condition(self, p):
        """condition : KEYWORD_IF LPAREN expresion RPAREN np_gotof body else_opt SEMICOL"""
        pass

    # Marcador punto 1: la expresion de control debe ser bool.
    def p_np_gotof(self, p):
        """np_gotof : empty"""
        cond = self.pop_operand()
        if cond[1] != "bool":
            self.add_sem_error(
                "la condicion del if debe ser bool, no %s" % cond[1], self._cur_line()
            )
        q = self.emit("gotof", cond[0], "-", None)
        self.jump_stack.append(q)

    # ELSE_OPT: sin else (np_no_else) o con else (np_goto ... np_end_else)
    def p_else_opt_empty(self, p):
        """else_opt : np_no_else"""
        pass

    def p_else_opt_else(self, p):
        """else_opt : np_goto KEYWORD_ELSE body np_end_else"""
        pass

    # Marcador punto 2 (sin else): rellena el gotof al siguiente cuadruplo.
    def p_np_no_else(self, p):
        """np_no_else : empty"""
        pending = self.jump_stack.pop()
        self.backpatch(pending, self.quad_count + 1)

    # Marcador punto 3 (al entrar al else): emite goto al fin, y rellena el
    # gotof del if para que salte al inicio del else.
    def p_np_goto(self, p):
        """np_goto : empty"""
        q = self.emit("goto", "-", "-", None)
        false_jump = self.jump_stack.pop()
        self.backpatch(false_jump, self.quad_count + 1)
        self.jump_stack.append(q)

    # Marcador punto 4 (tras el else): rellena el goto del fin del if.
    def p_np_end_else(self, p):
        """np_end_else : empty"""
        pending = self.jump_stack.pop()
        self.backpatch(pending, self.quad_count + 1)

    # CYCLE ::= DO_WHILE | WHILE_LOOP | FOR_LOOP
    def p_cycle_do_while(self, p):
        """cycle : do_while"""
        pass

    def p_cycle_while(self, p):
        """cycle : while_loop"""
        pass

    def p_cycle_for(self, p):
        """cycle : for_loop"""
        pass

    # DO_WHILE ::= keyword_do BODY keyword_while '(' EXPRESION ')' ';'
    # El cuerpo se ejecuta y al final se evalua la condicion: si es verdadera
    # se regresa al inicio (gotot).
    def p_do_while(self, p):
        """do_while : KEYWORD_DO np_do_start body KEYWORD_WHILE LPAREN np_do_cond expresion RPAREN np_do_end SEMICOL"""
        pass

    # Marca donde inicia la evaluacion de la condicion del do-while. Es el
    # destino correcto de un 'continue' (debe saltar a evaluar la condicion,
    # no saltarse su evaluacion).
    def p_np_do_cond(self, p):
        """np_do_cond : empty"""
        self.loop_stack[-1]["continue_target"] = self.quad_count + 1

    def p_np_do_start(self, p):
        """np_do_start : empty"""
        start = self.quad_count + 1
        self.jump_stack.append(start)
        ctx = {"breaks": [], "continues": [], "continue_target": start}
        self.loop_stack.append(ctx)
        self.break_stack.append(("loop", ctx))

    def p_np_do_end(self, p):
        """np_do_end : empty"""
        cond = self.pop_operand()
        if cond[1] != "bool":
            self.add_sem_error(
                "la condicion del do-while debe ser bool, no %s" % cond[1], self._cur_line()
            )
        start = self.jump_stack.pop()
        self.emit("gotot", cond[0], "-", start)
        ctx = self.loop_stack.pop()
        self.break_stack.pop()
        for b in ctx["breaks"]:
            self.backpatch(b, self.quad_count + 1)
        for c in ctx["continues"]:
            # continue en do-while salta a la RE-EVALUACION de la condicion
            # (no al gotot, que leeria un valor de condicion ya calculado)
            self.backpatch(c, ctx["continue_target"])

    # WHILE_LOOP ::= keyword_while '(' EXPRESION ')' BODY ';'
    def p_while_loop(self, p):
        """while_loop : KEYWORD_WHILE LPAREN np_while_start expresion RPAREN np_while_gotof body np_while_end SEMICOL"""
        pass

    # Marca el punto de retorno (inicio de la evaluacion de la condicion).
    def p_np_while_start(self, p):
        """np_while_start : empty"""
        ret = self.quad_count + 1
        self.jump_stack.append(ret)
        ctx = {"breaks": [], "continues": [], "continue_target": ret}
        self.loop_stack.append(ctx)
        self.break_stack.append(("loop", ctx))

    # Tras evaluar la condicion: valida bool y emite gotof pendiente.
    def p_np_while_gotof(self, p):
        """np_while_gotof : empty"""
        cond = self.pop_operand()
        if cond[1] != "bool":
            self.add_sem_error(
                "la condicion del while debe ser bool, no %s" % cond[1], self._cur_line()
            )
        q = self.emit("gotof", cond[0], "-", None)
        self.jump_stack.append(q)

    # Cierra el while: goto de regreso y relleno del gotof de salida.
    def p_np_while_end(self, p):
        """np_while_end : empty"""
        gotof_q = self.jump_stack.pop()
        ret = self.jump_stack.pop()
        self.emit("goto", "-", "-", ret)
        self.backpatch(gotof_q, self.quad_count + 1)
        ctx = self.loop_stack.pop()
        self.break_stack.pop()
        for b in ctx["breaks"]:
            self.backpatch(b, self.quad_count + 1)
        for c in ctx["continues"]:
            self.backpatch(c, ret)

    # FOR_LOOP ::= keyword_for '(' FOR_INIT ';' EXPRESION ';' FOR_UPDATE ')' BODY ';'
    # Traduccion clasica: init; L1: cond; gotof END; goto BODY; UPD: update;
    # goto L1; BODY: body; goto UPD; END:
    def p_for_loop(self, p):
        """for_loop : KEYWORD_FOR LPAREN for_init SEMICOL np_for_cond expresion SEMICOL np_for_gotof for_update np_for_after_update RPAREN body np_for_end SEMICOL"""
        pass

    def p_np_for_cond(self, p):
        """np_for_cond : empty"""
        cond_start = self.quad_count + 1
        self.jump_stack.append(cond_start)

    def p_np_for_gotof(self, p):
        """np_for_gotof : empty"""
        cond = self.pop_operand()
        if cond[1] != "bool":
            self.add_sem_error(
                "la condicion del for debe ser bool, no %s" % cond[1], self._cur_line()
            )
        gotof_q = self.emit("gotof", cond[0], "-", None) # a END
        goto_body_q = self.emit("goto", "-", "-", None) # a BODY
        update_start = self.quad_count + 1 # inicio del update
        self.jump_stack.append(gotof_q)
        self.jump_stack.append(goto_body_q)
        self.jump_stack.append(update_start)
        ctx = {
            "breaks": [], "continues": [], "continue_target": update_start
        }
        self.loop_stack.append(ctx)
        self.break_stack.append(("loop", ctx))

    def p_np_for_after_update(self, p):
        """np_for_after_update : empty"""
        update_start = self.jump_stack.pop()
        goto_body_q = self.jump_stack.pop()
        gotof_q = self.jump_stack.pop()
        cond_start = self.jump_stack.pop()
        self.emit("goto", "-", "-", cond_start) # fin del update -> condicion
        self.backpatch(goto_body_q, self.quad_count + 1) # body empieza aqui
        # se re-apilan los datos que faltan para cerrar
        self.jump_stack.append(gotof_q)
        self.jump_stack.append(update_start)

    def p_np_for_end(self, p):
        """np_for_end : empty"""
        update_start = self.jump_stack.pop()
        gotof_q = self.jump_stack.pop()
        self.emit("goto", "-", "-", update_start) # fin del body -> update
        self.backpatch(gotof_q, self.quad_count + 1) # END
        ctx = self.loop_stack.pop()
        self.break_stack.pop()
        for b in ctx["breaks"]:
            self.backpatch(b, self.quad_count + 1)
        for c in ctx["continues"]:
            self.backpatch(c, update_start)

    # FOR_INIT ::= ASSIGN_NO_SEMI | epsilon
    def p_for_init_assign(self, p):
        """for_init : assign_no_semi"""
        pass

    def p_for_init_empty(self, p):
        """for_init : empty"""
        pass

    # FOR_UPDATE ::= ASSIGN_NO_SEMI | INC_DEC_NO_SEMI | epsilon
    def p_for_update_assign(self, p):
        """for_update : assign_no_semi"""
        pass

    def p_for_update_inc_dec(self, p):
        """for_update : inc_dec_no_semi"""
        pass

    def p_for_update_empty(self, p):
        """for_update : empty"""
        pass

    # ASSIGN_NO_SEMI ::= ASSIGN_TARGET ASSIGN_OP EXPRESION
    def p_assign_no_semi(self, p):
        """assign_no_semi : assign_target assign_op expresion"""
        self.do_assign(p[1], p[2], 0)

    # INC_DEC_NO_SEMI ::= id '++' | id '--'
    # Se traduce i++ como i = i + 1 (e i-- como i = i - 1).
    def p_inc_dec_no_semi_inc(self, p):
        """inc_dec_no_semi : ID OP_INCREMENT"""
        self.gen_inc_dec(p[1], "+", p.lineno(1))

    def p_inc_dec_no_semi_dec(self, p):
        """inc_dec_no_semi : ID OP_DECREMENT"""
        self.gen_inc_dec(p[1], "-", p.lineno(1))

    # SWITCH_STMT ::= keyword_switch '(' EXPRESION ')' '{' CASE_LIST DEFAULT_OPT '}' ';'
    # Cada case compara el valor del switch contra su constante; si coincide
    # ejecuta su cuerpo y salta al final (auto-break). Si ningun case coincide, cae al default.
    def p_switch_stmt(self, p):
        """switch_stmt : KEYWORD_SWITCH LPAREN expresion RPAREN np_switch_start LBRACE case_list default_opt RBRACE np_switch_end SEMICOL"""
        pass

    def p_np_switch_start(self, p):
        """np_switch_start : empty"""
        val = self.pop_operand()
        ctx = {"val": val, "end_jumps": [], "seen": []}
        self.switch_stack.append(ctx)
        self.break_stack.append(("switch", ctx))

    def p_np_switch_end(self, p):
        """np_switch_end : empty"""
        sw = self.switch_stack.pop()
        self.break_stack.pop()
        for ej in sw["end_jumps"]:
            self.backpatch(ej, self.quad_count + 1)

    # CASE_LIST ::= CASE_LIST CASE_CLAUSE | CASE_CLAUSE
    def p_case_list_multiple(self, p):
        """case_list : case_list case_clause"""
        pass

    def p_case_list_single(self, p):
        """case_list : case_clause"""
        pass

    # CASE_CLAUSE ::= keyword_case CTE ':' STMT_LIST
    # np_case_test: compara switch_val == cte, gotof si no coincide.
    # np_case_end: goto al final del switch y relleno del gotof.
    def p_case_clause(self, p):
        """case_clause : KEYWORD_CASE cte np_case_test COLON stmt_list np_case_end"""
        pass

    def p_np_case_test(self, p):
        """np_case_test : empty"""
        cval = self.pop_operand()  # la constante del case (apilada por cte)
        sw = self.switch_stack[-1]
        if cval[1] != sw["val"][1]:
            self.add_sem_error(
                "el tipo del case (%s) debe ser igual al del switch (%s)"
                % (cval[1], sw["val"][1]),
                self._cur_line()
            )
        # un mismo valor de case no puede repetirse (los demas serian inalcanzables)
        if cval[0] in sw["seen"]:
            self.add_sem_error("valor de case duplicado: %s" % cval[0], self._cur_line())
        else:
            sw["seen"].append(cval[0])
        temp = self.new_temp()
        self.emit("==", sw["val"][0], cval[0], temp, "bool")
        gq = self.emit("gotof", temp, "-", None)
        self.jump_stack.append(gq)

    def p_np_case_end(self, p):
        """np_case_end : empty"""
        end_q = self.emit("goto", "-", "-", None)
        self.switch_stack[-1]["end_jumps"].append(end_q)
        skip = self.jump_stack.pop()
        self.backpatch(skip, self.quad_count + 1)

    # DEFAULT_OPT ::= keyword_default ':' STMT_LIST | epsilon
    def p_default_opt_default(self, p):
        """default_opt : KEYWORD_DEFAULT COLON stmt_list"""
        pass

    def p_default_opt_empty(self, p):
        """default_opt : empty"""
        pass

    # PRINT

    # PRINT ::= keyword_print '(' PRINT_LIST ')' ';'
    # Cada statement print finaliza implicitamente con un quad extra que
    # imprime un salto de linea, como se vio en clase. Un solo newline por sentencia print, sin importar cuantas expresiones contenga la lista.
    def p_print_stmt(self, p):
        """print_stmt : KEYWORD_PRINT LPAREN print_list RPAREN SEMICOL"""
        self.emit("print", "newline", "-", "-")

    # PRINT_LIST ::= PRINT_LIST ',' EXPRESION | EXPRESION
    # Cada expresion del print genera un cuadruplo print con su resultado.
    def p_print_list_multiple(self, p):
        """print_list : print_list COMMA expresion"""
        val = self.pop_operand()
        self.check_not_array(val, p.lineno(2))
        self.emit("print", val[0], "-", "-")

    def p_print_list_single(self, p):
        """print_list : expresion"""
        val = self.pop_operand()
        self.check_not_array(val)
        self.emit("print", val[0], "-", "-")

    # EXPRESIONES (por niveles de precedencia, de menor a mayor)
    # En cada produccion binaria se genera el cuadruplo en la reduccion, lo cual respeta la precedencia automaticamente  (el parser LR reduce primero las capas mas internas). 
    # No se necesita una pila de operadores, basta la pila de operandos

    # EXPRESION ::= EXPRESION_TERNARY
    def p_expresion(self, p):
        """expresion : expresion_ternary"""
        pass

    # NIVEL 1: TERNARIO
    # EXPRESION_TERNARY ::= EXPRESION_LOGIC_OR '?' EXPRESION ':' EXPRESION | EXPRESION_LOGIC_OR
    def p_expresion_ternary_op(self, p):
        """expresion_ternary : expresion_logic_or OP_TERNARY np_tern_q expresion np_tern_c COLON expresion np_tern_e"""
        pass

    def p_expresion_ternary_pass(self, p):
        """expresion_ternary : expresion_logic_or"""
        pass

    # Marcador tras '?': la condicion debe ser bool, gotof a la rama falsa.
    def p_np_tern_q(self, p):
        """np_tern_q : empty"""
        cond = self.pop_operand()
        if cond[1] != "bool":
            self.add_sem_error(
                "la condicion del ternario debe ser bool, no %s" % cond[1], self._cur_line()
            )
        gq = self.emit("gotof", cond[0], "-", None)
        self.jump_stack.append(gq)

    # Marcador tras la rama verdadera (antes de ':'): guarda el valor en un
    # temporal resultado y emite goto a la salida del ternario.
    def p_np_tern_c(self, p):
        """np_tern_c : empty"""
        tval = self.pop_operand()
        res_temp = self.new_temp()
        self.emit("=", tval[0], "-", res_temp, tval[1])
        goto_q = self.emit("goto", "-", "-", None)
        gotof_q = self.jump_stack.pop()
        self.backpatch(gotof_q, self.quad_count + 1)  # inicio de la rama falsa
        self.jump_stack.append(goto_q)
        self.tern_stack.append({"res": res_temp, "ttype": tval[1]})

    # Marcador tras la rama falsa: asigna su valor al mismo temporal, rellena
    # el goto de salida y empuja el resultado del ternario.
    def p_np_tern_e(self, p):
        """np_tern_e : empty"""
        fval = self.pop_operand()
        t = self.tern_stack.pop()
        self.emit("=", fval[0], "-", t["res"], fval[1])
        goto_q = self.jump_stack.pop()
        self.backpatch(goto_q, self.quad_count + 1)
        rtype = unifica_tipos(t["ttype"], fval[1])
        if rtype == "error":
            self.add_sem_error(
                "las ramas del ternario tienen tipos incompatibles (%s y %s)"
                % (t["ttype"], fval[1]),
                self._cur_line()
            )
            rtype = t["ttype"]
        self.operand_stack.append((t["res"], rtype))

    # NIVEL 2: OR LOGICO
    # EXPRESION_LOGIC_OR ::= EXPRESION_LOGIC_OR '||' EXPRESION_LOGIC_AND
    #                 | EXPRESION_LOGIC_AND
    def p_expresion_logic_or_op(self, p):
        """expresion_logic_or : expresion_logic_or OP_LOGICAL_OR expresion_logic_and"""
        self.gen_binary("||", p.lineno(2))

    def p_expresion_logic_or_pass(self, p):
        """expresion_logic_or : expresion_logic_and"""
        pass

    # NIVEL 3: AND LOGICO
    # EXPRESION_LOGIC_AND ::= EXPRESION_LOGIC_AND '&&' EXPRESION_EQUALITY
    #                  | EXPRESION_EQUALITY
    def p_expresion_logic_and_op(self, p):
        """expresion_logic_and : expresion_logic_and OP_LOGICAL_AND expresion_equality"""
        self.gen_binary("&&", p.lineno(2))

    def p_expresion_logic_and_pass(self, p):
        """expresion_logic_and : expresion_equality"""
        pass

    # NIVEL 4: IGUALDAD
    # EXPRESION_EQUALITY ::= EXPRESION_EQUALITY '==' EXPRESION_RELATIONAL
    #                 | EXPRESION_EQUALITY '!=' EXPRESION_RELATIONAL
    #                | EXPRESION_RELATIONAL
    def p_expresion_equality_eq(self, p):
        """expresion_equality : expresion_equality OP_EQUAL expresion_relational"""
        self.gen_binary("==", p.lineno(2))

    def p_expresion_equality_neq(self, p):
        """expresion_equality : expresion_equality OP_NOT_EQUAL expresion_relational"""
        self.gen_binary("!=", p.lineno(2))

    def p_expresion_equality_pass(self, p):
        """expresion_equality : expresion_relational"""
        pass

    # NIVEL 5: RELACIONALES
    # EXPRESION_RELATIONAL ::= EXPRESION_RELATIONAL '<' EXP
    #                   | EXPRESION_RELATIONAL '>' EXP
    #                   | EXPRESION_RELATIONAL '<=' EXP
    #                   | EXPRESION_RELATIONAL '>=' EXP
    #                   | EXP
    def p_expresion_relational_lt(self, p):
        """expresion_relational : expresion_relational OP_LESS_THAN exp"""
        self.gen_binary("<", p.lineno(2))

    def p_expresion_relational_gt(self, p):
        """expresion_relational : expresion_relational OP_GREATER_THAN exp"""
        self.gen_binary(">", p.lineno(2))

    def p_expresion_relational_le(self, p):
        """expresion_relational : expresion_relational OP_LESS_EQUAL exp"""
        self.gen_binary("<=", p.lineno(2))

    def p_expresion_relational_ge(self, p):
        """expresion_relational : expresion_relational OP_GREATER_EQUAL exp"""
        self.gen_binary(">=", p.lineno(2))

    def p_expresion_relational_pass(self, p):
        """expresion_relational : exp"""
        pass

    # NIVEL 6: SUMA/RESTA
    # EXP ::= EXP '+' TERMINO | EXP '-' TERMINO | TERMINO
    def p_exp_plus(self, p):
        """exp : exp OP_PLUS termino"""
        self.gen_binary("+", p.lineno(2))

    def p_exp_minus(self, p):
        """exp : exp OP_MINUS termino"""
        self.gen_binary("-", p.lineno(2))

    def p_exp_pass(self, p):
        """exp : termino"""
        pass

    # NIVEL 7: MULT/DIV/MOD
    # TERMINO ::= TERMINO '*' FACTOR_PREFIX
    #      | TERMINO '/' FACTOR_PREFIX
    #      | TERMINO '%' FACTOR_PREFIX
    #      | FACTOR_PREFIX
    def p_termino_mult(self, p):
        """termino : termino OP_MULT factor_prefix"""
        self.gen_binary("*", p.lineno(2))

    def p_termino_div(self, p):
        """termino : termino OP_DIV factor_prefix"""
        self.gen_binary("/", p.lineno(2))

    def p_termino_mod(self, p):
        """termino : termino OP_MOD factor_prefix"""
        self.gen_binary("%", p.lineno(2))

    def p_termino_pass(self, p):
        """termino : factor_prefix"""
        pass

    # NIVEL 8: PREFIJOS (unarios)
    # FACTOR_PREFIX ::= '!' FACTOR_PREFIX
    #            | '-' FACTOR_PREFIX
    #            | '+' FACTOR_PREFIX
    #            | FACTOR_SUFFIX
    def p_factor_prefix_not(self, p):
        """factor_prefix : OP_LOGICAL_NOT factor_prefix"""
        self.gen_unary("!")

    def p_factor_prefix_minus(self, p):
        """factor_prefix : OP_MINUS factor_prefix"""
        self.gen_unary("-")

    def p_factor_prefix_plus(self, p):
        """factor_prefix : OP_PLUS factor_prefix"""
        self.gen_unary("+")

    def p_factor_prefix_pass(self, p):
        """factor_prefix : factor_suffix"""
        pass

    # NIVEL 9: SUFIJOS
    # FACTOR_SUFFIX ::= FACTOR_SUFFIX '++'
    #            | FACTOR_SUFFIX '--'
    #            | FACTOR_SUFFIX '[' EXPRESION ']'
    #            | FACTOR
    def p_factor_suffix_inc(self, p):
        """factor_suffix : factor_suffix OP_INCREMENT"""
        self.gen_suffix_inc_dec("+")

    def p_factor_suffix_dec(self, p):
        """factor_suffix : factor_suffix OP_DECREMENT"""
        self.gen_suffix_inc_dec("-")

    def p_factor_suffix_index(self, p):
        """factor_suffix : factor_suffix LBRACKET expresion RBRACKET"""
        self.gen_array_access(p.lineno(2))

    def p_factor_suffix_pass(self, p):
        """factor_suffix : factor"""
        pass

    # NIVEL 10: FACTOR (parentesis o primario)
    # FACTOR ::= '(' EXPRESION ')'
    #      | FACTOR_PRIMARY
    def p_factor_paren(self, p):
        """factor : LPAREN expresion RPAREN"""
        pass

    def p_factor_primary(self, p):
        """factor : factor_primary"""
        pass

    # NIVEL 11: PRIMARIO
    # FACTOR_PRIMARY ::= id | CTE | F_CALL_EXPR
    def p_factor_primary_id(self, p):
        """factor_primary : ID"""
        rec = self.lookup_var(p[1])
        if rec is None:
            self.add_sem_error("variable '%s' no declarada" % p[1], p.lineno(1))
            self.operand_stack.append(("error", "error"))
        elif rec["is_array"]:
            self.operand_stack.append((p[1], "arreglo"))
        else:
            self.operand_stack.append((p[1], rec["tipo"]))

    def p_factor_primary_cte(self, p):
        """factor_primary : cte"""
        pass # la constante ya fue apilada en la regla cte

    def p_factor_primary_call(self, p):
        """factor_primary : f_call_expr"""
        pass # el valor de retorno ya fue apilado en end_call

    # CTE ::= const_int | const_float | const_str
    # Las constantes se apilan directamente en la pila de operandos.
    def p_cte_int(self, p):
        """cte : CONST_INT"""
        self.operand_stack.append((p[1], "int"))

    def p_cte_float(self, p):
        """cte : CONST_FLOAT"""
        self.operand_stack.append((p[1], "float"))

    def p_cte_str(self, p):
        """cte : CONST_STR"""
        self.operand_stack.append((p[1], "string"))

    # PRODUCCION EPSILON (vacio)
    def p_empty(self, p):
        """empty :"""
        pass

    # MANEJO DE ERRORES SINTACTICOS
    def p_statement_error(self, p):
        """statement : error SEMICOL"""
        self.parser.errok()

    def p_print_stmt_error(self, p):
        """print_stmt : KEYWORD_PRINT LPAREN error RPAREN SEMICOL"""
        self.parser.errok()

    def p_error(self, p):
        if p is None:
            self.add_error(
                "SYNTAX_ERROR", "EOF", 0, 0,
                "fin de archivo inesperado, falta cerrar alguna estructura",
            )
            return
        self.add_error(
            "SYNTAX_ERROR", p.value, p.lineno, p.lexpos,
            "token inesperado de tipo %s" % p.type,
        )
        # Si se acumulan demasiados errores de sintaxis , se aborta el parseo en vez de quedar atrapado consumiendo memoria.
        if len(self.errors) > 100:
            raise SyntaxError("demasiados errores de sintaxis; parseo abortado")
        # Descartar el token infractor para GARANTIZAR avance. Sin esto, en
        # ciertos estados PLY vuelve a ofrecer el mismo token y la recuperacion
        # entra en un bucle infinito (p. ej. un parentesis sin cerrar en un if).
        # errok() reactiva el parser para que continue con el siguiente token.
        self.parser.errok()

    # HELPERS DE GENERACION DE CODIGO Y SEMANTICA

    # Devuelve el scope actual (top de la pila de scopes)
    def current_scope(self):
        return self.scope_stack[-1] if self.scope_stack else self.global_scope

    # Genera un nuevo temporal t1, t2, etc (contados desde 1)
    def new_temp(self):
        self.temp_count += 1
        return "t" + str(self.temp_count)

    # Agrega un cuadruplo a la lista. Los cuadruplos se numeran desde 1.
    # res_type es el tipo del resultado.
    def emit(self, op, argl, argr, res, res_type="-"):
        self.quad_count += 1
        self.quads.append({
            "num": self.quad_count,
            "op": op,
            "argl": argl,
            "argr": argr,
            "res": res,
            "res_type": res_type,
        })
        return self.quad_count

    # Rellena el destino (res) de un cuadruplo pendiente
    def backpatch(self, quad_num, target):
        self.quads[quad_num - 1]["res"] = target

    # Pop seguro de la pila de operandos
    def pop_operand(self):
        if self.operand_stack:
            return self.operand_stack.pop()
        return ("error", "error")

    # Busca una variable en el scope actual y luego en el global
    def lookup_var(self, name):
        scope = self.current_scope()
        tabla = self.func_dir.get(scope, {}).get("var_table", {})
        if name in tabla:
            return tabla[name]
        gtabla = self.func_dir.get(self.global_scope, {}).get("var_table", {})
        if name in gtabla:
            return gtabla[name]
        return None

    # Registra un error semantico
    def add_sem_error(self, message, lineno=0):
        self.sem_errors.append({"message": message, "lineno": lineno})

    # Linea aproximada para errores en reglas marcador (np_*) y helpers, que no
    # tienen un token propio: se usa la del ultimo token leido por el lexer.
    def _cur_line(self):
        return getattr(self.tokenizer, "last_token_line", 0)

    # Indica si un nombre ya esta tomado por una funcion o por el programa.
    # Sirve para evitar colisiones entre los nombres de funciones y los de
    # variables/parametros, que viven en estructuras separadas (func_dir vs.
    # las tablas de variables) y de otro modo no se compararian entre si.
    def name_is_function(self, name):
        return name in self.func_dir

    # Verifica que un operando no sea un arreglo sin indexar. Devuelve True si
    # esta bien, o False (y reporta el error) si es un arreglo usado como
    # escalar. Checa tanto para print, return y argumentos.
    def check_not_array(self, operand, lineno=0):
        if operand[1] == "arreglo":
            self.add_sem_error(
                "'%s' es un arreglo sin indexar (usa %s[indice])"
                % (operand[0], operand[0]), lineno
            )
            return False
        return True

    # Genera el cuadruplo de una operacion binaria consultando el cubo
    def gen_binary(self, op, lineno=0):
        right = self.pop_operand()
        left = self.pop_operand()
        if left[1] == "error" or right[1] == "error":
            self.operand_stack.append(("error", "error"))
            return
        # Un arreglo sin indexar no puede participar en una operacion.
        for operand in (left, right):
            if operand[1] == "arreglo":
                self.add_sem_error(
                    "'%s' es un arreglo y debe indexarse (%s[indice])"
                    % (operand[0], operand[0]), lineno
                )
                self.operand_stack.append(("error", "error"))
                return
        res = self.cubo.resultado(left[1], right[1], op)
        if res == "error":
            self.add_sem_error(
                "operacion invalida: %s %s %s" % (left[1], op, right[1]), lineno
            )
            self.operand_stack.append(("error", "error"))
        else:
            temp = self.new_temp()
            self.emit(op, left[0], right[0], temp, res)
            self.operand_stack.append((temp, res))

    # Genera el cuadruplo de un operador unario
    def gen_unary(self, op):
        val = self.pop_operand()
        if val[1] == "error":
            self.operand_stack.append(("error", "error"))
            return
        # el + unario no genera codigo, solo valida que sea numerico
        if op == "+":
            if val[1] not in ("int", "float"):
                self.add_sem_error("'+' unario requiere numerico, no %s" % val[1], self._cur_line())
            self.operand_stack.append(val)
            return
        res = resultado_unario(op, val[1])
        if res == "error":
            self.add_sem_error("operador unario '%s' invalido para %s" % (op, val[1]), self._cur_line())
            self.operand_stack.append(("error", "error"))
        else:
            temp = self.new_temp()
            quad_op = "neg" if op == "-" else "!"
            self.emit(quad_op, val[0], "-", temp, res)
            self.operand_stack.append((temp, res))

    # Acceso a un arreglo dentro de una expresion: a[i]
    def gen_array_access(self, lineno=0):
        idx = self.pop_operand()
        base = self.pop_operand()
        if base[1] == "error":
            self.operand_stack.append(("error", "error"))
            return
        rec = self.lookup_var(base[0])
        
        if rec is None or not rec["is_array"]:
            self.add_sem_error(
                "no se puede indexar '%s': no es un arreglo" % str(base[0]),
                lineno,
            )
            self.operand_stack.append(("error", "error"))
            return
        if idx[1] != "int":
            self.add_sem_error(
                "el indice de '%s' debe ser int" % base[0], lineno
            )
        if rec["size"] is not None:
            self.emit("ver", idx[0], 0, rec["size"] - 1)
        temp = self.new_temp()
        self.emit("[]", base[0], idx[0], temp, rec["tipo"])
        self.operand_stack.append((temp, rec["tipo"]))

    # i++ / i-- como sufijo dentro de una expresion (devuelve el valor actual)
    def gen_suffix_inc_dec(self, op):
        val = self.pop_operand()
        rec = self.lookup_var(val[0])
        if rec is None:
            self.add_sem_error("'%s' no es asignable" % val[0], self._cur_line())
            self.operand_stack.append(("error", "error"))
            return
        if rec["tipo"] not in ("int", "float"):
            self.add_sem_error("'%s' debe ser numerico para ++/--" % val[0], self._cur_line())
        # se devuelve el valor actual y luego se actualiza la variable
        self.emit(op, val[0], 1, val[0], rec["tipo"])
        self.operand_stack.append((val[0], rec["tipo"]))

    # i++ / i-- como statement o como for_update
    def gen_inc_dec(self, name, op, lineno):
        rec = self.lookup_var(name)
        if rec is None:
            self.add_sem_error("variable '%s' no declarada" % name, lineno)
            return
        if rec["tipo"] not in ("int", "float"):
            self.add_sem_error("'%s' debe ser numerico para ++/--" % name, lineno)
        self.emit(op, name, 1, name, rec["tipo"])

    # Logica compartida de asignacion (usada por assign y assign_no_semi)
    def do_assign(self, target, op, lineno):
        rhs = self.pop_operand()
        tname, ttype = target["name"], target["type"]
        if ttype == "error" or rhs[1] == "error":
            return
        # No se puede asignar al arreglo completo; debe indexarse.
        if target.get("is_array"):
            self.add_sem_error(
                "'%s' es un arreglo y debe indexarse para asignar (%s[indice])"
                % (tname, tname), lineno
            )
            return
        if op == "=":
            res = compatible_asignacion(ttype, rhs[1])
            if res == "error":
                self.add_sem_error(
                    "no se puede asignar %s a %s ('%s')" % (rhs[1], ttype, tname),
                    lineno,
                )
            self.emit("=", rhs[0], "-", tname, ttype)
        else:
            base_op = op[0]  # '+','-','*','/','%'
            rtype = self.cubo.resultado(ttype, rhs[1], base_op)
            if rtype == "error":
                self.add_sem_error(
                    "operacion invalida en '%s': %s %s %s"
                    % (tname, ttype, base_op, rhs[1]), lineno
                )
                return
            temp = self.new_temp()
            self.emit(base_op, tname, rhs[0], temp, rtype)
            if compatible_asignacion(ttype, rtype) == "error":
                self.add_sem_error(
                    "no se puede asignar %s a %s ('%s')" % (rtype, ttype, tname),
                    lineno,
                )
            self.emit("=", temp, "-", tname, ttype)

    # Valida un argumento de llamada contra su parametro y emite PARAM
    def process_argument(self):
        arg = self.pop_operand()
        if not self.call_stack:
            return
        call = self.call_stack[-1]
        idx = call["idx"]
        if call["valid"]:
            if idx < len(call["params"]):
                expected = call["params"][idx]
                if arg[1] == "arreglo":
                    self.add_sem_error(
                        "argumento %d de '%s': '%s' es un arreglo sin indexar"
                        % (idx + 1, call["name"], arg[0]),
                        self._cur_line()
                    )
                elif compatible_asignacion(expected, arg[1]) == "error":
                    self.add_sem_error(
                        "argumento %d de '%s': se esperaba %s y se recibio %s"
                        % (idx + 1, call["name"], expected, arg[1]),
                        self._cur_line()
                    )
                self.emit("param", arg[0], "-", "-")
            else:
                self.emit("param", arg[0], "-", "-")
        call["idx"] += 1

    # Cierra una llamada: valida el numero de argumentos y emite GOSUB.
    # Si es en contexto de expresion, empuja el valor de retorno.
    def end_call(self, name, expr_context, lineno):
        call = self.call_stack.pop() if self.call_stack else None
        if call is None or not call["valid"]:
            if expr_context:
                self.operand_stack.append(("error", "error"))
            return
        n_expected = len(call["params"])
        if call["idx"] != n_expected:
            self.add_sem_error(
                "la funcion '%s' espera %d argumento(s) y recibio %d"
                % (name, n_expected, call["idx"]), lineno
            )
        start = self.func_dir[name]["start_quad"]
        self.emit("gosub", name, "-", start)
        rt = self.func_dir[name]["return_type"]
        if expr_context:
            if rt == "void":
                self.add_sem_error(
                    "la funcion void '%s' no puede usarse en una expresion" % name,
                    lineno,
                )
                self.operand_stack.append(("error", "error"))
            else:
                temp = self.new_temp()
                self.emit("=", name + "_ret", "-", temp, rt)
                self.operand_stack.append((temp, rt))

    # FUNCIONES AUXILIARES 
    # Reinicia el estado del parser y de las estructuras semanticas
    def clean(self):
        self.errors = []
        self.sem_errors = []
        self.func_dir = {}
        self.global_scope = None
        self.scope_stack = []
        self.operand_stack = []
        self.jump_stack = []
        self.call_stack = []
        self.loop_stack = []
        self.switch_stack = []
        self.break_stack = []
        self.tern_stack = []
        self.quads = []
        self.temp_count = 0
        self.quad_count = 0

    # Calcula la columna 1-indexed usando la posicion absoluta lexpos
    def find_column(self, lexpos):
        last_newline = self.source_code.rfind("\n", 0, lexpos)
        return lexpos - last_newline

    # Agrega un error sintactico a la lista de errores
    def add_error(self, error_type, value, lineno, lexpos, message=""):
        self.errors.append({
            "type": error_type,
            "value": value,
            "lineno": lineno,
            "lexpos": lexpos,
            "column": self.find_column(lexpos) if lexpos else 0,
            "message": message,
        })

    # CONSTRUCTOR
    def __init__(self, tokenizer=None):
        self.tokenizer = tokenizer if tokenizer else Tokenizer(keep_comments=False)
        self.source_code = ""
        self.cubo = CuboSemantico()
        self.clean()
        self.parser = yacc.yacc(
            module=self,
            debug=False, # False: no genera parser.out al ejecutar
            write_tables=False,
            errorlog=yacc.NullLogger(),
        )

    # METODO PRINCIPAL DE PARSEO
    def parse(self, input_string):
        self.clean()
        self.source_code = input_string
        try:
            self.parser.parse(input_string, lexer=self.tokenizer, tracking=True)
        except Exception as e:
            self.add_error("PARSER_EXCEPTION", str(e), 0, 0,
                           "excepcion no controlada del parser")
        return (len(self.errors) == 0 and len(self.sem_errors) == 0
                and len(self.tokenizer.errors) == 0)


# IMPRESION DE RESULTADOS

# Imprime los errores lexicos, sintacticos y semanticos
def print_all_errors(parser):
    if parser.tokenizer.errors:
        print("\nErrores lexicos:")
        for err in parser.tokenizer.errors:
            print("  %-32s linea %s" % (err["type"], err["lineno"]))
    if parser.errors:
        print("\nErrores sintacticos:")
        for err in parser.errors:
            print("  linea %-3s %s" % (err["lineno"], err.get("message", "")))
    if parser.sem_errors:
        print("\nErrores semanticos:")
        for err in parser.sem_errors:
            ln = err["lineno"]
            loc = ("linea %s: " % ln) if ln else ""
            print("  %s%s" % (loc, err["message"]))


# Construye las lineas de la representacion intermedia (cuadruplos) con la columna extra de tipo de resultado. Numeros desde 1.
def format_quads(parser):
    lines = []
    lines.append("Representacion intermedia (cuadruplos):")
    # Ancho fijo de cada columna de argumento. Los valores mas largos
    # (p. ej. cadenas de texto) se truncan para que las columnas no se
    # descuadren.
    col = 18

    # Acorta un valor para que quepa en el ancho de columna, agregando
    # "..." al final si se trunca.
    def fit(value):
        if value is None:
            return "-"
        text = str(value).replace("\n", "\\n")
        if len(text) <= col:
            return text
        return text[: col - 3] + "..."

    header = "%-5s %-8s %-*s %-*s %-*s %-8s" % (
        "num", "op", col, "argL", col, "argR", col, "res", "tipo")
    lines.append(header)
    for q in parser.quads:
        rtype = q["res_type"] if q["res_type"] else "-"
        lines.append("%-5d %-8s %-*s %-*s %-*s %-8s"
                     % (q["num"], q["op"], col, fit(q["argl"]),
                        col, fit(q["argr"]), col, fit(q["res"]), rtype))
    return "\n".join(lines)


# Construye las lineas de la tabla de simbolos (directorio de funciones + tablas de variables por scope).
def format_symbol_table(parser):
    lines = []
    lines.append("Tabla de simbolos:")
    for name, info in parser.func_dir.items():
        kind = "programa (global)" if name == parser.global_scope else "funcion"
        lines.append("")
        lines.append("%s: %s | retorno: %s | params: %d"
                     % (kind, name, info["return_type"], info["n_params"]))
        tabla = info["var_table"]
        if not tabla:
            lines.append("  (sin variables)")
            continue
        lines.append("  %-14s %-8s %-7s %-8s %-6s %s"
                    % ("nombre", "tipo", "param", "arreglo", "size", "scope"))
        for vname, v in tabla.items():
            lines.append("  %-14s %-8s %-7s %-8s %-6s %s"
                        % (vname, v["tipo"],
                            "si" if v["is_param"] else "no",
                            "si" if v["is_array"] else "no",
                            v["size"] if v["size"] is not None else "-",
                            v["scope"]))
    return "\n".join(lines)


# =====================================================================
# TERCERA ENTREGA: MEMORIA VIRTUAL Y MAQUINA VIRTUAL
#
# Esta seccion NO modifica el parser ni las acciones semanticas de la
# entrega anterior. Trabaja como un "post-pase" (un asignador de memoria
# / enlazador) que recibe los cuadruplos ya generados con NOMBRES y los
# traduce a DIRECCIONES de memoria virtual segun la convencion de clase.
#
# Convencion de regiones (inicio de cada region):
#   globales:   int 1000   float 2000   str 3000   void 4000
#   retorno:    5000  (un unico registro de retorno, compartido)
#   locales:    int 7000   float 8000   str 9000
#   temporales: int 12000  float 13000  bool 14000
#   constantes: int 17000  float 18000  str 19000
#
# Globales y constantes viven en UNA sola memoria compartida durante toda
# la ejecucion. Las locales y temporales de cada FUNCION viven en un
# activation record (frame) que se crea y destruye en cada llamada (lo
# maneja la maquina virtual). El programa principal (main) no tiene
# locales propias y usa la memoria global tambien para sus temporales.
# =====================================================================

import re

REGION_BASE = {
    "global_int": 1000, "global_float": 2000, "global_str": 3000, "global_void": 4000,
    "local_int": 7000, "local_float": 8000, "local_str": 9000,
    "temp_int": 12000, "temp_float": 13000, "temp_bool": 14000, "temp_str": 15000,
    "cte_int": 17000, "cte_float": 18000, "cte_str": 19000,
}
RET_REG = 5000          # registro unico de retorno (memoria global)
REGION_SPAN = 1000      # cada region tiene 1000 direcciones antes de la siguiente
MAIN_OWNER = "__main__"  # dueno ficticio de los temporales del main

_TEMP_RE = re.compile(r"^t\d+$")
_INT_RE = re.compile(r"^\d+$")
_FLOAT_RE = re.compile(r"^\d+\.\d+$")
_ARRAY_TARGET_RE = re.compile(r"^(\w+)\[(.+)\]$")


def _temp_region(tipo):
    # bool -> temp_bool, float -> temp_float, string -> temp_str, int -> temp_int
    if tipo == "bool":
        return "temp_bool"
    if tipo == "float":
        return "temp_float"
    if tipo == "string":
        return "temp_str"
    return "temp_int"


def _suf(tipo):
    # El tipo 'string' usa el sufijo de region 'str'
    return "str" if tipo == "string" else tipo


class MemoryAllocator:
    """Asigna direcciones de memoria virtual a variables, temporales y
    constantes, y traduce la lista de cuadruplos de nombres a direcciones."""

    def __init__(self, parser):
        self.parser = parser
        self.gscope = parser.global_scope
        self.quads = parser.quads

        # Mapas de direcciones
        self.var_addr = {}     # (scope, nombre) -> direccion
        self.temp_addr = {}    # (dueno, nombre_temp) -> direccion
        self.const_addr = {}   # (valor_literal, tipo) -> direccion
        self.const_list = []   # [(direccion, valor_python, tipo)] en orden de aparicion

        # Contadores de la memoria global (globales + temporales del main + cconstantes)
        self.global_counts = {k: 0 for k in REGION_BASE}

        # Info por funcion: nombre -> dict con start_quad, return_type, params, contadores
        self.func_info = {}

        # Rango de cuadruplos que pertenece a cada funcion / al main
        self.ranges = {}       # dueno -> (primer_quad, ultimo_quad)
        self.main_start = None
        self.errors = []       # errores de asignacion de memoria (p. ej. desborde de region)

    # ---- utilidades ----------------------------------------------------

    def _owner_of(self, quad_num):
        # Devuelve a que funcion (o al main) pertenece un cuadruplo
        for owner, (lo, hi) in self.ranges.items():
            if owner != MAIN_OWNER and lo <= quad_num <= hi:
                return owner
        return MAIN_OWNER

    def _lookup_var_scope(self, name, owner):
        # Resuelve un nombre de variable a su scope (local de la funcion o global)
        if owner != MAIN_OWNER:
            tabla = self.parser.func_dir.get(owner, {}).get("var_table", {})
            if name in tabla:
                return owner
        gtabla = self.parser.func_dir.get(self.gscope, {}).get("var_table", {})
        if name in gtabla:
            return self.gscope
        return None

    # ---- pase principal ------------------------------------------------

    def allocate(self):
        self._compute_ranges()
        self._alloc_globals()
        self._alloc_function_locals()
        self._alloc_temps()
        self._alloc_constants()

    def _compute_ranges(self):
        # main empieza en el destino del gotomain (cuadruplo 1)
        if self.quads:
            self.main_start = int(self.quads[0]["res"])
        # localizar el endfun de cada funcion
        for name, info in self.parser.func_dir.items():
            if name == self.gscope:
                continue
            start = info["start_quad"]
            if start is None:
                continue
            end = start
            for q in self.quads:
                if q["num"] >= start and q["op"] == "endfun":
                    end = q["num"]
                    break
            self.ranges[name] = (start, end)
            self.func_info[name] = {
                "start_quad": start,
                "return_type": info["return_type"],
                "n_params": info["n_params"],
                "param_addr": [],
                "counts": {"local_int": 0, "local_float": 0, "local_str": 0,
                           "temp_int": 0, "temp_float": 0, "temp_bool": 0, "temp_str": 0},
            }

    def _alloc_globals(self):
        tabla = self.parser.func_dir.get(self.gscope, {}).get("var_table", {})
        for name, v in tabla.items():
            region = "global_" + _suf(v["tipo"])
            cells = v["size"] if v["is_array"] and v["size"] else 1
            if self.global_counts[region] + cells > REGION_SPAN:
                self.errors.append(
                    "la variable/arreglo global '%s' (%d celda(s)) excede la "
                    "capacidad de la region %s (max %d celdas)"
                    % (name, cells, region, REGION_SPAN))
            addr = REGION_BASE[region] + self.global_counts[region]
            self.var_addr[(self.gscope, name)] = addr
            self.global_counts[region] += cells

    def _alloc_function_locals(self):
        for fname, fi in self.func_info.items():
            tabla = self.parser.func_dir[fname]["var_table"]
            local_counter = {"int": 0, "float": 0, "str": 0}
            # primero los parametros, en orden de declaracion (para la VM)
            for name, v in tabla.items():
                if not v["is_param"]:
                    continue
                region = "local_" + _suf(v["tipo"])
                addr = REGION_BASE[region] + local_counter[_suf(v["tipo"])]
                self.var_addr[(fname, name)] = addr
                self.func_info[fname]["param_addr"].append(addr)
                local_counter[_suf(v["tipo"])] += 1
                fi["counts"][region] += 1
            # luego las variables locales no-parametro
            for name, v in tabla.items():
                if v["is_param"]:
                    continue
                region = "local_" + _suf(v["tipo"])
                cells = v["size"] if v["is_array"] and v["size"] else 1
                if local_counter[_suf(v["tipo"])] + cells > REGION_SPAN:
                    self.errors.append(
                        "la variable/arreglo local '%s' de la funcion '%s' "
                        "(%d celda(s)) excede la capacidad de la region %s (max %d)"
                        % (name, fname, cells, region, REGION_SPAN))
                addr = REGION_BASE[region] + local_counter[_suf(v["tipo"])]
                self.var_addr[(fname, name)] = addr
                local_counter[_suf(v["tipo"])] += cells
                fi["counts"][region] += cells

    def _alloc_temps(self):
        # contadores de temporales por dueno
        counters = {}   # dueno -> {region: count}
        for q in self.quads:
            res = q["res"]
            if not isinstance(res, str) or not _TEMP_RE.match(res):
                continue
            tipo = q.get("res_type", "-")
            if tipo not in ("int", "float", "bool", "string"):
                continue
            owner = self._owner_of(q["num"])
            if (owner, res) in self.temp_addr:
                continue
            region = _temp_region(tipo)
            counters.setdefault(owner, {"temp_int": 0, "temp_float": 0,
                                        "temp_bool": 0, "temp_str": 0})
            addr = REGION_BASE[region] + counters[owner][region]
            counters[owner][region] += 1
            self.temp_addr[(owner, res)] = addr
            if owner == MAIN_OWNER:
                self.global_counts[region] += 1
            else:
                self.func_info[owner]["counts"][region] += 1

    def _alloc_constants(self):
        for q in self.quads:
            owner = self._owner_of(q["num"])
            for field in self._data_fields(q):
                self._maybe_add_constant(field)

    def _data_fields(self, q):
        # Devuelve los campos del cuadruplo que son OPERANDOS DE DATOS
        # (pueden ser constantes). Ignora numeros de cuadruplo, limites de
        # arreglo, nombres de funcion, etc.
        op = q["op"]
        L, R, S = q["argl"], q["argr"], q["res"]
        out = []
        if op in ("+", "-", "*", "/", "%",
                  "<", ">", "<=", ">=", "==", "!=", "&&", "||"):
            out += [L, R, S]
        elif op in ("neg", "!"):
            out += [L, S]
        elif op == "=":
            m = _ARRAY_TARGET_RE.match(str(S)) if isinstance(S, str) else None
            if m:                      # escritura a arreglo: a[idx]
                out += [L, m.group(2), m.group(1)]
            elif isinstance(L, str) and L.endswith("_ret"):
                out += [S]
            else:
                out += [L, S]
        elif op in ("gotof", "gotot"):
            out += [L]
        elif op == "print":
            if L != "newline":
                out += [L]
        elif op == "ver":
            out += [L]                 # argR/res son limites literales, no constantes
        elif op == "[]":
            out += [L, R, S]
        elif op == "param":
            out += [L]
        elif op == "return":
            if L != "-":
                out += [L]
        # gotomain, goto, sub, gosub, endfun, end: sin operandos de datos
        return out

    def _maybe_add_constant(self, value):
        if value is None:
            return
        s = str(value)
        if s == "-" or s == "newline":
            return
        if _TEMP_RE.match(s):
            return
        if s.endswith("_ret"):
            return
        # variable conocida?  (en cualquier scope)
        for scope_key in self.var_addr:
            if scope_key[1] == s:
                return
        # literal entero / flotante / cadena
        if _INT_RE.match(s):
            tipo, py = "int", int(s)
        elif _FLOAT_RE.match(s):
            tipo, py = "float", float(s)
        elif s.startswith('"') and s.endswith('"'):
            tipo, py = "str", s[1:-1]
        else:
            return
        key = (s, tipo)
        if key in self.const_addr:
            return
        region = "cte_" + tipo
        addr = REGION_BASE[region] + self.global_counts[region]
        self.global_counts[region] += 1
        self.const_addr[key] = addr
        self.const_list.append((addr, py, tipo))

    # ---- resolucion de un operando a direccion -------------------------

    def resolve(self, value, owner):
        if value is None:
            return -1
        s = str(value)
        if s == "-":
            return -1
        if s.endswith("_ret"):
            return RET_REG
        # variable
        sc = self._lookup_var_scope(s, owner)
        if sc is not None:
            return self.var_addr[(sc, s)]
        # temporal
        if _TEMP_RE.match(s):
            if (owner, s) in self.temp_addr:
                return self.temp_addr[(owner, s)]
            if (MAIN_OWNER, s) in self.temp_addr:
                return self.temp_addr[(MAIN_OWNER, s)]
        # constante
        if _INT_RE.match(s):
            return self.const_addr[(s, "int")]
        if _FLOAT_RE.match(s):
            return self.const_addr[(s, "float")]
        if s.startswith('"') and s.endswith('"'):
            return self.const_addr[(s, "str")]
        # no deberia ocurrir
        raise ValueError("operando no resuelto: %r (en %s)" % (value, owner))

    # ---- traduccion de cuadruplos a direcciones ------------------------

    def translate_quads(self):
        out = []
        for q in self.quads:
            owner = self._owner_of(q["num"])
            op = q["op"]
            L, R, S = q["argl"], q["argr"], q["res"]

            def D(v):
                return self.resolve(v, owner)

            def K(v):
                # mantener valor crudo (numero de cuadruplo o limite)
                if v is None or v == "-":
                    return -1
                return int(v)

            if op == "gotomain" or op == "goto":
                nq = [op, -1, -1, K(S)]
            elif op in ("gotof", "gotot"):
                nq = [op, D(L), -1, K(S)]
            elif op == "=":
                m = _ARRAY_TARGET_RE.match(str(S)) if isinstance(S, str) else None
                if m:   # a[idx] = L  -> escritura a arreglo
                    nq = ["=[]", D(L), D(m.group(2)), D(m.group(1))]
                elif isinstance(L, str) and L.endswith("_ret"):
                    nq = ["=", RET_REG, -1, D(S)]
                else:
                    nq = ["=", D(L), -1, D(S)]
            elif op in ("+", "-", "*", "/", "%",
                        "<", ">", "<=", ">=", "==", "!=", "&&", "||"):
                nq = [op, D(L), D(R), D(S)]
            elif op in ("neg", "!"):
                nq = [op, D(L), -1, D(S)]
            elif op == "print":
                if L == "newline":
                    nq = ["newline", -1, -1, -1]
                else:
                    nq = ["print", D(L), -1, -1]
            elif op == "ver":
                nq = ["ver", D(L), K(R), K(S)]
            elif op == "[]":
                nq = ["[]", D(L), D(R), D(S)]
            elif op == "sub":
                nq = ["sub", L, -1, -1]            # L = nombre de funcion
            elif op == "param":
                nq = ["param", D(L), -1, -1]
            elif op == "gosub":
                nq = ["gosub", L, -1, K(S)]        # L = nombre, S = start_quad
            elif op == "return":
                nq = ["return", (D(L) if L != "-" else -1), -1, -1]
            elif op in ("endfun", "end"):
                nq = [op, -1, -1, -1]
            else:
                nq = [op, D(L), D(R), D(S)]
            out.append([q["num"]] + nq)
        return out

    # ---- impresion de la representacion intermedia para la VM ----------

    def format_object_ir(self):
        """Forma final de la RI, apegada a la convencion vista en clase:
        - cons:  <valor>  <direccion>   (el tipo se infiere por el rango)
        - memo:  <region> <cantidad>    (solo regiones con cantidad > 0)
        - func:  un bloque por funcion (extension para funciones/arreglos)
        - quads: <num> <op> <argL> <argR> <res>   (solo direcciones)
        Es el archivo que la maquina virtual carga y ejecuta."""
        lines = []

        # Seccion de constantes:  valor  direccion  (valor primero, como en clase)
        lines.append("cons")
        for addr, py, tipo in self.const_list:
            if tipo == "str":
                esc = str(py).replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")
                val = '"' + esc + '"'
            else:
                val = str(py)
            lines.append("%s\t%d" % (val, addr))
        lines.append("")

        # Seccion de memoria global (globales + temporales del main + constantes).
        # Solo se listan las regiones con cantidad > 0; lo ausente vale 0.
        lines.append("memo")
        for region in ("global_int", "global_float", "global_str", "global_void",
                       "temp_int", "temp_float", "temp_bool", "temp_str",
                       "cte_int", "cte_float", "cte_str"):
            if self.global_counts[region] > 0:
                lines.append("%s %d" % (region, self.global_counts[region]))
        lines.append("")

        # Un bloque por funcion con la memoria que requiere su frame.
        # (solo se imprime si hay funciones; lo ausente significa "no hay")
        if self.func_info:
            lines.append("func")
            for fname, fi in self.func_info.items():
                lines.append("%s\t%d\t%s" % (fname, fi["start_quad"], fi["return_type"]))
                lines.append("params %d" % fi["n_params"])
                if fi["param_addr"]:
                    lines.append("param_addr " + " ".join(str(a) for a in fi["param_addr"]))
                for region in ("local_int", "local_float", "local_str",
                               "temp_int", "temp_float", "temp_bool", "temp_str"):
                    if fi["counts"][region] > 0:
                        lines.append("%s %d" % (region, fi["counts"][region]))
                lines.append("end")
            lines.append("")

        # Cuadruplos en direcciones
        lines.append("quads")
        for row in self.translate_quads():
            lines.append("\t".join(str(x) for x in row))
        return "\n".join(lines) + "\n"

    # ---- impresion de la RI con nombres + direcciones (debug) ----------

    def format_debug_ir(self):
        """RI con NOMBRES (legible) y, al lado, la direccion de cada
        operando. Util para depurar y para el reporte."""
        lines = []
        lines.append("REPRESENTACION INTERMEDIA (nombres) - solo debug")
        lines.append("")
        col = 16

        def fit(v):
            if v is None:
                return "-"
            t = str(v).replace("\n", "\\n")
            return t if len(t) <= col else t[:col - 3] + "..."

        lines.append("%-4s %-8s %-*s %-*s %-*s %-6s" %
                     ("num", "op", col, "argL", col, "argR", col, "res", "tipo"))
        for q in self.quads:
            rt = q["res_type"] if q["res_type"] else "-"
            lines.append("%-4d %-8s %-*s %-*s %-*s %-6s" %
                         (q["num"], q["op"], col, fit(q["argl"]),
                          col, fit(q["argr"]), col, fit(q["res"]), rt))

        # Mapa de direcciones (constantes, globales, locales, temporales)
        lines.append("")
        lines.append("MAPA DE DIRECCIONES DE MEMORIA VIRTUAL")
        lines.append("")
        lines.append("Constantes:")
        for addr, py, tipo in self.const_list:
            lines.append("  %-8d %-9s %s" % (addr, "cte_" + tipo, py))
        lines.append("")
        lines.append("Variables globales (%s):" % self.gscope)
        for (scope, name), addr in self.var_addr.items():
            if scope == self.gscope:
                lines.append("  %-8d %s" % (addr, name))
        for fname in self.func_info:
            lines.append("")
            lines.append("Locales/parametros de la funcion '%s':" % fname)
            for (scope, name), addr in self.var_addr.items():
                if scope == fname:
                    lines.append("  %-8d %s" % (addr, name))
            lines.append("Temporales de '%s':" % fname)
            for (owner, t), addr in self.temp_addr.items():
                if owner == fname:
                    lines.append("  %-8d %s" % (addr, t))
        lines.append("")
        lines.append("Temporales del main:")
        for (owner, t), addr in self.temp_addr.items():
            if owner == MAIN_OWNER:
                lines.append("  %-8d %s" % (addr, t))
        return "\n".join(lines) + "\n"


# =====================================================================
# PUNTO DE ENTRADA: compila input.txt y ejecuta su RI en la maquina virtual
# =====================================================================

ARCHIVO_FUENTE = "input.txt"
ARCHIVO_RI_NOMBRES = "ri_nombres.txt"   # RI con nombres, para debug
ARCHIVO_RI_MEMORIA = "ri_memoria.txt"   # RI con direcciones, la ejecuta la VM


def main():
    # 1) Leer el unico archivo de entrada (input.txt por defecto, o el nombre
    #    pasado por terminal)
    nombre = sys.argv[1] if len(sys.argv) > 1 else ARCHIVO_FUENTE
    try:
        source = open(nombre).read()
    except FileNotFoundError:
        print("No se encontro el archivo '%s'." % nombre)
        return

    # 2) Compilar: lexico, sintaxis, semantica
    parser = Parser(tokenizer=Tokenizer(keep_comments=False))
    ok = parser.parse(source)

    if not ok:
        print("Errores de compilacion:")
        print_all_errors(parser)
        return  # abortar: no se ejecuta nada

    # 3) Generar la representacion intermedia con memoria virtual
    alloc = MemoryAllocator(parser)
    alloc.allocate()
    if alloc.errors:
        print("Errores de asignacion de memoria:")
        for e in alloc.errors:
            print("  " + e)
        return  # abortar
    obj_ir = alloc.format_object_ir()
    debug_ir = alloc.format_debug_ir()

    # Archivos de salida (sin imprimir mensajes extra en exito)
    with open(ARCHIVO_RI_NOMBRES, "w", encoding="utf-8") as f:
        f.write(debug_ir)
    with open(ARCHIVO_RI_MEMORIA, "w", encoding="utf-8") as f:
        f.write(obj_ir)

    # 4) Ejecutar la RI en la maquina virtual (independiente)
    from quack_vm import VirtualMachine
    vm = VirtualMachine()
    try:
        vm.load(obj_ir)
        vm.run()
    except VMRuntimeError as e:
        print()
        print("Error en tiempo de ejecucion: %s" % e)
        return


# Excepcion de runtime compartida con la VM (se re-exporta desde quack_vm)
try:
    from quack_vm import VMRuntimeError
except Exception:
    class VMRuntimeError(Exception):
        pass


if __name__ == "__main__":
    main()