class Sequence:
    # Definition of sequence object
    def __init__(self, name, path):
        self.str = name
        self.path = path

class Sequences:
    def __init__(self):
        # Define sequences
        self.FID = Sequence('fid', 'sequence/FID.txt')
        self.SE = Sequence('se', 'sequence/SE_te.txt')
        self.IR = Sequence('ir', 'sequence/IR_ti.txt')
        self.SIR = Sequence('sir', 'sequence/SIR_ti.txt')
        self.imgSE = Sequence('imgSE', 'sequence/img/2DSE.txt')

class Gradients:
    def __init__(self):
        # Define Gradients
        self.X = 0
        self.Y = 1
        self.Z = 2
        self.Z2 = 3


sqncs = Sequences()
grads = Gradients()
