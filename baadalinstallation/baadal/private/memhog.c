#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>
#include<time.h>

int main(int argc, char *argv[]){

        long i,count=0;
        int chunk=1024;
        time_t start,end;
        start = time(NULL);
        double elapsed;
        end = time(NULL);
        elapsed = difftime(end, start);
        short *buffer=malloc(sizeof(char)*chunk);
        long total = 1024 * 1024 * 1024;
        printf("allocating and touching memory");
        while(buffer!=NULL || elapsed<=300.0){
                end = time(NULL);
                elapsed = difftime(end, start);
                buffer=malloc(sizeof(char)*chunk);
                if(buffer!=NULL){
                        count++;
                        memset(buffer,0,chunk);
                }
                else

                        printf("Could not allocate more memory");

        }

}

