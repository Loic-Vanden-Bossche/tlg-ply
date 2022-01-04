# -----------------------------------------------------------------------------
# calc.py
#
# Expressions arithmétiques sans variables
# -----------------------------------------------------------------------------

reserved = {
    'print': 'PRINT'
}

tokens = (
    'NUMBER','MINUS',
    'NAME', 'ASSIGNMENT',
    'PLUS','TIMES','DIVIDE',
    'LPAREN','RPAREN', 'OR', 'AND', 'TRUE', 'FALSE', 'SEMI',
    'LESSTHAN', 'BIGGERTHAN', 'EQUALS', 'NOTEQUALS'
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
t_LESSTHAN = r'<'
t_BIGGERTHAN = r'>'


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


def p_start_expr(p):
    'start : bloc'


def p_bloc_expr(p):
    '''bloc : bloc statement SEMI
    | statement SEMI'''


def p_statement_expr(p):
    'statement : PRINT LPAREN expression RPAREN'
    print(p[3])


def p_names_expr(p):
    'statement : NAME ASSIGNMENT expression'
    vars[p[1]] = p[3]
    print(f"La var {p[1]} = {p[3]}")


def p_expression_binop_plus(p):
    'expression : expression PLUS expression'
    p[0] = p[1] + p[3]


def p_expression_binop_times(p):
    'expression : expression TIMES expression'
    p[0] = p[1] * p[3]


def p_expression_binop_divide_and_minus(p):
    '''expression : expression MINUS expression
				| expression DIVIDE expression'''
    if p[2] == '-': p[0] = p[1] - p[3]
    else : p[0] = p[1] / p[3]	


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


def p_expression_binop_or(p):
    'expression : expression OR expression'
    p[0] = p[1] or p[3]


def p_expression_binop_and(p):
    'expression : expression AND expression'
    p[0] = p[1] and p[3]


def p_expression_binop_lessthan(p):
    'expression : expression LESSTHAN expression'
    p[0] = p[1] < p[3]


def p_expression_binop_biggerthan(p):
    'expression : expression BIGGERTHAN expression'
    p[0] = p[1] > p[3]


def p_expression_binop_equals(p):
    'expression : expression EQUALS expression'
    p[0] = p[1] == p[3]


def p_expression_binop_notequals(p):
    'expression : expression NOTEQUALS expression'
    p[0] = p[1] != p[3]


def p_error(p):
    print("Syntax error at '%s'" % p.value)


import ply.yacc as yacc

yacc.yacc()


def eval(t):
    print('eval de ', t)
    if type(t) is int: return t
    if type(t) is tuple:

        if t[0] is '+':     return eval(t[1]) + eval(t[2])
        if t[0] is '*':     return eval(t[1]) * eval(t[2])
    return 'UNK'


s = "print(2*3+1);" #input('calc > ')
yacc.parse(s)

    