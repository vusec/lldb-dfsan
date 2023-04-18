#include <sanitizer/dfsan_interface.h>

#include <stdlib.h>

struct Foo {
  int member;
  struct Foo *self;
  int trailing;
};

int main(int argc, char **argv) {
  struct Foo f;
  f.member = 1;
  f.self = &f;

  dfsan_label i_label = 1;
  dfsan_set_label(i_label, &f.member, sizeof(int));
  dfsan_set_label(i_label, &f.trailing, sizeof(int));

  return 0; // STOP
}
