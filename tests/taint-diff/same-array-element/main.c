#include <sanitizer/dfsan_interface.h>

int main(int argc, char **argv) {
  int array[3] = {1, 2, 3};

  dfsan_label i_label = 1;
  dfsan_set_label(i_label, &(array[1]), sizeof(int));

  int i;
  for (i = 0; i < 2; i++) {
    i += 0; //STOP
  }

}
