# Hanime.tv API

An asynchronous FastAPI-based API for accessing **Hanime.tv** content. This API provides endpoints to retrieve tags, videos by tags, and trending videos. The API supports caching for optimized performance and includes middleware for CORS and GZip compression.

---

## Features

- 🚀 **FastAPI**: Asynchronous and fast Python framework.
- 🏷️ **Tags and Videos**: Retrieve tags and videos by category.
- 📈 **Trending Videos**: Access trending videos by time range.
- ⚡ **Performance**: Optimized caching with `cachetools` and HTTP/2 support via `httpx`.
- 🌐 **CORS Enabled**: API accessible from any frontend.
- 🔧 **Docker Support**: Easy deployment with Docker.

---

## Endpoints

### Root
**GET** `/`
- Returns API information and available endpoints.

### Tags
**GET** `/tags`
- Retrieve all available tags.

**GET** `/tags/{tag}`
- Retrieve videos by a specific tag.
- **Query Parameters**:
  - `page` (default: `1`)
  - `limit` (default: `10`)

### Trending
**GET** `/trending/{time}`
- Retrieve trending videos by time range.
- **Path Parameters**:
  - `time`: `day`, `week`, `month`, `year`
- **Query Parameters**:
  - `page` (default: `1`)
  - `limit` (default: `10`)

---

## Requirements

- Python 3.10+
- FastAPI
- httpx
- cachetools
- pydantic
- python-dotenv
- uvicorn

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/hanime-tv-api.git
   cd hanime-tv-api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file:
   ```plaintext
   PORT=8000
   ```

4. Run the API:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---

## Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t hanime-tv-api .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8000:8000 hanime-tv-api
   ```

3. Access the API at:
   ```
   http://localhost:8000
   ```

---

## VPS Hosting Guide

For VPS deployment using Docker, follow these steps:
- [Host FastAPI on VPS using Docker](https://fastapi.tiangolo.com/deployment/docker/).

---

## Example Usage

### Fetch Tags
```bash
curl http://localhost:8000/tags
```

### Fetch Videos by Tag
```bash
curl http://localhost:8000/tags/action?page=1&limit=5
```

### Fetch Trending Videos
```bash
curl http://localhost:8000/trending/day?page=1&limit=5
```

---

## Contribution

1. Fork the repository.
2. Create your feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add some feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Contact

For any inquiries, please contact:
- **GitHub**: [habitual69](https://github.com/habitual69)
```

### How to Use:
1. Replace `your-username` and `your-email@example.com` with your details.
2. If you deploy the API publicly, update the URLs (e.g., `http://localhost:8000` -> `https://api.yourdomain.com`).
3. Customize as needed for additional features or endpoints.
