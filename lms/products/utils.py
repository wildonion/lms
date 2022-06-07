


import random


def discount_generator():
     code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
     code = ''
     for i in range(0, 7):
         slice_start = random.randint(0, 26)
         code += code_chars[slice_start: slice_start + 1]
     return code