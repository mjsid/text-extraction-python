import os
import sys
import json
import argparse
import asyncio
import signal
import websockets
from image_extraction.ocr import ExtractEnglishText

loop = asyncio.get_event_loop()
queue = asyncio.Queue()


async def echo(websocket, path):
    print("Starting server..")
    print(websocket)
    print("Sending echo message")
    print(path)
    while True:
        data = await queue.get()
        print(f"EXTRACTED DATA : {data}")
        jsonDumps = json.dumps(data)
        print(f"JSONDUMPS : {jsonDumps}")
        await websocket.send(json.dumps(data))


async def start_server():
    print("Starting server...")
    server = await websockets.server.serve(echo, 'localhost', 8765)
    return server

if __name__ == '__main__':
    my_parser = argparse.ArgumentParser(prog='run_ocr',
                                        description='Run the tesseract ocr over selected portion of the screen and extract text',
                                        allow_abbrev=False)
    my_parser.add_argument('--path', action='store', help="Provide installed tesseract engine path. Default path is 'C:\\Program Files\\Tesseract-OCR\\tesseract' ",
                           type=str, default=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    my_parser.add_argument('--dir', action='store', type=str,
                           help='Provide path of the dir to store extracted text in extracted.json file. If you doesn\'t provide the directory path, it will store extracted text in current working directory')
    my_parser.add_argument('--application', action='store', type=str,
                           help='Provide application on which ocr need to be applied (KBANK|SCB). Default is KBANK')
    args = my_parser.parse_args()

    path = args.path
    if not os.path.exists(path):
        print("Specified path does not exist")
        sys.exit()

    directory = args.dir
    if not directory or os.path.isdir(directory):
        directory = os.getcwd()

    application = args.application
    eng = ExtractEnglishText(path, directory, loop,
                             queue, application=application)

    loop.create_task(start_server())
    loop.run_in_executor(None, eng.setListener)
    loop.run_forever()
