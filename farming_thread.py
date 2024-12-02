from PySide6.QtCore import QThread, Signal
import asyncio
import threading
from core.utils.logger1 import logger

class FarmingThread(QThread):
    finished = Signal()
    
    def __init__(self, main_func):
        super().__init__()
        self.main_func = main_func
        self.running = False
        self._stop_event = threading.Event()
        self.db = None
        
    def run(self):
        self.running = True
        self._stop_event.clear()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.main_func())
        except Exception as e:
            logger.error(f"Ошибка в процессе фарминга: {e}")
        finally:
            self.running = False
            # Закрываем соединение с БД если оно открыто
            if hasattr(self, 'db') and self.db:
                try:
                    loop.run_until_complete(self.db.close_connection())
                except Exception as e:
                    logger.error(f"Ошибка при закрытии БД: {e}")
            loop.close()
            self.finished.emit()
            
    def stop(self):
        self.running = False
        self._stop_event.set()
        
    def is_stopped(self):
        return self._stop_event.is_set() 