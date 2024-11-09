#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>

#define PAGE_SIZE 4096      // Define PAGE_SIZE appropriately
#define TABLE_MAX_PAGES 100 // Define TABLE_MAX_PAGES appropriately

typedef struct
{
    int file_descriptor;
    uint32_t file_length;
    void *pages[TABLE_MAX_PAGES];
} Pager;

void pager_flush(Pager *pager, uint32_t page_num, uint32_t size)
{
    if (pager->pages[page_num] == NULL)
    {
        printf("Tried to flush null page\n");
        exit(EXIT_FAILURE);
    }

    printf("Pager file descriptor: %d\n", pager->file_descriptor); // Debugging line
    off_t offset = lseek(pager->file_descriptor, page_num * PAGE_SIZE, SEEK_SET);
    if (offset == -1)
    {
        printf("Error seeking: %d\n", errno);
        exit(EXIT_FAILURE);
    }

    ssize_t bytes_written = write(pager->file_descriptor, pager->pages[page_num], size);
    if (bytes_written == -1)
    {
        printf("Error writing: %d\n", errno);
        exit(EXIT_FAILURE);
    }

    printf("Flushed page %d to disk, bytes written: %zd\n", page_num, bytes_written); // Debugging line
}

int main()
{
    const char *filename = "example.txt";

    // Correct usage of open with bitwise OR to combine flags
    int fd = open(filename, O_RDWR | O_CREAT, S_IRUSR | S_IWUSR);
    if (fd == -1)
    {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    printf("File opened with descriptor: %d\n", fd);

    // Get the file length
    off_t file_length = lseek(fd, 0, SEEK_END);
    if (file_length == -1)
    {
        perror("Error seeking to end of file");
        close(fd); // Don't forget to close the file descriptor
        exit(EXIT_FAILURE);
    }

    printf("File length: %lld\n", (long long)file_length);

    // Allocate and initialize the Pager structure
    Pager *pager = (Pager *)malloc(sizeof(Pager));
    if (pager == NULL)
    {
        perror("Error allocating memory for Pager");
        close(fd); // Don't forget to close the file descriptor
        exit(EXIT_FAILURE);
    }

    pager->file_descriptor = fd;
    pager->file_length = (uint32_t)file_length;

    // Initialize pages
    for (int i = 0; i < TABLE_MAX_PAGES; i++)
    {
        pager->pages[i] = NULL; // Set all pages to NULL initially
    }

    // Allocate a page for testing
    uint32_t page_num = 1;
    pager->pages[page_num] = malloc(PAGE_SIZE);
    if (pager->pages[page_num] == NULL)
    {
        perror("Error allocating memory for page");
        free(pager);
        close(fd);
        exit(EXIT_FAILURE);
    }

    // Fill the page with some data for testing
    snprintf((char *)pager->pages[page_num], PAGE_SIZE, "This is a test page");

    // Example flush call
    pager_flush(pager, page_num, PAGE_SIZE);

    // Clean up
    free(pager->pages[page_num]);
    free(pager);
    close(fd);

    return 0;
}
