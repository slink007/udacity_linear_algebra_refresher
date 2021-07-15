# This will either have to go (most likely) or I'll have to
# put Decimal back into the other files.
from decimal import Decimal, getcontext
from copy import deepcopy

from vector import Vector
from plane import Plane

getcontext().prec = 30


class LinearSystem(object):

    ALL_PLANES_MUST_BE_IN_SAME_DIM_MSG = 'All planes in the system should live \
            in the same dimension'
    NO_SOLUTIONS_MSG = 'No solutions'
    INF_SOLUTIONS_MSG = 'Infinitely many solutions'

    def __init__(self, planes):
        """
        The 'planes' input expects an iterable composed of Plane objects.  A
        LinearSystem is a collection of Plane objects.  It has methods for
        swapping the order of those objects, increasing all terms in a Plane
        by a coefficient, and adding a multiple of one Plane to another Plane.
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
        self.planes[row1], self.planes[row2] = self.planes[row2],\
            self.planes[row1]


    def _multiply(self, coefficient, row):
        """
        Multiplies all terms in a Plane equation by a coefficient and returns
        the resulting Plane.
        """
        new_vector = [(coefficient * n)
                      for n in self.planes[row].normal_vector.coordinates]
        new_constant = coefficient * self.planes[row].constant_term
        return Plane(Vector(new_vector), new_constant)


    def multiply_coefficient_and_row(self, coefficient, row):
        """
        Multiplies all terms in a Plane equation by a coefficient.  Used to
        return the resulting Plane but test cases released after I coded
        the original version made it clear that the expectation was that we
        alter the original list of Planes.  So now this replaces the Plane
        at index 'row' with the new Plane.
        """
        self.planes[row] = self._multiply(coefficient, row)


    def add_multiple_times_row_to_row(
            self,
            coefficient,
            row_to_add,
            row_to_be_added_to):
        """
        Multiplies all terms in the Plane at index 'row_to_add' by the value
        'coefficient'.  The result is then added onto the Plane at index
        'row_to_be_added_to' and the resulting sum is stored at index
        'row_to_be_added_to'.
        """
        # p = self.multiply_coefficient_and_row(coefficient, row_to_add)
        p = self._multiply(coefficient, row_to_add)
        q = self.planes[row_to_be_added_to]
        new_vector = [
            (q.normal_vector.coordinates[i] +
             p.normal_vector.coordinates[i]) for i in range(
                q.dimension)]
        new_constant = q.constant_term + p.constant_term
        self.planes[row_to_be_added_to] = Plane(
            Vector(new_vector), new_constant)


    def indices_of_first_nonzero_terms_in_each_row(self):
        num_equations = len(self)
        # num_variables = self.dimension

        indices = [-1] * num_equations

        for i, p in enumerate(self.planes):
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
        temp = ['Equation {}: {}'.format(i + 1, p)
                for i, p in enumerate(self.planes)]
        ret += '\n'.join(temp)
        return ret


    def compute_triangular_form(self):
        """
        Makes a copy of the original system and attempts to put that copy
        into rectangular form.  Returns the copy.
        """
        system = deepcopy(self)
        # indices = system.indices_of_first_nonzero_terms_in_each_row()
        # for i in range(len(indices)):
        #     if i != indices[i]:
        #         j = i + 1
        #         while j < len(indices):
        #             if i == indices[j]:
        #                 system.swap_rows(i, j)
        #                break
        #             j += 1
        # return system
        num_equations = len(system)
        num_variables = system.dimension

        for i in range(num_equations):
            for j in range(num_variables):
                coefficient = MyDecimal(system[i].normal_vector[j])
                if coefficient.is_near_zero():
                    # Try to swap.  If we can't swap try the next
                    # coefficient.
                    if not system.swap_with_status(i, j):
                        continue
                system.clear_coefficients_below(i, j)


    def clear_coefficients_below(self, row, column):
        num_equations = len(self)
        # Need the coefficient of the variable in question on this row
        # to help form the scalar to multiply this line by when it is
        # added to a line below it.
        denominator = self[row].normal_vector[column]

        for k in range(row + 1, num_equations):
            vector = self[k].normal_vector
            numerator = vector[column]
            scalar = -(numerator / denominator)
            self.add_multiple_times_row_to_row(scalar, row, k)


    def swap_with_status(self, row, column):
        """
        It's assumed that the Plane at 'row' within the system has a
        zero coefficient at the 'column' variable.  This attempts to
        swap out a lower row and returns True/False based on the success
        of that attempt.
        """
        num_equations = len(self)

        # Start with next lowest plane and test all of them.
        for plane in range(row + 1, num_equations):
            coefficient = MyDecimal(self[plane].normal_vector[column])
            # Swap the planes if the next plane does NOT have a zero
            # coefficient for the variable in question.
            if not coefficient.is_near_zero():
                self.swap_rows(row, plane)
                return True
        return False


class MyDecimal(Decimal):
    def is_near_zero(self, eps=1e-10):
        return abs(self) < eps


if __name__ == "__main__":
    p0 = Plane(normal_vector=Vector([1, 1, 1]), constant_term=1)
    p1 = Plane(normal_vector=Vector([0, 1, 0]), constant_term=2)
    p2 = Plane(normal_vector=Vector([1, 1, -1]), constant_term=3)
    p3 = Plane(normal_vector=Vector([1, 0, -2]), constant_term=2)
    s = LinearSystem([p0, p1, p2, p3])

    # Test 1
    s.swap_rows(0, 1)
    result = 'passed'
    test = '1'
    if not (s[0] == p1 and s[1] == p0 and s[2] == p2 and s[3] == p3):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Test 2
    s.swap_rows(1, 3)
    result = 'passed'
    test = '2'
    if not (s[0] == p1 and s[1] == p3 and s[2] == p2 and s[3] == p0):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Test 3
    s.swap_rows(3, 1)
    result = 'passed'
    test = '3'
    if not (s[0] == p1 and s[1] == p0 and s[2] == p2 and s[3] == p3):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Test 4
    s.multiply_coefficient_and_row(1, 0)
    result = 'passed'
    test = '4'
    if not (s[0] == p1 and s[1] == p0 and s[2] == p2 and s[3] == p3):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Test 5
    s.multiply_coefficient_and_row(-1, 2)
    result = 'passed'
    test = '5'
    if not (s[0] == p1 and s[1] == p0 and s[2] ==
            Plane(Vector([-1, -1, 1]), -3) and s[3] == p3):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Test 6
    s.multiply_coefficient_and_row(10, 1)
    result = 'passed'
    test = '6'
    if not (s[0] == p1 and
            s[1] == Plane(Vector([10, 10, 10]), 10) and
            s[2] == Plane(Vector([-1, -1, 1]), -3) and
            s[3] == p3):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Test 7
    s.add_multiple_times_row_to_row(0, 0, 1)
    result = 'passed'
    test = '7'
    if not (s[0] == p1 and
            s[1] == Plane(Vector([10, 10, 10]), 10) and
            s[2] == Plane(Vector([-1, -1, 1]), -3) and
            s[3] == p3):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Test 8
    s.add_multiple_times_row_to_row(1, 0, 1)
    result = 'passed'
    test = '8'
    if not (s[0] == p1 and
            s[1] == Plane(Vector([10, 11, 10]), 12) and
            s[2] == Plane(Vector([-1, -1, 1]), -3) and
            s[3] == p3):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Test 9
    s.add_multiple_times_row_to_row(-1, 1, 0)
    result = 'passed'
    test = '9'
    if not (s[0] == Plane(Vector([-10, -10, -10]), -10) and
            s[1] == Plane(Vector([10, 11, 10]), 12) and
            s[2] == Plane(Vector([-1, -1, 1]), -3) and
            s[3] == p3):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Setup for next batch of tests
    p1 = Plane(Vector([1, 1, 1]), 1)
    p2 = Plane(Vector([0, 1, 1]), 2)
    s = LinearSystem([p1, p2])
    print(p1)
    print(p2)
    print(s.indices_of_first_nonzero_terms_in_each_row())
