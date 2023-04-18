#include <sanitizer/dfsan_interface.h>

int main(int argc, char **argv) {
  int i[3] = {1, 2, 3};

  dfsan_label i_label = 1;
  dfsan_set_label(i_label, &(i[0]), sizeof(int));

  return 0; // STOP
}
