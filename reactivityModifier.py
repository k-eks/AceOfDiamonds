import rhomb

class ReactivityModifier():
    """
    We define reactivity as r being the probability of reactivity in a site where its neighbor has already reacted and 1 - r being the probability of reaction if the site has unreacted neighbors.
    """

    def __init__(self, r, neighborOrder, reactedLateralNeighborsRequired, unreactedLateralNeighborsRequired):
        """
        Constructor
        r ... float reactivity modifier, should have a value from 0 to 1
        neighborOrder ... int the order of neighbor which is considered when this rule is applied
        lateralReactedNeighborsRequired ... int how many reacted neighbors in neighborOrder are required for this rule to apply, set to nan if this value should be skipped, use negative values if number should be exact
        lateralUnreactedNeighborsRequired ... int int how many unreacted neighbors in neighborOrder are required for this rule to apply, set to nan if this value should be skipped, use negative values if number should be exact
        """
        self.r = r # reactivity modifier
        self.neighborOrder = neighborOrder # order of the neighbor for which this rule applies
        self.reactedLateralNeighborsRequired = reactedLateralNeighborsRequired # how many reacted neighbors are at least required so that this rule applies, negative values mean exact values
        self.unreactedLateralNeighborsRequired = unreactedLateralNeighborsRequired # how many unreacted neighbors are at least required so that this rule applies, negative values mean exact values


    def __str__(self):
        """
        tostring functions
        returns string a human readable message that contains all properties of the modifier object
        """
        return "r = %0.02f, order = %i, reacted lateral = %s, unreacted lateral = %s" % (self.r, self.neighborOrder, self.reactedLateralNeighborsRequired, self.unreactedLateralNeighborsRequired)


    def createComplementaryRule(self):
        """
        Creates the r - 1 condition for the rule itself
        returns ReactivityModifier the r - 1 condition for itself
        """
        return ReactivityModifier(1 - self.r, self.neighborOrder, rhomb.MAXNEIGHBORS[self.neighborOrder - 1] - self.unreactedLateralNeighborsRequired + 1, rhomb.MAXNEIGHBORS[self.neighborOrder - 1] - self.reactedLateralNeighborsRequired + 1)