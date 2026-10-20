#include <cudnn_frontend.h>

#include <iostream>

int main() {
    auto tensor = cudnn_frontend::graph::Tensor_attributes()
                      .set_name("input")
                      .set_dim({1, 4, 8, 8})
                      .set_stride({256, 64, 8, 1})
                      .set_data_type(cudnn_frontend::DataType_t::FLOAT);
    if (tensor.get_name() != "input" || tensor.get_dim().size() != 4) {
        return 1;
    }

    std::cout << "cuDNN Frontend "
              << CUDNN_FRONTEND_MAJOR_VERSION << "."
              << CUDNN_FRONTEND_MINOR_VERSION << "."
              << CUDNN_FRONTEND_PATCH_VERSION << std::endl;
    return 0;
}
