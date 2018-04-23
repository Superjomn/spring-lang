import re


class Lexer(object):
    '''
    Input a string, get a stream of tokens.
    '''

    def __init__(self, ss):
        self.ss = ss
        self.cursor = 0

    def next(self):
        # skip spaces
        while self.cursor < len(self.ss) and self.ss[self.cursor] == ' ':
            self.cursor += 1

        if self.cursor >= len(self.ss):
            return Token(Token.kEOF)
        if self.ss[self.cursor] == '\n':
            return Token(Token.kEOL)
        res = self.eat_number()
        if res: return res
        res = self.eat_string()
        if res: return res
        res = self.eat_symbol()
        if res: return res
        res = self.eat_bool()
        if res: return res
        res = self.eat_comma()
        if res: return res
        res = self.eat_left_paren()
        if res: return res
        res = self.eat_right_paren()
        if res: return res
        res = self.eat_add()
        if res: return res
        res = self.eat_minus()
        if res: return res
        res = self.eat_equal()
        if res: return res
        res = self.eat_mul()
        if res: return res
        res = self.eat_div()
        if res: return res

    def match_create(self, pattern, method):
        ma = re.match(pattern, self.ss[self.cursor:])
        if ma:
            c = self.ss[self.cursor:][ma.start(0): ma.end(0)]
            res = method(c, offset=self.cursor)
            self.cursor = ma.end(0)
            return res

    def match_create_single(self, p, method, seperate_word=False):
        if self.ss[self.cursor:self.cursor + len(p)] == p:
            if not (seperate_word and self.cursor + len(p) + 1 < len(self.ss) and self.ss[
                self.cursor + len(p) + 1] == ' '):
                return
            self.cursor += len(p)
            return method(offset=self.cursor - 1)

    def eat_number(self):
        return self.match_create("^[0-9]+[.]?[0-9]*", Token.new_number)

    def eat_string(self):
        return self.match_create('^".*"', Token.new_string)

    def eat_symbol(self):
        return self.match_create("^[a-zA-Z_]+[a-zA-Z0-9_]*", Token.new_symbol)

    def eat_bool(self):
        true_ = self.match_create("^true", Token.new_bool)
        if true_: return true_
        return self.match_create("^false", Token.new_bool)

    def eat_comma(self):
        return self.match_create_single(',', Token.new_comma)

    def eat_left_paren(self):
        return self.match_create_single('(', Token.new_left_paren)

    def eat_right_paren(self):
        return self.match_create_single(')', Token.new_right_paren)

    def eat_add(self):
        return self.match_create_single('+', Token.new_add)

    def eat_minus(self):
        return self.match_create_single('-', Token.new_minus)

    def eat_equal(self):
        return self.match_create_single('=', Token.new_equal)

    def eat_mul(self):
        return self.match_create_single('*', Token.new_mul)

    def eat_div(self):
        return self.match_create_single('/', Token.new_div)

    def eat_var(self):
        return self.match_create_single('var', Token.new_var, seperate_word=True)


class Token:
    class Repr:
        counter = 0

        def __init__(self, repr, priority=0):
            '''
            :param id: token id
            :param repr: token string representation
            :param priority: larger better
            '''
            self.id = Token.counter
            Token.counter += 1
            self.repr = repr
            self.priority = priority

    kNumber = Repr("number")
    kString = Repr("string")
    kSymbol = Repr("symbol")
    kBool = Repr("bool")
    kComma = Repr("comma")
    kLeftParen = Repr("left_paren")
    kRightParen = Repr("right_paren")
    kAdd = Repr("add", 2)
    kMinus = Repr("minus", 2)
    kMul = Repr("mul", 3)
    kDiv = Repr("div", 3)
    kEqual = Repr("equal", 1)
    kVar = Repr("var")
    kEOL = Repr("EOL")  # end of line
    kEOF = Repr("EOF")  # end of file

    def __init__(self, type, c=None, offset=None):
        self.type = type
        self.c = c
        self.offset = offset

    def is_primary_element(self):
        return self.type in set(self.kNumber, self.kString)

    def is_element(self):
        return self.is_primary_element() or self.type == self.kSymbol

    def is_operator(self):
        return self.type in set(self.kEqual, self.kAdd, self.kMinus, self.kMul, self.kDiv)

    @staticmethod
    def new_number(c, offset=None): return Token(Token.kNumber, c, offset=offset)

    @staticmethod
    def new_string(c, offset=None): return Token(Token.kString, c, offset=offset)

    @staticmethod
    def new_symbol(c, offset=None): return Token(Token.kSymbol, c, offset=offset)

    @staticmethod
    def new_bool(c, offset=None): return Token(Token.kBool, c, offset=offset)

    @staticmethod
    def new_comma(c=None, offset=None): return Token(Token.kComma, c, offset=offset)

    @staticmethod
    def new_left_paren(c=None, offset=None): return Token(Token.kLeftParen, c, offset=offset)

    @staticmethod
    def new_right_paren(c=None, offset=None): return Token(Token.kRightParen, c, offset=offset)

    @staticmethod
    def new_add(c=None, offset=None): return Token(Token.kAdd, c, offset=offset)

    @staticmethod
    def new_minus(c=None, offset=None): return Token(Token.kMinus, c, offset=offset)

    @staticmethod
    def new_mul(c=None, offset=None): return Token(Token.kMul, c, offset=offset)

    @staticmethod
    def new_div(c=None, offset=None): return Token(Token.kDiv, c, offset=offset)

    @staticmethod
    def new_equal(c=None, offset=None): return Token(Token.kEqual, offset=offset)

    @staticmethod
    def new_equal(c=None, offset=None): return Token(Token.kVar, offset=offset)

    @staticmethod
    def new_eol(c=None, offset=None): return Token(Token.kEOL, offset=offset)

    @staticmethod
    def new_eof(c=None, offset=None): return Token(Token.kEOF, offset=offset)

    def __repr__(self):
        return '<Token %s %d>' % (self.type.repr, self.offset) if not self.c else '<Token %s %s %d>' % (
        self.type.repr, self.c, self.offset)


if __name__ == '__main__':
    lexer = Lexer("a0 = 32.1")
    print(lexer.next())
    print(lexer.next())
    print(lexer.next())
