class Parser:
    table_type = {
        "arithmetic": "C_ARITHMETIC",
        "push": "C_PUSH",
        "pop": "C_POP",
        "label": "C_LABEL",
        "goto": "C_GOTO",
        "if-goto": "C_IF",
        "function": "C_FUNCTION",
        "return": "C_RETURN",
        "call": "C_CALL"
    }
    arithmetic = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]

    def __init__(self, input_file):
        self.__input = input_file
        self.__commends = []
        self.__line = ""
        file = open(self.__input)
        for line in file:
            x = self.__remove_whitespace(line)
            if x != "":
                self.__commends.append(x)
        file.close()

    def __remove_whitespace(self, line):
        new_line = line.split("\n")
        new_line = new_line[0].replace("\t", "")
        split_line = new_line.split("//")
        if split_line[0] != "":
            split_line = split_line[0].split(' ')
            my_line = ''
            for w in split_line:
                if w != '':
                    my_line += w
                    my_line += ' '
            if my_line != '':
                my_line = my_line[:-1]
            return my_line
        else:
            return ""


    def hes_more_commands(self):
        if len(self.__commends) != 0:
            return True
        return False

    def advance(self):
        self.__line = self.__commends[0]
        self.__commends.remove(self.__line)

    def __split_line(self):
        split_line = self.__line.split(" ")
        return split_line

    def __type_commend(self):
        if self.__split_line()[0] in Parser.arithmetic:
            return True
        return False

    def commend_type(self):
        if self.__type_commend() and self.__split_line()[0] != 'return':
            return Parser.table_type["arithmetic"]
        else:
            return Parser.table_type[self.__split_line()[0]]

    def arg1(self):
        if self.__type_commend():
            return self.__split_line()[0]
        elif self.__split_line()[0] != "return":
            return self.__split_line()[1]

    def arg2(self):
        if not self.__type_commend() and len(self.__split_line()) >= 3:
            return self.__split_line()[2]
