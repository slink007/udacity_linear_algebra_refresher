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
        Adds one Vector to another Vector and returns a tuple containing the result.
        
        Returning a Vector is better option?  
        
        Currently this assumes both Vectors are of same size (problem?) and that both are
        two-dimensional Vectors (definitely a problem).
        """
        if not isinstance(v, Vector):
            raise TypeError('Tried to add a non-vector')

        return (self.coordinates[0] + v.coordinates[0], self.coordinates[1] + v.coordinates[1])
