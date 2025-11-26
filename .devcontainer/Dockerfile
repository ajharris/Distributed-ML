FROM mcr.microsoft.com/devcontainers/python:3.9

# Switch to root to install apt packages
USER root

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the non-root user devcontainers expect (often "vscode" or similar)
USER vscode
