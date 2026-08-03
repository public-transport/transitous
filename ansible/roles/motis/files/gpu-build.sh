# SPDX-FileCopyrightText: 2026 Traines <git@traines.eu>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

set -xe

export DEBIAN_FRONTEND=noninteractive
export CUDACXX=/usr/local/cuda/bin/nvcc
export LD_LIBRARY_PATH=/usr/local/cuda/lib64

cd /var/cache/motis-git

cmake --preset cuda -DCMAKE_CUDA_ARCHITECTURES="89" -DCMAKE_CXX_FLAGS="-march=native"
cmake --build --preset cuda --target motis

