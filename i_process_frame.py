from abc import ABC, abstractmethod
from cv2.typing import MatLike

class IProcessFrame(ABC):
    @abstractmethod
    def process_frame(self, frame: MatLike):
        pass