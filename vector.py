from numbers import Number

class Vector(object):
    def __init__(self, coordinates):
        try:
            if not coordinates:
                raise ValueError
            self.coordinates = tuple(coordinates)
            self.dimension = len(coordinates)

        except ValueError:
            raise ValueError('The coordinates must be nonempty')

        except TypeError:
            raise TypeError('The coordinates must be an iterable')


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

