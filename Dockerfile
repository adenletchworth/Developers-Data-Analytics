FROM apache/airflow:2.8.4

# Copy requirements file
COPY requirements.txt /requirements.txt

# Install dependencies
RUN pip install --user --upgrade pip && \
    pip install --user -r /requirements.txt
