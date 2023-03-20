#include <sanitizer/dfsan_interface.h>

int main(int argc, char **argv) {
  int i = 4;
  ++i;

  return 0; // STOP
}
