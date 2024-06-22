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
