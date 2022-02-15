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
            print("name: {} --> range: {}, number_points: {}, distribution: {}, data_type: {}, scale_factor: {};".format(name,
                                                              parameter.range,
                                                              parameter.number_points,
                                                              parameter.distribution,
                                                              parameter.data_type,
                                                              parameter.scale_factor))


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
    constraints: list
        List of constraints

    Attributes
    ----------

    data_points : list
        Data points to be explored for this parameter.

    """
    def __init__(self, name, parameter_range, number_points, data_type,
                 distribution, scale_factor):
        self.name = name
        self.range = parameter_range
        self.range[0] = float(self.range[0])
        self.range[1] = float(self.range[1])
        self.number_points = number_points
        self.data_points = []
        self.data_type = data_type
        self.scale_factor = scale_factor
        self.distribution = distribution

def dict_to_setparameters(set_param_dict):
    """
    set_param_dict: dict
        A dictionary with the parameters needed for the simulations as read from
        input file.

    Returns
    -------
    set_parameters : smartstopos.utils.parameter.SetParameters
        Set of parameters and their properties as read from the input file.
    """
    parameters = False
    set_parameters = SetParameters()
    minimal_requirements = {'min': False,
                            'max': False,
                            'num_points': False,
                            'distribution': False,
                            'type': False
                                    }
    for item in set_param_dict:
        name = item["name"]
        if item["max"]:
            minimal_requirements["max"] = True
            maxr = float(item["max"])
        if item["min"]:
            minimal_requirements["min"] = True
            minr = float(item["min"])
        if minr > maxr:
            raise ValueError("The minimum value is larger than the maximum for parameter '{}'".format(name))
        
        if item["number_points"]:
            minimal_requirements['num_points'] = True
            num_points = int(item["number_points"])
        if item["distribution"]:
            minimal_requirements['distribution'] = True
            valid_distributions = ["uniform", "log", "random", "normal"]
            dist = item["distribution"]
            if dist not in valid_distributions:
                raise ValueError("Distribution not define. "
                                 "Please chose an existing one or define your own in makedatapoints.py")
        if item["type"]:
            typep = str(item["type"])
            if typep not in ["discrete", "continuous"]:
                raise ValueError("Data type of parameter {} is not valid. "
                                 "Please chose between discrete and continuous".format(name))
            minimal_requirements['type'] = True
        if item['scale_factor']:
            scale_factor = float(item["scale_factor"])
        else:
            scale_factor = 1.0

        if all(minimal_requirements):
            set_parameters.add_parameter(Parameter(name, [minr, maxr],
                                         num_points, typep, dist, scale_factor))
        else:
            raise ValueError("One or more of the minimal requirements (min, max, number_points, type, distribution) for parameter {} is not defined".format(name))
    return set_parameters


