from PIL import ImageGrab, ImageEnhance


class ProcessedImage:
    def __init__(self, **kwargs):
        self.startX = kwargs.get('startX')
        self.startY = kwargs.get('startY')
        self.endX = kwargs.get('endX')
        self.endY = kwargs.get('endY')
        self._image = None
        self._processedImage = None
        self.setImage()
        self.setGrayImage()

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value

    @property
    def processedImage(self):
        return self._processedImage

    @processedImage.setter
    def processedImage(self, value):
        self._processedImage = value

    def setImage(self):
        image = ImageGrab.grab(
            bbox=(self.startX, self.startY, self.endX, self.endY))
        self._image = image

    def setGrayImage(self):
        grey_img = self.image.convert('LA')
        # grey_img.show()
        enhancer = ImageEnhance.Contrast(grey_img)

        factor = 4
        enhanced_image = enhancer.enhance(factor)

        self._processedImage = enhanced_image
