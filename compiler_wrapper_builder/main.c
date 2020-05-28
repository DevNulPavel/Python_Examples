#include <stdio.h>                                 
#include <stdlib.h>                                
#include <unistd.h>                                
#include <errno.h>                                
int main(int argc, char* argv[]){                  
    putenv("CCACHE_PREFIX=/usr/local/bin/distcc");          
    const int prefixes = 3;         
    char** args_new = (char**)malloc(sizeof(char*) * (argc + prefixes + 1)); 
    int index = 0;                                  
    args_new[index++] = "/usr/local/bin/ccache";
args_new[index++] = "/usr/bin/clang";
args_new[index++] = "-lstdc++";
                                          
    for(int j = 1; j < argc; j++){              
         args_new[index++] = argv[j];                     
    }                                               
    args_new[index] = NULL;                     
    if (execvp(args_new[0], args_new) != 0){        
         return -1;                                 
    }                                               
    return errno;                                   
};
