from i_process_frame import IProcessFrame
from process_frame_mistral import ProcessFrameMistral
from process_frame_openai import ProcessFrameOpenAI
from config import config

# global frame_processor
# Use configuration to determine which processor to instantiate
if config.OPENAI_API_KEY:
    frame_processor: IProcessFrame = ProcessFrameOpenAI(config.OPENAI_API_KEY, config.OPENAI_MODEL)
elif config.MISTRAL_API_KEY:
    frame_processor: IProcessFrame = ProcessFrameMistral(config.MISTRAL_API_KEY, config.MISTRAL_MODEL)
else:
    # Fallback to OpenAI with environment variable
    frame_processor: IProcessFrame = ProcessFrameOpenAI()
# frame_processor: IProcessFrame = ProcessFrameMistral()