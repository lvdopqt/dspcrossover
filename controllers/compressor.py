from controllers.base import BaseController


class Compressor(BaseController):
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.threshold = 0
        self.ratio = 0
        self.attack = 0
        self.release = 0
        self.makeup_gain = 0
        self.enabled = False

    @classmethod
    def name(cls):
        return "Compressor"

    def display(self):
        return f"Threshold: {self.threshold}\nRatio: {self.ratio}\nAttack: {self.attack}\nRelease: {self.release}\nMakeup Gain: {self.makeup_gain}\nEnabled: {self.enabled}"