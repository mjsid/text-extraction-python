'''This module let user set the configuration parameter for tesseract OCR engine'''

TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract'


class Config:
    def __init__(self, oem=3, psm=6, path=TESSERACT_PATH):
        '''method to initialise configuration values of tesseract'''
        self.oem = oem
        self.psm = psm
        self.path = path

    def getConfig(self):
        '''method to get configuration in string format'''
        config = f'--oem {self.oem} --psm {self.psm}'
        return config

    def getTesseractPath(self):
        if self.path == None:
            raise Exception("Set Tesseract path first in configuration object")

        return self.path

    def setTesseractPath(self, path):
        self.path = path

    def isPathSet(self):
        return self.path != None
