# -*- coding: utf-8 -*-
# =====================================================================
# Quack Virtual Machine  -  Little Duck (Equipo 5)
#
# Programa INDEPENDIENTE del compilador. Carga un archivo .txt con la
# representacion intermedia en DIRECCIONES de memoria virtual, simula la
# memoria por regiones (restringiendo el acceso solo a lo reservado) e
# interpreta los cuadruplos, ejecutando el programa.
#
# Errores de runtime que reporta:
#   - division (o modulo) entre cero
#   - acceso a memoria virtual no reservada
#   - indice de arreglo fuera de rango
#   - recursion maxima excedida
#
# Estructura de la RI que recibe (convencion del equipo):
#   cons
#   <dir>\t<tipo>\t<valor>            # constantes y su direccion
#   memo
#   <region> <cantidad>               # memoria global (globales + temps del main + ctes)
#   func
#   <nombre>\t<start_quad>\t<tipo>    # un bloque por funcion
#   params <n>
#   param_addr <a1> <a2> ...
#   local_int/.../temp_bool <n>
#   end
#   quads
#   <num>\t<op>\t<argL>\t<argR>\t<res>
# =====================================================================

import sys


# Inicio de cada region de memoria virtual (convencion vista en clase)
REGION_BASE = {
    "global_int": 1000, "global_float": 2000, "global_str": 3000, "global_void": 4000,
    "local_int": 7000, "local_float": 8000, "local_str": 9000,
    "temp_int": 12000, "temp_float": 13000, "temp_bool": 14000,
    "cte_int": 17000, "cte_float": 18000, "cte_str": 19000,
}
RET_REG = 5000          # registro unico de retorno
RECURSION_LIMIT = 5000  # profundidad maxima de la pila de llamadas


class VMRuntimeError(Exception):
    """Error semantico detectado en tiempo de ejecucion."""
    pass


class Quack:
    """Un cuadruplo de la representacion intermedia."""
    def __init__(self, lista):
        self.numero = int(lista[0])
        self.operador = lista[1]
        self.arg_izq = lista[2]
        self.arg_der = lista[3]
        self.resultado = lista[4]


class Frame:
    """Activation record: la memoria local+temporal de una invocacion."""
    def __init__(self, func_name, return_quad):
        self.func_name = func_name
        self.return_quad = return_quad
        self.mem = {}        # direccion -> valor (locales y temporales)


