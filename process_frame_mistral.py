import cv2
import base64
from mistralai.client import Mistral
import json
from i_process_frame import IProcessFrame
from notification import happy_person_detected, glasses_detected, image_summarization
from cv2.typing import MatLike
import functools
from typing import Optional

class ProcessFrameMistral(IProcessFrame):
    def __init__(self, api_key: Optional[str] = None, model: str = "pixtral-12b-2409"):
        """
        Initialize the Mistral frame processor.
        
        Args:
            api_key: Mistral API key. If None, will use the MISTRAL_API_KEY environment variable
            model: Mistral model to use for processing
        """
        self.client = Mistral(api_key=api_key) if api_key else Mistral()
        self.model = model
        
        # self.name_to_function = functools.partial(happy_person_detected)
        self.name_to_function = functools.partial(glasses_detected)
        # self.name_to_function = functools.partial(immage_summarization)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "glasses_detected",
                    "description": "Prints a message only when a person with the glasses is detected",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "analysis_result": {
                                "type": "string",
                                "description": "A summary or analysis of the person with glasses detection.",
                            }
                        },
                        "required": ["analysis_result"],
                    }
                }
            }
        ]
        pass

    def process_frame(self, frame: MatLike):
        print("Analyze the frame using Pixtral multimodal capabilities.")
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
                # {
                #     "role": "system",
                #     "content": "You are an AI assistant that analyzes images for specific situations."
                # },
                # # Happyness detection
                # {
                #     "role": "user",
                #     "content": [
                #         {"type": "text", "text": "There is a man on the picture. Does he excited or smiling a lot? If so, please call the 'happy_person_detected' function with a brief summary. Otherwise do not call any function!"},
                #         # {"type": "text", "text": "What do you see on the image?"},
                #         # {"type": "text", "text": "Analyze the following image and determine if it contains a happy or smiling person. If so, please call the 'happy_person_detected' function with a brief summary."},
                #         {
                #             "type": "image_url",
                #             "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                #         },
                #     ],
                # }
                # Glassess detection
                {
                    "role": "user",
                    "content": [
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
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                tools = self.tools,
                tool_choice = "any")

            # Check if a function was called
            if response and response.choices:
                first_choice = response.choices[0]
                if first_choice and first_choice.message and first_choice.message.tool_calls:
                    tool_call = first_choice.message.tool_calls[0]
                    if tool_call and tool_call.function:
                        function_name = tool_call.function.name
                        if tool_call.function.arguments:
                            try:
                                raw_arguments = tool_call.function.arguments
                                if isinstance(raw_arguments, str):
                                    function_params = json.loads(raw_arguments)
                                else:
                                    function_params = raw_arguments
                                function_result = self.name_to_function(**function_params)
                            except json.JSONDecodeError:
                                print("Error: Invalid JSON in function arguments")
                            except Exception as e:
                                print(f"Error calling function: {str(e)}")
                        else:
                            print("Error: Function arguments are missing")
                    else:
                        print("Error: Invalid tool call structure")
                else:
                    print("Error: No valid choices or tool calls in the response")
            else:
                print("Error: Invalid response structure")

        except Exception as e:
            print(f"Error processing frame: {e}")
