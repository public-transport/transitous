set -xe

export DEBIAN_FRONTEND=noninteractive
export CUDACXX=/usr/local/cuda/bin/nvcc
export LD_LIBRARY_PATH=/usr/local/cuda/lib64

cd /var/cache/motis-git

cmake --preset cuda -DCMAKE_CUDA_ARCHITECTURES="89" -DCMAKE_CXX_FLAGS="-march=native"
cmake --build --preset cuda --target motis

