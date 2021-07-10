from vector import Vector


class Plane(object):

    NO_NONZERO_ELTS_FOUND_MSG = 'No nonzero elements found'

    def __init__(self, normal_vector=None, constant_term=None):
        try:
            self.dimension = len(normal_vector.coordinates)
            self.normal_vector = normal_vector
        except TypeError:
            raise Exception("Require a Vector to declare a Plane")

        if not constant_term:
            constant_term = 0
        self.constant_term = constant_term

        self.set_basepoint()


    def __str__(self):

        num_decimal_places = 3

        def write_coefficient(coefficient, is_initial_term=False):
            coefficient = round(coefficient, num_decimal_places)
            if coefficient % 1 == 0:
                coefficient = int(coefficient)

            output = ''

            if coefficient < 0:
                output += '-'
            if coefficient > 0 and not is_initial_term:
                output += '+'

            if not is_initial_term:
                output += ' '

            if abs(coefficient) != 1:
                output += '{}'.format(abs(coefficient))

            return output

        n = self.normal_vector.coordinates

        try:
            initial_index = Plane.first_nonzero_index(n)
            terms = [
                write_coefficient(
                    n[i],
                    is_initial_term=(
                        i == initial_index)) +
                'x_{}'.format(
                    i +
                    1) for i in range(
                    self.dimension) if round(
                        n[i],
                    num_decimal_places) != 0]
            output = ' '.join(terms)

        except Exception as e:
            if str(e) == self.NO_NONZERO_ELTS_FOUND_MSG:
                output = '0'
            else:
                raise e

        constant = round(self.constant_term, num_decimal_places)
        if constant % 1 == 0:
            constant = int(constant)
        output += ' = {}'.format(constant)

        return output


    def set_basepoint(self):
        try:
            n = self.normal_vector.coordinates
            c = self.constant_term
            basepoint_coords = [0] * self.dimension

            initial_index = Plane.first_nonzero_index(n)
            initial_coefficient = n[initial_index]

            basepoint_coords[initial_index] = c / initial_coefficient
            self.basepoint = Vector(basepoint_coords)

        except Exception as e:
            if str(e) == Plane.NO_NONZERO_ELTS_FOUND_MSG:
                self.basepoint = None
            else:
                raise e


    def _is_parallel(self, p):
        """
        Return True if Plane p is parallel to this Plane, otherwise return False.
        """

        return self.normal_vector.is_parallel(p.normal_vector)


    def is_same_plane(self, p):
        """
        Return True if Plane p is the same plane as this Plane, otherwise return
        False.
        """

        # The Vector between the two basepoints
        basepoint_difference = self.basepoint.subtract(p.basepoint)

        # If the vector is orthogonal then these planes are the same.
        return basepoint_difference.is_orthogonal(self.normal_vector)


    def __eq__(self, p):
        """
        Returns True if all coefficients of all variables in this Plane and Plane 'p' are
        the same and if the constant_terms of both Planes are also the same.  Returns False
        if any of those conditions are not met.

        The suggested implementation of this has been moved to the is_same_plane method.
        Although that code is good enough for the lecture during which it was introduced this
        class is used within the LineSystem class and the expectation there is clearly what
        I have coded below.  The suggested code returned false positives.
        """
        try:
            assert self.dimension == p.dimension
            assert self.constant_term == p.constant_term
            for i in range(self.dimension):
                assert self.normal_vector.coordinates[i] == p.normal_vector.coordinates[i]
        except AssertionError:
            return False

        return True


    def intersection(self, p):
        """
        Returns a tuple indicating how the planes do, or do not, intersect.
        If the planes are the same return (-1,).
        If the planes are parallel, but not the same, return (0,).
        If the planes intersect return a tuple of the x and y coordinates of the
        intersection point.
        """
        if self._is_parallel(p):
            if self.is_same_plane(p):
                return (-1,)
            return (0,)

        # If we got here then the planes are not parallel and they have an 
        # intersection at (x, y) with:
        # x = (DK1 - BK2) / (AD - BC)
        # y = (AK2 - CK1) / (AD - BC)
        A, B = self.normal_vector.coordinates
        K1 = self.constant_term
        C, D = p.normal_vector.coordinates
        K2 = p.constant_term
        denominator = (A * D) - (B * C)
        x = ((D * K1) - (B * K2)) / denominator
        y = ((A * K2) - (C * K1)) / denominator

        return (x, y)


    @staticmethod
    def first_nonzero_index(iterable):
        for k, item in enumerate(iterable):
            if not (round(item, 9) == 0):
                return k
        raise Exception(Plane.NO_NONZERO_ELTS_FOUND_MSG)
