#include <sanitizer/dfsan_interface.h>

int main(int argc, char **argv) {
  int i = 4;

  dfsan_label i_label = 1;
  dfsan_set_label(i_label, &i, sizeof(i));

  return 0; // STOP
}
