class Plugin:
    '''
    A scheduling Profile allows you to configure the different stages of
    scheduling in the kube-scheduler. Each stage is exposed in an extension
    point. Plugins provide scheduling behaviors by implementing one or more
    of these extension points.
    '''
    def __init__(
                self, _pfhp=False, _pfh=False, _pfr=False, _mns=False,
                _nvzc=False, _ndc=False, _mCSIvc=False, _ptnt=False,
                _cvb=False, ssp=False, ipap=False, lrp=False, mrp=False,
                rtcrp=False, bra=False, npapp=False, nap=False, ttp=False,
                ilp=False, ssp_=False, ep=False, epsp=False
                ):

        # Predicates
        self.predicate_list = [_pfhp, _pfh, _pfr, _mns, _nvzc, _ndc,
                               _mCSIvc, _ptnt, _cvb]

        self.predicates_name = ['PodFitsHostPorts', 'PodFitsHost',
                                'PodFitsResources', 'MatchNodeSelector',
                                'NoVolumeZoneConflict', 'noDiskConflict',
                                'MaxCSIVolumeCount', 'PodToleratesNodeTaints',
                                'CheckVolumeBinding']

        # Priorites
        self.priorites_list = [ssp, ipap, lrp, mrp, rtcrp, bra, npapp, nap,
                               ttp, ilp, ssp_, ep, epsp]

        self.priorites_name = ['SelectorSpreadPriority',
                               'InterPodAffinityPriority',
                               'LeastRequestedPriority',
                               'MostRequestedPriority',
                               'RequestedToCapacityRatioPriority',
                               'BalancedResourceAllocation',
                               'NodePreferAvoidPodsPriority',
                               'NodeAffinityPriority',
                               'TaintTolerationPriority',
                               'ImageLocalityPriority',
                               'ServiceSpreadingPriority',
                               'EqualPriority',
                               'EvenPodsSpreadPriority']
