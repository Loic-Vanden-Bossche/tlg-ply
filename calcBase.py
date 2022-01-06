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
    'if'   : 'IF',
    'while': 'WHILE',
    'else' : 'ELSE',
}

tokens = (
    'NUMBER', 'MINUS',
    'NAME',
    'PLUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN', 'OR',
    'AND', 'TRUE', 'FALSE', 'SEMI',
    'LOWER', 'HIGHER', 'EQUAL',
    'LBRACKET', 'RBRACKET',
    'NOT'
    ) + tuple(reserved.values())

# Tokens
t_PLUS       = r'\+'
t_MINUS      = r'-'
t_TIMES      = r'\*'
t_DIVIDE     = r'/'
t_LPAREN     = r'\('
t_RPAREN     = r'\)'
t_LBRACKET   = r'\{'
t_RBRACKET   = r'\}'
t_OR         = r'\|'
t_AND        = r'&'
t_TRUE       = r'T'
t_FALSE      = r'F'
t_SEMI       = r';'
t_EQUAL      = r'='
t_NOT        = r'!'
t_LOWER      = r'<'
t_HIGHER     = r'>'


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

    p[0] = ('start', p[1])
    print('Arbre de dérivation = ', p[0])
    printTreeGraph(p[1])
    evalInst(p[1])


def p_bloc_expr(p):
    """bloc : bloc statement SEMI
    | statement SEMI"""

    if len(p) == 4:
        p[0] = ('bloc', p[1], p[2])
    else:
        p[0] = ('bloc', p[1], 'empty')


def p_statement_expr(p):
    """statement : PRINT LPAREN expression RPAREN"""
    p[0] = ('print', p[3])


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


def p_expression_op(p):
    """expression : MINUS expression
                | NOT expression"""
    p[0] = ('u-' if p[1] == '-' else p[1], p[2])


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

def evalExpr(t):
    debug('eval expr de ', t)
    if type(t) is bool: return t
    if type(t) is int: return t
    if type(t) is str: return vars[t]
    if type(t) is tuple:

        if t[0] == '+' :  return evalExpr(t[1]) +   evalExpr(t[2])
        if t[0] == '*' :  return evalExpr(t[1]) *   evalExpr(t[2])
        if t[0] == '/' :  return evalExpr(t[1]) /   evalExpr(t[2])
        if t[0] == '-' :  return evalExpr(t[1]) -   evalExpr(t[2])
        if t[0] == '==':  return evalExpr(t[1]) ==  evalExpr(t[2])
        if t[0] == '!=':  return evalExpr(t[1]) !=  evalExpr(t[2])
        if t[0] == '<' :  return evalExpr(t[1]) <   evalExpr(t[2])
        if t[0] == '<=':  return evalExpr(t[1]) <=  evalExpr(t[2])
        if t[0] == '>' :  return evalExpr(t[1]) >   evalExpr(t[2])
        if t[0] == '>=':  return evalExpr(t[1]) >=  evalExpr(t[2])
        if t[0] == '&' :  return bool(evalExpr(t[1])) and bool(evalExpr(t[2]))
        if t[0] == '|' :  return bool(evalExpr(t[1])) or bool(evalExpr(t[2]))
        if t[0] == 'u-':  return -evalExpr(t[1])
        if t[0] == '!' :  return not evalExpr(t[1])
    return 'UNK'


def evalInst(t):
    debug('Eval inst de', t)

    if type(t) == 'empty':
        return

    if t[0] == '=':  vars[t[1]] = evalExpr(t[2])

    if t[0] == 'print':
        print(evalExpr(t[1]))

    if t[0] == 'bloc':
        evalInst(t[1])
        evalInst(t[2])

    if t[0] == 'if':
        if evalExpr(t[1]):
            evalInst(t[2])

    if t[0] == 'if-else':
        if evalExpr(t[1]):
            evalInst(t[2])
        else:
            evalInst(t[3])

    if t[0] == 'else':
        evalInst(t[1])

    if t[0] == 'while':
        while evalExpr(t[1]):
            evalInst(t[2])


s = "i = 0; while (i <= 3) { i = i + 1; print(i); };"
yacc.parse(s)
    