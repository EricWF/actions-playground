#include <iostream>

// This will cause an unknown attribute warning/error similar to the one in clang-error.txt
[[clang::no_sanitize("shift-out-of-bounds")]]
void problematic_function() {
    std::cout << "This function has an unknown sanitizer attribute" << std::endl;
}

// This will cause an undefined variable error
void another_error() {
    undefined_variable = 42;
}

int main() {
    problematic_function();
    another_error();
    return 0;
}