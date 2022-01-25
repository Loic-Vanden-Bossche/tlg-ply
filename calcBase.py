# -----------------------------------------------------------------------------
# calc.py
#
# Expressions arithmétiques sans variables
# -----------------------------------------------------------------------------

from genereTreeGraphviz2 import printTreeGraph

isDebug = False


def debug(*args):
    if isDebug: print(args)


reserved = {
    'print': 'PRINT',
    'if': 'IF',
    'while': 'WHILE',
    'else': 'ELSE',
    'for': 'FOR',
    'function': 'FUNCTION',
    'return': 'RETURN',
}

tokens = (
    'NUMBER', 'MINUS',
    'NAME', 'COMMA',
    'PLUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN', 'OR',
    'AND', 'TRUE', 'FALSE', 'SEMI',
    'LOWER', 'HIGHER', 'EQUAL',
    'LBRACKET', 'RBRACKET',
    'NOT'
) + tuple(reserved.values())

# Tokens
t_PLUS     = r'\+'
t_MINUS    = r'-'
t_TIMES    = r'\*'
t_DIVIDE   = r'/'
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_LBRACKET = r'\{'
t_RBRACKET = r'\}'
t_OR       = r'\|'
t_AND      = r'&'
t_TRUE     = r'T'
t_FALSE    = r'F'
t_SEMI     = r';'
t_EQUAL    = r'='
t_NOT      = r'!'
t_LOWER    = r'<'
t_HIGHER   = r'>'
t_COMMA    = r','


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'NAME')
    return t


# Ignored characters
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
import ply.lex as lex

