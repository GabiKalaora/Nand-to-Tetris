import sys
import os
import compilation_engine
imp wrong


def main():
    """
     gets the input path to file or folder and checks all relevant checking
     and calling all relevant function to init compilation
     :return:
     """
    file_path = sys.argv[1]
    path_or_file = os.path.dirname(file_path)
    if path_or_file:  # stream is a path
        its_a_file = os.path.isfile(file_path)
        if its_a_file:  # path to file
            name = os.path.basename(file_path).split(".")
            file_name = name[0]
            compilation_engine.CompilationEngine(str(path_or_file) + "/" +
                                                 str(file_name) + ".jack",
                                                 str(path_or_file) + "/" +
                                                 str(file_name) + ".xml")
        else:  # path to dir
            for file in os.listdir(file_path):
                if file.endswith(".jack"):
                    name = file.split(".")
                    file_name = name[0]
                    compilation_engine.CompilationEngine(str(file_path) + "/" +
                    str(file_name) + ".jack", str(file_path) + "/" +
                                            str(file_name) + ".xml")
    else:  # stream is a not path
        if os.p
