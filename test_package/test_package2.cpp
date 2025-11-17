#include <cstdlib>
#include "asl2/asl.h"

int main(void) {

  auto asl_ = ASL_alloc(1);
  ASL_free(&asl_);

  return EXIT_SUCCESS;
}
