# FastAPI Implementation Guide - Chat with OpenAPI

This guide outlines the minimal viable implementation of the Chat with OpenAPI application using FastAPI, focusing on essential features while maintaining code simplicity.

## Project Structure

```
chat-openapi/
├── docker/
│   ├── Dockerfile.api
│   └── Dockerfile.frontend
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Environment configuration
│   │   ├── models.py         # Pydantic models
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── openapi.py    # OpenAPI processing
│   │       ├── vector_store.py # Qdrant operations
│   │       └── llm.py        # OpenRouter integration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── components/
│   │   │   ├── FileUpload.vue
│   │   │   └── Chat.vue
│   │   └── main.js
│   ├── package.json
│   └── tailwind.config.js
├── docker-compose.yml
└── .env.example
```

## Core Dependencies

### Backend (requirements.txt)
```
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
python-multipart==0.0.6
qdrant-client==1.6.4
langchain==0.0.335
pydantic==2.4.2
httpx==0.25.1
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "vue": "^3.3.8",
    "axios": "^1.6.2",
    "tailwindcss": "^3.3.5"
  }
}
```

## Implementation Steps

### 1. Environment Setup

**.env.example**
```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# OpenRouter
OPENROUTER_API_KEY=your_api_key
```

### 2. Docker Configuration

**docker-compose.yml**
```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
    depends_on:
      - qdrant

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  qdrant_data:
```

### 3. Backend Implementation

**app/config.py**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_host: str
    api_port: int
    qdrant_host: str
    qdrant_port: int
    openrouter_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
```

**app/models.py**
```python
from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatResponse(BaseModel):
    response: str
```

**app/services/openapi.py**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

class OpenAPIProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    async def process_spec(self, spec_content: str) -> List[str]:
        # Parse and validate OpenAPI spec
        spec_json = json.loads(spec_content)
        
        # Convert to string for chunking
        spec_str = json.dumps(spec_json, indent=2)
        
        # Split into chunks
        return self.text_splitter.split_text(spec_str)
```

**app/services/vector_store.py**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain.embeddings import OpenAIEmbeddings

class VectorStore:
    def __init__(self, host: str, port: int):
        self.client = QdrantClient(host=host, port=port)
        self.embeddings = OpenAIEmbeddings()
        self.collection_name = "openapi_specs"

    async def init_collection(self):
        # Create collection if not exists
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

    async def store_chunks(self, chunks: List[str]):
        # Generate embeddings and store
        embeddings = await self.embeddings.aembed_documents(chunks)
        
        # Store in Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                {"id": i, "vector": emb, "payload": {"text": chunk}}
                for i, (emb, chunk) in enumerate(zip(embeddings, chunks))
            ]
        )

    async def search_similar(self, query: str, limit: int = 3):
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Search in Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )
        
        return [hit.payload["text"] for hit in results]
```

**app/services/llm.py**
```python
import httpx
from typing import AsyncGenerator

class OpenRouterLLM:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"

    async def generate_stream(
        self,
        messages: List[dict],
        context: str
    ) -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "http://localhost:3000",
                },
                json={
                    "model": "mistralai/mistral-7b-instruct",
                    "messages": [
                        {"role": "system", "content": f"You are an AI assistant helping with OpenAPI specifications. Use this context to answer: {context}"},
                        *messages
                    ],
                    "stream": True
                },
                timeout=None
            )
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if content := data.get("choices", [{}])[0].get("delta", {}).get("content"):
                        yield content
```

**app/main.py**
```python
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .services.openapi import OpenAPIProcessor
from .services.vector_store import VectorStore
from .services.llm import OpenRouterLLM
from .models import ChatMessage, ChatResponse
from typing import List
from fastapi.responses import StreamingResponse

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
openapi_processor = OpenAPIProcessor()
vector_store = VectorStore(settings.qdrant_host, settings.qdrant_port)
llm = OpenRouterLLM(settings.openrouter_api_key)

@app.post("/upload")
async def upload_spec(file: UploadFile):
    if not file.filename.endswith('.json'):
        raise HTTPException(400, "Only JSON files are supported")
    
    content = await file.read()
    chunks = await openapi_processor.process_spec(content.decode())
    await vector_store.store_chunks(chunks)
    return {"message": "Specification processed successfully"}

