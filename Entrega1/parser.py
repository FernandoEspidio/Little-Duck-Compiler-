"""
Parser con PLY - Little Duck.

Se implementa el analisis sintactico de Little Duck utilizando ply.yacc (LALR(1)).
Se importa la clase Tokenizer del lexer y se le pasa al parser para que consuma tokens en orden.

La gramatica esta disenada como LR  y sigue los niveles de precedencia descritos en el reporte. 

Manejo de errores de sintaxis:
- La recuperación se implementa principalmente mediante reglas con el token
  especial 'error', como statement : error SEMICOL y
  print_stmt : KEYWORD_PRINT LPAREN error RPAREN SEMICOL.
- La función p_error() registra el token inesperado con su valor, línea y
  posición, y permite que PLY intente sincronizar usando dichas reglas de error.
- Todos los errores se acumulan en self.errors y se reportan al final.
"""

import os
from collections import defaultdict
from contextlib import redirect_stdout

import ply.yacc as yacc

from Entrega1.lexer import Tokenizer, read_source, shorten_value


"""
Se implementa el parser como una clase wrapper sobre ply.yacc, manteniendo la misma estructura que el lexer para reutilizar 
el patron de instancia con sus propios errores y estado, y porque facilita pasar self.tokens a yacc.

Muchas de las reglas se separan en varias funciones para evitar conflictos shift/reduce y reducir la complejidad de cada una, 
aunque eso hace que el parser tenga muchas funciones, pero al final son parte de la misma produccion de la regla
"""
class Parser:
    # Tokens importados del lexer
    tokens = Tokenizer.tokens

    # =====================================================================
    # BODY PRINCIPAL DEL PROGRAMA
    # =====================================================================

    # PROGRAM ::= keyword_program id ';' VARS_OPT FUNCS_LIST keyword_main BODY keyword_end
    def p_program(self, p):
        """program : KEYWORD_PROGRAM ID SEMICOL vars_opt funcs_list KEYWORD_MAIN body KEYWORD_END"""
        pass

    # VARS_OPT ::= VARS | ε
    def p_vars_opt_vars(self, p):
        """vars_opt : vars"""
        pass

    def p_vars_opt_empty(self, p):
        """vars_opt : empty"""
        pass

    # FUNCS_LIST ::= FUNCS_LIST FUNCS | ε
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

    # STMT_LIST ::= STMT_LIST STATEMENT | ε
    def p_stmt_list_multiple(self, p):
        """stmt_list : stmt_list statement"""
        pass

    def p_stmt_list_empty(self, p):
        """stmt_list : empty"""
        pass

    # =====================================================================
    # VARIABLES
    # =====================================================================

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
    def p_var_decl(self, p):
        """var_decl : id_list COLON type SEMICOL"""
        pass

    # ID_LIST ::= ID_LIST ',' id | id
    def p_id_list_multiple(self, p):
        """id_list : id_list COMMA ID"""
        pass

    def p_id_list_single(self, p):
        """id_list : ID"""
        pass

    # TYPE ::= keyword_int | keyword_float | keyword_string | TYPE '[' const_int ']'
    def p_type_int(self, p):
        """type : KEYWORD_INT"""
        pass

    def p_type_float(self, p):
        """type : KEYWORD_FLOAT"""
        pass

    def p_type_string(self, p):
        """type : KEYWORD_STRING"""
        pass

    def p_type_array(self, p):
        """type : type LBRACKET CONST_INT RBRACKET"""
        pass

    # =====================================================================
    # FUNCIONES
    # =====================================================================

    # FUNCS ::= keyword_void id '(' PARAMS_OPT ')' '[' VARS_OPT BODY ']' ';'
    #        |  TYPE id '(' PARAMS_OPT ')' '[' VARS_OPT BODY ']' ';'
    def p_funcs_void(self, p):
        """funcs : KEYWORD_VOID ID LPAREN params_opt RPAREN LBRACKET vars_opt body RBRACKET SEMICOL"""
        pass

    def p_funcs_typed(self, p):
        """funcs : type ID LPAREN params_opt RPAREN LBRACKET vars_opt body RBRACKET SEMICOL"""
        pass

    # PARAMS_OPT ::= PARAM_LIST | ε
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
    def p_param(self, p):
        """param : ID COLON type"""
        pass

    # =====================================================================
    # STATEMENTS (cada alternativa en funcion separada)
    # =====================================================================

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
    # Se reutiliza la produccion INC_DEC_NO_SEMI (que ya se usaba en for_update)
    # y solo se agrega el ';' final para convertirla en un statement valido.
    # Esto permite escribir 'i++;' o 'i--;' como statements sueltos, no solo dentro de un for.
    def p_inc_dec_stmt(self, p):
        """inc_dec_stmt : inc_dec_no_semi SEMICOL"""
        pass

    # BREAK_STMT ::= keyword_break ';'
    def p_break_stmt(self, p):
        """break_stmt : KEYWORD_BREAK SEMICOL"""
        pass

    # CONTINUE_STMT ::= keyword_continue ';'
    def p_continue_stmt(self, p):
        """continue_stmt : KEYWORD_CONTINUE SEMICOL"""
        pass

    # RETURN_STMT ::= keyword_return ';' | keyword_return EXPRESION ';'
    def p_return_stmt_void(self, p):
        """return_stmt : KEYWORD_RETURN SEMICOL"""
        pass

    def p_return_stmt_value(self, p):
        """return_stmt : KEYWORD_RETURN expresion SEMICOL"""
        pass

    # =====================================================================
    # ASSIGN Y FUNCTION CALL
    # =====================================================================

    # ASSIGN ::= ASSIGN_TARGET ASSIGN_OP EXPRESION ';'
    def p_assign(self, p):
        """assign : assign_target assign_op expresion SEMICOL"""
        pass

    # ASSIGN_TARGET ::= id | id '[' EXPRESION ']'
    def p_assign_target_id(self, p):
        """assign_target : ID"""
        pass

    def p_assign_target_array(self, p):
        """assign_target : ID LBRACKET expresion RBRACKET"""
        pass

    # ASSIGN_OP ::= '=' | '+=' | '-=' | '*=' | '/=' | '%='
    def p_assign_op_assign(self, p):
        """assign_op : OP_ASSIGN"""
        pass

    def p_assign_op_plus(self, p):
        """assign_op : OP_PLUS_ASSIGN"""
        pass

    def p_assign_op_minus(self, p):
        """assign_op : OP_MINUS_ASSIGN"""
        pass

    def p_assign_op_mult(self, p):
        """assign_op : OP_MULT_ASSIGN"""
        pass

    def p_assign_op_div(self, p):
        """assign_op : OP_DIV_ASSIGN"""
        pass

    def p_assign_op_mod(self, p):
        """assign_op : OP_MOD_ASSIGN"""
        pass

    # F_CALL_STMT ::= id '(' ARGS_OPT ')' ';'
    def p_f_call_stmt(self, p):
        """f_call_stmt : ID LPAREN args_opt RPAREN SEMICOL"""
        pass

    # F_CALL_EXPR ::= id '(' ARGS_OPT ')'
    def p_f_call_expr(self, p):
        """f_call_expr : ID LPAREN args_opt RPAREN"""
        pass

    # ARGS_OPT ::= ARG_LIST | ε
    def p_args_opt_list(self, p):
        """args_opt : arg_list"""
        pass

    def p_args_opt_empty(self, p):
        """args_opt : empty"""
        pass

    # ARG_LIST ::= ARG_LIST ',' EXPRESION | EXPRESION
    def p_arg_list_multiple(self, p):
        """arg_list : arg_list COMMA expresion"""
        pass

    def p_arg_list_single(self, p):
        """arg_list : expresion"""
        pass

    # =====================================================================
    # CONDITION Y CYCLE
    # =====================================================================

    # CONDITION ::= keyword_if '(' EXPRESION ')' BODY ELSE_OPT ';'
    def p_condition(self, p):
        """condition : KEYWORD_IF LPAREN expresion RPAREN body else_opt SEMICOL"""
        pass

    # ELSE_OPT ::= keyword_else BODY | ε
    def p_else_opt_else(self, p):
        """else_opt : KEYWORD_ELSE body"""
        pass

    def p_else_opt_empty(self, p):
        """else_opt : empty"""
        pass

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
    def p_do_while(self, p):
        """do_while : KEYWORD_DO body KEYWORD_WHILE LPAREN expresion RPAREN SEMICOL"""
        pass

    # WHILE_LOOP ::= keyword_while '(' EXPRESION ')' BODY ';'
    def p_while_loop(self, p):
        """while_loop : KEYWORD_WHILE LPAREN expresion RPAREN body SEMICOL"""
        pass

    # FOR_LOOP ::= keyword_for '(' FOR_INIT ';' EXPRESION ';' FOR_UPDATE ')' BODY ';'
    def p_for_loop(self, p):
        """for_loop : KEYWORD_FOR LPAREN for_init SEMICOL expresion SEMICOL for_update RPAREN body SEMICOL"""
        pass

    # FOR_INIT ::= ASSIGN_NO_SEMI | ε
    def p_for_init_assign(self, p):
        """for_init : assign_no_semi"""
        pass

    def p_for_init_empty(self, p):
        """for_init : empty"""
        pass

    # FOR_UPDATE ::= ASSIGN_NO_SEMI | INC_DEC_NO_SEMI | ε
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
        pass

    # INC_DEC_NO_SEMI ::= id '++' | id '--'
    def p_inc_dec_no_semi_inc(self, p):
        """inc_dec_no_semi : ID OP_INCREMENT"""
        pass

    def p_inc_dec_no_semi_dec(self, p):
        """inc_dec_no_semi : ID OP_DECREMENT"""
        pass

    # SWITCH_STMT ::= keyword_switch '(' EXPRESION ')' '{' CASE_LIST DEFAULT_OPT '}' ';'
    def p_switch_stmt(self, p):
        """switch_stmt : KEYWORD_SWITCH LPAREN expresion RPAREN LBRACE case_list default_opt RBRACE SEMICOL"""
        pass

    # CASE_LIST ::= CASE_LIST CASE_CLAUSE | CASE_CLAUSE
    def p_case_list_multiple(self, p):
        """case_list : case_list case_clause"""
        pass

    def p_case_list_single(self, p):
        """case_list : case_clause"""
        pass

    # CASE_CLAUSE ::= keyword_case CTE ':' STMT_LIST
    def p_case_clause(self, p):
        """case_clause : KEYWORD_CASE cte COLON stmt_list"""
        pass

    # DEFAULT_OPT ::= keyword_default ':' STMT_LIST | ε
    def p_default_opt_default(self, p):
        """default_opt : KEYWORD_DEFAULT COLON stmt_list"""
        pass

    def p_default_opt_empty(self, p):
        """default_opt : empty"""
        pass

    # =====================================================================
    # PRINT
    # =====================================================================

    # PRINT ::= keyword_print '(' PRINT_LIST ')' ';'
    def p_print_stmt(self, p):
        """print_stmt : KEYWORD_PRINT LPAREN print_list RPAREN SEMICOL"""
        pass

    # PRINT_LIST ::= PRINT_LIST ',' EXPRESION | EXPRESION
    # (Se eliminó la alternativa const_str porque ya está cubierta por
    # EXPRESION -> CTE -> const_str, evitando un conflicto que se generaba al ofrecer dos caminos pero es más largo para llegar
    def p_print_list_multiple(self, p):
        """print_list : print_list COMMA expresion"""
        pass

    def p_print_list_single(self, p):
        """print_list : expresion"""
        pass

    # =====================================================================
    # EXPRESIONES (por niveles de precedencia, de menor a mayor)
    # =====================================================================

    # EXPRESION ::= EXPRESION_TERNARY
    def p_expresion(self, p):
        """expresion : expresion_ternary"""
        pass

    # NIVEL 1: TERNARIO
    # EXPRESION_TERNARY ::= EXPRESION_LOGIC_OR '?' EXPRESION ':' EXPRESION
    #                    |  EXPRESION_LOGIC_OR
    def p_expresion_ternary_op(self, p):
        """expresion_ternary : expresion_logic_or OP_TERNARY expresion COLON expresion"""
        pass

    def p_expresion_ternary_pass(self, p):
        """expresion_ternary : expresion_logic_or"""
        pass

    # NIVEL 2: OR LOGICO
    # EXPRESION_LOGIC_OR ::= EXPRESION_LOGIC_OR '||' EXPRESION_LOGIC_AND
    #                    |  EXPRESION_LOGIC_AND
    def p_expresion_logic_or_op(self, p):
        """expresion_logic_or : expresion_logic_or OP_LOGICAL_OR expresion_logic_and"""
        pass

    def p_expresion_logic_or_pass(self, p):
        """expresion_logic_or : expresion_logic_and"""
        pass

    # NIVEL 3: AND LOGICO
    # EXPRESION_LOGIC_AND ::= EXPRESION_LOGIC_AND '&&' EXPRESION_EQUALITY
    #                     |  EXPRESION_EQUALITY
    def p_expresion_logic_and_op(self, p):
        """expresion_logic_and : expresion_logic_and OP_LOGICAL_AND expresion_equality"""
        pass

    def p_expresion_logic_and_pass(self, p):
        """expresion_logic_and : expresion_equality"""
        pass

    # NIVEL 4: IGUALDAD
    # EXPRESION_EQUALITY ::= EXPRESION_EQUALITY '==' EXPRESION_RELATIONAL
    #                    |  EXPRESION_EQUALITY '!=' EXPRESION_RELATIONAL
    #                    |  EXPRESION_RELATIONAL
    def p_expresion_equality_eq(self, p):
        """expresion_equality : expresion_equality OP_EQUAL expresion_relational"""
        pass

    def p_expresion_equality_neq(self, p):
        """expresion_equality : expresion_equality OP_NOT_EQUAL expresion_relational"""
        pass

    def p_expresion_equality_pass(self, p):
        """expresion_equality : expresion_relational"""
        pass

    # NIVEL 5: RELACIONALES
    # EXPRESION_RELATIONAL ::= EXPRESION_RELATIONAL '<'  EXP
    #                       |  EXPRESION_RELATIONAL '>'  EXP
    #                       |  EXPRESION_RELATIONAL '<=' EXP
    #                       |  EXPRESION_RELATIONAL '>=' EXP
    #                       |  EXP
    def p_expresion_relational_lt(self, p):
        """expresion_relational : expresion_relational OP_LESS_THAN exp"""
        pass

    def p_expresion_relational_gt(self, p):
        """expresion_relational : expresion_relational OP_GREATER_THAN exp"""
        pass

    def p_expresion_relational_le(self, p):
        """expresion_relational : expresion_relational OP_LESS_EQUAL exp"""
        pass

    def p_expresion_relational_ge(self, p):
        """expresion_relational : expresion_relational OP_GREATER_EQUAL exp"""
        pass

    def p_expresion_relational_pass(self, p):
        """expresion_relational : exp"""
        pass

    # NIVEL 6: SUMA/RESTA
    # EXP ::= EXP '+' TERMINO | EXP '-' TERMINO | TERMINO
    def p_exp_plus(self, p):
        """exp : exp OP_PLUS termino"""
        pass

    def p_exp_minus(self, p):
        """exp : exp OP_MINUS termino"""
        pass

    def p_exp_pass(self, p):
        """exp : termino"""
        pass

    # NIVEL 7: MULT/DIV/MOD
    # TERMINO ::= TERMINO '*' FACTOR_PREFIX
    #          |  TERMINO '/' FACTOR_PREFIX
    #          |  TERMINO '%' FACTOR_PREFIX
    #          |  FACTOR_PREFIX
    def p_termino_mult(self, p):
        """termino : termino OP_MULT factor_prefix"""
        pass

    def p_termino_div(self, p):
        """termino : termino OP_DIV factor_prefix"""
        pass

    def p_termino_mod(self, p):
        """termino : termino OP_MOD factor_prefix"""
        pass

    def p_termino_pass(self, p):
        """termino : factor_prefix"""
        pass

    # NIVEL 8: PREFIJOS, es decir, las operaciones unarias que van antes del operando
    # FACTOR_PREFIX ::= '!' FACTOR_PREFIX | '-' FACTOR_PREFIX | '+' FACTOR_PREFIX
    #                | FACTOR_SUFFIX
    def p_factor_prefix_not(self, p):
        """factor_prefix : OP_LOGICAL_NOT factor_prefix"""
        pass

    def p_factor_prefix_minus(self, p):
        """factor_prefix : OP_MINUS factor_prefix"""
        pass

    def p_factor_prefix_plus(self, p):
        """factor_prefix : OP_PLUS factor_prefix"""
        pass

    def p_factor_prefix_pass(self, p):
        """factor_prefix : factor_suffix"""
        pass

    # NIVEL 9: SUFIJOS, es decir, las operaciones que van despues del operando
    # FACTOR_SUFFIX ::= FACTOR_SUFFIX '++' | FACTOR_SUFFIX '--'
    #               |  FACTOR_SUFFIX '[' EXPRESION ']'
    #               |  FACTOR
    def p_factor_suffix_inc(self, p):
        """factor_suffix : factor_suffix OP_INCREMENT"""
        pass

    def p_factor_suffix_dec(self, p):
        """factor_suffix : factor_suffix OP_DECREMENT"""
        pass

    def p_factor_suffix_index(self, p):
        """factor_suffix : factor_suffix LBRACKET expresion RBRACKET"""
        pass

    def p_factor_suffix_pass(self, p):
        """factor_suffix : factor"""
        pass

    # NIVEL 10: FACTOR (parentesis o primario)
    # FACTOR ::= '(' EXPRESION ')' | FACTOR_PRIMARY
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
        pass

    def p_factor_primary_cte(self, p):
        """factor_primary : cte"""
        pass

    def p_factor_primary_call(self, p):
        """factor_primary : f_call_expr"""
        pass

    # CTE ::= const_int | const_float | const_str
    def p_cte_int(self, p):
        """cte : CONST_INT"""
        pass

    def p_cte_float(self, p):
        """cte : CONST_FLOAT"""
        pass

    def p_cte_str(self, p):
        """cte : CONST_STR"""
        pass

    # =====================================================================
    # PRODUCCION EPSILON (vacio)
    # =====================================================================
    def p_empty(self, p):
        """empty :"""
        pass

    # =====================================================================
    # MANEJO DE ERRORES SINTACTICOS
    # =====================================================================
    # Se implementa una estrategia hibrida segun la documentacion de PLY seguida de dos puntos en específico:
    #
    # 1- REGLAS DE ERROR: se introduce el token especial 'error' en producciones de re-sincronizacion. Cuando ocurre un 
    #    error sintactico dentro de un statement o body, el parser descarta tokens hasta encontrar el siguiente token de sincronizacion (';' o '}') y
    #    continua el analisis. Esto permite reportar multiples errores en una sola ejecucion en lugar de detenerse en el primero.
    #
    # 2) p_error(): La función p_error() registra el token inesperado con su valor, línea y columna. Después de eso, deja que PLY 
    # intente sincronizar usando las reglas con el token especial 'error'. Si el error ocurre al final del archivo, se reporta EOF.

    # Regla de error a nivel de statement, si algo falla dentro de un statement, descarta hasta el ';' que termina el statement y continua.
    # Esta es la principal regla de recuperacion: la mayoria de errores de sintaxis ocurren dentro de algun statement y todos terminan en ';'.

    # No se reporta error aqui porque p_error() ya lo reporta con detalle
    # del token, esta regla solo hace la recuperacion
    def p_statement_error(self, p):
        """statement : error SEMICOL"""
        # parser.errok() le dice al parser que volvio a un estado estable
        self.parser.errok()

    # Regla de error de print, es diferente ya que si los argumentos del print no parsean, descarta hasta el ')' del print y continua. Es una regla mas especifica
    # que la de statement para dar mejor diagnostico cuando el error es un edge case dentro de un print.
    def p_print_stmt_error(self, p):
        """print_stmt : KEYWORD_PRINT LPAREN error RPAREN SEMICOL"""
        self.parser.errok()

    # Los errores dentro del body se recuperan principalmente a nivel de statement, ya que la regla statement : error SEMICOL permite avanzar hasta el siguiente
    # ';' y continuar con el análisis. p_error() registra el error

    def p_error(self, p):
        if p is None:
            # Error al final del archivo: no hay token donde reportar
            self.add_error(
                "SYNTAX_ERROR",
                "EOF",
                0,
                0,
                "fin de archivo inesperado, falta cerrar alguna estructura"
            )
            return

        # Se reporta el token infractor con su linea y posicion
        self.add_error(
            "SYNTAX_ERROR",
            p.value,
            p.lineno,
            p.lexpos,
            f"token inesperado de tipo {p.type}"
        )
        # No se llama a parser.errok() aqui debido a que se busca que PLY use el token 'error' para activar las reglas de recuperacion
        # PLY automaticamente reemplaza el token actual por 'error' y busca una regla que lo acepte.

    # =====================================================================
    # CONSTRUCTOR
    # =====================================================================
    """
    El constructor del parser recibe el tokenizer que sera utilizado para obtener tokens. 
    Se inicializa la lista de errores sintacticos y se construye el parser de PLY usando la clase
    actual
    """
    def __init__(self, tokenizer=None):
        # Se guarda el tokenizer para poder pasarselo a yacc.parse()
        self.tokenizer = tokenizer if tokenizer else Tokenizer(keep_comments=False)

        # Lista de errores sintacticos encontrados durante el parseo,
        # cada error es un diccionario con tipo, valor, linea, posicion y mensaje
        self.errors = []
        self.source_code = ""

        # Se construye el parser de PLY. errorlog=yacc.NullLogger() silencia
        # los warnings esperados de yacc al construir el parser, debug=True permite generar parser.out con la tabla LR y mensajes
        # detallados, util para el reporte. write_tables=False evita escribir parsetab.py (el archivo de tablas pre-compiladas).
        self.parser = yacc.yacc(
            module=self,
            debug=True,
            write_tables=False,
            errorlog=yacc.NullLogger(),
        )

    # =====================================================================
    # FUNCIONES AUXILIARES
    # =====================================================================

    # Funcion para limpiar los errores y reiniciar el estado del parser
    # antes de parsear una nueva cadena
    def clean(self):
        self.errors = []

    # Funcion para calcular la columna 1-indexed usando la posicion absoluta lexpos
    def find_column(self, lexpos):
        last_newline = self.source_code.rfind("\n", 0, lexpos)
        return lexpos - last_newline

    # Funcion para agregar un error sintactico a la lista de errores
    def add_error(self, error_type, value, lineno, lexpos, message=""):
        self.errors.append({
            "type": error_type,
            "value": value,
            "lineno": lineno,
            "lexpos": lexpos,
            "column": self.find_column(lexpos) if lexpos else 0,
            "message": message,
        })

    # =====================================================================
    # METODO PRINCIPAL DE PARSEO
    # =====================================================================
    """
    Funcion principal para parsear una cadena de entrada.
    Recibe:
        input_string: el codigo fuente como string.
    Returns:
        True si no hubo errores sintacticos ni lexicos, False en caso contrario.
    """
    def parse(self, input_string):
        # Se limpia el estado del parser antes de parsear una nueva cadena
        self.clean()
        self.source_code = input_string

        # Se le pasa la cadena al parser, especificando que use self.tokenizer como lexer 
        # tracking=True permite usar lineno y lexpos en las acciones semanticas.
        try:
            self.parser.parse(input_string, lexer=self.tokenizer, tracking=True)
        except Exception as e:
            # Si ocurre algun error inesperado, se registra como error generico.
            # Esto NO es lo normal, las reglas de error y p_error deberian
            # capturar todo, pero por seguridad se incluye.
            self.add_error("PARSER_EXCEPTION", str(e), 0, 0,
                           "excepcion no controlada del parser")

        # Retorna True si no hubo errores (ni lexicos ni sintacticos)
        return len(self.errors) == 0 and len(self.tokenizer.errors) == 0


