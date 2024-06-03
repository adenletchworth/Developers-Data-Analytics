# Real-Time Developer Trends Analysis Dashboard

## Overview

This project aims to build a real-time analytics dashboard that visualizes developer trends by integrating data from various sources, including GitHub and Reddit. The project includes a scalable and advanced data-pipeline that leverages Apache Kafka for streaming data, Apache Spark for processing, MongoDB for storage, and Flask for the backend API. The frontend visualizations are powered by D3.js and other visualization libraries. Docker and Apache Airflow are used to orchestrate the data pipeline and ensure seamless integration and scalability. The Named Entity Recognition (NER) model used is a custom fine-tuned transformer model trained on computer science domain data.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Data Pipeline](#data-pipeline)
- [Visualizations](#visualizations)
- [Contributing](#contributing)
- [License](#license)

## Features

- Real-Time Data Streaming: Integrates with APIs such as GitHub and Reddit to stream data in real time using Apache Kafka.
- Data Processing: Utilizes Apache Spark for real-time data processing and analytics.
- Orchestration: Apache Airflow for orchestrating and scheduling data pipelines.
- Backend API: Flask provides the backend API for serving processed data to the frontend.
- Custom NER Model: A custom fine-tuned transformer model trained on computer science domain data for accurate entity recognition.
- Storage: Stores processed data in MongoDB.
- Interactive Visualizations: Provides a range of visualizations, including force-directed graphs, word clouds, and more using D3.js.
- Scalable Architecture: Designed to scale with the use of Docker containers and microservices.

## Architecture

### Data Ingestion:

- GitHub and Reddit APIs
- Apache Kafka for streaming data

### Data Processing:

- Apache Spark for real-time data processing
- Text preprocessing, KeyBERT, and NER

### Orchestration:

- Apache Airflow to manage and schedule the data pipeline

### Backend API:

- Flask API to serve processed data to the frontend

### Data Storage:

- MongoDB for storing processed data

### Data Visualization:

- D3.js for interactive visualizations
- Word clouds and force-directed graphs

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/adenletchworth/Developers-Data-Analytics.git
    cd Developers-Data-Analytics
    ```

2. Set up Docker containers:

    ```bash
    docker-compose up
    ```

3. Install Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. Start the Docker containers:

    ```bash
    docker-compose up
    ```

2. Access Apache Airflow:

    Open your web browser and navigate to http://localhost:8080 to access the Airflow web UI. From there, you can manage and trigger DAGs.

3. Launch the Flask API:

    ```bash
    python app.py
    ```

4. Access the application:

    Open your web browser and go to http://localhost:5000 to access the application and view the visualizations.

## Data Pipeline

### Ingestion:

- GitHub API and Reddit API data are ingested and streamed to Kafka.

### Processing:

- Spark processes the data, performing text preprocessing, KeyBERT, and NER.

### Orchestration:

- Apache Airflow schedules and manages the data pipeline tasks.

### Backend:

- Flask API serves the processed data to the frontend.

### Storage:

- Processed data is stored in MongoDB for easy retrieval and visualization.

## Visualizations

- Force-Directed Graph:
  Visualizes topics and keywords with distinct colors and blended colors for shared keywords.

- Word Cloud:
  Displays the most significant keywords extracted from the data.

- Time-Series Analysis:
  Charts showing trends over time, such as the popularity of certain topics.

- Metadata Dashboard:
  Provides insights into repository information, metadata, and extracted keywords/entities.

