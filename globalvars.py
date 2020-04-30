class SqncObject:
    # Definition of sequence object
    def __init__(self, name, path):
        self.str = name
        self.path = path

class Sequences:
    FID = SqncObject('fid', 'sequence/FID.txt')
    SE = SqncObject('se', 'sequence/SE_te.txt')
    IR = SqncObject('ir', 'sequence/IR_ti.txt')
    SIR = SqncObject('sir', 'sequence/SIR_ti.txt')
    imgSE = SqncObject('imgSE', 'sequence/img/2DSE.txt')

class Gradients:
    X = 0
    Y = 1
    Z = 2
    Z2 = 3

class Relaxations:
    T1 = 'T1'
    T2 = 'T2'


sqncs = Sequences()
grads = Gradients()
rlxs = Relaxations()
