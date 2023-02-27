import jack_tokenizer


class CompilationEngine:
    OP = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
    UNARY_OP = {"-", "~"}
    KEYWORD_CONSTANT = {"true", "false", "null", "this"}

    # ***************  CONSTRUCTOR  ***************

    def __init__(self, input_file, output_file):
        self.__tokenizer = jack_tokenizer.JackTokenizer(input_file)
        self.__out_file = open(output_file, 'w')
        self.__out = ""
        self.__num_indentation = 0
        self.compile_class()

    # ************  API of CompilationEngine  ******************8

    def compile_class(self):
        """
        compiles a whole class by calling all relevant methods
        """
        self.__init_non_terminals("class")

        self.__keyword()  # class
        self.__identifier()  # className
        self.__symbol()  # { 

        if self.__tokenizer.key_word() in {"static",
                                           "field"}:  # classVarDec in class?
            self.compile_class_var_dec()  # classVarDec

        if (self.__tokenizer.key_word() in {"constructor", "function",
                                            "method"}):  # subroutineDec in class?
            self.compile_subroutine()  # subRoutine

        self.__symbol()  # }
        self.__end_non_terminals("class")

    def compile_class_var_dec(self):
        """
        compiles class var_dec according to api
        """
        while self.__tokenizer.key_word() in {"static", "field"}:
            self.__init_non_terminals("classVarDec")
            self.__keyword()
            self.__type()
            self.__identifier()
            while self.__tokenizer.symbol() == ",":
                self.__symbol()
                self.__identifier()
            self.__symbol()
            self.__end_non_terminals("classVarDec")

    def compile_subroutine(self):
        """
        compiles subroutine calls
        """
        while self.__tokenizer.key_word() in {"constructor", "function",
                                              "method"}:
            self.__init_non_terminals("subroutineDec")
            self.__keyword()
            self.__type()
            self.__identifier()
            self.__symbol()
            # if self.__tokenizer.symbol() != ")":
            self.compile_parameter_list()
            self.__symbol()
            self.__subroutine_body()
            self.__end_non_terminals("subroutineDec")

    def compile_parameter_list(self):
        """
        compiles all list of parameters
        """
        self.__init_non_terminals("parameterList")
        while self.__tokenizer.symbol() != ")":
            self.__type()
            self.__identifier()
            if self.__tokenizer.symbol() == ",":
                self.__symbol()
        self.__end_non_terminals("parameterList")

    def compile_var_dek(self):
        """
        compiles class var_dec according to api
        """
        while self.__tokenizer.key_word() == "var":
            self.__init_non_terminals("varDec")
            self.__keyword()
            self.__type()
            self.__identifier()
            while self.__tokenizer.symbol() == ",":
                self.__symbol()
                self.__identifier()
            self.__symbol()
            self.__end_non_terminals("varDec")

    def compile_statements(self):
        """
        compiles a statement call
        """
        self.__init_non_terminals("statements")
        while self.__tokenizer.symbol() != "}" and self.__tokenizer.token_type() != "SYMBOL":
            if self.__tokenizer.key_word() == "let":
                self.compile_let()
            elif self.__tokenizer.key_word() == "if":
                self.compile_if()
            elif self.__tokenizer.key_word() == "while":
                self.compile_while()
            elif self.__tokenizer.key_word() == "do":
                self.compile_do()
            elif self.__tokenizer.key_word() == "return":
                self.compile_return()
        self.__end_non_terminals("statements")

    def compile_let(self):
        """
        compile let instruction
        """
        self.__init_non_terminals("letStatement")  # <letStatement>
        self.__keyword()  # let
        self.__identifier()  # varName
        if self.__tokenizer.symbol() == "[":
            self.__symbol()  # [
            self.compile_expression()  # expression
            self.__symbol()  # ]
        self.__symbol()  # =
        self.compile_expression()  # expression
        self.__symbol()  # ;
        self.__end_non_terminals("letStatement")  # </letStatement>

    def compile_if(self):
        """
        compile if calls
        """
        self.__init_non_terminals("ifStatement")  # <ifStatement>
        self.__keyword()  # if
        self.__symbol()  # (
        self.compile_expression()  # expression
        self.__symbol()  # )
        self.__symbol()  # {
        self.compile_statements()  # statement
        self.__symbol()  # }
        if self.__tokenizer.token_type() == "KEYWORD" and self.__tokenizer.key_word() == "else":
            self.__keyword()  # else
            self.__symbol()  # {
            self.compile_statements()  # statement
            self.__symbol()  # }
        self.__end_non_terminals("ifStatement")  # </ifStatement>

    def compile_while(self):
        """
        compile while calls
        """
        self.__init_non_terminals("whileStatement")  # <whileStatement>
        self.__keyword()  # while
        self.__symbol()  # (
        self.compile_expression()  # expression
        self.__symbol()  # )
        self.__symbol()  # {
        self.compile_statements()  # statement
        self.__symbol()  # }
        self.__end_non_terminals("whileStatement")  # </whileStatement>

    def compile_do(self):
        """
        compile do calls
        """
        self.__init_non_terminals("doStatement")  # <doStatement>
        self.__keyword()  # do
        self.__sub_routine_call()
        self.__symbol()  # ;
        self.__end_non_terminals("doStatement")  # </doStatement>

    def __sub_routine_call(self):
        """
        compile sub routine calls
        """
        self.__identifier()  # subRoutineName / className / varName
        if self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == ".":
            self.__symbol()  # .
            self.__identifier()  # subRoutineName
        self.__symbol()  # (
        self.compile_expression_list()  # expressionList
        self.__symbol()  # )

    def compile_return(self):
        """
        compile return calls
        """
        self.__init_non_terminals("returnStatement")  # <returnStatement>
        self.__keyword()  # return
        if not (
                self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == ";"):
            self.compile_expression()  # expression
        self.__symbol()  # }
        self.__end_non_terminals("returnStatement")  # </returnStatement>

    def compile_expression(self):
        """
        compile expression calls
        """
        self.__init_non_terminals("expression")
        self.compile_term()
        while self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() in CompilationEngine.OP:
            self.__symbol()
            self.compile_term()
        self.__end_non_terminals("expression")

    def compile_term(self):
        """
        compile term calls
        """
        self.__init_non_terminals("term")
        if self.__tokenizer.token_type() == "KEYWORD" and \
                self.__tokenizer.key_word() in \
                CompilationEngine.KEYWORD_CONSTANT:  # term = KeywordConstant
            self.__keyword()  # KeywordConst

        elif self.__tokenizer.token_type() == "INT_CONST":  # term = IntegerConstant
            self.__int_const()  # IntegerConst

        elif self.__tokenizer.token_type() == "STRING_CONST":  # term = StringConstant
            self.__string_const()  # StringConst

        elif self.__tokenizer.token_type() == "IDENTIFIER":  # term = VarName/SubRoutineCall
            self.__identifier()  # VarName/SubRoutineName/(ClassName|VarName)
            if self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == "[":  # [expression]
                self.__symbol()  # [
                self.compile_expression()  # expression
                self.__symbol()  # ]
            elif self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == "(":  # (expressionList)
                self.__symbol()  # (
                self.compile_expression_list()  # ExpressionList
                self.__symbol()  # )
            elif self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == ".":  # .SubRoutineName(ExpressionList)
                self.__symbol()  # .
                self.__identifier()  # SubRoutineName
                self.__symbol()  # (
                self.compile_expression_list()  # ExpressionList
                self.__symbol()  # )

        # elif self.__tokenizer.token_type() == "SYMBOL":
        elif self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == "(":  # term = (expression)
            self.__symbol()  # (
            self.compile_expression()  # expression
            self.__symbol()  # )
        elif self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() in CompilationEngine.UNARY_OP:  # term = UnaryOp term
            self.__symbol()  # UnaryOp
            self.compile_term()  # term
        self.__end_non_terminals("term")

    def compile_expression_list(self):
        """
         compile expression list calls
         """
        self.__init_non_terminals("expressionList")
        while self.__tokenizer.symbol() != ")":
            self.compile_expression()
            if self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == ",":
                self.__symbol()
                # self.compile_expression()
        self.__end_non_terminals("expressionList")

    # ***************  a private methods  ******************

    def __write(self, line):
        """
        writes in to out file
        :param line: to write to file
        """
        self.__out_file.write("  " * self.__num_indentation + line)

    def __advancer(self):
        """
        check if tokenizer has more tokens if true gets it
        :return: next token in list
        """
        if self.__tokenizer.hes_more_tokens():
            self.__tokenizer.advance()

    def __subroutine_body(self):
        """
        helper to sub routine body compiler
        :return:
        """
        self.__init_non_terminals("subroutineBody")
        self.__symbol()
        if self.__tokenizer.key_word() == "var":
            self.compile_var_dek()
        self.compile_statements()
        self.__symbol()
        self.__end_non_terminals("subroutineBody")

    def __string_const(self):
        """
        compile string constant
        """
        line = "<" + "stringConstant" + "> " + \
               self.__tokenizer.string_val() + " </" + \
               "stringConstant" + ">\n"
        self.__write(line)
        self.__advancer()

    def __int_const(self):
        """
        compiles int constant
        """
        line = "<" + "integerConstant" + "> " + \
               str(self.__tokenizer.int_val()) + " </" + \
               "integerConstant" + ">\n"
        self.__write(line)
        self.__advancer()

    def __type(self):
        """
        gets type of identifier of given token
        """
        if self.__tokenizer.token_type() == "IDENTIFIER":
            self.__identifier()
        else:
            self.__keyword()

    def __symbol(self):
        """
         changes few symbol for avoiding html crush and gets the symbol
         """
        symbol = self.__tokenizer.symbol()
        if symbol == '"':
            symbol = "&quot;"
        if symbol == '&':
            symbol = "&amp;"
        elif symbol == '<':
            symbol = "&lt;"
        elif symbol == '>':
            symbol = "&gt;"
        line = "<" + self.__tokenizer.token_type().lower() + "> " + \
               symbol + " </" + \
               self.__tokenizer.token_type().lower() + ">\n"
        self.__write(line)
        self.__advancer()
        a = self.__tokenizer.token_type()

    def __identifier(self):
        """
        writes the cur identifier
        """
        line = "<" + self.__tokenizer.token_type().lower() + "> " + \
               self.__tokenizer.identifier() + " </" + \
               self.__tokenizer.token_type().lower() + ">\n"
        self.__write(line)
        self.__advancer()

    def __keyword(self):
        """
        write keyword according to cur token
        """
        line = "<" + self.__tokenizer.token_type().lower() + "> " + \
               self.__tokenizer.key_word() + " </" + \
               self.__tokenizer.token_type().lower() + ">\n"
        self.__write(line)
        self.__advancer()

    def __init_non_terminals(self, type_terminal):
        """
        init a non terminal call by writing a new identation of code in ou file
        :param type_terminal: type of non terminal call
        """
        self.__write("<" + type_terminal + ">\n")
        self.__num_indentation += 1

    def __end_non_terminals(self, type_terminal):
        """
        ends a non terminal call by writing into end of iden part out file
        :param type_terminal: type of non terminal call
        """
        self.__num_indentation -= 1
        self.__write("</" + type_terminal + ">\n")


func notPython(){
    fmt.Println("Hi")
}
