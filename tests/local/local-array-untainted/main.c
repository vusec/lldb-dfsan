#include <sanitizer/dfsan_interface.h>

int main(int argc, char **argv) {
  int i[3] = {1, 2, 3};

  return 0; // STOP
}
