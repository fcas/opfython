import numpy as np

import opfython.utils.constants as c
import opfython.utils.exception as e
import opfython.utils.logging as l
from opfython.core.subgraph import Subgraph

logger = l.get_logger(__name__)


class KNNSubgraph(Subgraph):
    """A KNNSubgraph is used to implement a k-nearest neightbours subgraph.

    """

    def __init__(self, X=None, Y=None, from_file=None):
        """Initialization method.

        Args:
            X (np.array): Array of features.
            Y (np.array): Array of labels.
            from_file (bool): Whether Subgraph should be directly created from a file.

        """

        logger.info('Overriding class: Subgraph -> KNNSubgraph.')

        # Override its parent class with the receiving arguments
        super(KNNSubgraph, self).__init__(X=X, Y=Y, from_file=from_file)

        # Number of adjacent nodes (k-nearest neighbours)
        self.best_k = 0

        # Constant for computing the probability density function (p.d.f.)
        self.k = 0.0

        # Density of the subgraph
        self.density = 0.0

        # Minimum density of the subgraph
        self.min_density = 0.0

        # Maximum density of the subgraph
        self.max_density = 0.0

        logger.info('Class overrided.')

    @property
    def best_k(self):
        """int: Number of adjacent nodes (k-nearest neighbours).

        """

        return self._best_k

    @best_k.setter
    def best_k(self, best_k):
        if not isinstance(best_k, int):
            raise e.TypeError('`best_k` should be an integer')
        if best_k < 0:
            raise e.ValueError('`best_k` should be >= 0')

        self._best_k = best_k

    @property
    def k(self):
        """float: Constant for computing the probability density function (p.d.f.).

        """

        return self._k

    @k.setter
    def k(self, k):
        if not (isinstance(k, float) or isinstance(k, int)):
            raise e.TypeError('`k` should be a float or integer')

        self._k = k

    @property
    def density(self):
        """float: Density of the subgraph.

        """

        return self._density

    @density.setter
    def density(self, density):
        if not (isinstance(density, float) or isinstance(density, int)):
            raise e.TypeError('`density` should be a float or integer')

        self._density = density

    @property
    def min_density(self):
        """float: Minimum density of the subgraph.

        """

        return self._min_density

    @min_density.setter
    def min_density(self, min_density):
        if not (isinstance(min_density, float) or isinstance(min_density, int)):
            raise e.TypeError('`min_density` should be a float or integer')

        self._min_density = min_density

    @property
    def max_density(self):
        """float: Maximum density of the subgraph.

        """

        return self._max_density

    @max_density.setter
    def max_density(self, max_density):
        if not (isinstance(max_density, float) or isinstance(max_density, int)):
            raise e.TypeError('`max_density` should be a float or integer')

        self._max_density = max_density

    def calculate_pdf(self, best_k, distance_function, pre_computed_distance=False, pre_distances=None):
        """Calculates the probability density function for the best `k` values.

        Args:
            best_k (int): Best value of k.
            distance_function (callable): The distance function to be used to calculate the arcs.
            pre_computed_distance (bool): Whether OPF should use a pre-computed distance or not.
            pre_distances (np.array): Pre-computed distance matrix.

        """

        # Calculating constant for computing the probability density function
        self.k = 2 * self.density / 9

        # Defining subgraph's minimum density
        self.min_density = c.FLOAT_MAX

        # Defining subgraph's maximum density
        self.max_density = c.FLOAT_MAX * -1

        # Creating an array to hold the p.d.f. calculation
        pdf = np.zeros(self.n_nodes)

        # For every possible node
        for i in range(self.n_nodes):
            # Initialize the p.d.f. as zero
            pdf[i] = 0

            # Initialize the number of p.d.f. calculations as 1
            n_pdf = 1

            # For every possible `k`
            for k in range(best_k):
                # Gathering adjacent node from the list
                j = int(self.nodes[i].adjacency[k])

                # If it is supposed to use a pre-computed distance
                if pre_computed_distance:
                    # Gathers the distance from the matrix
                    distance = pre_distances[self.nodes[i].idx][self.nodes[j].idx]

                # If it is supposed to calculate the distance
                else:
                    # Calculates the distance between nodes `i` and `j`
                    distance = distance_function(self.nodes[i].features, self.nodes[j].features)

                # Calculates the p.d.f.
                pdf[i] += np.exp(-distance / self.k)

                # Increments the number of p.d.f. calculations
                n_pdf += 1

            # Calculates the p.d.f. mean value
            pdf[i] /= n_pdf

            # If p.d.f. value is smaller than minimum density
            if pdf[i] < self.min_density:
                # Applies subgraph's minimum density as p.d.f.'s value
                self.min_density = pdf[i]

            # If p.d.f. value is bigger than maximum density
            if pdf[i] > self.max_density:
                # Applies subgraph's maximum density as p.d.f.'s value
                self.max_density = pdf[i]

        # If subgraph's minimum density is the same as the maximum density
        if self.min_density == self.max_density:
            # For every possible node
            for i in range(self.n_nodes):
                # Applies node's density as maximum possible density
                self.nodes[i].density = c.MAX_DENSITY

                # Applies node's cost as maximum possible density - 1
                self.nodes[i].cost = c.MAX_DENSITY - 1

        # If subgraph's minimum density is different than the maximum density
        else:
            # For every possible node
            for i in range(self.n_nodes):
                # Calculates the node's density
                self.nodes[i].density = (
                    (c.MAX_DENSITY - 1) * (pdf[i] - self.min_density) / (self.max_density - self.min_density)) + 1

                # Calculates the node's cost
                self.nodes[i].cost = self.nodes[i].density - 1

    def create_arcs(self, k, distance_function, pre_computed_distance=False, pre_distances=None):
        """Creates arcs for each node (adjacency relation).

        Args:
            k (int): Number of neighbours in the adjacency relation.
            distance_function (callable): The distance function to be used to calculate the arcs.
            pre_computed_distance (bool): Whether OPF should use a pre-computed distance or not.
            pre_distances (np.array): Pre-computed distance matrix.

        Returns:
            The maximum possible distances for each value of k.

        """

        # Creating an array of distances
        distances = np.zeros(k + 1)

        # Creating an array of nearest neighbours indexes
        neighbours_idx = np.zeros(k + 1)

        # Creating an array of maximum distances
        max_distances = np.zeros(k)

        # For every possible node
        for i in range(self.n_nodes):
            # Filling array of distances with maximum value
            distances.fill(c.FLOAT_MAX)

            # For every possible node
            for j in range(self.n_nodes):
                # If they are different nodes
                if j != i:
                    # If it is supposed to use a pre-computed distance
                    if pre_computed_distance:
                        # Gathers the distance from the matrix
                        distances[k] = pre_distances[self.nodes[i].idx][self.nodes[j].idx]

                    # If it is supposed to calculate the distance
                    else:
                        # Calculates the distance between nodes `i` and `j`
                        distances[k] = distance_function(
                            self.nodes[i].features, self.nodes[j].features)

                    # Apply node `j` as a neighbour
                    neighbours_idx[k] = j

                    # Gathers current `k`
                    current_k = k

                    # While current `k` is bigger than 0 and the `k` distance is smaller than `k-1` distance
                    while current_k > 0 and distances[current_k] < distances[current_k - 1]:
                        # Swaps the distance from `k` and `k-1`
                        distances[current_k], distances[current_k -
                                                        1] = distances[current_k - 1], distances[current_k]

                        # Swaps the neighbours indexex from `k` and `k-1`
                        neighbours_idx[current_k], neighbours_idx[current_k -
                                                                  1] = neighbours_idx[current_k - 1], neighbours_idx[current_k]

                        # Decrements `k`
                        current_k -= 1

            # Make sure that current node's radius is 0
            self.nodes[i].radius = 0.0

            # Also make sure that it does not have any adjacent nodes
            self.nodes[i].n_adjacency = 0

            # For every possible decreasing `k`
            for l in range(k - 1, -1, -1):
                # Checks if distance is different from maximum value
                if distances[l] != c.FLOAT_MAX:
                    # If distance is bigger than subgraph's density
                    if distances[l] > self.density:
                        # Apply subgraph's density as the distance
                        self.density = distances[l]

                    # If distance is bigger than node's radius
                    if distances[l] > self.nodes[i].radius:
                        # Apply node's radius as the distance
                        self.nodes[i].radius = distances[l]

                    # If distance is bigger than maximum distance
                    if distances[l] > max_distances[l]:
                        # Apply maximum distance as the distance
                        max_distances[l] = distances[l]

                    # Adds the neighbour to the adjacency list of node `i`
                    self.nodes[i].adjacency.insert(0, neighbours_idx[l])

        # If subgraph's density is smaller than a threshold
        if self.density < 0.00001:
            # Resets its to one
            self.density = 1

        return max_distances

    def destroy_arcs(self):
        """Destroy the arcs present in the subgraph.

        """

        # For every possible node
        for i in range(self.n_nodes):
            # Reset the number of adjacent nodes
            self.nodes[i].n_adjacency = 0

            # Resets the list of adjacent nodes
            self.nodes[i].adjacency = []

    def eliminate_maxima_height(self, height):
        """Eliminates maxima values in the subgraph that are below the inputted height.

        Args:
            height (float): Height's threshold.

        """

        logger.debug(f'Eliminating maxima above height = {height} ...')

        # Checks if height is bigger than zero
        if height > 0:
            # For every possible node
            for i in range(self.nodes):
                # Calculates its new cost
                self.nodes[i].cost = np.maximum(
                    self.nodes[i].density - height, 0)

        logger.debug('Maxima eliminated.')

    def eliminate_maxima_area(self, area):
        """Eliminates maxima values in the subgraph that are below the inputted area.

        Args:
            area (float): Area's threshold.

        """

        logger.debug(f'Eliminating maxima above area = {area} ...')

        logger.debug('Maxima eliminated.')

    def eliminate_maxima_volume(self, volume):
        """Eliminates maxima values in the subgraph that are below the inputted volume.

        Args:
            volume (float): Volume's threshold.

        """

        logger.debug(f'Eliminating maxima above volume = {volume} ...')

        logger.debug('Maxima eliminated.')


    def normalized_cut(self):
        pass
