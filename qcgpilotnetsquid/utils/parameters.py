"""
Defines class Parameter and SetParameters.
"""

from collections import OrderedDict


def str2bool(v):
    return v.lower() in ("True", "yes", "true", "t", "1")


class SetParameters:
    """Contains parameters that will be explored during the simulation.

    Parameters
    ----------
        args: list of parameters to be explored

    """
    def __init__(self, *args):
        self.parameters = {}
        self.parameters = OrderedDict(self.parameters)
        for item in args:
            if not isinstance(item, Parameter):
                raise TypeError("Item is not a Parameter")
            self.parameters[item.name] = item

    def add_parameter(self, parameter):
        """ Adds a new parameter to the set of parameters to explore.

        Parameters
        ----------
        parameter : smartstopos.utils.parameters.Parameter
            New parameter to be explore
        """
        if not isinstance(parameter, Parameter):
            raise TypeError("Not a Parameter type")
        self.parameters[parameter.name] = parameter

    def remove_parameter(self, name_parameter):
        """Removes a parameter from the list of parameters to explore.

        Parameters
        ---------
        name_parameter : str
            Name of smartopos.utils.parameters.Parameter to be
            removed from exploration list.
        """
        self.parameters.popitem(name_parameter)

    def list_parameters(self):
        """Prints list of parameters"""
        for name, parameter in self.parameters.items():
            print("name: {} --> range: {}, number_points: {}, distribution: {}, data_type: {}, scale_factor: {};"
                  "width_distribution: {}; weight: {}".format(name,
                                                              parameter.range,
                                                              parameter.number_points,
                                                              parameter.distribution,
                                                              parameter.data_type,
                                                              parameter.scale_factor,
                                                              parameter.width_distribution,
                                                              parameter.weight))


class Parameter:
    """Defines a class for any type of parameter we want to vary in our simulation.

    Parameters
    ----------

    name : str
        Name of the parameter
    parameter_range : list(min, max)
        List with the min and max value of the parameter; min and max are floats
    number_points: int
        Number of points to be explored
    data_type: str
        Type of variable: discrete or continuous, optional.
    distribution : str
        Type of distribution of the points.
    scale_factor: float
        Scaling factor for algorithms
    width_distribution: float
        Width gaussian for algorithms
    weight : float, optional
        Weight of the parameter (0,1). Default is 1.0 for all parameters
    active: bool
        Whether this is a parameter currently being explored or fixed.
    constraints: list
        List of constraints

    Attributes
    ----------

    data_points : list
        Data points to be explored for this parameter.

    """
    def __init__(self, name, parameter_range, number_points, data_type,
                 distribution, scale_factor, width_distribution, variance,
                 weight=1.0, active=True):
        self.name = name
        self.range = parameter_range
        self.range[0] = float(self.range[0])
        self.range[1] = float(self.range[1])
        self.number_points = number_points
        self.data_points = []
        self.data_type = data_type
        self.distribution = distribution
        self.active = active
        self.weight = weight
        self.scale_factor = scale_factor
        self.width_distribution = width_distribution
        self.variance = variance
