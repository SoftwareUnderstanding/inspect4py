FROM python:3.7

RUN git clone https://github.com/SoftwareUnderstanding/inspect4py
RUN cd inspect4py && pip install -e .

