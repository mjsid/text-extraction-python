import re
import os
import json
import asyncio
import pytesseract
from image_extraction.imageprocessing import ProcessedImage
from image_extraction.eventhandler import ExtractText


class ExtractEnglishText(ExtractText):
    def __init__(self, path, directory, loop, queue, config=None, image=None, application='KBANK'):
        super().__init__()
        self.config = config
        self.image = image
        self.directory = directory
        self.application = application
        self.queue = queue
        self.loop = loop

        if self.config == None:
            from image_extraction.ocr import Config
            self.config = Config()

        if path:
            self.config.path = path

        self.setTesseract()

    def setTesseract(self):
        pytesseract.pytesseract.tesseract_cmd = self.config.path

    def extractText(self):
        if not self.image:
            raise Exception("Image must be provided for extraction")
        custom_config = self.config.getConfig()
        # self.image.show()
        content = pytesseract.image_to_string(
            self.image, config=custom_config)

        print(f"Extracted Content :\n{content}")

        output = None
        if self.application == "KBANK":
            output = self.parsed_kbank_text(content)
        if self.application == "SCB":
            output = self.parsed_scb_text(content)
        if self.application == "KRUNGSRI":
            output = self.parsed_krungsri_text(content)

        print(f"Parsed json :\n{output}")
        self.queue.put_nowait(output)
        print("Updated queue..")
        if output:
            self.writeToJsonFile(output)

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.startX = x
            self.startY = y
        if not pressed:
            self.endX = x
            self.endY = y

            width = self.endX - self.startX
            height = self.endY - self.startY

            if width > 0 and height > 0:
                obj = {
                    'startX': self.startX,
                    'startY': self.startY,
                    'endX': self.endX,
                    'endY': self.endY
                }

                piObj = ProcessedImage(**obj)
                # self.image = piObj.image
                # self.image.show()
                self.image = piObj.processedImage
                self.image.show()
                self.extractText()

    def parsed_krungsri_text(self, raw_text):
        '''This method parsed the text from Krungsri application'''
        data = []
        lines = raw_text.splitlines()
        lines = [line for line in lines if line]
        print(lines)
        while lines:
            item = dict()
            line = lines.pop(0)
            if re.search(r'(TRANSFER.*NOBOOK).*([0-9,\.]+)', line):
                m = re.search(r'(TRANSFER.*NOBOOK)\D*([0-9|\.|,]*)', line)
                transactionType = m.group(1)
                amount = m.group(2)
                item.update({"transactionType": transactionType})
                item.update({'amount': amount})
                if lines:
                    line = lines.pop(0)
                    if re.search(r'\d\d[\s|\.]+[A-Z][a-z]{2,3}[-|\s]*\d{4,}', line):
                        m = re.search(
                            r'(\d\d[\s|\.]+[A-Z][a-z]{2,3}[-|\s]*\d{4,})', line)
                        timestamp = m.group(1)
                        item.update({'timestamp': timestamp})
                    data.append(item)
        return data

    def parsed_scb_text(self, raw_text):
        '''This method parsed the text from SCB application and output json object'''
        data = []
        lines = raw_text.splitlines()
        lines = [line for line in lines if line]

        while lines:
            item = dict()
            line = lines.pop(0)
            if re.search(r'Withdrawal|Deposit', line):
                m = re.search(
                    r'([A-Z][a-z]+ - [A-Z]+) [-|+]?([[0-9,\.]+)', line)
                transactionType = m.group(1)
                amount = m.group(2)

                item.update({"transactionType": transactionType})
                item.update({'amount': amount})
                if lines:
                    line = lines.pop(0)
                    if re.search(r'\d\d[\s|\.][A-Z][a-z]{2,3}[-|\s]*\d\d:\d\d', line):
                        m = re.search(
                            r'(\d\d[\s|\.][A-Z][a-z]{2,3}[-|\s|~]*\d\d:\d\d)', line)
                        timestamp = m.group(1)
                        item.update({'timestamp': timestamp})
                    data.append(item)
        return data

    def parsed_kbank_text(self, raw_text):
        '''This method parsed the text and output json object'''
        d = dict()
        lines = raw_text.splitlines()
        lines = [line for line in lines if line]
        print(lines)

        try:
            if len(lines) >= 6:
                if re.search(r'\d+ [a-zA-Z]{3,4} \d\d', lines[0]):
                    print("Captured Date")
                    lines = lines[1:]

                if "Channel" in lines[-1]:
                    payment_details, time, application, accountNum, *accountName, channel = lines
                else:
                    payment_details, time, application, accountNum, *accountName = lines
                # print(f"DATE : {date}")
                print(f"PAYMENT : {payment_details}")
                print(f"TIME: {time}")
                print(f"APPLICATION : {application}")
                print(f"ACCOUNT NUM : {accountNum}")
                print(f"ACCOUNT NAME: {accountName}")

                m = re.search(
                    r'([a-z|A-Z|\s]*) -?([0-9|\.|,]*)', payment_details)
                d['paymentType'] = m.group(1)
                d['amount'] = m.group(2)

                m = re.search(r'(\d\d:\d\d [A-Z][A-Z])', time)
                t = m.group(1)
                timestamp = f"{t}"
                d['time'] = timestamp

                d['application'] = application

                m = re.search(r'([\w\-\s]{13,15})', accountNum)
                d['accountNumber'] = m.group(1)
                account = " ".join(accountName)
                m = re.search(r'To Acc Name: (.*)', account)
                d['accountName'] = m.group(1)
        except Exception as e:
            print(f"Probably not able to extract properly : {e}")

        return d

    def writeToJsonFile(self, data):
        '''Method to dump dictionary into json file'''
        file_path = os.path.join(self.directory, 'extracted.json')
        fh = open(file_path, 'a+')
        fh.write("\n")
        json.dump(data, fh)
