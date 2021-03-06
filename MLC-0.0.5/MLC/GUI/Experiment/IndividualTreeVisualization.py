# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import networkx as nx
import os
import sys

from MLC.Common.LispTreeExpr.LispTreeExpr import LispTreeExpr
from MLC.GUI.Common.util import test_individual_value
from MLC.GUI.Autogenerated.autogenerated import Ui_IndividualTreeVisualization
from MLC.Log.log import get_gui_logger
from MLC.mlc_parameters.mlc_parameters import Config

from PyQt5.QtCore import QPointF
# from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow

logger = get_gui_logger()

class IndividualTreeVisualization(QMainWindow):

    def __init__(self, parent, experiment_name, current_gen, gen_data):
        QMainWindow.__init__(self, parent)
        self._experiment_name = experiment_name
        self._log_prefix = "[INDIV_TREE_VISUALIZATION_WINDOW]"
        self._gen_data = gen_data
        self._current_gen = current_gen

        # Store the GUI objects references to easily access them
        self._autogenerated_object = Ui_IndividualTreeVisualization()
        self._autogenerated_object.setupUi(self)
        self._indiv_index_combo = self._autogenerated_object.indiv_index_combo
        self._simplify_check = self._autogenerated_object.simplify_check
        self._evaluate_check = self._autogenerated_object.evaluate_check

        self._indiv_index_combo.addItems([str(x + 1) for x in xrange(len(self._gen_data))])

    def on_dialog_button_box_clicked(self):
        logger.debug('{0} [DIALOG_BUTTON_CLICKED] - Executing on_dialog_button_box_clicked function'
                     .format(self._log_prefix))

        pop_index = int(self._indiv_index_combo.currentText()) - 1
        indiv_index = self._gen_data[pop_index][1]
        value = self._gen_data[pop_index][5]

        self._draw_individual_tree(pop_index=pop_index,
                                   indiv_index=indiv_index,
                                   simplify=self._simplify_check.isChecked(),
                                   evaluate=self._evaluate_check.isChecked(),
                                   value=value)

    def _draw_individual_tree(self, 
                              pop_index, 
                              indiv_index, 
                              simplify, 
                              evaluate,
                              value):
        fig = plt.figure()
        # Put figure window on top of all other windows
        fig.canvas.manager.window.setWindowModality(Qt.ApplicationModal)
        fig.canvas.manager.window.setWindowTitle("Individual Tree Representation")

        # Simplify the tree if neccesary
        tree = LispTreeExpr(value)
        if simplify == True:
            tree.simplify_tree()
        graph = tree.construct_graph()

        # Evaluate the Individual if necessary
        cost = None
        if evaluate == True:
            cost = test_individual_value(parent=self,
                                         experiment_name=self._experiment_name,
                                         log_prefix=self._log_prefix,
                                         indiv_value=value,
                                         config=Config.get_instance())

        # Remove image axes
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')

        # Networkx use the node id as label. We have to relabel every node
        labels = {}
        for node_id in graph:
            labels[node_id] = graph.node[node_id]['value']

        # Use Pygraph to visualize the graph as a hierarchical tree
        pos = nx.nx_pydot.graphviz_layout(graph, prog='dot')

        # Draw nodes and edges in separated nodes to be able to change 
        # the perimter color of the nodes
        nodes = nx.draw_networkx_nodes(graph, pos, node_size=1000, node_color='#D3D3D3')
        nodes.set_edgecolor('k')
        nx.draw_networkx_edges(graph, pos, arrows=False)
        nx.draw_networkx_labels(graph, pos, labels, font_size=12)

        # Set the figure Title
        plt.rc('font', family='serif')
        title = (u"Generation N°{0} - Individual N°{1} - Simplified: {2}"
                .format(self._current_gen, indiv_index, simplify))

        if evaluate == True:
            title += " - Cost: {0}".format(cost)

        plt.suptitle(title, fontsize=12)
        plt.show()
        self.close()