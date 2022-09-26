FROM gitpod/openvscode-server

USER root 
RUN apt update
RUN apt -y install software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update
RUN apt -y install python3.8
RUN apt -y install python3-pip
