"""
This module is used to grab the portion of the screen
"""
import asyncio
from pynput import mouse, keyboard

loop = asyncio.get_event_loop()


class ExtractText:

    def __init__(self):
        self.startX = None
        self.startY = None
        self.endX = None
        self.endY = None

    def setListener(self):
        print("Setting Listeners...")
        self.mouse_listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)

        self.mouse_listener.start()

        with keyboard.Listener(
                on_release=self.on_release) as listener:
            listener.join()

    def on_release(self, key):
        if key == keyboard.Key.esc:
            self.mouse_listener.stop()
            loop.stop()
            return False
        if key == keyboard.Key.f1:
            self.mouse_listener.stop()
            self.mouse_listener = mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click,
                on_scroll=self.on_scroll)
            self.mouse_listener.start()
            return True
        if key == keyboard.Key.f10:
            self.mouse_listener.stop()
            return True

    def on_move(self, x, y):
        '''override this method to the child class'''
        pass

    def on_click(self, x, y, button, pressed):
        '''override this method to the child class'''
        pass

    def on_scroll(self, x, y, dx, dy):
        '''override this method to the child class'''
        pass
