FROM ubuntu:22.04
ENV DEBIAN_FRONTEND noninteractive

# Generics
RUN apt-get update && apt-get install -y 
RUN apt-get install git-all -y
RUN apt-get install -y python3
RUN apt-get install -y pip

# MongoDb Installation
RUN apt-get install gnupg curl -y
RUN curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
    --dearmor

RUN echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list

RUN apt-get update 

RUN apt-get install -y mongodb-org

RUN echo "mongodb-org hold" |  dpkg --set-selections
RUN echo "mongodb-org-database hold" |  dpkg --set-selections
RUN echo "mongodb-org-server hold" |  dpkg --set-selections
RUN echo "mongodb-mongosh hold" |  dpkg --set-selections
RUN echo "mongodb-org-mongos hold" |  dpkg --set-selections
RUN echo "mongodb-org-tools hold" |  dpkg --set-selections

# Clone package
RUN git clone https://github.com/SamueleSandrini/synergistic_hrtp_results

# Install Requirements
RUN pip install -r /synergistic_hrtp_results/requirements.txt

# Import data to mongodb (create database and load collections)
RUN ./synergistic_hrtp_results/import_data.sh
