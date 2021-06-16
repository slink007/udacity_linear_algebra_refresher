from numbers import Number
import math


class Vector(object):
    def __init__(self, coordinates):
        try:
            if not coordinates:
                raise ValueError
            self.coordinates = tuple(coordinates)
            self.dimension = len(coordinates)
            if self.dimension < 2:
                raise IndexError

        except ValueError:
            raise ValueError('The coordinates must be nonempty')

        except TypeError:
            raise TypeError('The coordinates must be an iterable')

        except IndexError:
            raise IndexError('Vector needs at least 2 coordinates')


    def __str__(self):
        return 'Vector: {}'.format(self.coordinates)


    def __eq__(self, v):
        return self.coordinates == v.coordinates


    def add(self, v):
        """
        Adds one Vector to another Vector and returns a Vector 
        containing the result.
        """

        if not isinstance(v, Vector):
            raise TypeError('Added value is not a vector')

        if self.dimension == v.dimension:  # vectors are equal size
            result = [self.coordinates[i] + v.coordinates[i] for i in range(self.dimension)]
        elif self.dimension > v.dimension: # this vector has more dimensions than the other one
            result = [self.coordinates[i] + v.coordinates[i] for i in range(v.dimension)]
            result += self.coordinates[v.dimension:]
        else:  # the other vector has more dimensions than this one
            result = [self.coordinates[i] + v.coordinates[i] for i in range(self.dimension)]
            result += v.coordinates[self.dimension:]

        return Vector(result)


    def subtract(self, v):
        """
        Subtracts one Vector from another Vector and returns a Vector 
        containing the result.
        """

        if not isinstance(v, Vector):
            raise TypeError('Subtracted value is not a vector')

        if self.dimension == v.dimension:  # vectors are equal size
            result = [self.coordinates[i] - v.coordinates[i] for i in range(self.dimension)]
        elif self.dimension > v.dimension: # this vector has more dimensions than the other one
            result = [self.coordinates[i] - v.coordinates[i] for i in range(v.dimension)]
            result += self.coordinates[v.dimension:]
        else:  # the other vector has more dimensions than this one
            # I'm not entirely sure what should happen here.  I'm going on the assumption that
            # the "missing" fields from this Vector are populated with zeroes.
            result = [self.coordinates[i] - v.coordinates[i] for i in range(self.dimension)]
            temp = [0 - x for x in v.coordinates[self.dimension:]]
            result += temp

        return Vector(result)


    def scalar(self, n):
        """
        Multiplies each element in a Vector by a constant and returns a Vector 
        containing the result.
        """
        
        if not isinstance(n, Number):
            raise TypeError('Scalar needs to be a number')
        
        temp = [n * x for x in self.coordinates]

        return Vector(temp)


    def magnitude(self):
        """
        Returns the magnitude of the vector
        """
        sum_of_squares = [x * x for x in self.coordinates]
        return math.sqrt(sum(sum_of_squares))


    def unit(self):
        """
        Returns a Vector which is the unit vector for the calling Vector.
        """
        try:
            mag = self.magnitude()
            return self.scalar(1/mag)

        except ZeroDivisionError:
            raise Exception("Can not find unit vector of a zero vector")


    def dot(self, v):
        """
        Returns the dot product of two Vectors.
        """

        if not isinstance(v, Vector):
            raise TypeError('Dot product requires a vector')

        if self.dimension < v.dimension:
            result = [self.coordinates[i] * v.coordinates[i] for i in range(self.dimension)]
        else:  
            result = [self.coordinates[i] * v.coordinates[i] for i in range(v.dimension)]

        return sum(result)


    def angle(self, v, in_radians=True):
        """
        Returns the angle between this Vector and another Vector.
        Result is in radians unless that is set to False in which case the
        result is in degrees.
        """

        if not isinstance(v, Vector):
            raise TypeError('Other element must be a vector')

        try:
            angle = math.acos(self.dot(v)/(self.magnitude() * v.magnitude()))

        except ZeroDivisionError:
            raise Exception("Angle to a zero vector is undefined")

        if in_radians:
            return angle
        return math.degrees(angle)


    def is_zero(self):
        """
        Returns True if Vector is a zero vector, returns False if not 
        a zero vector.
        """
        try:
            for item in self.coordinates:
                assert item == 0
        except AssertionError:
            return False

        return True


    def is_parallel(self, v):
        """
        Returns True if Vector v is parallel to this Vector, returns False 
        if not parallel.
        """
        if not isinstance(v, Vector):
            raise TypeError('Must compare to a vector')

        if self.is_zero() or v.is_zero():  # zero vectors always parallel
            return True

        if self.dimension != v.dimension:  # unequally sized vectors not parallel
            return False

        ratio = v.coordinates[0] / self.coordinates[0]
        try:
            for i in range(1, len(self.coordinates)):
                assert (v.coordinates[i] / self.coordinates[i]) == ratio
        except AssertionError:
            return False
        return True


    def is_orthogonal(self, v):
        """
        Returns True if Vector v is orthogonal to this Vector, returns False 
        if not orthogonal.
        """
        if not isinstance(v, Vector):
            raise TypeError('Must compare to a vector')

        if (round(self.dot(v), 9)) == 0:
            return True
        return False


    def projected(self, v):
        """
        Returns the Vector that results when projecting this Vector onto Vector v.
        """
        return (v.unit()).scalar( self.dot(v.unit()) )


    def orthogonal(self, v):
        """
        Returns the Vector which would be orthogonal to the Vector that results from
        projecting this Vector onto Vector v.
        """
        return self.subtract(self.projected(v))


    def cross(self, v):
        """
        Returns a Vector which the result of the cross product of this Vector and Vector v.
        """

        if not isinstance(v, Vector):
            raise TypeError('Cross product requires a vector')

        if (self.dimension > 3) or (v.dimension > 3):
            raise IndexError('Cross product not valid for Vectors having more than 3 coordintates.')

        a = list(self.coordinates)
        b = list(v.coordinates)

        # Turns a 2-D Vector into a 3-D.  If Vector is already 3-D having an extra element doesn't 
        # hurt as the extra won't be used anyway.
        a.append(0)
        b.append(0)

        result = [((a[1]*b[2]) - (b[1]*a[2])), 
                    0 - ((a[0] * b[2]) - (b[0] * a[2])), 
                    ((a[0]*b[1]) - (b[0]*a[1]))]
        return Vector(result)


    def p_area(self, v):
        """
        If two vectors are to be subjected to a cross product, and those vectors are placed end-to-end,
        we can construct a parallelogram out of the possible ways these vectors can be combined.
        This method returns the area of such a parallelogram although I have no idea why anyone
        would want such a thing.  But the class I'm taking requires this functionality so here it
        is.
        """
        return (self.cross(v)).magnitude()


    def t_area(self, v):
        """
        If two vectors are to be subjected to a cross product, and those vectors are placed end-to-end,
        we can construct a parallelogram out of the possible ways these vectors can be combined.
        Furthermore, we can draw a line across this parallelogram and create two equal triangles.
        This method returns the area of such a triangle although I have no idea why anyone
        would want such a thing.  But the class I'm taking requires this functionality so here it
        is.
        """
        return (self.p_area(v)) / 2
