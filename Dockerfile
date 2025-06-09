FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV OPENPBS_VERSION=23.06.06

# Install system dependencies including cJSON
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    autoconf \
    automake \
    libtool \
    libhwloc-dev \
    libx11-dev \
    libxt-dev \
    libedit-dev \
    libical-dev \
    libncurses-dev \
    swig \
    libexpat-dev \
    libssl-dev \
    tcl-dev \
    tk-dev \
    libpython3-dev \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    postgresql-server-dev-all \
    sendmail \
    unzip \
    libcjson-dev && \
    rm -rf /var/lib/apt/lists/*

# Clone and build OpenPBS
RUN git clone https://github.com/openpbs/openpbs.git /openpbs && \
    cd /openpbs && \
    ./autogen.sh && \
    ./configure --prefix=/opt/pbs && \
    make -j"$(nproc)" && \
    make install

# Run OpenPBS post-install setup
RUN chmod 4755 /opt/pbs/sbin/pbs_iff /opt/pbs/sbin/pbs_rcp


# Ensure PBS environment is sourced in shells
RUN echo "source /etc/profile.d/pbs.sh" >> /etc/bash.bashrc

WORKDIR /workspace

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 15001-15010 17001

ENTRYPOINT ["/entrypoint.sh"]