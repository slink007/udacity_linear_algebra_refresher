from decimal import Decimal, getcontext

from vector import Vector

getcontext().prec = 30


class Line(object):

    NO_NONZERO_ELTS_FOUND_MSG = 'No nonzero elements found'

    def __init__(self, normal_vector=None, constant_term=None):
        """
        Expects a line in the form of Ax + By = k.

        The normal_vector input needs to be an iterable suitable for forming
        a Vector.  The values in that iterable must be the 'A' and 'B' 
        values from the line equation.

        Constant term = k. 
        """
        self.dimension = 2

        if not normal_vector:
            all_zeros = ['0']*self.dimension
            normal_vector = Vector(all_zeros)
        self.normal_vector = normal_vector

        if not constant_term:
            constant_term = Decimal('0')
        self.constant_term = Decimal(constant_term)

        self.set_basepoint()


    def set_basepoint(self):
        try:
            n = self.normal_vector
            c = self.constant_term
            basepoint_coords = ['0']*self.dimension

            initial_index = Line.first_nonzero_index(n)
            initial_coefficient = n[initial_index]

            basepoint_coords[initial_index] = c/initial_coefficient
            self.basepoint = Vector(basepoint_coords)

        except Exception as e:
            if str(e) == Line.NO_NONZERO_ELTS_FOUND_MSG:
                self.basepoint = None
            else:
                raise e


    def __str__(self):
    """
    Creates the string that is printed out when a Line object is
    printed.  For example, if the Line is 3x - 2y = 1 this will
    print 3x_1 - 2x_2 = 1.
    """
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

        n = self.normal_vector

        try:
            initial_index = Line.first_nonzero_index(n)
            terms = [write_coefficient(n[i], is_initial_term=(i==initial_index)) + 'x_{}'.format(i+1)
                     for i in range(self.dimension) if round(n[i], num_decimal_places) != 0]
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


    @staticmethod
    def first_nonzero_index(iterable):
        for k, item in enumerate(iterable):
            if not MyDecimal(item).is_near_zero():
                return k
        raise Exception(Line.NO_NONZERO_ELTS_FOUND_MSG)


    def is_parallel(self, l):
        """
        Return True if Line l is parallel to this Line, otherwise return False.
        """
        v1 = Vector(self.normal_vector)
        v2 = Vector(l.normal_vector)

        return v1.is_parallel(v2)


    def is_same(self, l):
        """
        Returns True if this Line and Line l describe the same line.  Returns False
        if that is not the case.
        """
        ratio = self.normal_vector[0] / l.normal_vector[0]
        try:
            for i in range(1, len(self.normal_vector)):
                diff = MyDecimal( abs((self.normal_vector[i] / l.normal_vector[i]) - ratio) )
                assert diff.is_near_zero()
        except AssertionError:
            return False
        return True


    def intersection(self, l):
        """
        Returns a tuple indicating how many intersections there are between two Lines.
        If lines are parallel, and there are no intersections, it returns (0,).
        If lines are parallel, and the lines are the same, it returns (-1,).
        If lines are not parallel it calculates the intersection point and returns the
        coordinates of that intersection as (x, y).
        """
        if not isinstance(l, Line):
            raise TypeError('Intersection test requires a line.')

        if is_parallel(l):
            if is_same(l):
                return (-1,)
            return (0,)

        # If we got here then the lines are not parallel and they have an intersection at
        # (x, y) with:
        # x = (DK1 - BK2) / (AD - BC)
        # y = (AK2 - CK1) / (AD - BC)
        A = self.normal_vector[0]
        B = self.normal_vector[1]
        K1 = self.constant_term
        C = l.normal_vector[0]
        D = l.normal_vector[1]
        K2 = l.constant_term
        denominator = (A * D) - (B * C)
        x = ((D * K1) - (B * K2)) / denominator
        y = ((A * K2) - (C * K1)) / denominator

        return (x, y)

class MyDecimal(Decimal):
    def is_near_zero(self, eps=1e-10):
        return abs(self) < eps
