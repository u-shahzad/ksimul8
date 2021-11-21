class Plugin:

    def __init__(self):

        # Predicates
        self._PodFitsHostPorts = False
        self._PodFitsHost = False
        self._PodFitsResources = False
        self._MatchNodeSelector = False
        self._NoVolumeZoneConflict = False
        self._NoDiskConflict = False
        self._MaxCSIVolumeCount = False
        self._PodToleratesNodeTaints = False
        self._CheckVolumeBinding = False

        # Priorites
        self._SelectorSpreadPriority = False
        self._InterPodAffinityPriority = False
        self._LeastRequestedPriority = False
        self._MostRequestedPriority = False
        self._RequestedToCapacityRatioPriority = False
        self._BalancedResourceAllocation = False
        self._NodePreferAvoidPodsPriority = False
        self._NodeAffinityPriority = False
        self._TaintTolerationPriority = False
        self._ImageLocalityPriority = False
        self._ServiceSpreadingPriority = False
        self._EqualPriority = False
        self._EvenPodsSpreadPriority = False

    def custom_plugin1(self):

        if self._PodFitsResources == True and self._PodFitsHostPorts == True:
            return True
        else:
            return False