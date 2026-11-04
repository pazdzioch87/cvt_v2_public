# CVT v2 - Computer Vision Toolkit

A computer vision application for real-time video analysis using YOLO object detection and multimodal AI processing.

## Features

- Real-time RTMP/RTSP video stream analysis
- YOLO-based object detection
- Multimodal AI processing with OpenAI GPT-4 and Mistral Pixtral
- Docker containerization for easy deployment

## Architecture

The application follows a modular architecture with clear separation of concerns:

1. **API Layer** (`main.py`): FastAPI endpoints for controlling the application
2. **Configuration Management** (`config.py`): Centralized configuration using environment variables
3. **State Management** (`state.py`): Thread-safe state management for concurrent operations
4. **Video Processing** (`analyze_video.py`): Core video stream processing logic
5. **Frame Processing** (`process_frame_*.py`): Multimodal AI analysis of individual frames
6. **Abstraction Layer** (`i_process_frame.py`): Interface for frame processors
7. **Factory Pattern** (`processor_factory.py`): Dynamic processor instantiation
8. **Error Handling** (`exceptions.py`): Custom exception classes
9. **Data Models** (`models.py`): Pydantic models for API requests/responses

## Setup

### Environment Variables

Copy `.env.example` to `.env` and set the variables:

```
# API Keys (at least one is required)
OPENAI_API_KEY=your_openai_api_key
MISTRAL_API_KEY=your_mistral_api_key

# Environment
PYTHON_ENV=development  # or production
YOLO_VERBOSE=False

# Model settings
YOLO_MODEL_PATH=yolo11n.pt
OPENAI_MODEL=gpt-4o
MISTRAL_MODEL=pixtral-12b-2409

# Server settings
HOST=127.0.0.1
PORT=8000

# SRS settings
SRS_HOST=srs
```

### Installation

```bash
pip install -r requirements.txt
```

Ultralytics downloads `yolo11n.pt` on first use when that file is not already present.

### Running the Application

```bash
# Direct execution
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build and run with docker-compose
docker-compose up --build
```

## API Endpoints

- `POST /frame-parser`: Initialize a frame processor
- `POST /start_analysis`: Start video analysis from an RTMP/RTSP URL
- `POST /stop_analysis`: Stop video analysis for a URL

## Development

### Code Structure

The application follows these best practices:

1. **Dependency Injection**: Configuration and dependencies are injected rather than hardcoded
2. **Thread Safety**: State management uses thread-safe patterns
3. **Error Handling**: Comprehensive error handling with custom exception types
4. **Configuration Management**: Centralized configuration using environment variables
5. **Interface Abstraction**: Clear interfaces for extensibility
6. **Factory Pattern**: Dynamic object creation based on configuration

### Adding New Processors

1. Implement the `IProcessFrame` interface
2. Register the processor in `ProcessorFactory`
3. Add any required configuration to `config.py`

## Security

- API keys should be stored in environment variables, not in source code
- Input validation is performed on all API endpoints
- Docker containers run with minimal privileges