from fvm import CrsMatrix

from jadapy import NumPyInterface

from scipy import sparse

class JadaOp:
    def __init__(self, mat):
        self.fvm_mat = mat
        self.mat = sparse.csr_matrix((mat.coA, mat.jcoA, mat.begA), shape=(mat.n, mat.n))
        self.dtype = mat.coA.dtype
        self.shape = (mat.n, mat.n)

    def matvec(self, x):
        return self.mat * x

    def __matmul__(self, x):
        return self.mat * x

class JadaPrecOp(object):
    def __init__(self, op, interface, shifted=True):
        self.op = op
        self.interface = interface
        self.shifted = shifted

        self.dtype = self.op.dtype
        self.shape = self.op.shape

    def matvec(self, x):
        alpha = self.op.alpha
        beta = self.op.beta
        try:
            if len(alpha.shape) == 2:
                alpha = alpha[0, 0]
                beta = beta[0, 0]
            elif len(alpha.shape) == 1:
                alpha = alpha[0]
                beta = beta[0]
        except AttributeError:
            pass

        if not self.shifted:
            rhs = x.copy()
            return self.op.proj(self.interface.solve(self.op.A.fvm_mat, rhs))

        rhs = x.copy()
        mat = beta * self.op.A.mat - alpha * self.op.B.mat
        crs_mat = CrsMatrix(mat.data, mat.indices, mat.indptr)
        return self.op.proj(self.interface.solve(crs_mat, rhs))

class JadaInterface(NumPyInterface.NumPyInterface):
    def __init__(self, interface, jac_op, mass_op, *args):
        super().__init__(*args)
        self.interface = interface
        self.jac_op = jac_op
        self.mass_op = mass_op

    # def solve(self, op, x, tol, maxit):
    #     if op.dtype.char != op.dtype.char.upper():
    #         # Real case
    #         if abs(op.alpha.real) < abs(op.alpha.imag):
    #             op.alpha = op.alpha.imag
    #         else:
    #             op.alpha = op.alpha.real
    #         op.beta = op.beta.real

    #     out = x.copy()
    #     for i in range(x.shape[1]):
    #         out[:, i] , info = sparse.linalg.gmres(op, x[:, i], restart=100, maxiter=10, tol=tol, atol=0,
    #                                                M=JadaPrecOp(op, self.interface, False))
    #         if info < 0:
    #             raise Exception('GMRES returned ' + str(info))
    #         elif info > 0:
    #             warnings.warn('GMRES did not converge in ' + str(info) + ' iterations')
    #     return out

    # def solve(self, op, x, tol, maxit):
    #     out = x.copy()
    #     for i in range(x.shape[1]):
    #         out[:, i] , info = sparse.linalg.gmres(op, x[:, i], restart=100, maxiter=10, tol=tol, atol=0)
    #         if info < 0:
    #             raise Exception('GMRES returned ' + str(info))
    #         elif info > 0:
    #             warnings.warn('GMRES did not converge in ' + str(info) + ' iterations')
    #     return out

    def prec(self, x, *args):
        rhs = x.copy()
        return self.interface.solve(self.jac_op.fvm_mat, rhs)

    def shifted_prec(self, x, alpha, beta):
        try:
            if len(alpha.shape) == 2:
                alpha = alpha[0, 0]
                beta = beta[0, 0]
            elif len(alpha.shape) == 1:
                alpha = alpha[0]
                beta = beta[0]
        except AttributeError:
            pass

        rhs = x.copy()
        mat = beta * self.jac_op.mat - alpha * self.mass_op.mat
        crs_mat = CrsMatrix(mat.data, mat.indices, mat.indptr)
        return self.interface.solve(crs_mat, rhs)
