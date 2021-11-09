import sys
import os
import compilation_engine


def main():
    """
    this is main function to handle all relevant functions and calls
    """
    file_path = sys.argv[1]
    path_or_file = os.path.dirname(file_path)
    if path_or_file:  # stream is a path
        its_a_file = os.path.isfile(file_path)
        if its_a_file:  # path to file
            name = os.path.basename(file_path).split(".")
            file_name = name[0]
            compilation_engine.CompilationEngine(str(path_or_file) +
                                                 str(file_name) + ".jack",
                                                 str(path_or_file) +
                                                 str(file_name) + ".vm")
        else:  # path to dir
            for file in os.listdir(file_path):
                if file.endswith(".jack"):
                    name = file.split(".")
                    file_name = name[0]
                    compilation_engine.CompilationEngine(str(file_path) + "/" +
                    str(file_name) + ".jack", str(file_path) + "/" +
                                            str(file_name) + ".vm")
    else:  # stream is a not path
        if os.path.isfile(file_path):  # it's a file
            name = file_path.split(".")
            compilation_engine.CompilationEngine(str(name[0]) + ".jack",
                                                str(name[0]) + ".vm")
        else:  # it's a dir
            abs_path = os.path.abspath(file_path)
            for file in os.listdir(abs_path):
                if file.endswith(".jack"):
                    name = file.split(".")
                    file_name = name[0]
                    compilation_engine.CompilationEngine(str(abs_path) + "/" +
                    str(file_name) + ".jack", str(abs_path) + "/" +
                                            str(file_name) + ".vm")


if __name__ == '__main__':
    main()