class VirtualMachine:
    def __init__(self):
        self.const_mem = {}      # direccion -> valor (solo lectura)
        self.global_mem = {}     # globales + temporales del main + registro de retorno
        self.global_counts = {}  # region -> cantidad reservada (memoria global)
        self.func_dir = {}       # nombre -> dict con start_quad, return_type, param_addr, counts
        self.quads = []          # lista de Quack (1-indexada: quads[0] no se usa)
        self.call_stack = []     # pila de Frame (vacia => estamos en el main)
        self.pending_stack = []  # pila de llamadas en preparacion (soporta anidacion)

    # ---- carga del archivo de RI --------------------------------------

    def load(self, text):
        section = None
        cur_func = None
        self.quads = [None]   # indice 0 sin usar; los cuadruplos empiezan en 1

        for raw in text.split("\n"):
            line = raw.rstrip()
            if line.strip() == "":
                continue
            head = line.split()[0]

            if head in ("cons", "memo", "func", "quads"):
                section = head
                cur_func = None
                continue

            if section == "cons":
                # <dir>\t<tipo>\t<valor>
                parts = line.split("\t")
                addr = int(parts[0].strip())
                tipo = parts[1].strip()
                raw_val = parts[2] if len(parts) > 2 else ""
                self.const_mem[addr] = self._parse_const(tipo, raw_val)

            elif section == "memo":
                toks = line.split()
                self.global_counts[toks[0]] = int(toks[1])

            elif section == "func":
                toks = line.split()
                if toks[0] == "params":
                    self.func_dir[cur_func]["params"] = int(toks[1])
                elif toks[0] == "param_addr":
                    self.func_dir[cur_func]["param_addr"] = [int(x) for x in toks[1:]]
                elif toks[0] in ("local_int", "local_float", "local_str",
                                 "temp_int", "temp_float", "temp_bool"):
                    self.func_dir[cur_func]["counts"][toks[0]] = int(toks[1])
                elif toks[0] == "end":
                    cur_func = None
                else:
                    # encabezado de funcion: nombre  start_quad  tipo
                    p = line.split("\t")
                    name = p[0].strip()
                    cur_func = name
                    self.func_dir[name] = {
                        "start_quad": int(p[1]),
                        "return_type": p[2].strip(),
                        "params": 0,
                        "param_addr": [],
                        "counts": {"local_int": 0, "local_float": 0, "local_str": 0,
                                   "temp_int": 0, "temp_float": 0, "temp_bool": 0},
                    }

            elif section == "quads":
                toks = line.split()
                # num op argL argR res
                self.quads.append(Quack(toks[:5]))

    def _parse_const(self, tipo, raw):
        raw = raw.strip()
        if tipo == "cte_int":
            return int(raw)
        if tipo == "cte_float":
            return float(raw)
        # cadena: quitar comillas y restaurar saltos de linea
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        return raw.replace("\\n", "\n")

    # ---- simulacion de memoria por regiones ---------------------------

    def _region_of(self, addr):
        if addr == RET_REG:
            return "ret"
        base = (addr // 1000) * 1000
        for region, rbase in REGION_BASE.items():
            if rbase == base:
                return region
        return None

    def _check_reserved(self, addr, region):
        # Verifica que la direccion este dentro de la memoria reservada
        offset = addr - REGION_BASE[region]
        if region.startswith("cte_"):
            if addr not in self.const_mem:
                self._fail("acceso a constante no reservada (dir %d)" % addr)
            return
        if region.startswith("global_"):
            limit = self.global_counts.get(region, 0)
            if not (0 <= offset < limit):
                self._fail("acceso a memoria global no reservada (dir %d)" % addr)
            return
        # local_* / temp_* : dependen del contexto actual
        if self.call_stack:
            counts = self.func_dir[self.call_stack[-1].func_name]["counts"]
            limit = counts.get(region, 0)
        else:
            # en el main: solo se reservan temporales (en memoria global)
            limit = self.global_counts.get(region, 0) if region.startswith("temp_") else 0
        if not (0 <= offset < limit):
            self._fail("acceso a memoria no reservada (dir %d)" % addr)

    def read(self, addr):
        addr = int(addr)
        if addr == RET_REG:
            return self.global_mem.get(RET_REG, 0)
        region = self._region_of(addr)
        if region is None:
            self._fail("direccion de memoria invalida (%d)" % addr)
        self._check_reserved(addr, region)
        if region.startswith("cte_"):
            return self.const_mem[addr]
        if region.startswith("global_"):
            return self.global_mem.get(addr, 0)
        # local_* / temp_*
        if self.call_stack:
            return self.call_stack[-1].mem.get(addr, 0)
        return self.global_mem.get(addr, 0)   # temporales del main

    def write(self, addr, value):
        addr = int(addr)
        if addr == RET_REG:
            self.global_mem[RET_REG] = value
            return
        region = self._region_of(addr)
        if region is None:
            self._fail("direccion de memoria invalida (%d)" % addr)
        if region.startswith("cte_"):
            self._fail("intento de escribir en una constante (dir %d)" % addr)
        self._check_reserved(addr, region)
        if region.startswith("global_"):
            self.global_mem[addr] = value
        elif self.call_stack:
            self.call_stack[-1].mem[addr] = value
        else:
            self.global_mem[addr] = value      # temporales del main

    def _fail(self, msg):
        raise VMRuntimeError("%s [cuadruplo %d]" % (msg, self.cur))

    # ---- ejecucion -----------------------------------------------------

    def run(self):
        self.cur = 1
        n = len(self.quads) - 1
        while 1 <= self.cur <= n:
            q = self.quads[self.cur]
            op = q.operador

            if op == "gotomain":
                self.cur = int(q.resultado)

            elif op == "goto":
                self.cur = int(q.resultado)

            elif op == "gotof":
                if not self._truth(self.read(q.arg_izq)):
                    self.cur = int(q.resultado)
                else:
                    self.cur += 1

            elif op == "gotot":
                if self._truth(self.read(q.arg_izq)):
                    self.cur = int(q.resultado)
                else:
                    self.cur += 1

            elif op == "=":
                self.write(q.resultado, self.read(q.arg_izq))
                self.cur += 1

            elif op == "=[]":
                # escritura a arreglo: mem[base + indice] = valor
                base = int(q.resultado)
                idx = self.read(q.arg_der)
                self.write(base + idx, self.read(q.arg_izq))
                self.cur += 1

            elif op == "[]":
                # lectura de arreglo: res = mem[base + indice]
                base = int(q.arg_izq)
                idx = self.read(q.arg_der)
                self.write(q.resultado, self.read(base + idx))
                self.cur += 1

            elif op in ("+", "-", "*", "/", "%"):
                self._arith(q)
                self.cur += 1

            elif op in ("<", ">", "<=", ">=", "==", "!=", "&&", "||"):
                self._relational(q)
                self.cur += 1

            elif op == "neg":
                self.write(q.resultado, -self.read(q.arg_izq))
                self.cur += 1

            elif op == "!":
                self.write(q.resultado, not self._truth(self.read(q.arg_izq)))
                self.cur += 1

            elif op == "ver":
                self._verify_bounds(q)
                self.cur += 1

            elif op == "print":
                sys.stdout.write(self._fmt(self.read(q.arg_izq)))
                self.cur += 1

            elif op == "newline":
                sys.stdout.write("\n")
                self.cur += 1

            elif op == "sub":
                # inicia la preparacion de una llamada a q.arg_izq
                self.pending_stack.append({"func": q.arg_izq, "args": []})
                self.cur += 1

            elif op == "param":
                self.pending_stack[-1]["args"].append(self.read(q.arg_izq))
                self.cur += 1

            elif op == "gosub":
                self._gosub(q)

            elif op == "return":
                self._return(q)

            elif op == "endfun":
                self._endfun()

            elif op == "end":
                sys.stdout.flush()
                return

            else:
                self._fail("operador desconocido: %s" % op)

        sys.stdout.flush()

    # ---- helpers de ejecucion -----------------------------------------

    def _truth(self, v):
        return bool(v)

    def _fmt(self, v):
        if isinstance(v, bool):
            return "true" if v else "false"
        return str(v)

    def _arith(self, q):
        a = self.read(q.arg_izq)
        b = self.read(q.arg_der)
        op = q.operador
        if op == "+":
            r = a + b
        elif op == "-":
            r = a - b
        elif op == "*":
            r = a * b
        elif op == "/":
            if b == 0:
                self._fail("division entre cero")
            r = a / b                     # division real (produce float)
        elif op == "%":
            if b == 0:
                self._fail("modulo entre cero")
            r = a % b
        self.write(q.resultado, r)

    def _relational(self, q):
        a = self.read(q.arg_izq)
        b = self.read(q.arg_der)
        op = q.operador
        if op == "<":
            r = a < b
        elif op == ">":
            r = a > b
        elif op == "<=":
            r = a <= b
        elif op == ">=":
            r = a >= b
        elif op == "==":
            r = a == b
        elif op == "!=":
            r = a != b
        elif op == "&&":
            r = self._truth(a) and self._truth(b)
        elif op == "||":
            r = self._truth(a) or self._truth(b)
        self.write(q.resultado, r)

    def _verify_bounds(self, q):
        idx = self.read(q.arg_izq)
        low = int(q.arg_der)
        high = int(q.resultado)
        if not (low <= idx <= high):
            self._fail("indice de arreglo fuera de rango (%s, valido %d..%d)"
                       % (idx, low, high))

    def _gosub(self, q):
        func = q.arg_izq
        start = int(q.resultado)
        if len(self.call_stack) + 1 > RECURSION_LIMIT:
            self._fail("recursion maxima excedida (limite %d)" % RECURSION_LIMIT)
        # nuevo frame; regresa al cuadruplo siguiente al gosub
        frame = Frame(func, self.cur + 1)
        # copiar los argumentos staged a las direcciones de los parametros
        pending = self.pending_stack.pop()
        param_addr = self.func_dir[func]["param_addr"]
        for i, val in enumerate(pending["args"]):
            frame.mem[param_addr[i]] = val
        self.call_stack.append(frame)
        self.cur = start

    def _return(self, q):
        if q.arg_izq != "-1" and q.arg_izq != -1:
            self.global_mem[RET_REG] = self.read(q.arg_izq)
        frame = self.call_stack.pop()
        self.cur = frame.return_quad

    def _endfun(self):
        # funcion void que termina sin return explicito
        frame = self.call_stack.pop()
        self.cur = frame.return_quad


# ---- uso como programa independiente ----------------------------------

def main():
    archivo = sys.argv[1] if len(sys.argv) > 1 else "ri_memoria.txt"
    try:
        text = open(archivo, encoding="utf-8").read()
    except FileNotFoundError:
        print("No se encontro el archivo de RI '%s'." % archivo)
        return
    vm = VirtualMachine()
    try:
        vm.load(text)
        vm.run()
    except VMRuntimeError as e:
        print()
        print("Error en tiempo de ejecucion: %s" % e)


if __name__ == "__main__":
    main()