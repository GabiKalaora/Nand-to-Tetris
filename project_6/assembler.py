import sys
import os
"""
values of all type of comp  from ASM to ML
"""
comp = {"0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "!D": "0001101",
        "!A": "0110001",
        "-D": "0001111",
        "-A": "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",
        "M": "1110000",
        "!M": "1110001",
        "-M": "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101",
        "D*A": "0000000",
        "D*M": "1000000",
        "<<D": "0110000",
        "<<A": "0100000",
        "<<M": "1100000",
        ">>D": "0010000",
        ">>A": "0000000",
        ">>M": "1000000"}

"""
all dest vals translated to ML
"""
dest = {"null": "000",
        "M": "001",
        "D": "010",
        "A": "100",
        "MD": "011",
        "AM": "101",
        "AD": "110",
        "AMD": "111"}

"""
all jump instructions from ASM to ML
"""
jump = {"null": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111"}
"""
all commands needed for extended ALU
"""
extend_alu = {"mul": "10",
              "shift": "01",
              "null": "11"}


def initial_table(table):
    """
    init table with fixed memmory locations
    :param table: empty msp to init
    :return: None
    """
    table["SP"] = 0
    table["LCL"] = 1
    table["ARG"] = 2
    table["THIS"] = 3
    table["THAT"] = 4
    table["SCREEN"] = 16384
    table["KBD"] = 24576

    for i in range(16):
        ram = "R" + str(i)
        table[ram] = i
    return


def remove_whitespace(line, line_counter, table):
    """
    removes all wight spaces form line in VM code
    :param line: line to remove wight space from
    :param line_counter: gets the num of this line to add to file
    :param table: table of vals  to add to
    :return: a line with out white spaces
    """
    my_line = ""
    i = 0
    x = line[i]
    while x != '\n' and x != '/':
        if x != " ":
            my_line += x
        i += 1
        x = line[i]
    if "(" in my_line:
        temp_str = my_line[1:-1]
        table[temp_str] = line_counter
        my_line = ""
    return my_line


def c_parser(line):
    """
    parsers all c type commands
    :param line: line to parse
    :return: a list of c instructions parsed from line
    """
    instruction_list = []
    split_line1 = line.split("=")
    split_line2 = line.split(";")
    if len(split_line1) == 2:
        dest = split_line1[0]
        if ">" in split_line1[1] or "<" in split_line1[1]:
            extend = "shift"
        elif "*" in split_line1[1]:
            extend = "mul"
        else:
            extend = "null"
        if ";" in split_line1[1]:
            split11 = split_line1[1].split(";")
            comp = split11[0]
            jump = split11[1]
        else:
            comp = split_line1[1]
            jump = "null"
    else:
        dest = "null"
        comp = split_line2[0]
        jump = split_line2[1]
        extend = "null"
    instruction_list.extend((extend, comp, dest, jump))
    return instruction_list


def first_pass(file_name, table):
    """
    first pass removes all whits spaces and init tabeles
    :param file_name: file name or path of file to open
    :param table: table to update vals to
    :return: a list of list each list holdes a line values
    """
    input_file = open(file_name + ".asm")
    temp_list = []
    line_counter = 0
    for line in input_file:
        x = remove_whitespace(line, line_counter, table)
        if x != "":
            line_counter += 1
            temp_list.append(x)
    input_file.close()
    return temp_list


def second_pass(file_name, temp_list, table):
    """
    second pass on data from file
    :param file_name: file name for output file name
    :param temp_list: list of list with all lines in it to translate to ML
    :param table: table of vals to update and get vals from
    :return: None
    """
    out_file = open(file_name + ".hack", 'w')
    num_reg = [16]
    for line in temp_list:
        if line[0] == "@":

            x = a_instruction(line, num_reg, table)
        else:
            x = c_instruction(line)

        out_file.write(x)
    out_file.close()


def c_instruction(line):
    """
    translates all c instructions according to table vals
    :param line: c line command to translate
    :return: binary val to insert in output file
    """
    instruction_list = c_parser(line)
    binary_val = "1" + extend_alu[instruction_list[0]] + comp[instruction_list
    [1]] + dest[instruction_list[2]] + jump[instruction_list[3]] + "\n"
    return binary_val


def a_instruction(line, reg_num, table):
    """
    translates all a instructions
    :param line: a line command to translate
    :param reg_num: register to update
    :param table: table of content to get data from
    :return: translated A command line for output file
    """
    if line[1].isdigit():
        out_line = bin(int(line[1:])).replace("b", "").zfill(16)
    else:
        symb = line[1:]
        if symb in table.keys():
            y = table[symb]
            out_line = bin(y).replace("b", "").zfill(16)
        else:
            table[symb] = reg_num[0]
            out_line = bin(reg_num[0]).replace("b", "").zfill(16)
            reg_num[0] += 1
    return str(out_line) + "\n"


def main():
    """
    gets sys[1] and calls all relevant functions with path or dir
    handel both absolute path and relative paths
    :return: None
    """
    list_of_files = []
    file_path = sys.argv[1]
    path_or_file = os.path.dirname(file_path)
    if path_or_file:  # stream is a path
        its_a_file = os.path.isfile(file_path)
        if its_a_file:  # path to file
            name = os.path.basename(file_path).split(".")
            file_name = name[0]
            list_of_files.append(path_or_file + "/" + str(file_name))
        else:  # path to dir
            for file in os.listdir(file_path):
                if file.endswith(".asm"):
                    name = file.split(".")
                    file_name = name[0]
                    list_of_files.append(file_path + "/" + file_name)
    else:  # stream is a not path
        if os.path.isfile(file_path):  # it's a file
            list_of_files.append(file_path.split(".")[0])
        else:  # it's a dir
            abs_path = os.path.abspath(file_path)
            for file in os.listdir(abs_path):
                if file.endswith(".asm"):
                    list_of_files.append(abs_path + "/" + str(file.split(".")[0]))

    for file in list_of_files:
        symbol_table = {}
        initial_table(symbol_table)
        lst = first_pass(file, symbol_table)
        second_pass(file, lst, symbol_table)



if __name__ == '__main__':
    main()
