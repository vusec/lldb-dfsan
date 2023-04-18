#include <sanitizer/dfsan_interface.h>

#include <stdlib.h>

struct Foo {
  int member;
  int *member2;
};

int main(int argc, char **argv) {
  struct Foo f;
  f.member = 1;
  f.member2 = malloc(sizeof(int));

  dfsan_label i_label = 1;
  dfsan_set_label(i_label, f.member2, sizeof(int));

  return 0; // STOP
}
