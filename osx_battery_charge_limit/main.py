#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
import os
import os.path
import re
import sys


def get_smc_binary_path(script_directory) -> str:
    smc_directory = os.path.join(script_directory, "smc-command")

    binary_path = os.path.join(smc_directory, "smc")
    exists = os.path.exists(binary_path)
    
    if not exists:
        os.chdir(smc_directory)
        out = subprocess.run(["make"], capture_output=True)
        os.chdir("..")
        if out.returncode != 0:
            print("SMC build failed!", file=sys.stderr)
            print(out.stderr)
            exit(1)
    
    return binary_path
        

def get_arguments():
    parser = argparse.ArgumentParser(description="Macbook battery charge limit using SMC")

    parser.add_argument("-c, --current", 
                        dest="current",
                        default=False,
                        action="store_true",
                        help="Current limit value")

    parser.add_argument("-r, --reset", 
                        dest="reset",
                        default=False,
                        action="store_true",
                        help="Reset on default value (100)")

    parser.add_argument("-s, --set", 
                        dest="change", 
                        type=int,
                        default=None,
                        help="Target charge limit in percents, from 40 to 100")

    args = parser.parse_args()
    
    return args


def get_and_check_current_battery_charge_limit(smc_binary_path) -> int:
    #./smc -r -k BCLM
    get_value_out = subprocess.run([smc_binary_path, "-r", "-k", "BCLM"], capture_output=True)
    # print(get_value_out)
    if (get_value_out.returncode != 0) or (len(get_value_out.stdout) == 0):
        print("Battery limit value read failed:", file=sys.stderr)
        print(get_value_out.stderr, file=sys.stderr)
        exit(1)

    out_string = get_value_out.stdout.decode("utf-8").rstrip("\n")
    # print(out_string)

    # "  BCLM  [ui8 ]  60 (bytes 3c)"
    parse_result = re.match(r"  BCLM  \[([a-z0-9]*)\s*\]  ([0-9a-f]+) \(bytes (.+)\)", out_string)
    if parse_result is None:
        error_text = "SMC out parse failed:\nvalid \"{}\"\ncurrent \"{}\"".format(
            "  BCLM  [ui8 ]  60 (bytes 3c)", 
            out_string
        )
        print(error_text, file=sys.stderr)
        exit(1)

    #print(get_value_out.stdout)
    value_type = parse_result.group(1)
    current_value = int(parse_result.group(2))
    #bytes_value = parse_result.group(3)
    
    value_type_valid = (value_type == "ui8")
    current_value_valid = (current_value >= 20) and (current_value <= 100)
    if not value_type_valid or not current_value_valid:
        error_text = \
            "Invalid SMC output values: type = {}, value = {}\n"\
            "must be: type = {}, value = {}"\
            .format(value_type, current_value, "ui8", "20 <= val <= 100")
        print(error_text, file=sys.stderr)
        exit(1)

    return current_value


def main():
    # Директория текущего скрипта
    script_directory = os.path.dirname(os.path.realpath(__file__))
    # print(script_directory)

    # Путь к исполняемому файлику
    smc_binary_path = get_smc_binary_path(script_directory)
    # print(smc_binary_path)
    
    # Аргументы скрипта
    args = get_arguments()
    # print(args)

    if args.current:
        current_value = get_and_check_current_battery_charge_limit(smc_binary_path)
        print("Current battery charge limit is {}%".format(current_value))


if __name__ == "__main__":
    main()