class Plugin:

    def __init__(self, _pfhp = False, _pfh = False, _pfr = False, _mns = False,
                    _nvzc = False, _ndc = False, _mCSIvc = False, _ptnt = False,
                    _cvb = False, ssp = False, ipap = False, lrp = False,
                    mrp = False, rtcrp = False, bra = False, npapp = False,
                    nap = False, ttp = False, ilp = False, ssp_ = False,
                    ep = False, epsp = False):

        # Predicates
        self._PodFitsHostPorts = _pfhp
        self._PodFitsHost = _pfh
        self._PodFitsResources = _pfr
        self._MatchNodeSelector = _mns
        self._NoVolumeZoneConflict = _nvzc
        self._NoDiskConflict = _ndc
        self._MaxCSIVolumeCount = _mCSIvc
        self._PodToleratesNodeTaints = _ptnt
        self._CheckVolumeBinding = _cvb

        # Priorites
        self._SelectorSpreadPriority = ssp
        self._InterPodAffinityPriority = ipap
        self._LeastRequestedPriority = lrp
        self._MostRequestedPriority = mrp
        self._RequestedToCapacityRatioPriority = rtcrp
        self._BalancedResourceAllocation = bra
        self._NodePreferAvoidPodsPriority = npapp
        self._NodeAffinityPriority = nap
        self._TaintTolerationPriority = ttp
        self._ImageLocalityPriority = ilp
        self._ServiceSpreadingPriority = ssp_
        self._EqualPriority = ep
        self._EvenPodsSpreadPriority = epsp

    def customPlugin1(self):

        self._PodFitsHost = True
        self._PodFitsHostPorts = True
        self._PodFitsResources = True

        self._ImageLocalityPriority = True
        self._LeastRequestedPriority = True

    def customPlugin2(self):

        self._PodFitsResources = True
        self._PodFitsHostPorts = True
        self._MatchNodeSelector = True

        self._ImageLocalityPriority = True
        self._LeastRequestedPriority = True

    def customPlugin3(self):

        self._PodFitsResources = True

        self._LeastRequestedPriority = True
        self._ImageLocalityPriority = True
