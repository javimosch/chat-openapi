# Chat with OpenAPI

An intelligent, context-aware chat application for exploring OpenAPI specifications using AI-powered retrieval and generation techniques.

## Features

- Upload and process OpenAPI specifications
- Semantic search and retrieval
- AI-powered chat interface
- Vector-based storage with Qdrant
- Modern Vue.js frontend
- CLI interface for testing and management

## Tech Stack

- **Backend**: FastAPI (Python)
- **Vector Database**: Qdrant
- **Frontend**: Vue.js + Tailwind CSS
- **LLM Integration**: OpenRouter
- **Containerization**: Docker + Docker Compose

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 20+

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chat-openapi.git
   cd chat-openapi
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
chat-openapi/
├── backend/             # FastAPI application
│   ├── app/
│   │   ├── api/        # API routes
│   │   ├── core/       # Core functionality
│   │   ├── models/     # Data models
│   │   └── services/   # Business logic
│   └── requirements.txt
├── frontend/           # Vue.js application
├── docker/            # Dockerfile definitions
├── docs/             # Documentation
└── docker-compose.yml
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
