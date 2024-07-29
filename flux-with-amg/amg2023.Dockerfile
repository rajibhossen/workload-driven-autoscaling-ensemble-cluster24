FROM ubuntu:22.04 as builder

ARG spack_cpu_arch=zen3
ARG build_jobs=6

RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install \
    autotools-dev \
    autoconf \
    automake \
    unzip \
    cmake \
    git \
    python3 \
    openssh-server \
    openssh-client \
    apt-utils \
    gcc \
    gfortran \
    libatomic1 \
    libnuma-dev \
    libgomp1 \
    openssh-server \
    openssh-client \
    dnsutils \
    g++ \
    build-essential \
    software-properties-common

# What we want to install and how we want to install it
# is specified in a manifest file (spack.yaml)
RUN mkdir /opt/spack-environment \
    &&  (echo "spack:" \
    &&   echo "  specs:" \
    &&   echo "  - openmpi@4.1.4 fabrics=ofi +legacylaunchers" \
    &&   echo "  - libfabric@1.19.0 fabrics=efa,tcp,udp,sockets,verbs,shm,mrail,rxd,rxm" \
    &&   echo "  - amg2023" \
    &&   echo "  - flux-core" \
    &&   echo "  - flux-sched" \
    &&   echo "  - flux-pmix" \
#    &&   echo "  - flux-security" \
    &&   echo "  concretizer:" \
    &&	 echo "    unify: true" \
    &&   echo "  config:" \
    &&   echo "    install_tree: /opt/software" \
    &&   echo "  view: /opt/view") > /opt/spack-environment/spack.yaml

# Install the software, remove unnecessary deps
RUN cd /opt/spack-environment \
    && git clone --single-branch --branch v0.21.1 https://github.com/spack/spack.git \
    && . spack/share/spack/setup-env.sh \
    && spack env activate . \
    && spack external find openssh \
    && spack external find cmake \
    && spack install --reuse --fail-fast \
    && spack gc -y

# Modifications to the environment that are necessary to run
RUN cd /opt/spack-environment \
    && . spack/share/spack/setup-env.sh \
    && spack env activate --sh -d . >> /etc/profile.d/z10_spack_environment.sh

## Now we build the AMG image
#FROM ubuntu:22.04
#
#COPY --from=builder /opt/spack-environment /opt/spack-environment
#COPY --from=builder /opt/software /opt/software
#COPY --from=builder /opt/view /opt/view
#COPY --from=builder /etc/profile.d/z10_spack_environment.sh /etc/profile.d/z10_spack_environment.sh
#
#RUN apt-get update
#RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install --no-install-recommends \
#    libatomic1 \
#    libnuma-dev \
#    libgomp1 \
#    openssh-server \
#    openssh-client \
#    dnsutils \
#    && apt-get clean \
#    && apt-get autoremove \
#    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
