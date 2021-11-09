class VN_writer:
    """
    class VN_writer aids in translating after compilation from jack to vm code
    """
    def __init__(self, output_file):
        self.__file = open(output_file, 'w')

    def write_push(self, segment, index):
        """
        handles push command in the vm files code
        :param segment: to push to
        :param index: where to push
        """
        line = "push {0} {1}\n".format(segment, index)
        self.__writer(line)

    def write_pop(self, segment, index):
        """
        handles pop command in vm file code
        :param segment: to po from
        :param index: from where to pop
        :return:
        """
        line = "pop {0} {1}\n".format(segment, index)
        self.__writer(line)

    def write_arithmetic(self, command):
        """
        handles arithmetic command in vm code for vm file
        :param command: typeof arithmetic command
        """
        line = ""
        if command == "+":
            line += "add\n"
        elif command == "-":
            line += "sub\n"
        elif command == "--":
            line += "neg\n"
        elif command == "=":
            line += "eq\n"
        elif command == ">":
            line += "gt\n"
        elif command == "<":
            line += "lt\n"
        elif command == "&":
            line += "and\n"
        elif command == "|":
            line += "or\n"
        elif command == "~":
            line += "not\n"
        elif command == "*":
            line = "call Math.multiply 2\n"
        elif command == "/":
            line = "call Math.divide 2\n"
        self.__writer(line)

    def write_label(self, label):
        """
        writes labels in vm for vm files
        :param label: to write in vm
        """
        line = "label {0}\n".format(label)
        self.__writer(line)

    def write_goto(self, label):
        """
        handles goto commands in vm for vm files
        :param label: to make goto command on
        """
        line = "goto {0}\n".format(label)
        self.__writer(line)

    def write_if(self, label):
        """
        handles if commands in vm for vm files
        :param label: to make if command on
        """
        line = "if-goto {0}\n".format(label)
        self.__writer(line)

    def write_call(self, name, n_args):
        """
        handles call commands in vm for vm files gets name of func
        call and the num of arguments
        """
        line = "call {0} {1}\n".format(name, n_args)
        self.__writer(line)

    def write_function(self, name, n_locals):
        """
        handles function commands in vm for vm files gets name of func
        call and the num of arguments
        """
        line = "function {0} {1}\n".format(name, n_locals)
        self.__writer(line)

    def write_return(self):
        """
        write return in vm file
        """
        line = "return\n"
        self.__writer(line)

    def write_string(self, string):
        """
        handles strings pushing and adding for the vm file
        :param string: to add to vm file
        """
        self.write_push("constant", len(string))
        self.write_call("String.new", 1)
        for c in string:
            self.write_push("constant", ord(c))
            self.write_call("String.appendChar", 2)

    def close(self):
        """
        closes file
        """
        self.__file.close()

    # ******************    private methods    ******************#

    def __writer(self, line):
        """
        writes lie of vm code in to the appropriate file
        :param line: to write ito vm code file
        """
        self.__file.write(line)
