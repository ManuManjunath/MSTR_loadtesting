FROM base-centos7:prod-latest

#pre environment
RUN mkdir -p /etc/loadtest/logs

# installs
RUN yum -y update && \
    yum -y install \
    yum-utils \
    development \
    groupinstall \
    openssl-devel \
    wget \
    && \
    yum clean all

RUN cd /etc/loadtest; \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm; \
    yum -y install /etc/loadtest/google-chrome-stable_current_*.rpm

RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm; \
    yum -y install python36u; \
    yum -y install python36u-pip; \
    yum -y install python36u-devel

RUN pip3.6 install selenium

COPY ./chrome* /etc/loadtest/
COPY ./LTEST*.csv /etc/loadtest/

RUN chmod 777 /etc/loadtest/chromedriver; \
    chmod 777 /etc/loadtest/chromedriver2

# copy load script
COPY ./OIDC_Merch_RunRep.py /etc/loadtest

CMD python3.6 /etc/loadtest/OIDC_Merch_RunRep.py && tail -f /dev/null
Target
Target
