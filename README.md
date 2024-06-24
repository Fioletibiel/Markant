# b2b onboarding application - coding challenge

## Challenge 1: Web App - URL shortener

### Description

---

Your assignment is to implement a URL shortening service using Python (backend) and any framework of your choice.

### Required functionality

---

Short link is a URL shortening service where you enter a URL such as `https://en.wikipedia.org/wiki/Computer` and it returns a short URL such as `http://short.est/GeAi9K.`

### Requirements

---

There is no restriction on how your encode/decode algorithm should work. You just need to make sure that a URL can be encoded to a short URL and the short URL can be decoded to the original URL. Please follow these requirements:

- Language: **Python**
- Framework: **any framework**
- Two endpoints are required
  - **/encode** - Encodes a URL to a shortened URL
  - **/decode** - Decodes a shortened URL to its original URL.
- Both endpoints should **return JSON**
- **Provide API tests** for both endpoints
- **Provide detailed instructions** on how to run your app and your tests in a separate markdown file
- You do not need to persist short URLs to a database. Keep them in memory.
- **Bonus**: Store all shortened URLs in a simple database (e.g. mongoDB)
- **Bonus**: Build a small UI where you can de- and encode short URLs

### Evaluation Criteria

---

- **Best Practice: Python** best practices
- **API:** API implemented featuring a /encode and /decode endpoint
- **Documentation** Can we run the project from scratch easily with the docs you provided (including dependency management)?
- **Completeness:** did you complete the features? Are all the tests running?
- **Correctness:** does the functionality act insensible, thought-out ways?
- **Maintainability:** is it written in a clean, maintainable way?
- **Auditability:** Show us your work through your commit history


---

---


# URL Shortener Service

This project is a URL shortening service built with FastAPI.

## Installation

1. **Clone the repository:**  
`git clone https://github.com/Fioletibiel/Markant.git`  
`cd <project-directory>`  
  

2. **Install dependencies:**  `pip install -r requirements.txt`.

## Running Tests

To run tests, use pytest: `pytest`.

## Running the Server

To start the FastAPI server:
`uvicorn src.main:app --reload`.

The server will start at `http://localhost:8000`.

## Viewing API Documentation

### Swagger UI

FastAPI automatically generates Swagger documentation. After starting the server, navigate to:

http://localhost:8000/docs

Here you can explore the API endpoints, send requests, and view responses interactively.

### Redoc

To view the API documentation in Redoc format, go to:

http://localhost:8000/redoc


Redoc provides a clean, responsive interface for exploring your API specifications.

## Additional Notes

- **Deployment:** For deploying FastAPI applications to production, consider using ASGI servers like `uvicorn` behind a reverse proxy (e.g., Nginx, Apache) for load balancing and security.     

  
- **Recruitment:** This project was made for Markant in a recruitment process.
