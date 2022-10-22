#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <pthread.h>

double rand01()
{
    return (double)rand() / RAND_MAX;
}

double get_pi()
{
    int M = 0;
    int N = 400000;
    for (int j = 0; j < N; j++)
    {
        double x = rand01();
        double y = rand01();
        if (x * x + y * y < 1) {
            M++;
        }
    }
    return (double)M / N * 4;
}

int guess_clock(unsigned time_stamp, const char **right, int clock_start, int clock_stop)
{
    int thread_count = 8;

    char target[100] = {0};

    for (int i = clock_start; i < clock_stop; ++i)
    {
        srand(time_stamp + i);

        size_t j;
        for (j = 0; j < 3; ++j)
        {
            double pi = get_pi();
            sprintf(target, "%1.5f", pi);
            if (strcmp(target, right[j]))
            {
                break;
            }
        }

        if (j == 3)
        {
            return i;
        }
    }

    return -1;
}

void print_usage()
{
    printf("usage:                \n\
\t./monte_carlo 0 1666924394 3.14316 3.13776 3.14237 0 10000 \n\
\t./monte_carlo 1 1666924394 1785     \n\
\n    \
\t// argv[1]: 0 -> crack clock using given timestamp and result       \n\
\t// argv[1]: 1 -> guess result using given timestamp and clock        \n\
");
}

int main(int argc, char **argv)
{
    if (argc < 2)
    {
        print_usage();
        exit(EXIT_FAILURE);
    }

    int mode = atoi(argv[1]);
    if (mode == 0)
    {
        if (argc != 8)
        {
            print_usage();
            exit(EXIT_FAILURE);
        }

        unsigned time_stamp = atoi(argv[2]);
        const char *right1 = argv[3];
        const char *right2 = argv[4];
        const char *right3 = argv[5];
        const char *right[] = {right1, right2, right3};

        int clock_start = atoi(argv[6]);
        int clock_stop = atoi(argv[7]);

        printf("%i\n", guess_clock(time_stamp, right, clock_start, clock_stop));
    }
    else if (mode == 1)
    {
        if (argc != 4)
        {
            print_usage();
            exit(EXIT_FAILURE);
        }

        unsigned time_stamp = atoi(argv[2]);
        unsigned clock = atoi(argv[3]);
        char target[100] = {0};

        srand(time_stamp + clock);

        for (size_t i = 0; i < 5; ++i)
        {
            double pi = get_pi();
            sprintf(target, "%1.5f", pi);
            printf("%s\n", target);
        }
    }
    else
    {
        return -1;
    }

    return 0;
}