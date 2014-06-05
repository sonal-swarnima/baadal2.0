#include<stdlib.h>
#include<stdio.h>
#include<unistd.h>
#include<sys/prctl.h>
#include<sys/types.h>
#include<sys/sysinfo.h>
#include<errno.h>
#include<sys/wait.h>
#include<time.h>
#include<errno.h>
#include<string.h>


#define UNIT_SIZE 4096


int main(int argc, char **argv)
{
	time_t rawtime;
	struct tm * timeinfo;

	time ( &rawtime );
	timeinfo = localtime ( &rawtime );
	printf ( "Current local time and date: %s\n", asctime (timeinfo) );

	printf("In main!!!\n");
	pid_t childPID;

	printf("Invoking Fork!!!\n");
	childPID = fork();

	if(childPID >= 0) { //fork was successful

		printf("Fork Invoked Successfully!!!\n");

		if(childPID == 0) { //child process

			printf("In Child!!!\n");

			unsigned long max_alloc;
			char **a, *ptr;
			long i;
			struct sysinfo info;
			int retval = sysinfo(&info);

			if(retval == 0)  {

				printf("Sysinfo fetched successfully!!!\n");

				max_alloc = (info.totalram)/2;

				printf("Allocating %ld units\n", max_alloc);
				a = (char **)malloc(max_alloc);

				if (!a) {

					printf(".....could not allocate a!\n");
					exit(1);
				}

				for (i = 0; (i < max_alloc) && (getppid() != 1); i++) {

					a[i] = (char *)malloc(UNIT_SIZE);

					if (!a[i]) {

						printf("could not allocate a!\n");
						exit(1);
					}
				}

				printf("Allocation finished, now touching memory\n");

				while (getppid() != 1) {

					for (i = 0; (i < max_alloc) && (getppid() != 1); i++) {

						ptr = a[i] + (rand() % UNIT_SIZE);
						(*ptr)++;
					}
				}
			}

			else {

				printf("Error while fetching Sysinfo:  %s\n", strerror(errno));

			}

			printf("Child Completed!!!\n");		
		}

		else { //parent process

			printf("In Parent!!!\n");
			printf("Parent going to sleep!!!\n");
			sleep(30);
			printf("Parent awake!!!\n");
		}
	}

	else { //fork failed

		printf("\n Fork failed, quitting!!!!!!\n");
		return 1;
	}

	time ( &rawtime );
	timeinfo = localtime ( &rawtime );
	printf ( "Current local time and date: %s\n", asctime (timeinfo) );

	return 0;
}
