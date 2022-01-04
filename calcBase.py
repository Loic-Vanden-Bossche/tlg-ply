# -----------------------------------------------------------------------------
# calc.py
#
# Expressions arithmétiques sans variables
# -----------------------------------------------------------------------------

from genereTreeGraphviz2 import printTreeGraph

reserved = {
    'print': 'PRINT'
}

tokens = (
    'NUMBER','MINUS',
    'NAME', 'ASSIGNMENT',
    'PLUS','TIMES','DIVIDE',
    'LPAREN','RPAREN', 'OR', 'AND', 'TRUE', 'FALSE', 'SEMI',
    'LOWER', 'HIGHER', 'EQUALS', 'NOTEQUALS'
    ) + tuple(reserved.values())

# Tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_OR      = r'\|'
t_AND     = r'&'
t_TRUE    = r'T'
t_FALSE   = r'F'
t_SEMI    = r';'
t_ASSIGNMENT  = r'='
t_EQUALS  = r'=='
t_NOTEQUALS  = r'!='
t_LOWER = r'<'
t_HIGHER = r'>'


vars = {}

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]+'
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
    ('nonassoc', 'LOWER', 'HIGHER', 'EQUALS', 'NOTEQUALS'),
    ('left','PLUS','MINUS'),
    ('left','TIMES','DIVIDE'),
)


def p_start_expr(p):
    'start : bloc'

    p[0] = ('start', p[1])
    print('Arbre de dérivation = ', p[0])
    printTreeGraph(p[1])
    evalInst(p[1])


def p_bloc_expr(p):
    '''bloc : bloc statement SEMI
    | statement SEMI'''

    if len(p) == 4:
        p[0] = ('bloc', p[1], p[2])
    else:
        p[0] = ('bloc', p[1], None)


def p_statement_expr(p):
    'statement : PRINT LPAREN expression RPAREN'
    p[0] = ('print', p[3])


def p_names_expr(p):
    'statement : NAME ASSIGNMENT expression'
    vars[p[1]] = p[3]
    p[0] = ('=', p[1], p[3])


def p_expression_binop(p):
    '''expression : expression PLUS expression
                | expression MINUS expression
                | expression TIMES expression
                | expression OR expression
                | expression AND expression
                | expression LOWER expression
                | expression HIGHER expression
                | expression EQUALS expression
                | expression NOTEQUALS expression
                | expression DIVIDE expression'''

    p[0] = (p[2], p[1], p[3])


def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]


def p_expression_var(p):
    'expression : NAME'
    p[0] = vars.get(p[1])


def p_expression_true(p):
    'expression : TRUE'
    p[0] = True


def p_expression_false(p):
    'expression : FALSE'
    p[0] = False


def p_error(p):
    print("Syntax error at '%s'" % p.value)


import ply.yacc as yacc

yacc.yacc()


def evalExpr(t):
    print('eval expr de ', t)
    if type(t) is int: return t
    if type(t) is str: return vars.get(t)
    if type(t) is tuple:

        if t[0] == '+':          return evalExpr(t[1]) + evalExpr(t[2])
        if t[0] == '*':          return evalExpr(t[1]) * evalExpr(t[2])
        if t[0] == '/':          return evalExpr(t[1]) / evalExpr(t[2])
        if t[0] == '-':          return evalExpr(t[1]) - evalExpr(t[2])
        if t[0] == '&':        return evalExpr(t[1]) and evalExpr(t[2])
        if t[0] == '==':     return evalExpr(t[1]) == evalExpr(t[2])
        if t[0] == '!=':  return evalExpr(t[1]) != evalExpr(t[2])
        if t[0] == '|':         return evalExpr(t[1]) or evalExpr(t[2])
        if t[0] == '<':          return evalExpr(t[1]) < evalExpr(t[2])
        if t[0] == '>':          return evalExpr(t[1]) > evalExpr(t[2])
    return 'UNK'


def evalInst(t):
    print('eval inst de ', t)
    if type(t) is None:
        return

    if t[0] == 'print':
        print(evalExpr(t[1]))

    if t[0] == 'bloc':
        print(evalInst(t[1]))


s = "test = 12 + 34 * 8; print(1 != 2);"
yacc.parse(s)
    