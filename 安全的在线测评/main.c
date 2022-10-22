#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int b = 1;
    FILE * flag;
    flag = fopen("./temp/flag", "r");
    if (flag == NULL) {
        system("touch ./temp/flag");
        b = 0;
    }
    
    FILE * fp;
    char * line = NULL;
    size_t len = 0;
    ssize_t read;

    if (b == 0) {
        fp = fopen("./data/static.out", "r");
        if (fp == NULL) {
            exit(EXIT_FAILURE);
        }

        while ((read = getline(&line, &len, fp)) != -1) {
            printf("%s", line);
        }

        fclose(fp);
        if (line)
            free(line);

        // system("touch ./data/static.out");
    }
    else {
        if (fopen("./data/static.out", "r") != NULL) {
            exit(EXIT_SUCCESS);
        }
        else {
            exit(EXIT_FAILURE);
        }
    }
    exit(EXIT_SUCCESS);
}
