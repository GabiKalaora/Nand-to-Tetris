KEYWORDS = {"CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD",
            "LET", "DO", "IF", "ELSE", "WHILE", "RETURN", "TRUE",
            "FALSE", "NULL", "THIS"}

SYMBOLS = {'(', ')', '[', ']', '{', '}', ',', ';', '=', '.', '+', '-', '*',
           '/', '&', '|', '~', '<', '>'}

WHITE_SPACE = {'/', "\n", "\t"}


class JackTokenizer:
    """
    handles all tokenizing from file that is needed to compile
    a token is a word or letter or a symbol that represents a func/call in Jack
    """
    def __init__(self, input_file):
        self.__file = open(input_file, 'r')
        self.__list_of_tokens = []
        self.__cur_token = ""
        self.__index_advance = 0
        self.__parser(self.__file)

    def __parser(self, file):
        """
        parser through a line in file and extracts tokens from it
        :param file: to pars over
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
        handles removing of white spaces and all documentation or "hearot"
        :param file: to pars over
        :param tok: word to check if is part of the jack program
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
        checks if there are more tokens
        :return: True if there is else False
        """
        return True if len(
            self.__list_of_tokens) != self.__index_advance else False

    def advance(self):
        """
        advances current tokenizer
        """
        self.__index_advance += 1
        if self.__index_advance < len(self.__list_of_tokens):
            self.__cur_token = self.__list_of_tokens[self.__index_advance]

    def token_type(self):
        """
        gets current token type
        """
        if self.__cur_token.upper() in KEYWORDS:
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
        returns the key_word of token
        """
        return self.__cur_token.upper()

    def symbol(self):
        """
        returns the symbol of token
        """
        return self.__cur_token

    def identifier(self):
        """
        returns the identifier of token
        """
        return self.__cur_token

    def int_val(self):
        """
        returns the int value of token
        """
        return int(self.__cur_token)

    def string_val(self):
        """
        returns the string val of token
        """
        return self.__cur_token[1:-1]