@app.post("/chat")
async def chat(messages: List[ChatMessage]):
    # Get last user message
    last_message = messages[-1].content
    
    # Search relevant contexts
    contexts = await vector_store.search_similar(last_message)
    context = "\n".join(contexts)
    
    return StreamingResponse(
        llm.generate_stream(
            [{"role": m.role, "content": m.content} for m in messages],
            context
        ),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
```

### 4. Frontend Implementation

**src/App.vue**
```vue
<template>
  <div class="container mx-auto px-4 py-8">
    <FileUpload @file-uploaded="handleFileUpload" />
    <Chat v-if="specUploaded" />
  </div>
</template>

<script>
import FileUpload from './components/FileUpload.vue'
import Chat from './components/Chat.vue'

export default {
  components: { FileUpload, Chat },
  data() {
    return {
      specUploaded: false
    }
  },
  methods: {
    handleFileUpload() {
      this.specUploaded = true
    }
  }
}
</script>
```

**src/components/FileUpload.vue**
```vue
<template>
  <div class="mb-8">
    <input
      type="file"
      accept=".json"
      @change="uploadFile"
      class="hidden"
      ref="fileInput"
    >
    <button
      @click="$refs.fileInput.click()"
      class="bg-blue-500 text-white px-4 py-2 rounded"
    >
      Upload OpenAPI Spec
    </button>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  methods: {
    async uploadFile(event) {
      const file = event.target.files[0]
      if (!file) return

      const formData = new FormData()
      formData.append('file', file)

      try {
        await axios.post('http://localhost:8000/upload', formData)
        this.$emit('file-uploaded')
      } catch (error) {
        console.error('Upload failed:', error)
      }
    }
  }
}
</script>
```

**src/components/Chat.vue**
```vue
<template>
  <div class="max-w-2xl mx-auto">
    <div class="bg-gray-100 p-4 rounded-lg h-96 overflow-y-auto mb-4">
      <div v-for="(message, i) in messages" :key="i" class="mb-4">
        <div :class="message.role === 'user' ? 'text-right' : ''">
          <span class="bg-white p-2 rounded inline-block">
            {{ message.content }}
          </span>
        </div>
      </div>
    </div>
    
    <form @submit.prevent="sendMessage" class="flex gap-2">
      <input
        v-model="input"
        type="text"
        class="flex-1 border p-2 rounded"
        placeholder="Ask about the API..."
      >
      <button
        type="submit"
        class="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Send
      </button>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      messages: [],
      input: '',
      currentResponse: ''
    }
  },
  methods: {
    async sendMessage() {
      if (!this.input.trim()) return

      // Add user message
      this.messages.push({ role: 'user', content: this.input })
      this.input = ''

      try {
        const response = await axios.post('http://localhost:8000/chat', 
          this.messages,
          { responseType: 'stream' }
        )

        // Add assistant message placeholder
        this.currentResponse = ''
        this.messages.push({ role: 'assistant', content: '' })

        // Process streaming response
        const reader = response.data.getReader()
        const decoder = new TextDecoder()

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          this.currentResponse += chunk
          this.messages[this.messages.length - 1].content = this.currentResponse
        }
      } catch (error) {
        console.error('Chat failed:', error)
      }
    }
  }
}
</script>
```

## Minimal Features Included

1. **File Upload**
   - Single OpenAPI spec JSON upload
   - Basic validation
   - Automatic chunking

2. **Vector Storage**
   - Simple Qdrant collection
   - Basic similarity search
   - No persistence between sessions (can be added later)

3. **Chat Interface**
   - Clean, minimal UI
   - Real-time streaming responses
   - Basic message history

4. **LLM Integration**
   - Streaming responses
   - Context-aware responses
   - Single model support (Mistral 7B)

## What's Not Included (Future Enhancements)

1. User authentication
2. Chat history persistence
3. Multiple file support
4. Advanced error handling
5. Loading states
6. Model selection
7. Advanced OpenAPI validation
8. Test coverage

## Running the Application

1. Copy `.env.example` to `.env` and add your OpenRouter API key
2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
3. Access the application at `http://localhost:3000`

## Next Steps

1. Test the basic functionality
2. Add error handling for edge cases
3. Implement loading states
4. Add persistent storage
5. Enhance the UI/UX
