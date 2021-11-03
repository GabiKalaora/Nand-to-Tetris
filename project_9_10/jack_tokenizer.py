KEYWORDS = ["class", "method", "function", "constructor", "int",
            "boolean", "char", "void", "var", "static", "field",
            "let", "do", "if", "else", "while", "return", "true",
            "false", "null", "this"]

SYMBOLS = {'(', ')', '[', ']', '{', '}', ',', ';', '=', '.', '+', '-', '*',
           '/', '&', '|', '~', '<', '>'}

WHITE_SPACE = {'/', "\n", "\t"}


class JackTokenizer:

    def __init__(self, input_file):
        self.__file = open(input_file, 'r')
        self.__list_of_tokens = []
        self.__cur_token = ""
        self.__index_advance = 0
        self.__parser(self.__file)

    def __parser(self, file):
        """
        parsers threw each line from each jack file to compile
        :param file:
        :return:
        """
        word = ""
        while True:
            token = file.read(1)
            if not token:
                break
            elif token in WHITE_SPACE:
                self.__list_of_tokens.append(word) if word else None
                file.seek(self.__white_space(file, token))
                word = ""
            else:
                if token in SYMBOLS:
                    self.__list_of_tokens.append(word) if word else None
                    self.__list_of_tokens.append(token)
                    word = ""
                elif token == " ":
                    self.__list_of_tokens.append(word) if word else None
                    word = ""
                elif token == '"':
                    word += token
                    while True:
                        token = file.read(1)
                        word += token
                        if token == '"':
                            break
                    self.__list_of_tokens.append(word)
                    word = ""
                else:
                    word += token
        self.__cur_token = self.__list_of_tokens[0]

    def __white_space(self, file, tok):
        """
        removes every not relevant text from every line in every file
        such as \\, white space etc
        :param file: to remove all white space from
        :param tok: tok to check if needed to compile
        :return: location to continue running from
        """
        if tok == "\n" or tok == "\t":
            return file.tell()
        elif tok == '/':
            t = tok + str(file.read(1))
            if t == "//":
                file.readline()
                pos = file.tell()
            elif t == "/*":
                sign = ""
                while True:
                    char = file.read(1)
                    if sign + char == "*/":
                        pos = file.tell()
                        break
                    sign = char
            else:
                self.__list_of_tokens.append(tok)
                pos = file.tell() - 1
            return pos

    def hes_more_tokens(self):
        """
        :return: true if length of tokens list is
        """
        return True if len(
            self.__list_of_tokens) != self.__index_advance else False

    def advance(self):
        """
        advances cur tokenizer and holds a new tokenizer
        """
        self.__index_advance += 1
        if self.__index_advance < len(self.__list_of_tokens):
            self.__cur_token = self.__list_of_tokens[self.__index_advance]

    def token_type(self):
        """
        checks the cur token type
        """
        if self.__cur_token in KEYWORDS:
            return "KEYWORD"
        elif self.__cur_token in SYMBOLS:
            return "SYMBOL"
        elif self.__cur_token.isdigit():
            return "INT_CONST"
        elif '"' in self.__cur_token:
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def key_word(self):
        """
         :return: key word token
         """
        return self.__cur_token

    def symbol(self):
        """
        :return: symbol token
        """
        return self.__cur_token

    def identifier(self):
        """
        :return: identifier token
        """
        return self.__cur_token

    def int_val(self):
        """
        :return: int_val token
        """
        return int(self.__cur_token)

    def string_val(self):
        """
        :return: string_val token
        """
        return self.__cur_token[1:-1]

