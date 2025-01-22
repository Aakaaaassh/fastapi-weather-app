# FastAPI Weather Information API

A simple FastAPI application for fetching and processing weather information using METAR data.


## FastAPI Backend Deployed on Render
- The screenshot below shows the FastAPI backend successfully deployed and running on Render. 
- The ```/metar/ping``` endpoint confirms the API is live and operational.
- URL: [https://fastapi-weather-app.onrender.com](https://fastapi-weather-app.onrender.com)
  
![Screenshot (5)](https://github.com/user-attachments/assets/346d5c10-8d84-4642-9e57-83774a30eee5)

## Streamlit Frontend - Raw METAR Data Fetch
- This screenshot demonstrates the Streamlit frontend's functionality for fetching raw METAR data using a station code.
- It communicates with the FastAPI backend to retrieve the raw data.
- URL: [https://metar-code-translater.streamlit.app/](https://metar-code-translater.streamlit.app/)
  
![Screenshot (4)](https://github.com/user-attachments/assets/cf3a3fff-4ce8-4c2c-a6b3-4dec19bbef26)

## Streamlit Frontend - Processed Weather Information
- The screenshot showcases the processed weather information for a specific station code.
- It uses the FastAPI backend to extract and display weather details like wind speed and visibility.
- URL: [https://metar-code-translater.streamlit.app/](https://metar-code-translater.streamlit.app/)
  
![Screenshot (3)](https://github.com/user-attachments/assets/f8ea7378-5c79-4e80-8aab-7111a0206a03)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
  - [Raw Info](#raw-info)
  - [Processed Info](#processed)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The FastAPI Weather Information API is a simple web service that provides weather information based on METAR data. It can fetch raw METAR data and process it to extract relevant weather information.

## Features

- Fetch raw METAR data for a specific station code.
- Process METAR data to extract weather information such as wind speed, visibility, cloud layers, and more.

## Getting Started

### Prerequisites

Before you can run the FastAPI Weather Information API, make sure you have the following installed:

- Python 3.x
- pip (Python package manager)
- Redis (for caching METAR data)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Aakaaaassh/fastapi-weather-app.git
   cd fastapi-weather-app


2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Make sure you have a Redis server running on `localhost` (default settings).

4. Start the FastAPI application:

   ```bash
   python Metar.py
   or
   uvicorn Metar:app
   or
   uvicorn Metar:app --reload
   ```

The API should now be running at `http://127.0.0.1:8080`.

## Usage

You can interact with the FastAPI Weather Information API using the provided endpoints. Here are the available endpoints:


## Endpoints

### Raw Info

Fetch raw METAR data for a specific station code.

- **Endpoint:** `/metar/Raw info`
- **HTTP Method:** GET
- **Query Parameter:**
  - `scode` (required): The station code (e.g., KSGS).

Example:

```bash
curl http://127.0.0.1:8080/metar/Raw%20info?scode=KSGS
```

### Processed

Fetch processed weather information for a specific station code.

- **Endpoint:** `/metar/Processed info`
- **HTTP Method:** GET
- **Query Parameters:**
  - `scode` (required): The station code (e.g., KSGS).
  - `nocache` (optional, default: 1): Set to 1 to bypass cache and fetch fresh data.

Example:

```bash
curl http://127.0.0.1:8080/metar/Processed%20info?scode=KSGS&nocache=1
```

## Contributing

Contributions to this project are welcome. If you find a bug or have an enhancement in mind, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
