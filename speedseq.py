from globals import SPEEDSEQ


class Speedseq():
    def __init__(self):
        self.idx = 0

    def increase_speed(self):
        self.idx += 1
        if self.idx > len(SPEEDSEQ) - 1:
            self.idx = len(SPEEDSEQ) - 1

    def decrease_speed(self, nb=1):
        self.idx -= nb
        if self.idx < 0:
            self.idx = 0

    def cut_speed(self, factor):
        self.idx = (int)(self.idx/factor)
        self.idx = 0

    def reset_speed(self):
        self.idx = 0

    @property
    def speed(self):
        return(SPEEDSEQ[self.idx])
