## 0x06 安全的在线测评
### 无法 AC 的题目
分析源码发现，第一题的输入在文件`./data/static.in`中，答案在文件`./data/static.out`中，题目暗示第一题输入数据会泄漏。

尝试读取`./data/static.out`，发现`runner`用户可读，那么直接读答案然后输出就好了。

```
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
```

### 动态数据
看了半天，不会。