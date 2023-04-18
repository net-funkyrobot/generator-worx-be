FROM mcr.microsoft.com/devcontainers/base:bullseye

RUN apt-get -qqy update && apt-get install -qqy \
  libpq-dev \
  openjdk-11-jre

# Add src/ to PYTHONPATH so Python modules inside it are accessible
ENV PYTHONPATH "${PYTHONPATH}:/workspace/src/python"