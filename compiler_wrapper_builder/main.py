#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import subprocess
import os
import os.path
import multiprocessing


# $ cat ~/.ccache/ccache.conf
# max_size = 50.0G
# run_second_cpp = true
# hard_link = true
# sloppiness = clang_index_store,file_macro,time_macros,include_file_mtime,include_file_ctime,file_stat_matches,file_stat_matches_ctime

# $ cat ~/.distcc/hosts
# Для хорошего распределения можно вообще убрать локальный компьютер, тогда серверы будут работать почти на 100%,
#     то есть для базового сборочного компьютера можно спользовать слабый комп, но мощные сервера
# Еще лучше - вообще не использовать локальный компьютер для сборки, так как он активно занимается препроцессингом задач
# Для удаленных компов лучше ставить x1.5-2, для локального - по количеству ядер
# 192.168.1.21/12
# 192.168.1.22/12
# localhost/12


def build_bash_wrapper(result_folder, compiler_path, compiler_args, use_distcc, use_ccache, distcc_path, ccache_path) -> str:
    # Тест компилятора и его аргументов
    if compiler_path and compiler_args:
        compiler_text=" {compiler_path} {compiler_args}".format(compiler_path=compiler_path, compiler_args=compiler_args)
    elif compiler_path:
        compiler_text=" {compiler_path}".format(compiler_path=compiler_path)
    else:
        compiler_text=""

    # В зависимости от параметров выдаем текст
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
        # Создаем папку если нету
        if not os.path.exists(result_folder):
            os.makedirs(result_folder)

        # Получаем абсолютный путь к файлику и пишем туда текст
        file_path = os.path.abspath(os.path.join(result_folder, "compiler_wrapper.sh"))
        with open(file_path, "w") as file:
            file.write(text)

        # Файлик делаем исполняемым
        os.system("chmod u+x {}".format(file_path))

        # Возвращаем путь к нему
        return file_path
    else:
        return None


def get_C_compiler():
    # Ищем компилятор для кода на C
    compilator_for_c_code = None

    # Clang
    clang_out = subprocess.run(["which", "clang"], capture_output=True)
    if (clang_out.returncode == 0) and (len(clang_out.stdout) > 2):
        compilator_for_c_code = clang_out.stdout.decode("utf-8").rstrip("\n")
    else:
        # GCC
        gcc_out = subprocess.run(["which", "gcc"], capture_output=True)
        if (gcc_out.returncode == 0) and (len(gcc_out.stdout) > 2):
            compilator_for_c_code = gcc_out.stdout.decode("utf-8").rstrip("\n")
        else:
            # XCode
            xcode_clang = "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang"
            if os.path.exists(xcode_clang):
                compilator_for_c_code = xcode_clang

    return compilator_for_c_code


