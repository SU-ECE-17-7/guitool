from __future__ import absolute_import, division, print_function
from guitool.__PYQT__ import QtCore, QtGui
from guitool import api_item_view
#from guitool import guitool_components
from guitool.guitool_decorators import signal_, slot_
import utool

(print, print_, printDBG, rrr, profile) = utool.inject(
    __name__, '[APITreeView]', DEBUG=False)


# If you need to set the selected index try:
# AbstractItemView::setCurrentIndex
# AbstractItemView::scrollTo
# AbstractItemView::keyboardSearch

API_VIEW_BASE = QtGui.QTreeView
#API_VIEW_BASE = QtGui.QAbstractItemView


class APITreeView(API_VIEW_BASE):
    """
    Tree view of API data.
    Implicitly inherits from APIItemView
    """
    rows_updated = signal_(str, int)
    contextMenuClicked = signal_(QtCore.QModelIndex, QtCore.QPoint)
    API_VIEW_BASE = API_VIEW_BASE

    def __init__(view, parent=None):
        # Qt Inheritance
        API_VIEW_BASE.__init__(view, parent)
        # Implicitly inject common APIItemView functions
        api_item_view.injectviewinstance(view)
        #utool.inject_instance(view, API_VIEW_BASE)
        # Allow sorting by column
        view._init_tree_behavior()
        view.col_hidden_list = []
        ##view._init_header_behavior()
        # Context menu
        view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        view.customContextMenuRequested.connect(view.on_customMenuRequested)
        #view.cornerButton = guitool_components.newButton(view)
        #view.setCornerWidget(view.cornerButton)

    #---------------
    # Initialization
    #---------------

    def _init_tree_behavior(view):
        """ Tree behavior """
        view.setWordWrap(True)
        view.setSortingEnabled(True)
        view._defaultEditTriggers = QtGui.QAbstractItemView.AllEditTriggers
        view.setEditTriggers(view._defaultEditTriggers)

    def _init_header_behavior(view):
        """ Header behavior

        CommandLine:
            python -m guitool.api_tree_view --test-_init_header_behavior

        Example:
            >>> # ENABLE_DOCTEST
            >>> # TODO figure out how to test these
            >>> from guitool.api_tree_view import *  # NOQA
            >>> view = APITreeView()
            >>> view._init_header_behavior()
        """
        # Row Headers
        # Column headers
        header = view.header()
        header.setVisible(True)
        header.setStretchLastSection(True)
        header.setSortIndicatorShown(True)
        header.setHighlightSections(True)
        # Column Sizes
        # DO NOT USE RESIZETOCONTENTS. IT MAKES THINGS VERY SLOW
        #horizontalHeader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        #horizontalHeader.setResizeMode(QtGui.QHeaderView.Stretch)
        header.setResizeMode(QtGui.QHeaderView.Interactive)
        #horizontalHeader.setCascadingSectionResizes(True)
        # Columns moveable
        header.setMovable(True)

    #---------------
    # Qt Overrides
    #---------------

    def setModel(view, model):
        """ QtOverride: Returns item delegate for this index """
        api_item_view.setModel(view, model)

    #---------------
    # Slots
    #---------------

    @slot_(str, int)
    def on_rows_updated(view, tblname, num):
        # re-emit the model signal
        view.rows_updated.emit(tblname, num)

    @slot_(QtCore.QPoint)
    def on_customMenuRequested(view, pos):
        index = view.indexAt(pos)
        view.contextMenuClicked.emit(index, pos)


if __name__ == '__main__':
    """
    CommandLine:
        python -m guitool.api_tree_view
        python -m guitool.api_tree_view --allexamples
        python -m guitool.api_tree_view --allexamples --noface --nosrc
    """
    import multiprocessing
    multiprocessing.freeze_support()  # for win32
    import utool as ut  # NOQA
    ut.doctest_funcs()