lex.lex()

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'NOT'),
    ('nonassoc', 'LOWER', 'HIGHER', 'EQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)


def p_start_expr(p):
    """start : bloc"""

    p[0] = ('START', p[1])
    print('Arbre de dérivation = ', p[0])
    printTreeGraph(p[0])
    evalInst(p[1])


def p_bloc_expr(p):
    """bloc : bloc statement SEMI
    | statement SEMI"""

    if len(p) == 4:
        p[0] = ('bloc', p[1], p[2])
    else:
        p[0] = ('bloc', p[1], 'empty')


def p_f_bloc_expr(p):
    """fbloc : fbloc out
        | out"""
    if len(p) == 3:
        p[0] = ('fbloc', p[1], p[2])
    else:
        p[0] = ('fbloc', p[1], 'empty')


def p_out_expr(p):
    """out : return
        | bloc"""
    p[0] = (p[1])

def p_return_expr(p):
    """return : RETURN SEMI
        | RETURN expression SEMI"""
    if len(p) == 4:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return', 'empty')


def p_print_expr(p):
    """statement : PRINT LPAREN expression RPAREN"""
    p[0] = ('print', p[3])


def p_function_expr(p):
    """statement : FUNCTION NAME LPAREN parameter RPAREN LBRACKET fbloc RBRACKET
            | FUNCTION NAME LPAREN RPAREN LBRACKET fbloc RBRACKET"""
    if len(p) == 9:
        p[0] = ('function', (p[2], p[4], p[7]))
    else:
        p[0] = ('function', (p[2], 'empty', p[6]))


def p_function_parameter(p):
    """parameter : NAME
            | parameter COMMA parameter"""

    if len(p) == 2:
        p[0] = ('param', p[1])
    elif len(p) == 4:
        p[0] = (*p[1], p[3])
    else:
        p[0] = ('param', 'empty')


def p_call_expr(p):
    """statement : NAME LPAREN callParameter RPAREN
                | NAME LPAREN RPAREN"""

    if len(p) == 5:
        p[0] = ('call', p[1], p[3])
    else:
        p[0] = ('call', p[1], 'empty')


def p_call_parameter(p):
    """callParameter : expression
            | callParameter COMMA callParameter"""

    if len(p) == 2:
        p[0] = ('exp', p[1])
    elif len(p) == 4:
        p[0] = (*p[1], p[3])
    else:
        p[0] = ('exp', 'empty')


def p_if_expr(p):
    """statement : IF LPAREN expression RPAREN LBRACKET bloc RBRACKET
                | IF LPAREN expression RPAREN LBRACKET bloc RBRACKET else"""

    if len(p) == 8:
        p[0] = ('if', p[3], p[6])
    elif len(p) == 9:
        p[0] = ('if-else', p[3], p[6], p[8])


def p_else(p):
    """else : ELSE LBRACKET bloc RBRACKET"""
    p[0] = ('else', p[3])


def p_while_expr(p):
    """statement : WHILE LPAREN expression RPAREN LBRACKET bloc RBRACKET"""
    p[0] = ('while', p[3], p[6])


def p_names_expr(p):
    """statement : NAME EQUAL expression"""
    p[0] = ('=', p[1], p[3])


def p_for_expr(p):
    """statement : FOR LPAREN statement SEMI expression SEMI statement RPAREN LBRACKET bloc RBRACKET"""
    p[0] = ('for', p[3], p[5], p[7], p[10])


def p_expression_op_left(p):
    """expression : MINUS expression
                | NOT expression"""
    p[0] = ('u-' if p[1] == '-' else p[1], p[2])


def p_op_right(p):
    """statement : NAME PLUS PLUS
                | NAME MINUS MINUS"""
    p[0] = ('++', '=', p[1], (p[2], p[1], 1))


def p_expression_binop(p):
    """expression : expression PLUS expression
                | expression MINUS expression
                | expression TIMES expression
                | expression OR expression
                | expression AND expression
                | expression LOWER expression
                | expression LOWER EQUAL expression
                | expression HIGHER expression
                | expression HIGHER EQUAL expression
                | expression EQUAL EQUAL expression
                | expression NOT EQUAL expression
                | expression DIVIDE expression"""

    if len(p) == 5:
        p[0] = (p[2] + p[3], p[1], p[4])
    else:
        p[0] = (p[2], p[1], p[3])


def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_expression_number(p):
    """expression : NUMBER"""
    p[0] = p[1]


def p_expression_var(p):
    """expression : NAME"""
    p[0] = p[1]


def p_expression_true(p):
    """expression : TRUE"""
    p[0] = True


def p_expression_false(p):
    """expression : FALSE"""
    p[0] = False


def p_error(p):
    print("Syntax error at '%s'" % p.value)


import ply.yacc as yacc

yacc.yacc()

vars = {}
functions = {}


def evalExpr(t, s_vars):
    debug('eval expr de ', t)
    if type(t) is bool: return t
    if type(t) is int: return t
    if type(t) is str: return s_vars[t]
    if type(t) is tuple:

        if t[0] == '+' : return evalExpr(t[1], s_vars) +  evalExpr(t[2], s_vars)
        if t[0] == '*' : return evalExpr(t[1], s_vars) *  evalExpr(t[2], s_vars)
        if t[0] == '/' : return evalExpr(t[1], s_vars) /  evalExpr(t[2], s_vars)
        if t[0] == '-' : return evalExpr(t[1], s_vars) -  evalExpr(t[2], s_vars)
        if t[0] == '==': return evalExpr(t[1], s_vars) == evalExpr(t[2], s_vars)
        if t[0] == '!=': return evalExpr(t[1], s_vars) != evalExpr(t[2], s_vars)
        if t[0] == '<' : return evalExpr(t[1], s_vars) <  evalExpr(t[2], s_vars)
        if t[0] == '<=': return evalExpr(t[1], s_vars) <= evalExpr(t[2], s_vars)
        if t[0] == '>' : return evalExpr(t[1], s_vars) >  evalExpr(t[2], s_vars)
        if t[0] == '>=': return evalExpr(t[1], s_vars) >= evalExpr(t[2], s_vars)
        if t[0] == '&' : return bool(evalExpr(t[1], s_vars)) and bool(evalExpr(t[2], s_vars))
        if t[0] == '|' : return bool(evalExpr(t[1], s_vars)) or bool(evalExpr(t[2], s_vars))
        if t[0] == 'u-': return -evalExpr(t[1], s_vars)
        if t[0] == '!' : return not evalExpr(t[1], s_vars)
    return 'UNK'

def evalFunc(t, s_vars):

    if t[0] == 'fbloc':

        evalFunc(t[1], s_vars)
        evalFunc(t[2], s_vars)

    if t[0] == 'bloc':
        evalInst(t[1], s_vars)
        evalInst(t[2], s_vars)

    if t[0] == 'return':
        print('return')

def evalInst(t, ps_vars=None):

    if ps_vars is None:
        ps_vars = {}

    s_vars = ps_vars

    debug('Eval inst de', t)

    if type(t) == 'empty':
        return

    if t[0] == '=':
        s_vars[t[1]] = evalExpr(t[2], s_vars)

    if t[1] == '=':
        s_vars[t[2]] = evalExpr(t[3], s_vars)

    if t[0] == 'function':
        functions[t[1][0]] = t[1]

    if t[0] == 'call':

        try:
            if functions[t[1]][1] != 'empty' and t[2] != 'empty':

                params = [p for p in functions[t[1]][1] if p != 'param']
                expressions = [e for e in t[2] if e != 'exp']

                s_vars = ps_vars.copy()

                for i in [(params[i], expressions[i]) for i in range(0, len(params))]:
                    s_vars[i[0]] = evalExpr(i[1], s_vars)

            elif len(functions[t[1]][1]) != len(t[2]):
                raise ValueError
        except ValueError:
            raise Exception('Wrong number of parameters')

        evalFunc(functions[t[1]][2], s_vars)

    if t[0] == 'print':
        print(evalExpr(t[1], s_vars))

    if t[0] == 'bloc':
        evalInst(t[1], s_vars)
        evalInst(t[2], s_vars)

    if t[0] == 'if':
        if evalExpr(t[1], s_vars):
            evalInst(t[2], ps_vars.copy())

    if t[0] == 'if-else':
        if evalExpr(t[1], s_vars):
            evalInst(t[2], ps_vars.copy())
        else:
            evalInst(t[3], ps_vars.copy())

    if t[0] == 'else':
        evalInst(t[1], ps_vars.copy())

    if t[0] == 'while':
        while evalExpr(t[1], s_vars):
            evalInst(t[2], ps_vars.copy())

    if t[0] == 'for':
        evalInst(t[1], s_vars)
        while evalExpr(t[2], s_vars):
            evalInst(t[4], ps_vars.copy())
            evalInst(t[3], ps_vars.copy())


s = "function test() { print(1); return; return; print(1); }; test();\n"
yacc.parse(s)
