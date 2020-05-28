#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
import os
import os.path


def build_bash_wrapper(result_folder, compiler_path, compiler_args, use_distcc, use_ccache, distcc_path, ccache_path) -> str:
    if compiler_path and compiler_args:
        compiler_text=" {compiler_path} {compiler_args}".format(compiler_path=compiler_path, compiler_args=compiler_args)
    elif compiler_path:
        compiler_text=" {compiler_path}".format(compiler_path=compiler_path)
    else:
        compiler_text=""

    if use_ccache and use_distcc:
        text = ""\
        "#!/usr/bin/env bash\n"\
        "export CCACHE_PREFIX=\"{distcc_path}\"\n"\
        "exec {ccache_path}{compiler_text} \"$@\"\n"\
        .format( distcc_path=distcc_path, 
                    ccache_path=ccache_path, 
                    compiler_text=compiler_text)
    elif use_ccache:
        text = ""\
        "#!/usr/bin/env bash\n"\
        "exec {ccache_path}{compiler_text} \"$@\"\n"\
        .format( ccache_path=ccache_path, 
                    compiler_text=compiler_text)
    elif use_distcc:
        text = ""\
        "#!/usr/bin/env bash\n"\
        "exec {distcc_path}{compiler_text} \"$@\"\n"\
        .format( distcc_path=distcc_path, 
                    compiler_text=compiler_text)
    else:
        text = ""\
        "#!/usr/bin/env bash\n"\
        "exec{compiler_text} \"$@\"\n"\
        .format( compiler_text=compiler_text)

    if result_folder:
        if not os.path.exists(result_folder):
            os.makedirs(result_folder)

        file_path = os.path.join(result_folder, "compiler_wrapper.sh")
        with open(file_path, "w") as file:
            file.write(text)

        return file_path        
    else:
        return None


def build_c_wrapper(result_folder, compiler_path, compiler_args: str, use_distcc, use_ccache, distcc_path, ccache_path) -> str:
    compiler_path = None

    clang_out = subprocess.run(["which", "clang"], capture_output=True)
    if (clang_out.returncode == 0) and (len(clang_out.stdout) > 1):
        compiler_path = clang_out.stdout.decode("utf-8").rstrip("\n")
    else:
        gcc_out = subprocess.run(["which", "gcc"], capture_output=True)
        if (gcc_out.returncode == 0) and (len(gcc_out.stdout) > 1):
            compiler_path = gcc_out.stdout.decode("utf-8").rstrip("\n")

    if not compiler_path:
        return None
    
    if use_ccache and use_distcc:
        args = ""
        prefixes_count = 0

        args += "args_new[index++] = \"{}\";\n".format(ccache_path)
        prefixes_count += 1
        
        if compiler_path:
            args += "args_new[index++] = \"{}\";\n".format(compiler_path)
            prefixes_count += 1

            compiler_args_array = compiler_args.split(" ")
            for param in compiler_args_array:
                prefixes_count += 1
                args += "args_new[index++] = \"{}\";\n".format(param)

        text = ""\
        "#include <stdio.h>                                 \n"\
        "#include <stdlib.h>                                \n"\
        "#include <unistd.h>                                \n"\
        "#include <errno.h>                                \n"\
        "int main(int argc, char* argv[]){{                  \n"\
        "    putenv(\"CCACHE_PREFIX={distcc_path}\");          \n"\
        "    const int prefixes = {prefixes_count};         \n"\
        "    char** args_new = (char**)malloc(sizeof(char*) * (argc + prefixes + 1)); \n"\
        "    int index = 0;                                  \n"\
        "    {args}                                          \n"\
        "    for(int j = 1; j < argc; j++){{              \n"\
        "         args_new[index++] = argv[j];                     \n"\
        "    }}                                               \n"\
        "    args_new[index] = NULL;                     \n"\
        "    if (execvp(args_new[0], args_new) != 0){{        \n"\
        "         return -1;                                 \n"\
        "    }}                                               \n"\
        "    return errno;                                   \n"\
        "}};\n"\
        .format( distcc_path=distcc_path, 
                 prefixes_count=prefixes_count, 
                 args=args) 
    elif use_ccache:
        args = ""
        prefixes_count = 0

        args += "args_new[index++] = \"{}\";\n".format(ccache_path)
        prefixes_count += 1
        
        if compiler_path:
            args += "args_new[index++] = \"{}\";\n".format(compiler_path)
            prefixes_count += 1

            compiler_args_array = compiler_args.split(" ")
            for param in compiler_args_array:
                prefixes_count += 1
                args += "args_new[index++] = \"{}\";\n".format(param)

        text = ""\
        "#include <stdio.h>                                 \n"\
        "#include <stdlib.h>                                \n"\
        "#include <unistd.h>                                \n"\
        "#include <errno.h>                                \n"\
        "int main(int argc, char* argv[]){{                  \n"\
        "    const int prefixes = {prefixes_count};         \n"\
        "    char** args_new = (char**)malloc(sizeof(char*) * (argc + prefixes + 1)); \n"\
        "    int index = 0;                                  \n"\
        "    {args}                                          \n"\
        "    for(int j = 1; j < argc; j++){{              \n"\
        "         args_new[index++] = argv[j];                     \n"\
        "    }}                                               \n"\
        "    args_new[index] = NULL;                     \n"\
        "    if (execvp(args_new[0], args_new) != 0){{        \n"\
        "         return -1;                                 \n"\
        "    }}                                               \n"\
        "    return errno;                                   \n"\
        "}};\n"\
        .format( prefixes_count=prefixes_count, 
                 args=args)
    elif use_distcc:
        args = ""
        prefixes_count = 0

        args += "args_new[index++] = \"{}\";\n".format(distcc_path)
        prefixes_count += 1
        
        if compiler_path:
            args += "args_new[index++] = \"{}\";\n".format(compiler_path)
            prefixes_count += 1

            compiler_args_array = compiler_args.split(" ")
            for param in compiler_args_array:
                prefixes_count += 1
                args += "args_new[index++] = \"{}\";\n".format(param)

        text = ""\
        "#include <stdio.h>                                 \n"\
        "#include <stdlib.h>                                \n"\
        "#include <unistd.h>                                \n"\
        "#include <errno.h>                                \n"\
        "int main(int argc, char* argv[]){{                  \n"\
        "    const int prefixes = {prefixes_count};         \n"\
        "    char** args_new = (char**)malloc(sizeof(char*) * (argc + prefixes + 1)); \n"\
        "    int index = 0;                                  \n"\
        "    {args}                                          \n"\
        "    for(int j = 1; j < argc; j++){{              \n"\
        "         args_new[index++] = argv[j];                     \n"\
        "    }}                                               \n"\
        "    args_new[index] = NULL;                     \n"\
        "    if (execvp(args_new[0], args_new) != 0){{        \n"\
        "         return -1;                                 \n"\
        "    }}                                               \n"\
        "    return errno;                                   \n"\
        "}};\n"\
        .format( prefixes_count=prefixes_count, 
                 args=args)
                
    else:
        # TODO: ???
        text = ""
        
    if result_folder:
        if not os.path.exists(result_folder):
            os.makedirs(result_folder)

        wrapper_file_path = os.path.join(result_folder, "compiler_wrapper")

        with open("/tmp/main.c", "w") as f:
            f.write(text)

        compiler_out = subprocess.run([compiler_path, "-O2", "/tmp/main.c", "-o", wrapper_file_path], capture_output=True)
        if compiler_out.returncode != 0:
            print(compiler_out.stderr)
            return None

        return wrapper_file_path
    else:
        return None
    
    

