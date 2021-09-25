# Author: Dennis Yakovlev

# None related parsing items needed in parsing files.

class Info:
    def __init__(self, index, arr) -> None:
        self.index = index
        self.arr = arr

class Hold:
    def __init__(self, ty, val) -> None:
        self.ty = ty
        self.val = val

    def lessThan(self, num):

        return False if self.val == -1 else self.val < num

    def __str__(self) -> str:
        return f'{self.ty} {self.val}, '
