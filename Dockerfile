FROM python:3.7

RUN apt update &&\
    apt install -y git &&\
    apt install -y graphviz

RUN pip install --upgrade pip

RUN git clone https://github.com/SoftwareUnderstanding/inspect4py
RUN cd inspect4py && pip install -e .
