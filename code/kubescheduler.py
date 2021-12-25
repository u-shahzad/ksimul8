from predicates import Predicates
from priorites import Priorites
from rich.console import Console
from rich.table import Table
from rich.traceback import install
import logging
install()  # creates a better readable traceback


console = Console(record=True)

logging.basicConfig(filename='test.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')


class Kubescheduler(Predicates, Priorites):

    '''
    The Kubernetes scheduler is a control plane process which assigns Pods to
    Nodes. The scheduler determines which Nodes are valid placements for each
    Pod in the scheduling queue according to constraints and available
    resources. The scheduler then ranks each valid Node and binds the Pod to
    a suitable Node.
    '''

    def __init__(self, name='Kubescheduler'):
        super().__init__()
        self.name = name  # name of the scheduler
        self.feasible_nodes = []  # list of feasible nodes for the pod
        self.selected_node = None  # final selected node for the pod

        self.predicate_methods = [self.podFitsHostPorts, self.podFitsHost,
                                  self.podFitsResources,
                                  self.matchNodeSelector,
                                  self.noVolumeZoneConflict,
                                  self.noDiskConflict,
                                  self.maxCSIVolumeCount,
                                  self.podToleratesNodeTaints,
                                  self.checkVolumeBinding]

        self.priorites_methods = [self.selectorSpreadPriority,
                                  self.interPodAffinityPriority,
                                  self.leastRequestedPriority,
                                  self.mostRequestedPriority,
                                  self.requestedToCapacityRatioPriority,
                                  self.balancedResourceAllocation,
                                  self.nodePreferAvoidPodsPriority,
                                  self.nodeAffinityPriority,
                                  self.taintTolerationPriority,
                                  self.imageLocalityPriority,
                                  self.serviceSpreadingPriority,
                                  self.equalPriority,
                                  self.evenPodsSpreadPriority]

    def scheduling_cycle(self, cluster, pod, simTime):
        nodes = cluster.get_node_list()  # list of all the nodes
        global node_passed  # check to add node in feasible list
        node_passed = False  # initially node is not feasible

        for node in nodes:

            priority_parameters = {'cluster': cluster,
                                   'node': node, 'pod': pod}

            '''
            This loop finds the number of feasible node(s)
            for the pod by applying a set of predicates.
            '''
            for pred in range(len(pod.plugin.predicate_list)):

                # checks whether plugin is ON/OFF
                if pod.plugin.predicate_list[pred]:
                    if (self.predicate_methods[pred](node, pod)):
                        console.log(":thumbs_up: {} ---> {}".format(
                                    pod.plugin.predicates_name[pred],
                                    node.name), style="cyan")
                        node_passed = True

                    else:
                        console.log(":thumbs_down: {} ---> {}".format(
                                    pod.plugin.predicates_name[pred],
                                    node.name), style="cyan")
                        node_passed = False
                        break

            if node_passed:
                self.feasible_nodes.append(node)

            # Applying Priorites
            for pri in range(len(pod.plugin.priorites_list)):
                if pod.plugin.priorites_list[pri]:
                    self.priorites_methods[pri](priority_parameters)

        # check that feasible nodes list is not empty
        if len(self.feasible_nodes) > 0:

            # sort the nodes on the basis of their score
            self.feasible_nodes.sort(key=lambda x: x.score, reverse=True)

            # select the node with the highest score
            self.selected_node = self.feasible_nodes[0]
            self.selected_node.add_pod(pod)  # add the pod to the selected node
            pod.node = self.selected_node  # bind pod to the selected node

            logging.info(' \"The selected node: {}\"\n'.format(
                         self.selected_node.name))

            console.log("\n---> Selected node = {} *** [Simulation Time: {} seconds]\n".format(
                        self.selected_node.name, simTime), style="bold green")

        else:
            pod.nodeName = ''  # no feasible node for pod

        table = Table(title="Node Description")

        table.add_column("Name", justify="center", style="cyan")
        table.add_column("ID", justify="center", style="magenta")
        table.add_column("Num of Pods", justify="center", style="green")
        table.add_column("Memory", justify="center", style="cyan")
        table.add_column("CPU", justify="center", style="magenta")
        table.add_column("Score", justify="center", style="green")
        table.add_column("Port", justify="center", style="cyan")

        for node in nodes:

            table.add_row(node.name, str(node.id), str(node.num_of_pods),
                          str(node.memory), str(node.cpu), str(node.score),
                          str(node.port))

            node.score = 0  # clear the node score for the next pod scheduling

        console.log(table)
