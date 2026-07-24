#include <NvInfer.h>
#include <iostream>

class Logger : public nvinfer1::ILogger {
public:
    void log(Severity severity, const char* msg) noexcept override {
        if (severity <= Severity::kWARNING) {
            std::cout << msg << std::endl;
        }
    }
};

int main() {
    std::cout << "TensorRT version: " << NV_TENSORRT_MAJOR << "."
              << NV_TENSORRT_MINOR << "." << NV_TENSORRT_PATCH << std::endl;

    Logger logger;
    auto builder = nvinfer1::createInferBuilder(logger);
    if (builder) {
        std::cout << "Successfully created TensorRT builder" << std::endl;
        delete builder;
        return 0;
    } else {
        std::cerr << "Failed to create TensorRT builder" << std::endl;
        return 1;
    }
}
