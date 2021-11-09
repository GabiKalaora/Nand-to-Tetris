import jack_tokenizer
import VM_writer
import symbol_table


class CompilationEngine:
    """
    compiles jack file into vm code by calling all relevant funcs and methods
    """
    OP = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
    UNARY_OP = {"-", "~"}
    KEYWORD_CONSTANT = {"TRUE", "FALSE", "NULL", "THIS"}

    # ***************  CONSTRUCTOR  ***************

    def __init__(self, input_file, output_file):
        """
        CompilationEngine constructor
        :param input_file: name of file to open and compile
        :param output_file: name of output file
        """
        self.__tokenizer = jack_tokenizer.JackTokenizer(input_file)
        self.__symbol_table = symbol_table.SymbolTable()
        self.VM_writer = VM_writer.VN_writer(output_file)
        self.__if_counter = 0
        self.__while_counter = 0
        self.__class_name = ""
        self.compile_class()

    # ************  API of CompilationEngine  ******************

    def compile_class(self):
        """
        handles compilation of class
        :return: calls relevant function t continue compilation
        """
        self.__advancer()  # class
        self.__class_name = self.__identifier()  # className
        self.__advancer()  # {

        if self.__tokenizer.key_word() in {"STATIC",
                                           "FIELD"}:  # classVarDec in class?
            self.compile_class_var_dec()  # classVarDec

        if (self.__tokenizer.key_word() in {"CONSTRUCTOR", "FUNCTION",
                                            "METHOD"}):  # subroutineDec in class?
            self.compile_subroutine()  # subRoutine
        self.__advancer()  # }

    def compile_class_var_dec(self):
        """
        handles compilation of class var dec
        :return: calls relevant function t continue compilation
        """
        while self.__tokenizer.key_word() in {"STATIC", "FIELD"}:
            kind = self.__keyword()  # static/field
            var_type = self.__type()  # var type
            name = self.__identifier()  # var name
            self.__enter_to_symbol_table(name, var_type, kind)

            while self.__tokenizer.symbol() == ",":
                self.__advancer()  # ,
                name = self.__identifier()  # var name
                self.__enter_to_symbol_table(name, var_type, kind)
            self.__advancer()  # ;

    def compile_subroutine(self):
        """
        handles compilation of subroutine calls
        :return: calls relevant function to continue compilation
        """
        while self.__tokenizer.key_word() in {"CONSTRUCTOR", "FUNCTION",
                                              "METHOD"}:
            self.__if_counter = 0
            self.__symbol_table.start_subroutine()
            sub_type = self.__keyword()  # constructor/function/method
            return_type = self.__type()  # func type
            sub_name = self.__identifier()  # func name

            if sub_type == "method":
                self.__enter_to_symbol_table("this", self.__class_name, "arg")
            self.__advancer()  # (
            self.compile_parameter_list()
            self.__advancer()  # )

            self.__subroutine_body(sub_type, sub_name)

            if return_type == "void":
                self.VM_writer.write_push("constant", 0)
            self.VM_writer.write_return()

    def compile_parameter_list(self):
        """
        handles compiling of parameter list calls
        :return: calls relevant function to continue compilation
        """
        while self.__tokenizer.symbol() != ")":
            arg_type = self.__type()
            arg_name = self.__identifier()
            self.__enter_to_symbol_table(arg_name, arg_type, "arg")
            if self.__tokenizer.symbol() == ",":
                self.__advancer()

    def compile_var_dek(self):
        """
        handles compiling of var dec calls
        :return: calls relevant function to continue compilation
        """
        num_var = 0
        while self.__tokenizer.key_word() == "VAR":
            self.__advancer()  # var
            var_type = self.__type()  # type of var
            var_name = self.__identifier()  # name of var
            self.__enter_to_symbol_table(var_name, var_type, "local")
            num_var += 1
            while self.__tokenizer.symbol() == ",":
                self.__advancer()
                var_name = self.__identifier()
                self.__enter_to_symbol_table(var_name, var_type, "local")
                num_var += 1
            self.__advancer()
        return num_var

    def compile_statements(self):
        """
        handles compilation of statements calls
        :return: calls relevant function to continue compilation
        """
        while self.__tokenizer.symbol() != "}" and self.__tokenizer.token_type() != "SYMBOL":
            if self.__tokenizer.key_word() == "LET":
                self.compile_let()
            elif self.__tokenizer.key_word() == "IF":
                self.compile_if()
            elif self.__tokenizer.key_word() == "WHILE":
                self.compile_while()
            elif self.__tokenizer.key_word() == "DO":
                self.compile_do()
            elif self.__tokenizer.key_word() == "RETURN":
                self.compile_return()

    def compile_let(self):
        """
        handles compilation of let command
        :return: calls relevant function to continue compilation
        """
        self.__advancer()  # let
        var_name = self.__identifier()
        if self.__tokenizer.symbol() == "[":

            self.__advancer()  # [
            self.compile_expression()  # expression
            self.__push(var_name)
            self.VM_writer.write_arithmetic("+")
            self.__advancer()  # ]

            self.__advancer()  # =
            self.compile_expression()
            self.VM_writer.write_pop("temp", 0)
            self.VM_writer.write_pop("pointer", 1)
            self.VM_writer.write_push("temp", 0)
            self.VM_writer.write_pop("that", 0)
        else:
            self.__advancer()  # =
            self.compile_expression()  # expression
            self.__pop(var_name)
        self.__advancer()  # ;

    def compile_if(self):
        """
        handles compilation of if command
        :return: calls relevant function to continue compilation
        """
        self.__advancer()  # if
        self.__advancer()  # (
        self.compile_expression()  # if condition
        self.__advancer()  # )
        f_label = "IF_FALSE" + str(self.__if_counter)
        t_label = "IF_TRUE" + str(self.__if_counter)
        e_label = "IF_END" + str(self.__if_counter)
        self.__if_counter += 1

        self.VM_writer.write_if(t_label)
        self.VM_writer.write_goto(f_label)
        self.VM_writer.write_label(t_label)

        self.__advancer()  # {
        self.compile_statements()  # statement
        self.__advancer()  # }

        if self.__tokenizer.token_type() == "KEYWORD" and self.__tokenizer.key_word() == "ELSE":
            self.VM_writer.write_goto(e_label)
            self.VM_writer.write_label(f_label)
            self.__advancer()  # else
            self.__advancer()  # {
            self.compile_statements()  # statement
            self.__advancer()  # }
            self.VM_writer.write_label(e_label)
        else:
            self.VM_writer.write_label(f_label)

    def compile_while(self):
        """
        handles compilation of while calls
        :return: calls relevant function to continue compilation
        """
        l_idx = self.__while_counter
        self.__while_counter += 1
        self.VM_writer.write_label("WHILE_EXP{0}".format(l_idx))
        self.__advancer()  # while
        self.__advancer()  # (
        self.compile_expression()  # expression
        self.__advancer()  # )

        self.VM_writer.write_arithmetic("~")  # not of the condition
        self.VM_writer.write_if("WHILE_END{}".format(l_idx))

        self.__advancer()  # {
        self.compile_statements()  # statement
        self.__advancer()  # }
        self.VM_writer.write_goto("WHILE_EXP{0}".format(l_idx))
        self.VM_writer.write_label("WHILE_END{}".format(l_idx))

    def compile_do(self):
        """
        handles compilation of do commands
        :return: calls relevant function to continue compilation
        """
        self.__advancer()  # do
        name = self.__identifier()  # subRoutineName / className / varName
        self.__subroutine_call(name)
        self.VM_writer.write_pop("temp",0)

        self.__advancer()  # ;

    def compile_return(self):
        """
        handles compilation of return commands
        :return: calls relevant function to continue compilation
        """
        self.__advancer()  # return
        if not (
                self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == ";"):
            self.compile_expression()  # expression
        self.__advancer()  # }

    def compile_expression(self):
        """
        handles compilation of expressions
        :return: calls relevant function to continue compilation
        """
        self.compile_term()
        while self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() in CompilationEngine.OP:
            symbol_arithmetic = self.__symbol()
            self.compile_term()
            self.VM_writer.write_arithmetic(symbol_arithmetic)

    def compile_term(self):
        """
        hndles compilation of terms
        :return: calls relevant function to continue compilation
        """
        if self.__tokenizer.token_type() == "KEYWORD" and \
                self.__tokenizer.key_word() in \
                CompilationEngine.KEYWORD_CONSTANT:  # term = KeywordConstant
            cur_keyword = self.__keyword()
            if cur_keyword == "true":
                self.VM_writer.write_push("constant", 0)
                self.VM_writer.write_arithmetic("~")
            elif cur_keyword == "this":
                self.VM_writer.write_push("pointer", 0)
            else:
                self.VM_writer.write_push("constant", 0)


        elif self.__tokenizer.token_type() == "INT_CONST":  # term = IntegerConstant
            self.VM_writer.write_push("constant", self.__int_const())

        elif self.__tokenizer.token_type() == "STRING_CONST":  # term = StringConstant
            self.VM_writer.write_string(self.__string_const())  # StringConst

        elif self.__tokenizer.token_type() == "IDENTIFIER":  # term = VarName/SubRoutineCall
            name = self.__identifier()  # VarName/SubRoutineName/(ClassName|VarName)
            if self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == "[":  # [expression] = it's array
                self.__advancer()  # [
                self.__is_array(name)  # expression of array
                self.__advancer()  # ]
            elif self.__tokenizer.token_type() == "SYMBOL" and \
                    (self.__tokenizer.symbol() == "(" or self.__tokenizer.symbol() == "."):
                self.__subroutine_call(name)  # ExpressionList
            else:
                self.__push(name)
        elif self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == "(":  # term = (expression)
            self.__advancer()  # (
            self.compile_expression()  # expression
            self.__advancer()  # )
        elif self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() in CompilationEngine.UNARY_OP:  # term = UnaryOp term
            symbol = self.__symbol()  # UnaryOp
            self.compile_term()  # term
            if symbol == "-":
                symbol = "--"
            self.VM_writer.write_arithmetic(symbol)

    def __subroutine_call(self, name):
        """
        subroutine compilation helper
        :param name: name of subroutine call
        :return: calls relevant function to continue compilation
        """
        num_param = 0
        if self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == ".":
            self.__advancer()  # .
            method_name = self.__identifier()  # subRoutineName
            if self.__symbol_table.kind_of(
                    name) is None:  # name is a class name
                call = "{0}.{1}".format(name, method_name)
            else:  # name is a var of a class name
                call = "{0}.{1}".format(self.__symbol_table.type_of(name),
                                        method_name)
                num_param += 1  # parameter of this
                self.__push(name)
        else:
            self.VM_writer.write_push("pointer", 0)
            call = "{0}.{1}".format(self.__class_name, name)
            num_param += 1  # parameter of this

        self.__advancer()  # (
        num_param += self.compile_expression_list()  # expressionList
        self.__advancer()  # )

        self.VM_writer.write_call(call, num_param)

    def compile_expression_list(self):
        num_exp = 0
        while self.__tokenizer.symbol() != ")":
            num_exp += 1
            self.compile_expression()
            if self.__tokenizer.token_type() == "SYMBOL" and self.__tokenizer.symbol() == ",":
                self.__advancer()  # ,
        return num_exp

    # ***************  a private methods  ******************

    def __subroutine_body(self, sub_type, sub_name):
        """
        helper for subroutine compilation
        :param sub_type: type of subroutine
        :param sub_name: name of subroutine call
        """
        self.__advancer()  # {
        num_var = 0
        if self.__tokenizer.key_word() == "VAR":
            num_var = self.compile_var_dek()
        name = "{0}.{1}".format(self.__class_name, sub_name)
        self.VM_writer.write_function(name, num_var)

        if sub_type == "method":
            self.VM_writer.write_push("argument", 0)
            self.VM_writer.write_pop("pointer", 0)

        if sub_type == "constructor":
            self.VM_writer.write_push("constant",
                                      self.__symbol_table.var_count("field"))
            self.VM_writer.write_call("Memory.alloc", 1)
            self.VM_writer.write_pop("pointer", 0)

        self.compile_statements()
        self.__advancer()  # }

    def __enter_to_symbol_table(self, name, var_type, kind):
        """
        sets values in symbol table
        """
        self.__symbol_table.define(name, var_type, kind)

    def __is_array(self, name):
        self.compile_expression()
        self.__push(name)
        self.VM_writer.write_arithmetic(
            '+')  # add expression to base adders of array
        self.VM_writer.write_pop("pointer", 1)  # enter it to THAT
        self.VM_writer.write_push("that", 0)

    def __push(self, name):
        """
        helper for push oriented commands
        :param name: to push
        """
        kind = str(self.__symbol_table.kind_of(name)).upper()
        if kind is not None:
            index = self.__symbol_table.index_of(name)
            if kind == "FIELD":
                self.VM_writer.write_push("this", index)
            elif kind == "STATIC":
                self.VM_writer.write_push("static", index)
            elif kind == "LOCAL":
                # print("******** ", "local ", index)
                self.VM_writer.write_push("local", index)
            elif kind == "ARG":
                self.VM_writer.write_push("argument", index)

    def __pop(self, name):
        """
        helper for pop oriented commands
        :param name: to pop
        """
        kind = self.__symbol_table.kind_of(name).upper()
        if kind is not None:
            index = self.__symbol_table.index_of(name)
            if kind == "FIELD":
                self.VM_writer.write_pop("this", index)
            elif kind == "STATIC":
                self.VM_writer.write_pop("static", index)
            elif kind == "LOCAL":
                self.VM_writer.write_pop("local", index)
            elif kind == "ARG":
                self.VM_writer.write_pop("argument", index)

    def __int_const(self):
        """
        helper for constant int compilation
        """
        int_const = self.__tokenizer.int_val()
        self.__advancer()
        return int_const

    def __string_const(self):
        """
        helper for string constant compilation
        """
        str_const = self.__tokenizer.string_val()
        self.__advancer()
        return str_const

    def __advancer(self):
        """
        advances pointer to next token
        """
        if self.__tokenizer.hes_more_tokens():
            self.__tokenizer.advance()

    def __identifier(self):
        """
        gets the identifier
        """
        identifier = self.__tokenizer.identifier()
        self.__advancer()
        return identifier

    def __keyword(self):
        """
        gets the keyword of current tokenizer
        """
        keyword = self.__tokenizer.key_word().lower()
        self.__advancer()
        return keyword

    def __symbol(self):
        """
        gets the symbol of current tokenizer
        """
        symbol = self.__tokenizer.symbol()
        self.__advancer()
        return symbol

    def __type(self):
        """
        gets the type of current tokenizer
        """
        if self.__tokenizer.token_type() == "IDENTIFIER":
            return self.__identifier()
        else:
            return self.__keyword()
