# Konrad Brüggemann
# Universität Potsdam
# Bachelor Computerlinguistik
# 4. Semester


from model.Auxillary import Config, Art
from model.BKTree import BKTree
from model.tests import BKTreeTests
from model.Visualizer import Visualizer
from View import View
import ntpath
import os
import pickle


class Controller:

    def __init__(self, path, demo, dist):
        self.path = path
        self.file = self._load()
        self.dist = dist or "lev"
        self.file_name = f"{self.file[1]}_{self.dist[:3]}"
        self.word_list = self.file[0]
        self.save = demo != "demo"

    def _load_saved_pickle(self):
        """
        If a pickle file corresponding to the input word list was found,
        this method will load the tree and generate a graph for it
        """
        print("A tree was already generated for this word list. Loading...")

        with open(f"output/{self.file_name}.pickle", "rb") as f:
            self.tree = pickle.load(f)

        # making sure the tree that was loaded was built correctly
        tester = BKTreeTests(self.tree)
        print(tester.test_if_tree_is_correct())

        # graph is being generated and shown if not too long
        if len(self.word_list) >= Config.max_items:
            print("Cannot plot graph since tree is too large.")
        else:
            vis = Visualizer(self.tree)
            graph = vis.graph
            graph.show()

    def _generate_new_files(self):
        """
        If the input word list has not previously been used,
        a new tree and a new graph will be generated
        in demo mode, only the graph will be shown and no files will be stored
        otherwise the tree will be stored in a pickle file (and in text format) and the graph will be saved as a png
        """
        print("Tree is being generated...")
        tree = BKTree(self.word_list, edit_dist=self.dist)
        self.tree = tree.tree
        print(f"The maximum height of the tree is {tree.max_depth} and it has {len(self.word_list)} nodes.")
        if len(self.word_list) <= Config.max_items:
            print("Plotting graph...")
        graph = tree.graph
        if self.save:
            self._save_files(tree=tree, graph=graph, file_name=self.file_name)
        try:
            graph.show()
        except AttributeError:
            pass

    def _load(self):
        """
        Loads the word list from input file and does a bit of pre processing
        assuming there is one word per line in the file
        :return:
        a tuple consisting of the word list and the name of the file without extension
        """
        with open(file=self.path, encoding="UTF-8") as file:
            text = file.read()

        word_list = ""

        # finding out what separator is used
        word_list_type = text[:50]

        if "\n" in word_list_type: word_list = text.split("\n")
        elif "," in word_list_type: word_list = text.split(",")
        elif " " in word_list_type: word_list = text.split()

        # determining the file name excl extension
        file_name = ntpath.basename(file.name)
        file_name = file_name.strip(".txt")

        return word_list, file_name

    @staticmethod
    def _save_files(tree, file_name, graph):
        """
        Saves the tree in a pickle file and a text version of the tree in a .txt file
        The graph is also being saved in a png file
        :param tree: tree object generated by _generate_new_files method
        :param file_name: name of the word list file without extension
        :param graph: graph visualization of the tree
        """
        with open(f"output/{file_name}.pickle", "wb") as f:
            pickle.dump(tree.tree, f)
        with open(f"output/{file_name}_result.txt", "w", encoding="UTF-8") as f:
            f.write(str(tree.tree))

        try:
            graph.savefig(f"output/{file_name}.png", bbox_inches="tight", dpi=100)
        except AttributeError:
            pass

    def main(self):
        os.makedirs("output", exist_ok=True)
        # If the word list has been previously used, the tree will be loaded from the pickle file
        if os.path.exists(f"output/{self.file_name}.pickle"):
            self._load_saved_pickle()
        else:
            # otherwise the tree will be newly generated
            self._generate_new_files()
        print(Art.interactive_mode)
        view = View(tree=self.tree, dist=self.dist)
        view.main()