def build_c_wrapper(result_folder, compiler_path, compiler_args: str, use_distcc, use_ccache, distcc_path, ccache_path) -> str:
    # Ищем компилятор для кода на C
    compilator_for_c_code = get_C_compiler()
    if not compilator_for_c_code:
        return None
    
    # Параметры для текста ошибки
    args = ""
    prefixes_count = 0
    env = ""

    # ccache + distcc
    if use_ccache and use_distcc:
        env = "          putenv(\"CCACHE_PREFIX={}\");\n".format(distcc_path)
        args += "          args_new[index++] = \"{}\";\n".format(ccache_path)
        prefixes_count += 1
    elif use_ccache:
        args += "          args_new[index++] = \"{}\";\n".format(ccache_path)
        prefixes_count += 1
    elif use_distcc:
        args += "          args_new[index++] = \"{}\";\n".format(distcc_path)
        prefixes_count += 1
    else:
        pass

    # Путь к компилятору и его аргументам
    if compiler_path:
        args += "          args_new[index++] = \"{}\";\n".format(compiler_path)
        prefixes_count += 1

        if compiler_args:
            compiler_args_array = compiler_args.split(" ")
            for param in compiler_args_array:
                prefixes_count += 1
                args += "          args_new[index++] = \"{}\";\n".format(param)

    # Тест программы
    text = ""\
    "#include <stdio.h>                                                                  \n"\
    "#include <stdlib.h>                                                                 \n"\
    "#include <unistd.h>                                                                 \n"\
    "#include <errno.h>                                                                  \n"\
    "int main(int argc, char* argv[]){{                                                  \n"\
    "     if(fork() == 0){{                                                              \n"\
    "{env}"\
    "          const int prefixes = {prefixes_count};                                    \n"\
    "          char** args_new = (char**)malloc(sizeof(char*) * (argc + prefixes + 1));  \n"\
    "          int index = 0;                                                            \n"\
    "{args}"\
    "          for(int j = 1; j < argc; j++){{                                           \n"\
    "              args_new[index++] = argv[j];                                          \n"\
    "          }}                                                                        \n"\
    "          args_new[index] = NULL;                                                   \n"\
    "          if (execvp(args_new[0], args_new) != -1){{                                \n"\
    "               exit(0);                                                             \n"\
    "               return 0;                                                            \n"\
    "          }}else{{                                                                  \n"\
    "               exit(errno);                                                         \n"\
    "               return errno;                                                        \n"\
    "          }}                                                                        \n"\
    "    }}                                                                              \n"\
    "    int status;                                                                     \n"\
    "    wait(&status);                                                                  \n"\
    "    return WEXITSTATUS(status);                                                     \n"\
    "}}                                                                                  \n"\
    .format(env=env,
            prefixes_count=prefixes_count, 
            args=args)
        
    # print(text)

    if result_folder:
        # Создаем папку если надо
        if not os.path.exists(result_folder):
            os.makedirs(result_folder)
        
        # Путь к файлику враппера
        wrapper_file_path = os.path.abspath(os.path.join(result_folder, "compiler_wrapper"))

        # Путь к компилируемому файлику
        main_file_path = os.path.join(result_folder, "main.c")

        # Пишем файлик
        with open(main_file_path, "w") as f:
            f.write(text)

        # Компилируем, выходим из функции если ошибка
        compiler_out = subprocess.run([compilator_for_c_code, "-O2", main_file_path, "-o", wrapper_file_path], capture_output=True)
        if compiler_out.returncode != 0:
            print(compiler_out.stderr)
            return None

        # Исполняемый файлик делаем исполняемым для пользователя на всякий случай
        os.system("chmod u+x {}".format(wrapper_file_path))

        return wrapper_file_path
    else:
        return None
    

def get_executable_path(executable_name: str) -> str:
    # Получаем путь с помощью терминальной команды which
    out = subprocess.run(["which", executable_name], capture_output=True)
    if (out.returncode == 0) and (len(out.stdout) > 1):
        return out.stdout.decode("utf-8").rstrip("\n")
    else:
        return None


def get_arguments():
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

    args = parser.parse_args()
    
    return args


def print_compile_jobs_count(use_distcc: bool):
    if use_distcc:
        # Рекомендуемое количество - удвоенное количество таргетов + 1
        # Но надо учитывать локальный комп
        out = subprocess.run(["distcc", "-j"], capture_output=True)
        if (out.returncode == 0) and (len(out.stdout) > 1):
            text = out.stdout.decode("utf-8").rstrip("\n")
            count = int(int(text)*2 + 1)
            print(count)
        else:
            # Просто количество ядер
            print(multiprocessing.cpu_count())
    else:
        # Просто количество ядер
        print(multiprocessing.cpu_count())


def main():
    # Аргументы скрипта
    args = get_arguments()
    #print(args)

    # Получим путь к нашим исполняемым файликам
    distcc_path = get_executable_path("distcc")
    ccache_path = get_executable_path("ccache")

    # Если есть путь - используем
    if distcc_path:
        use_distcc = args.use_distcc
    else:
        use_distcc = False

    # Если есть путь - используем
    if ccache_path:
        use_ccache = args.use_ccache
    else:
        use_ccache = False

    # Если нам надо вывести просто количество потоков сборки
    if args.jobs:
        # тогда выводим
        print_compile_jobs_count(use_distcc)
    else:
        # Пробуем создать враппер на C
        result_file = build_c_wrapper(args.result_folder, args.compiler, args.compiler_args, use_distcc, use_ccache, distcc_path, ccache_path)
        if not result_file:
            # Если не вышло, создаем на bash
            result_file = build_bash_wrapper(args.result_folder, args.compiler, args.compiler_args, use_distcc, use_ccache, distcc_path, ccache_path)
        
        # Выводим имя файлика
        if result_file:
            print(result_file)
        else:
            print("ERROR-no_wrapper_file")


if __name__ == "__main__":
    main()