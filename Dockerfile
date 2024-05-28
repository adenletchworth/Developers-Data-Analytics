FROM apache/airflow:2.8.4

# Copy requirements file
COPY requirements.txt /requirements.txt

# Install dependencies
RUN pip install --user --upgrade pip && \
    pip install --user -r /requirements.txt

# Install OpenJDK and Spark
USER root
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk wget tar procps && \
    apt-get clean

# Install Spark
ENV SPARK_VERSION=3.5.1
RUN wget -qO- https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop3.tgz | tar -xz -C /usr/local/ && \
    ln -s /usr/local/spark-$SPARK_VERSION-bin-hadoop3 /usr/local/spark

# Set environment variables
ENV SPARK_HOME=/usr/local/spark
ENV PATH=$PATH:/usr/local/spark/bin
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Verify Spark installation
RUN echo "Spark Home: $SPARK_HOME" && \
    echo "Path: $PATH" && \
    ls -l /usr/local/spark/bin && \
    echo "Java Home: $JAVA_HOME" && \
    ls -l $JAVA_HOME

USER airflow
