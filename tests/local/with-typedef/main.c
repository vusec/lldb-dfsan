#include <sanitizer/dfsan_interface.h>

typedef int typedefd;

int main(int argc, char **argv) {
  typedefd i = 4;

  dfsan_label i_label = 1;
  dfsan_set_label(i_label, &i, sizeof(i));

  return 0; // STOP
}
