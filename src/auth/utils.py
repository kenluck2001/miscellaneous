class Vector:
    @staticmethod
    def mul(X, Y):
        """Compute vector multiplication X * Y"""
        nrows_X = len(X)
        nrows_Y = len(Y)
        assert nrows_X == nrows_Y, "Mismatched vector dimensions"
        R = [0 for _ in range(nrows_Y)]
        for i in range(nrows_X):
            R[i] = X[i] * Y[i]
        return R

    @staticmethod
    def add(X, Y):
        """Compute vector addition X + Y"""
        nrows_X = len(X)
        nrows_Y = len(Y)
        assert nrows_X == nrows_Y, "Mismatched vector dimensions"
        R = [0 for _ in range(nrows_X)]
        for i in range(nrows_Y):
            R[i] = X[i] + Y[i]
        return R

    @staticmethod
    def sub(X, Y):
        """Compute vector subtraction X - Y"""
        nrows_X = len(X)
        nrows_Y = len(Y)
        assert nrows_X == nrows_Y, "Mismatched vector dimensions"
        R = [0 for _ in range(nrows_Y)]
        for i in range(nrows_X):
            R[i] = X[i] - Y[i]
        return R

    @staticmethod
    def scalarMul(X, scalar):
        """Compute vector scalar multiplication X * scalar"""
        nrows_X = len(X)
        R = [0 for _ in range(nrows_X)]
        for i in range(nrows_X):
            R[i] = X[i] * scalar
        return R