def get_executable_path(executable_name: str) -> str:
    #command = os.system(executable_name);
    out = subprocess.run(["which", executable_name], capture_output=True)
    if (out.returncode == 0) and (len(out.stdout) > 1):
        return out.stdout.decode("utf-8").rstrip("\n")
    else:
        return None

def main():
    parser = argparse.ArgumentParser(description='DistCC and CCache wrapper builder')

    parser.add_argument("--compiler", 
                        dest="compiler", 
                        type=str,
                        help="Predefine compiler")

    parser.add_argument("--compiler_args", 
                        dest="compiler_args", 
                        type=str,
                        help="Predefine compiler_args")                    

    parser.add_argument("--use_distcc", 
                        dest="use_distcc",
                        #type=bool,
                        default=False,
                        action="store_true",
                        help="Use distcc?")

    parser.add_argument("--use_ccache", 
                        dest="use_ccache", 
                        #type=bool,
                        default=False,
                        action="store_true",
                        help="Use ccache?")

    parser.add_argument("--jobs", 
                        dest="jobs", 
                        default=False,
                        action="store_true",
                        help="Use ccache?")

    parser.add_argument("--result_folder", 
                        dest="result_folder", 
                        type=str,
                        default=None,
                        help="Result folder")

    distcc_path = get_executable_path("distcc")
    ccache_path = get_executable_path("ccache")

    args = parser.parse_args()
    #print(args)

    if distcc_path:
        use_distcc = args.use_distcc
    else:
        use_distcc = False

    if ccache_path:
        use_ccache = args.use_ccache
    else:
        use_ccache = False

    result_file = build_c_wrapper(args.result_folder, args.compiler, args.compiler_args, use_distcc, use_ccache, distcc_path, ccache_path)
    if not result_file:
        result_file = build_bash_wrapper(args.result_folder, args.compiler, args.compiler_args, use_distcc, use_ccache, distcc_path, ccache_path)
    
    print(result_file)   


if __name__ == "__main__":
    main()