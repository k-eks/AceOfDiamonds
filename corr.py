class Correlation():

    def __init__(self, neighborOrder, siteMultiplicationReacted, siteMultiplicationReactedMaximum, propabilityModifierReacted, propabilityModifierUnreacted):
        self.order = neighborOrder
        self.propR = propabilityModifierReacted
        self.multR = siteMultiplicationReacted
        self.maxiR = siteMultiplicationReactedMaximum
        self.propU = propabilityModifierUnreacted