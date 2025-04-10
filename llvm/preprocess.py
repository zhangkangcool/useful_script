#!/usr/bin/env python3

import argparse
import os

'''
将一行输入文件，可以由opt -S input.ll -o output.ll -O1 -debug-pass=Structure得到
转为为一个pass占用一行。
'''

passname_file = "passname.txt"
output_file = "preprocess_" + passname_file

def handle_arg():
    parser = argparse.ArgumentParser(description="Preprocess the opt arg")
    parser.add_argument("passname_file", nargs = '?', help="The passname file name", default = "passname.txt")
    args = parser.parse_args()
    global passname_file, output_file
    passname_file = args.passname_file


def convert_file(passname_file):
    try:
        # 打开文件并读取内容
        with open(passname_file, 'r') as file_a:
            content = file_a.read()

        # 处理内容
        lines = content.split()

        # 打开文件 B 并写入处理后的内容
        output_file = "preprocess_" + passname_file
        with open(output_file, 'w') as file_b:
            for line in lines:
                file_b.write(line + '\n')

        print(f"Has written {output_file} successfully")
    except FileNotFoundError:
        print(f"Error：Can't find the file {passname_file}")
    except Exception as e:
        print(f"Unknown error：{e}")


# 返回list，list中的每个元素是一个还一个pass_info,其实就是preprocess_passname_file文件中的一行
# 该函数是给其他函数提供的接口
# 传入的preprocess_file = preprocess_passname.txt
def get_pass_info_list(preprocess_file):
    if not os.path.exists(preprocess_file):
        # 提取passname_file
        passname_file = "_".join(preprocess_file.split('_')[1:])
        convert_file(passname_file)

    try:
        # Open the file in read mode
        with open(preprocess_file, 'r') as file:
            # Read all lines of the file into a list
            pass_info = file.readlines()
            # Remove the newline character at the end of each line
            pass_info = [line.strip() for line in pass_info]
        # Print a prompt indicating that the file content has been successfully read into the list
        print("File content has been successfully read into the list.")
        return pass_info
    except FileNotFoundError:
        # Print an error message if the file is not found
        print("Error: The specified file was not found.")
        return []
    except Exception as e:
        # Print an error message if an unknown error occurs
        print(f"An unknown error occurred: {e}")
        return []


def main():
    global passname_file
    handle_arg()
    convert_file(passname_file)
    print(get_pass_info_list(output_file))
#    print(get_pass_info_list("preprocess_test.txt"))


if __name__ == "__main__":
    main();
