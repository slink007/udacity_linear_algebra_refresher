from decimal import Decimal, getcontext  # This will either have to go (most likely) or I'll have to 
                                         # put Decimal back into the other files.
from copy import deepcopy

from vector import Vector
from plane import Plane

getcontext().prec = 30


class LinearSystem(object):

    ALL_PLANES_MUST_BE_IN_SAME_DIM_MSG = 'All planes in the system should live in the same dimension'
    NO_SOLUTIONS_MSG = 'No solutions'
    INF_SOLUTIONS_MSG = 'Infinitely many solutions'

    def __init__(self, planes):
        """
        The 'planes' input expects an iterable composed of Plane objects.  A LinearSystem is a collection
        of Plane objects.  It has methods for swapping the order of those objects, increasing all terms
        in a Plane by a coefficient, and adding a multiple of one Plane to another Plane.
        """
        try:
            d = planes[0].dimension
            for p in planes:
                assert p.dimension == d

            self.planes = planes
            self.dimension = d

        except AssertionError:
            raise Exception(self.ALL_PLANES_MUST_BE_IN_SAME_DIM_MSG)


    def swap_rows(self, row1, row2):
        """
        Swap the positions of two planes within the list of planes.
        """
        self.planes[row1], self.planes[row2] = self.planes[row2], self.planes[row1] 


    def multiply_coefficient_and_row(self, coefficient, row):
        """
        Multiplies all terms in a Plane equation by a coefficient and returns the resulting
        Plane.
        """
        new_vector = [(coefficient * n) for n in self.planes[row].normal_vector.coordinates]
        new_constant = coefficient * self.planes[row].constant_term
        return Plane( Vector(new_vector), new_constant )


    def add_multiple_times_row_to_row(self, coefficient, row_to_add, row_to_be_added_to):
        """
        Multiplies all terms in the Plane at index 'row_to_add' by the value 'coefficient'.
        The result is then added onto the Plane at index 'row_to_be_added_to' and the resulting
        sum is stored at index 'row_to_be_added_to'.
        """
        p = self.multiply_coefficient_and_row(coefficient, row_to_add)
        q = self.planes[row_to_be_added_to]
        new_vector = [(q.normal_vector.coordinates[i] + p.normal_vector.coordinates[i]) for i in range(q.dimension)]
        new_constant = q.constant_term + p.constant_term
        self.planes[row_to_be_added_to] = Plane( Vector(new_vector), new_constant )


    def indices_of_first_nonzero_terms_in_each_row(self):
        num_equations = len(self)
        num_variables = self.dimension

        indices = [-1] * num_equations

        for i,p in enumerate(self.planes):
            try:
                indices[i] = p.first_nonzero_index(p.normal_vector.coordinates)
            except Exception as e:
                if str(e) == Plane.NO_NONZERO_ELTS_FOUND_MSG:
                    continue
                else:
                    raise e

        return indices


    def __len__(self):
        return len(self.planes)


    def __getitem__(self, i):
        return self.planes[i]


    def __setitem__(self, i, x):
        try:
            assert x.dimension == self.dimension
            self.planes[i] = x

        except AssertionError:
            raise Exception(self.ALL_PLANES_MUST_BE_IN_SAME_DIM_MSG)


    def __str__(self):
        ret = 'Linear System:\n'
        temp = ['Equation {}: {}'.format(i+1,p) for i,p in enumerate(self.planes)]
        ret += '\n'.join(temp)
        return ret


class MyDecimal(Decimal):
    def is_near_zero(self, eps=1e-10):
        return abs(self) < eps


if __name__ == "__main__":
    p0 = Plane(normal_vector=Vector([1, 1, 1]), constant_term=1)
    p1 = Plane(normal_vector=Vector([0, 1, 0]), constant_term=2)
    p2 = Plane(normal_vector=Vector([1, 1, -1]), constant_term=3)
    p3 = Plane(normal_vector=Vector([1, 0, -2]), constant_term=2)

    s = LinearSystem([p0, p1, p2, p3])

    print(s.indices_of_first_nonzero_terms_in_each_row())
    print(f"{s[0]}, {s[1]}, {s[2]}, {s[3]}")

    print(len(s))
    print(s)

    s.swap_rows(0, 1)
    print('')
    print(s)

    print('')
    print(s.multiply_coefficient_and_row(2, 1))

    s.add_multiple_times_row_to_row(3, 2, 1)
    print('')
    print(s)
    #print MyDecimal('1e-9').is_near_zero()
    #print MyDecimal('1e-11').is_near_zero()
