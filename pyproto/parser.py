from queue import Queue, PriorityQueue
from lexer import Lexer, Token


class AST:
    class Node:
        def __init__(self):
            pass

    def __init__(self, source, targets):
        self.source = source
        self.targets = targets

    def is_primary_element(self):
        return self.source.is_primary_element()

    def is_element(self):
        pass


class Parser(object):
    '''
    parsing tokens from a lexer, and generate ASTs
    '''

    def __init__(self, lexer, k=1):
        self.lexer = lexer
        self.k = k
        self.queue = Queue()

    def consume(self, k, type=None):
        ''' consume k steps, check their types and return the tokens '''
        arguments = []
        assert k > 0
        if type is not None:
            if not (isinstance(type, list) or isinstance(type, tuple)):
                type = [type]
            assert len(type) == k

        for i in range(k):
            if type: assert self.LA(0).type == type[i]
            arguments.append(self.LA(0))
            self.forward_one_step()
        return arguments if k > 0 else arguments[0]

    def forward_one_step(self):
        ''' lexer forward one step, this will trigger an maintaince of a k-length queue. '''
        if not self.queue.empty(): self.queue.get_nowait()
        # the init, will push k times
        k = self.k if self.queue.empty() else 1
        for i in range(k):
            next = self.lexer.next()
            if next:
                self.queue.put_nowait(next)
            else:
                break

    def eat_statement(self):
        pass

    def eat_assign(self):
        '''
        a = statement
        '''
        if self.queue[0].type == Token.kSymbol and self.queue[1].type == Token.kEqual:
            left = self.queue[0]
            root = self.queue[1]
            self.consume(2)
            right = self.eat_expression()
            return AST(root, [left, right])

    def eat_declare_var(self):
        '''
        var a
        var a = expression

        :return
            AST
            var
             |
           symbol
             |
         expression
        '''
        var = self.consume(1, Token.kVar)  # eat var
        symbol = self.consume(1, Token.kSymbol)  # eat symbol
        if self.to_end():
            return AST(var, [symbol])
        # an declaration with initial value.
        self.consume(1, Token.kEqual)
        expression = self.eat_expression()
        return AST(var, [AST(symbol, [expression])])

    def eat_expression(self):
        '''
        a + 1
        a > 2
        (b+1)
        :return:
        '''

        arguments = []

        types0 = set(Token.kSymbol, Token.kNumber, Token.kString)
        while self.LA(0).type != Token.kComma and self.LA(0):
            if self.to_end(): break
            res = self.eat_function_call()
            if res: arguments.append(res); continue
            res = self.eat_paren_pair()
            if res: arguments.append(res); continue
            if self.LA(0) in types0:
                arguments.append(self.LA(0))
                self.consume(1)
                continue
        # parse arguments
        # get priorities, and sort from most important
        operators = []
        for id, node in enumerate(arguments):
            if isinstance(node, Token) and node.is_operator():
                operators.append((id, node))
        operators = sorted(operators, lambda a,b: a[1].type.priority > b[1].type.priority)
        # visit operators
        for op in operators:
            pass


    def eat_function_def(self):
        pass

    def eat_function_call(self):
        if self.queue[0].type == Token.kSymbol and self.queue[1].type == Token.kLeftParen:
            func_name = self.queue[0]
            self.consume(1)  # eat func_name

            # consume the arguments in the parentheses
            assert self.queue[0].type == Token.kLeftParen
            self.consume(1)  # eat (

            arguments = []
            last_token_type = Token.kComma
            while self.queue[0].type != Token.kRightParen:
                if last_token_type == Token.kComma:
                    assert self.queue[0].type != Token.kComma, ",, found, wrong syntax"
                    continue
                # eat an argument
                arguments.append(self.eat_expression())
            self.consume(1)  # eat )

            return AST(func_name, arguments)

    def eat_paren_pair(self):
        '''
        (a+1)
        '''
        assert self.queue[0].type == Token.kLeftParen
        self.consume(1)  # eat (
        ast = self.eat_expression()
        assert self.queue[0].type == Token.kRightParen
        self.consume(1)  # skip )
        return ast

    def LA(self, id):
        return self.queue[id]

    def to_end(self):
        return self.LA(0).type == Token.kEOL or self.LA(0).type == Token.kEOF
