class MemeOverflowError(Exception):
    "Module base exception"

class ImgFlipError(MemeOverflowError):
    "Error raised in the ImgFlip class"

class TwitterError(MemeOverflowError):
    "Error raised in the Twitter class"

class StackExchangeError(MemeOverflowError):
    "Error raised in the StackExchange class"

class MemeOverflowWarning(Warning):
    "Module base warning"

class StackExchangeNoKeyWarning(MemeOverflowWarning):
    "Warning raise when no StackExchange API key is provided"
