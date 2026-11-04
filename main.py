from fastapi import FastAPI, HTTPException
import uvicorn
import multiprocessing
from typing import Dict

from models import FrameParserRequest, StartAnalysisRequest, StopAnalysisRequest, APIResponse, ErrorResponse
from processor_factory import ProcessorFactory
from exceptions import CVTError, ProcessorNotFoundError
from config import config
from state import process_manager
import analyze_video

app = FastAPI()

@app.post('/frame-parser', response_model=APIResponse)
async def frame_parser(request: FrameParserRequest):
    """
    Initialize a frame processor based on the specified implementation.
    """
    try:
        processor = ProcessorFactory.create_processor(request.implementation)
        return APIResponse(
            status='success',
            message=f'Processor {request.implementation} initialized successfully'
        )
    except ProcessorNotFoundError as e:
        return ErrorResponse(
            status='error',
            message=e.message,
            details=e.details
        )
    except Exception as e:
        return ErrorResponse(
            status='error',
            message='An unexpected error occurred',
            details=str(e)
        )

@app.post('/start_analysis', response_model=APIResponse)
async def start_analysis(request: StartAnalysisRequest):
    """
    Start analyzing the video stream from the provided RTMP/RTSP URL.
    """
    try:
        if not request.rtmp_url:
            return ErrorResponse(
                status='error',
                message='RTMP/RTSP URL is required'
            )

        p = multiprocessing.Process(target=analyze_video.analyze_video, args=(request.rtmp_url,))
        p.start()
        
        if not process_manager.add_process(request.rtmp_url, p):
            # Process already exists, terminate the new one
            p.terminate()
            return ErrorResponse(
                status='error',
                message=f'Process for {request.rtmp_url} already exists'
            )
            
        return APIResponse(
            status='success',
            message='Video analysis started'
        )
    except Exception as e:
        return ErrorResponse(
            status='error',
            message='Failed to start video analysis',
            details=str(e)
        )

@app.post('/stop_analysis', response_model=APIResponse)
async def stop_analysis(request: StopAnalysisRequest):
    """
    Stop analyzing the video stream for the provided RTMP/RTSP URL.
    """
    try:
        if process_manager.remove_process(request.rtmp_url):
            return APIResponse(
                status='success',
                message=f"Process {request.rtmp_url} stopped"
            )
        else:
            return ErrorResponse(
                status='error',
                message=f"No process with identifier {request.rtmp_url} found"
            )
    except Exception as e:
        return ErrorResponse(
            status='error',
            message='Failed to stop video analysis',
            details=str(e)
        )

if __name__ == '__main__':
    uvicorn.run(app, host=config.HOST, port=config.PORT)
