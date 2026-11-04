import cv2
import base64
from openai import OpenAI
import json
from i_process_frame import IProcessFrame
from notification import happy_person_detected, glasses_detected, image_summarization
from cv2.typing import MatLike
from typing import Optional

class ProcessFrameOpenAI(IProcessFrame):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize the OpenAI frame processor.
        
        Args:
            api_key: OpenAI API key. If None, will use the OPENAI_API_KEY environment variable
            model: OpenAI model to use for processing
        """
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.model = model
        
        self.function_schema = {
            "name": "glasses_detected",
            "description": "Prints a message when a person wearing glasses is detected on the image frame.",
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis_result": {
                        "type": "string",
                        "description": "A summary or analysis of the person with glasses detection."
                    }
                },
                "required": ["analysis_result"]
            }
        }
        # self.function_schema = {
        #     "name": "happy_person_detected",
        #     "description": "Prints a message when a happy person is detected in the video frame.",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "analysis_result": {
        #                 "type": "string",
        #                 "description": "A summary or analysis of the detected happy person."
        #             }
        #         },
        #         "required": ["analysis_result"]
        #     }
        # }
        pass

    def process_frame(self, frame: MatLike):
        print("Analyze the frame using GPT-4's multimodal capabilities.")
        try:
            # Encode the frame as JPEG
            retval, buffer = cv2.imencode('.jpg', frame)
            if not retval:
                print("Failed to encode frame.")
                return

            # Convert to base64
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            # Prepare the messages for GPT-4
            messages = [
                {
                    "role": "system",
                    "content": "You are an AI assistant that analyzes images for specific situations."
                },
                {
                    "role": "user",
                    "content": [
                        # {"type": "text", "text": "There is a man on the picture. Does he smiling? If so, please call the 'happy_person_detected' function with a brief summary."},
                        {"type": "text", "text": "When you detect a person in the image, check if they are wearing glasses, if so - call 'glasses_detected' function. Otherwise do not call any function!"},
                        # {"type": "text", "text": "What do you see on the image?"},
                        # {"type": "text", "text": "Analyze the following image and determine if it contains a happy or smiling person. If so, please call the 'happy_person_detected' function with a brief summary."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                        },
                    ],
                }
            ]

            # Call OpenAI GPT-4 API with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=[self.function_schema],
                function_call="auto")

            # Check if a function was called
            if response.choices[0].finish_reason == "function_call":
                function_call = response.choices[0].message.function_call
                if function_call.name == 'glasses_detected':
                    # Parse the arguments
                    arguments = json.loads(function_call.arguments)
                    analysis_result = arguments.get('analysis_result', 'No analysis provided.')
                    # Call the function
                    glasses_detected(analysis_result)
        except Exception as e:
            print(f"Error processing frame: {e}")
