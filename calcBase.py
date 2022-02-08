# -----------------------------------------------------------------------------
# calc.py
#
# Loïc Vanden Bossche | Enzo Soares
# -----------------------------------------------------------------------------
import pprint
from functools import partial
from more_itertools import zip_equal, more as iter_errors

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
    'var': 'VARIABLE',
    'return': 'RETURN',
    'true': 'TRUE',
    'false': 'FALSE',
}

tokens = (
             'NUMBER', 'MINUS',
             'NAME', 'COMMA',
             'PLUS', 'TIMES', 'DIVIDE',
             'LPAREN', 'RPAREN', 'OR',
             'AND', 'SEMI',
             'LOWER', 'HIGHER', 'EQUAL',
             'LBRACKET', 'RBRACKET',
             'NOT'
         ) + tuple(reserved.values())

# Tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\{'
t_RBRACKET = r'\}'
t_OR = r'\|'
t_AND = r'&'
t_SEMI = r';'
t_EQUAL = r'='
t_NOT = r'!'
t_LOWER = r'<'
t_HIGHER = r'>'
t_COMMA = r','


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
    enclose(p[1])


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
        p[0] = ('bloc', p[1], p[2])
    else:
        p[0] = ('bloc', p[1], 'empty')


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
    else:
        p[0] = (*p[1], p[3])


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
    else:
        p[0] = (*p[1], p[3])


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


def p_var_names_expr(p):
    """statement : VARIABLE NAME EQUAL expression"""
    p[0] = ('var', p[2], p[4])


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

stack = []

def evalExpr(t):
    debug('eval expr de ', t)
    if type(t) is bool: return t
    if type(t) is int: return t
    if type(t) is str: return get_element('vars', t)
    if type(t) is tuple:
        if t[0] == '+': return evalExpr(t[1]) + evalExpr(t[2])
        if t[0] == '*': return evalExpr(t[1]) * evalExpr(t[2])
        if t[0] == '/': return evalExpr(t[1]) / evalExpr(t[2])
        if t[0] == '-': return evalExpr(t[1]) - evalExpr(t[2])
        if t[0] == '==': return evalExpr(t[1]) == evalExpr(t[2])
        if t[0] == '!=': return evalExpr(t[1]) != evalExpr(t[2])
        if t[0] == '<': return evalExpr(t[1]) < evalExpr(t[2])
        if t[0] == '<=': return evalExpr(t[1]) <= evalExpr(t[2])
        if t[0] == '>': return evalExpr(t[1]) > evalExpr(t[2])
        if t[0] == '>=': return evalExpr(t[1]) >= evalExpr(t[2])
        if t[0] == '&': return bool(evalExpr(t[1])) and bool(evalExpr(t[2]))
        if t[0] == '|': return bool(evalExpr(t[1])) or bool(evalExpr(t[2]))
        if t[0] == 'u-': return -evalExpr(t[1])
        if t[0] == '!': return not evalExpr(t[1])
    return 'UNK'


def get_scopes(scope_type):
    return [scope[1][scope_type] for scope in stack if scope[0] == 'scope'][::-1]


def get_element(elem_type, elem_name):
    for scope in get_scopes(elem_type):
        if elem_name in scope:
            return scope[elem_name]
    raise Exception(f'{elem_type.rstrip("s")} "{elem_name}" not found')


def assign_element(elem_type, elem_name, value):
    for scope in get_scopes(elem_type):
        if elem_name in scope:
            scope[elem_name] = value
            return
    raise Exception(f'{elem_type.rstrip("s")} "{elem_name}" not found')


def declare_element(elem_type, elem_name, value):
    for scope in get_scopes(elem_type):
        if elem_name in scope:
            raise Exception(f'{elem_type.rstrip("s")} "{elem_name}" already declared')

    get_scopes(elem_type)[0][elem_name] = value


def extract_params(raw_params):
    if raw_params == 'empty': return []

    def flatten(params):
        for i, param in enumerate(params):
            if isinstance(param, tuple) and (param[0] == 'param' or param[0] == 'exp'):
                yield from flatten(param)
            elif i == 1:
                yield from [param]

    return list(flatten(raw_params))


def get_function_params(func_name, params):
    try:
        return dict(
            zip_equal(get_element('functions', func_name)[0], [evalExpr(param) for param in extract_params(params)]))
    except iter_errors.UnequalIterablesError:
        raise Exception(f'Wrong number of parameters for function "{func_name}"')


def initScope(s_vars=None):
    if s_vars is None: s_vars = {}
    return  {
        'vars': s_vars,
        'functions': {},
        'classes': {},
    }


def enclose(*instructions, s_vars=None):

    stack.append(('scope', initScope(s_vars)))

    for i, instruction in enumerate(instructions):
        evalInst(instruction)

    stack.pop()


def evalInst(t):
    debug('Eval inst de', t)

    if type(t) == 'empty':
        return

    if t[0] == 'var':
        declare_element('vars', t[1], evalExpr(t[2]))

    if t[0] == '=':
        assign_element('vars', t[1], evalExpr(t[2]))

    if t[1] == '=':
        assign_element('vars', t[2], evalExpr(t[3]))

    if t[0] == 'function':
        declare_element('functions', t[1][0], (extract_params(t[1][1]), t[1][2]))

    if t[0] == 'call':
        enclose(get_element('functions', t[1])[1], s_vars=get_function_params(t[1], t[2]))

    if t[0] == 'print':
        print(evalExpr(t[1]))

    if t[0] == 'bloc':
        stack.append(t[1])
        evalInst(stack[-1])
        stack.pop()
        stack.append(t[2])
        evalInst(stack[-1])
        stack.pop()

    if t[0] == 'if':
        if evalExpr(t[1]):
            enclose(t[2])

    if t[0] == 'if-else':
        if evalExpr(t[1]):
            enclose(t[2])
        else:
            enclose(t[3])

    if t[0] == 'else':
        enclose(t[1])

    if t[0] == 'while':
        while evalExpr(t[1]):
            enclose(t[2])

    if t[0] == 'for':
        evalInst(t[1])
        while evalExpr(t[2]):
            enclose(t[4], t[3])


with open('code.ukn') as f:
    yacc.parse(f.read())
