#!/usr/bin/env bash

python3 main.py --compiler "clang" --compiler_args="-lstdc++" --use_distcc --use_ccache --result_folder res
python3 main.py --compiler "clang" --compiler_args="-lstdc++" --use_ccache --result_folder res
python3 main.py --compiler "clang" --compiler_args="-lstdc++" --use_distcc --result_folder res
python3 main.py --compiler "clang" --compiler_args="-lstdc++" --result_folder res
python3 main.py --compiler "clang"  --use_distcc --use_ccache --result_folder res
python3 main.py --compiler "clang"  --use_ccache --result_folder res
python3 main.py --compiler "clang"  --use_distcc --result_folder res
python3 main.py --compiler "clang" --result_folder res
python3 main.py --result_folder res
python3 main.py --jobs
python3 main.py --jobs --use_distcc

# python3 main.py -h
#  2> /dev/null
./res/compiler_wrapper clang res/main.c -o res/result

time bash -c "for i in {0..500}
do
    res/compiler_wrapper clang 2> /dev/null
done"

