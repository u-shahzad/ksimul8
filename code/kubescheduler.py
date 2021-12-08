from predicates import Predicates
from priorites import Priorites
from rich.console import Console
from rich.table import Table
from rich.traceback import install
import logging
import time
install()  # creates a better readable traceback


console = Console()

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
        self.name = name  # name of the scheduler
        self.feasible_nodes = []  # list of feasible nodes for the pod
        self.selected_node = None  # final selected node for the pod

        self.predicate_methods = [self.podFitsHostPorts, self.podFitsHost,
                                self.podFitsResources, self.matchNodeSelector,
                                self.noVolumeZoneConflict, self.noDiskConflict,
                                self.maxCSIVolumeCount, self.podToleratesNodeTaints,
                                self.checkVolumeBinding]

    def scheduling_cycle(self, cluster, pod):
        nodes = cluster.get_node_list()  # list of all the nodes
        lrp_check = False  # check for LeastRequestedPriority
        mrp_check = False  # check for MostRequestedPriority
        global node_passed
        node_passed = False

        for node in nodes:

            '''
            This loop finds the number of feasible node(s) for the pod by
            applying a set of predicates.
            '''
            for pred in range(len(pod.plugin.predicate_list)):

                # checks whether plugin is ON/OFF
                if pod.plugin.predicate_list[pred]:
                    if (self.predicate_methods[pred](node, pod)):
                        console.log(
                            ":thumbs_up: {}: {}".format(
                            pod.plugin.predicates_name[pred], node.name),
                            style="cyan")
                        node_passed = True

                    else:
                        console.log(
                            ":thumbs_down: {}: {}".format(
                            pod.plugin.predicates_name[pred], node.name),
                            style="cyan")
                        node_passed = False
                        break

            if node_passed:
                self.feasible_nodes.append(node)

            # Applying Priorites

            if pod.plugin.priorites_list[9]:
                if (self.imageLocalityPriority(node, pod)):
                    node.score += 1
                    console.log(":cd: Image locality Found", style="cyan")

            if pod.plugin.priorites_list[2] and lrp_check is False:
                self.leastRequestedPriority(cluster)
                lrp_check = True

            if pod.plugin.priorites_list[3] and mrp_check is False:
                self.mostRequestedPriority(cluster)
                mrp_check = True

        # check that feasible nodes list is not empty
        if len(self.feasible_nodes) > 0:

            # sort the nodes on the basis of their score
            self.feasible_nodes.sort(key=lambda x: x.score, reverse=True)

            # select the node with the highest score
            self.selected_node = self.feasible_nodes[0]
            self.selected_node.add_pod(pod)  # add the pod to the selected node
            pod.node = self.selected_node  # bind pod to the selected node

            logging.info(' \"Selected Node: {}\"\n'.format(
                            self.selected_node.name))

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
            # print(node.serialize(), '\n')

            table.add_row(node.name, str(node.id), str(node.num_of_pods),
                            str(node.memory), str(node.cpu), str(node.score),
                            str(node.port))

            node.score = 0  # clear the node score for the next pod scheduling

        console.log(table)

