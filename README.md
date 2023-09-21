# FastAPI Weather Information API

A simple FastAPI application for fetching and processing weather information using METAR data.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
  - [Ping](#ping)
  - [Raw Info](#raw-info)
  - [Processed Info](#processed-info)
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

### Ping

Check if the API is running.

- **Endpoint:** `/metar/ping`
- **HTTP Method:** GET

Example:

```bash
curl http://127.0.0.1:8080/metar/ping
```

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

### Processed Info

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
