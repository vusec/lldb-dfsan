#include <sanitizer/dfsan_interface.h>

struct Foo {
  int member;
  int member2;
};

int main(int argc, char **argv) {
  struct Foo f;
  f.member = 1;
  f.member2 = 2;

  dfsan_label i_label = 1;
  dfsan_set_label(i_label, &f.member, sizeof(int));

  return 0; // STOP
}
