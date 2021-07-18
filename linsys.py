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
        num_eq = len(system)
        num_var = system.dimension
        for row in range(num_eq):
            for col in range(num_var):
                coefficient = \
                        MyDecimal(system[row].normal_vector.coordinates[col])
                if coefficient.is_near_zero():
                    if not system.swap_row_below(row, col):
                        continue
                # Once all coefficients in 'col' column are cleared
                # in the rows below 'row' break out of this loop
                # and process the next row.
                system.clear_coefficients_below(row, col)
                break

        return system


    def clear_coefficients_below(self, row, col):
        num_eq = len(self)
        # beta = MyDecimal(self[row].normal_vector.coordinates[col])
        beta = self[row].normal_vector.coordinates[col]

        for k in range(row + 1, num_eq):
            n = self[k].normal_vector
            gamma = n.coordinates[col]
            alpha = -gamma/beta
            self.add_multiple_times_row_to_row(alpha, row, k)


    def swap_row_below(self, row, col):
        """
        It's assumed that the Plane at 'row' within the system has a
        zero coefficient at the 'col' variable.  This attempts to
        swap out a lower row and returns True/False based on the success
        of that attempt.
        """
        num_eq = len(self)
        for k in range(row + 1, num_eq):
            c = MyDecimal(self[k].normal_vector.coordinates[col])
            if not c.is_near_zero():
                self.swap_rows(row, k)
                return True
        return False

    def compute_rref(self):
        """
        Converts a system of linear equations into Reduced Row
        Echelon Form (RREF) and returns the converted system.
        """
        system = self.compute_triangular_form()
        pivot_indices = system.indices_of_first_nonzero_terms_in_each_row()
        for i, row in reversed(list(enumerate(system.planes))):
            first_non_zero_index = pivot_indices[i]
            if first_non_zero_index < 0:
                continue
            system.scale_row(i, first_non_zero_index)
            system.clear_coefficients_above(i, first_non_zero_index)
        return system


    def scale_row(self, row_index, column_index):
        """
        Finds the coefficient of the variable at 'column_index' within row
        'row_index' and calculates a scalar based on that coefficient. When
        the row in question is multiplied by that scalar the coefficient of
        the variable at 'column_index' becomes 1.  Instead of returning
        something this will modify the existing row.
        """
        scalar = 1 / \
            self.planes[row_index].normal_vector.coordinates[column_index]
        self.multiply_coefficient_and_row(scalar, row_index)


    def clear_coefficients_above(self, row, col):
        for k in range(row)[::-1]:
            scalar = -(self[k].normal_vector.coordinates[col])
            self.add_multiple_times_row_to_row(scalar, row, k)


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

    # Test 10
    p1 = Plane(Vector([1, 1, 1]), 1)
    p2 = Plane(Vector([0, 1, 1]), 2)
    s = LinearSystem([p1, p2])
    t = s.compute_triangular_form()
    result = 'passed'
    test = '10'
    if not (t[0] == p1 and t[1] == p2):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Test 11
    p1 = Plane(Vector([1, 1, 1]), 1)
    p2 = Plane(Vector([0, 1, 0]), 2)
    p3 = Plane(Vector([1, 1, -1]), 3)
    p4 = Plane(Vector([1, 0, -2]), 2)
    s = LinearSystem([p1, p2, p3, p4])
    t = s.compute_triangular_form()
    result = 'passed'
    test = '11'
    if not (t[0] == p1 and
            t[1] == p2 and
            t[2] == Plane(Vector([0, 0, -2]), 2) and
            t[3] == Plane(Vector([0, 0, 0]), 0)):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Test 12
    p1 = Plane(Vector([0, 1, 1]), 1)
    p2 = Plane(Vector([1, -1, 1]), 2)
    p3 = Plane(Vector([1, 2, -5]), 3)
    s = LinearSystem([p1, p2, p3])
    t = s.compute_triangular_form()
    result = 'passed'
    test = '12'
    if not (t[0] == Plane(Vector([1, -1, 1]), 2) and
            t[1] == Plane(Vector([0, 1, 1]), 1) and
            t[2] == Plane(normal_vector=Vector([0, 0, -9]), constant_term=-2)):
        result = 'failed'
    print("Test case " + test + " " + result)

    # Test 13
    # I honestly have no idea if this test is valid or not.  Despite promises
    # from the course instructor to provide test cases for computing rref
    # none were provided.  I compared the results from my solution against
    # the results from the instructor's solution, saw that they were the
    # same, and wrote this test to expect that result.
    p1 = Plane(Vector([0, 1, 1]), 1)
    p2 = Plane(Vector([1, -1, 1]), 2)
    p3 = Plane(Vector([1, 2, -5]), 3)
    s = LinearSystem([p1, p2, p3])
    t = s.compute_rref()
    result = 'passed'
    test = '13'
    if not (t[0] == Plane(Vector([1.0, 0.0, 0.0]), 2.5555555555555554) and
            t[1] == Plane(Vector([0.0, 1.0, 0.0]), 0.7777777777777778) and
            t[2] == Plane(Vector([-0.0, -0.0, 1.0]), 0.2222222222222222)):
        result = 'failed'
    print("Test case " + test + " " + result)
