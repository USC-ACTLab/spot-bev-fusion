#ifndef __TENSORDESC_HPP__
#define __TENSORDESC_HPP__

#include <vector>
#include <cstdint>
#include <string>
#include "tensor.hpp"

namespace nv {

struct TensorDesc {
  std::vector<int64_t> shape;
  
  DataType dtype;

  TensorDesc() : dtype(DataType::None) {}

  TensorDesc(const std::vector<int64_t>& shape, DataType dtype)
      : shape(shape), dtype(dtype) {}

  TensorDesc(const std::vector<int32_t>& shape32, DataType dtype)
      : dtype(dtype) {
    for (auto s : shape32) {
      shape.push_back(static_cast<int64_t>(s));
    }
  }

  size_t numel() const {
    size_t total = 1;
    for (auto d : shape) {
      total *= d;
    }
    return total;
  }

  std::string to_string() const {
    std::string s = "TensorDesc(shape=[";
    for (size_t i = 0; i < shape.size(); i++) {
      s += std::to_string(shape[i]);
      if (i + 1 < shape.size()) {
        s += ", ";
      }
    }
    s += "], dtype=";
    s += dtype_string(dtype);
    s += ")";
    return s;
  }
};

} 

#endif
