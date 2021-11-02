from Parser import Parser
from pathlib import Path
import sys
import os


class CodeWriter:
    segments = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT",
        "temp": "5",
        "adders": "R13"
    }

    def __init__(self, stream):
        self.__stream = stream
        self.__file_name = ""
        self.__parser = None
        self.__type = ""
        self.__arg1 = ""
        self.__index = ""
        self.__out = ""
        self.__label_counter = 0
        self.__func_name = ""

    def __new_line(self):
        self.__parser.advance()
        self.__type = self.__parser.commend_type()
        self.__arg1 = self.__parser.arg1()
        self.__index = str(self.__parser.arg2())

    def __write(self, stream):
        self.__parser = Parser(stream)
        while self.__parser.hes_more_commands():
            self.__new_line()
            if self.__type == "C_ARITHMETIC":
                self.write_arithmetic(self.__arg1)
            elif self.__type == "C_PUSH" or self.__type == "C_POP":
                self.write_push_pop(self.__type, self.__arg1,self.__index)
            elif self.__type == "C_LABEL":
                self.write_label(self.__arg1)
            elif self.__type == "C_GOTO":
                self.write_goto(self.__arg1)
            elif self.__type == "C_IF":
                self.write_if(self.__arg1)
            elif self.__type == "C_FUNCTION":
                self.write_function(self.__arg1, self.__index)
            elif self.__type == "C_RETURN":
                self.write_return()
            elif self.__type == "C_CALL":
                self.write_call(self.__arg1, self.__index)

    def set_file_name(self, stream):  # not work with path only explicit file
        path_or_file = os.path.dirname(stream)
        if path_or_file:  # stream is path
            its_a_file = os.path.isfile(stream)
            if its_a_file:  # path with file ending
                name = os.path.basename(stream).split(".")
                self.__file_name = name[0]
                self.__out = open(str(path_or_file) + "/" +
                                  str(self.__file_name) + ".asm", 'w')
                self.__write(stream)
            else:  # path to dir
                name = Path(stream)
                add = name.stem
                self.__file_name = add
                self.__out = open(str(name) + "/" + add + ".asm", 'w')
                for entry in os.scandir(stream):
                    if entry.path.endswith(".vm"):
                        self.__file_name = os.path.basename(entry)
                        self.__write(entry)
        else:  # stream is a not path
            if os.path.isfile(stream):  # it's a file
                name = stream.split(".")
                self.__file_name = name[0]
                self.__out = open(str(self.__file_name) + ".asm", 'w')
                self.__write(stream)
            else:  # it's a dir
                abs_path = os.path.abspath(stream)
                self.__out = open(abs_path + "/" + stream + ".asm", 'w')
                for file in os.listdir(stream):
                    if file.endswith(".vm"):
                        self.__file_name = file
                        self.__write(abs_path + "/" + file)


    def __arithmetic_helper(self, commend):
        line = "// " + commend + "\n"
        if commend == "add":
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "M=M+D\n"
        elif commend == "sub":
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "M=M-D\n"
        elif commend == "neg":
            line += "@SP\n"
            line += "A=M-1\n"
            line += "M=-M\n"
        elif commend == "eq":
            self.__label_counter += 1
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@13\n"
            line += "M=D\n"
            line += "@Y_NEG" + str(self.__label_counter) + "\n"
            line += "D;JLT\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "D=M\n"
            line += "@BOTH" + str(self.__label_counter) + "\n"
            line += "D;JGE\n"
            # " ***  y > x  ***"
            line += "@NOT_EQ" + str(self.__label_counter) + "\n"
            line += "0;JMP\n"
            line += "(Y_NEG" + str(self.__label_counter) + ")\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "D=M\n"
            line += "@BOTH" + str(self.__label_counter) + "\n"
            line += "D;JLT\n"
            # "***  x > y  ***"
            line += "@NOT_EQ" + str(self.__label_counter) + "\n"
            line += "0;JMP\n"
            line += "(BOTH" + str(self.__label_counter) + ")\n"
            line += "@13\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "D=M-D\n"
            line += "M=-1\n"
            line += "@END" + str(self.__label_counter) + "\n"
            line += "D;JEQ\n"
            line += "(NOT_EQ" + str(self.__label_counter) + ")\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "M=0\n"
            line += "(END" + str(self.__label_counter) + ")\n"
        elif commend == "gt":
            self.__label_counter += 1
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@13\n"
            line += "M=D\n"
            line += "@Y_NEG" + str(self.__label_counter) + "\n"
            line += "D;JLT\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "D=M\n"
            line += "@BOTH" + str(self.__label_counter) + "\n"
            line += "D;JGE\n"
            # " ***  y > x  ***"
            line += "@NOT_GT" + str(self.__label_counter) + "\n"
            line += "0;JMP\n"
            line += "(Y_NEG" + str(self.__label_counter) + ")\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "D=M\n"
            line += "@BOTH" + str(self.__label_counter) + "\n"
            line += "D;JLE\n"
            # "***  x > y  ***"
            line += "@GT" + str(self.__label_counter) + "\n"
            line += "0;JMP\n"
            line += "(BOTH" + str(self.__label_counter) + ")\n"
            line += "@13\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "D=M-D\n"
            line += "(GT" + str(self.__label_counter) + ")\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "M=-1\n"
            line += "@END" + str(self.__label_counter) + "\n"
            line += "D;JGT\n"
            line += "(NOT_GT" + str(self.__label_counter) + ")\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "M=0\n"
            line += "(END" + str(self.__label_counter) + ")\n"
        elif commend == "lt":
            self.__label_counter += 1
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@13\n"
            line += "M=D\n"
            line += "@Y_NEG" + str(self.__label_counter) + "\n"
            line += "D;JLT\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "D=M\n"
            line += "@BOTH" + str(self.__label_counter) + "\n"
            line += "D;JGE\n"
            # " ***  y > x  ***"
            line += "@LT" + str(self.__label_counter) + "\n"
            line += "0;JMP\n"
            line += "(Y_NEG" + str(self.__label_counter) + ")\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "D=M\n"
            line += "@BOTH" + str(self.__label_counter) + "\n"
            line += "D;JLT\n"
            # "***  x > y  ***"
            line += "@NOT_LT" + str(self.__label_counter) + "\n"
            line += "0;JMP\n"
            line += "(BOTH" + str(self.__label_counter) + ")\n"
            line += "@13\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "D=M-D\n"
            line += "(LT" + str(self.__label_counter) + ")\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "M=-1\n"
            line += "@END" + str(self.__label_counter) + "\n"
            line += "D;JLT\n"
            line += "(NOT_LT" + str(self.__label_counter) + ")\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "M=0\n"
            line += "(END" + str(self.__label_counter) + ")\n"
        elif commend == "and":
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "M=M&D\n"
        elif commend == "or":
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "A=M-1\n"
            line += "M=M|D\n"
        elif commend == "not":
            line += "@SP\n"
            line += "A=M-1\n"
            line += "M=!M\n"
        return line

    def write_arithmetic(self, arithmetic_command):
        line = self.__arithmetic_helper(arithmetic_command)
        self.__out.write(line)

    def __push_helper(self, segment, index):
        line = "// push " + segment + " " + index + "\n"
        if segment == "constant":
            line += "@" + index + "\n"
            line += "D=A\n"
            line += "@SP\n"
            line += "A=M\n"
            line += "M=D\n"
            line += "@SP\n"
            line += "M=M+1\n"
        elif segment == "pointer":
            flag = "this" if index == "0" else "that"
            line += "@" + CodeWriter.segments[flag] + "\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "A=M\n"
            line += "M=D\n"
            line += "@SP\n"
            line += "M=M+1\n"
        elif segment == "static":
            line += "@" + self.__file_name + "." + index + "\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "A=M\n"
            line += "M=D\n"
            line += "@SP\n"
            line += "M=M+1\n"
        elif segment == "temp":
            line += "@" + CodeWriter.segments[segment] + "\n"
            line += "D=A\n"
            line += "@" + index + "\n"
            line += "A=D+A\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "A=M\n"
            line += "M=D\n"
            line += "@SP\n"
            line += "M=M+1\n"
        else:
            line += "@" + CodeWriter.segments[segment] + "\n"
            line += "D=M\n"
            line += "@" + index + "\n"
            line += "A=D+A\n"
            line += "D=M\n"
            line += "@SP\n"
            line += "A=M\n"
            line += "M=D\n"
            line += "@SP\n"
            line += "M=M+1\n"
        return line

    def __pop_helper(self, segment, index):
        line = "// pop " + segment + " " + index + "\n"
        if segment == "static":
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@" + self.__file_name + "." + index + "\n"
            line += "M=D\n"
        elif segment == "pointer":
            flag = "this" if index == "0" else "that"
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@" + CodeWriter.segments[flag] + "\n"
            line += "M=D\n"
        elif segment == "temp":
            line += "@" + CodeWriter.segments[segment] + "\n"
            line += "D=A\n"
            line += "@" + index + "\n"
            line += "D=D+A\n"
            line += "@" + CodeWriter.segments["adders"] + "\n"
            line += "M=D\n"
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@" + CodeWriter.segments["adders"] + "\n"
            line += "A=M\n"
            line += "M=D\n"
        else:
            line += "@" + CodeWriter.segments[segment] + "\n"
            line += "D=M\n"
            line += "@" + index + "\n"
            line += "D=D+A\n"
            line += "@" + CodeWriter.segments["adders"] + "\n"
            line += "M=D\n"
            line += "@SP\n"
            line += "AM=M-1\n"
            line += "D=M\n"
            line += "@" + CodeWriter.segments["adders"] + "\n"
            line += "A=M\n"
            line += "M=D\n"
        return line

    def write_push_pop(self, command, segment, index):
        if command == "C_PUSH":
            line = self.__push_helper(segment, index)
        else:
            line = self.__pop_helper(segment, index)
        self.__out.write(line)
        return

    def close(self):
        self.__out.close()

    def write_init(self):
        line = '// init\n'
        line += "@256\n"
        line += "D=A\n"
        line += "@SP\n"
        line += "M=D\n"
        self.__out.write(line)
        self.write_call("Sys.init", 0)

    def write_label(self, label_name):
        line = "(" + self.__func_name + "$" + label_name + ")\n"
        self.__out.write(line)

    def write_goto(self, label_name):
        line = "// goto " + self.__func_name + "$"+ label_name + "\n"
        line += "@" + self.__func_name + "$" + label_name + "\n"
        line += "0;JMP\n"
        self.__out.write(line)

    def write_if(self, label_name):
        line = "// if-goto " + self.__func_name + "$"+ label_name + "\n"
        line += "@SP\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@" + self.__func_name + "$" + label_name + "\n"
        line += "D;JNE\n"
        self.__out.write(line)

    def write_call(self, func_name, num_args):
        self.__label_counter += 1
        line = "//call " + func_name + "\n"
        line += "@" + self.__func_name + "$" + "RETURN_ADDERS" + str(self.__label_counter) + "\n"
        line += "D=A\n"
        line += "@SP\n"
        line += "A=M\n"
        line += "M=D\n"
        line += "@SP\n"
        line += "M=M+1\n"

        line += "@LCL\n"
        line += "D=M\n"
        line += "@SP\n"
        line += "A=M\n"
        line += "M=D\n"
        line += "@SP\n"
        line += "M=M+1\n"

        line += "@ARG\n"
        line += "D=M\n"
        line += "@SP\n"
        line += "A=M\n"
        line += "M=D\n"
        line += "@SP\n"
        line += "M=M+1\n"

        line += "@THIS\n"
        line += "D=M\n"
        line += "@SP\n"
        line += "A=M\n"
        line += "M=D\n"
        line += "@SP\n"
        line += "M=M+1\n"

        line += "@THAT\n"
        line += "D=M\n"
        line += "@SP\n"
        line += "A=M\n"
        line += "M=D\n"
        line += "@SP\n"
        line += "M=M+1\n"

        line += "@" + str(int(num_args) + 5) + '\n'
        line += "D=A\n"
        line += "@SP\n"
        line += "D=M-D\n"
        line += "@ARG\n"
        line += "M=D\n"

        line += "@SP\n"
        line += "D=M\n"
        line += "@LCL\n"
        line += "M=D\n"
        line += "@" + func_name + "\n"
        line += "0;JMP\n"
        self.__out.write(line)
        # self.write_goto(func_name)
        self.write_label("RETURN_ADDERS" + str(self.__label_counter))

    def write_return(self):
        self.__label_counter += 1
        line = '// return\n'
        # frame = LCL
        line += "@LCL\n"
        line += "D=M\n"
        line += "@R13\n"
        line += "M=D\n"
        # ret = *(frame -5)
        line += "@5\n"
        line += "A=D-A\n"
        line += "D=M\n"
        line += "@R14\n"
        line += "M=D\n"
        # *arg = pop()
        line += "@SP\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@ARG\n"
        line += "A=M\n"
        line += "M=D\n"
        # sp = arg + 1
        line += "@ARG\n"
        line += "D=M+1\n"
        line += "@SP\n"
        line += "M=D\n"
        # that = *(frame - 1)
        line += "@R13\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@THAT\n"
        line += "M=D\n"
        # this = *(frame -2)
        line += "@R13\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@THIS\n"
        line += "M=D\n"
        # arg = *(frame - 3)
        line += "@R13\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@ARG\n"
        line += "M=D\n"
        # lcl = *(frame - 4)
        line += "@R13\n"
        line += "AM=M-1\n"
        line += "D=M\n"
        line += "@LCL\n"
        line += "M=D\n"
        # goto ret
        line += "@14\n"
        line += "A=M\n"
        line += "0;JMP\n"
        self.__out.write(line)

    def write_function(self, func_name, num_locals):
        line = '// function' + str(func_name) + '\n'
        self.__func_name = func_name
        # self.write_label(func_name)
        line += "(" + func_name + ")\n"
        for i in range(int(num_locals)):
            line += "@SP\n"
            line += "A=M\n"
            line += "M=0\n"
            line += "@SP\n"
            line += "M=M+1\n"
        self.__out.write(line)


def main():
    source = sys.argv[1]
    x = CodeWriter(source)
    x.set_file_name(source)
    x.close()


if __name__ == '__main__':
    main()
