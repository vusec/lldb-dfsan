#include <sanitizer/dfsan_interface.h>

#include <stdlib.h>

struct FooNested {
  int nested;
};

struct Foo {
  int member;
  struct FooNested *member2;
};

int main(int argc, char **argv) {
  struct Foo f;
  f.member = 1;
  f.member2 = malloc(sizeof(struct FooNested));
  f.member2->nested = 2;

  dfsan_label i_label = 1;
  dfsan_set_label(i_label, &f.member2->nested, sizeof(int));

  return 0; // STOP
}
