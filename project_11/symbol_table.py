class SymbolTable:
    def __init__(self):
        """
        constructor for SymbolTable class
        """
        self.__symbol_class = {}
        self.__symbol_subroutine = {}
        self.__idx_of_kind = {"field": 0, "static": 0, "arg": 0, "local": 0}

    def start_subroutine(self):
        """
        starts subroutine by updating the dictionary AKA symbol table
        """
        self.__symbol_subroutine.clear()
        self.__idx_of_kind["arg"] = 0
        self.__idx_of_kind["local"] = 0

    def define(self, name, kind_type, kind):
        """
        checks what type of command it is by looking over into the symbol table
        :param name: to check for
        :param kind_type: to check for
        :param kind: to check for
        """
        if name not in self.__symbol_class and kind == "field" or kind == "static":
            self.__symbol_class[name] = [kind_type, kind, self.__idx_of_kind[kind]]
            self.__idx_of_kind[kind] += 1

        elif name not in self.__symbol_subroutine and kind == "arg" or kind == "local":
            self.__symbol_subroutine[name] = [kind_type, kind, self.__idx_of_kind[kind]]
            self.__idx_of_kind[kind] += 1

    def var_count(self, kind):
        """
        gets to kind key in the ttble
        :param kind: keyto search for
        """
        return self.__idx_of_kind[kind]

    def kind_of(self, name):
        """
        gets the kind of name in symbol table
        :param name: to check in the table
        """
        if name in self.__symbol_subroutine:
            return self.__symbol_subroutine[name][1]
        elif name in self.__symbol_class:
            return self.__symbol_class[name][1]

    def type_of(self, name):
        """
        gets the type of name in symbol table
        :param name: to check in the table
        """
        if name in self.__symbol_subroutine:
            return self.__symbol_subroutine[name][0]
        elif name in self.__symbol_class:
            return self.__symbol_class[name][0]

    def index_of(self, name):
        """
        gets the index of name in symbol table
        :param name: to check in the table
        """
        if name in self.__symbol_subroutine:
            return self.__symbol_subroutine[name][2]
        elif name in self.__symbol_class:
            return self.__symbol_class[name][2]@!
