from vector import Vector


class Line(object):

    NO_NONZERO_ELTS_FOUND_MSG = 'No nonzero elements found'

    def __init__(self, normal_vector=None, constant_term=None):
        '''
        self.dimension = 2

        if not normal_vector:
            all_zeros = ['0']*self.dimension
            normal_vector = Vector(all_zeros)
        self.normal_vector = normal_vector
        '''
        try:
            self.dimension = len(normal_vector.coordinates)
            self.normal_vector = normal_vector
        except TypeError:
            raise Exception("Require a Vector to declare a Line")

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


    def set_basepoint(self):
        try:
            n = self.normal_vector.coordinates
            c = self.constant_term
            basepoint_coords = [0]*self.dimension

            initial_index = Line.first_nonzero_index(n)
            initial_coefficient = n[initial_index]
            basepoint_coords[initial_index] = c/initial_coefficient
            self.basepoint = Vector(basepoint_coords)

        except Exception as e:
            if str(e) == Line.NO_NONZERO_ELTS_FOUND_MSG:
                self.basepoint = None
            else:
                raise e


    def _is_parallel(self, l):
        """
        Return True if Line l is parallel to this Line, otherwise return False.
        """

        return self.normal_vector.is_parallel(l.normal_vector)


    def __eq__(self, l):
        """
        Return True if Line l is the same line as this Line, otherwise return False.
        """

        # The Vector between the two basepoints
        basepoint_difference = self.basepoint.subtract(l.basepoint)

        # If the vector is orthogonal then these lines are the same.
        return basepoint_difference.is_orthogonal(self.normal_vector)


    def intersection(self, l):
        """
        Returns a tuple indicating how the lines do, or do not, intersect.
        If the lines are the same return (-1,).
        If the lines are parallel, but not the same, return (0,).
        If the lines intersect return a tuple of the x and y coordinates of the 
        intersection point.
        """
        if self._is_parallel(l):
            if self.__eq__(l):
                return (-1,)
            return (0,)

        # If we got here then the lines are not parallel and they have an intersection at
        # (x, y) with:
        # x = (DK1 - BK2) / (AD - BC)
        # y = (AK2 - CK1) / (AD - BC)
        A,B = self.normal_vector.coordinates
        K1 = self.constant_term
        C,D = l.normal_vector.coordinates
        K2 = l.constant_term
        denominator = (A * D) - (B * C)
        x = ((D * K1) - (B * K2)) / denominator
        y = ((A * K2) - (C * K1)) / denominator

        return (x, y)



    @staticmethod
    def first_nonzero_index(iterable):
        for k, item in enumerate(iterable):
            if not (round(item, 9) == 0):
                return k
        raise Exception(Line.NO_NONZERO_ELTS_FOUND_MSG)



