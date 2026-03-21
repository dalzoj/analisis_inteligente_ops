from abc import ABC, abstractmethod

class LLMBase(ABC):
    
    @abstractmethod
    async def basic_call():
        pass
 
    @abstractmethod
    async def history_call():
        pass