# =========================================================================
# FUNCIONES DE PRUEBA
# =========================================================================

# Funcion para imprimir los errores lexicos y sintacticos de forma legible
def print_errors(parser):
    # Errores lexicos del tokenizer
    if parser.tokenizer.errors:
        print("\nErrores lexicos:")
        for err in parser.tokenizer.errors:
            value = shorten_value(err["value"])
            print(
                f"  {err['type']:<35} "
                f"value: {value:<20} "
                f"linea: {err['lineno']:<3} "
                f"lexpos: {err['lexpos']:<5} "
            )

    # Errores sintacticos del parser
    if parser.errors:
        print("\nErrores sintacticos:")
        for err in parser.errors:
            value = shorten_value(err["value"])
            msg = err.get("message", "")
            print(
                f"  {err['type']:<25} "
                f"value: {value:<20} "
                f"linea: {err['lineno']:<3} "
                f"col: {err['column']:<3} "
                f"-- {msg}"
            )

    # Si no hubo errores, se reporta que todo estuvo válido
    if not parser.tokenizer.errors and not parser.errors:
        print("\nAnalisis completado sin errores.")


# Funcion de prueba para parsear un archivo con PLY
def test_parser(fileName, parser):
    textInput = read_source(fileName)
    print(f"Resultados del parser: {fileName}\n")

    # Se parsea el archivo
    ok = parser.parse(textInput)

    print(f"Codigo fuente:\n{'=' * 60}")
    print(textInput)
    print("=" * 60)

    # Se imprimen los errores (si los hay) o exito
    print_errors(parser)
    print()
    print(f"Resultado: {'OK' if ok else 'CON ERRORES'}")
    print(f"Errores lexicos: {len(parser.tokenizer.errors)}")
    print(f"Errores sintacticos: {len(parser.errors)}")

    return ok

