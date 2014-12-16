from __future__ import absolute_import, division, print_function
from six.moves import map
from guitool.__PYQT__ import QtCore, QtGui  # NOQA
from guitool.__PYQT__.QtCore import Qt
from os.path import split
# UTool
import platform
import utool
from utool import util_cache, util_path
import utool as ut
ut.noinject(__name__, '[guitool.delegates]', DEBUG=False)


SELDIR_CACHEID = 'guitool_selected_directory'


def _guitool_cache_write(key, val):
    """ Writes to global IBEIS cache """
    util_cache.global_cache_write(key, val, appname='ibeis')  # HACK, user should specify appname


def _guitool_cache_read(key, **kwargs):
    """ Reads from global IBEIS cache """
    return util_cache.global_cache_read(key, appname='ibeis', **kwargs)  # HACK, user should specify appname


def user_option(parent=None, msg='msg', title='user_option',
                options=['No', 'Yes'], use_cache=False):
    """
    Prompts user with several options with ability to save decision

    Args:
        parent (None):
        msg (str):
        title (str):
        options (list):
        use_cache (bool):

    Returns:
        str: reply

    CommandLine:
        python -m guitool.guitool_dialogs --test-user_option

    Example:
        >>> # DISABLE_DOCTEST
        >>> from guitool.guitool_dialogs import *  # NOQA
        >>> # build test data
        >>> parent = None
        >>> msg = 'msg'
        >>> title = 'user_option'
        >>> options = ['No', 'Yes']
        >>> use_cache = False
        >>> # execute function
        >>> reply = user_option(parent, msg, title, options, use_cache)
        >>> # verify results
        >>> result = str(reply)
        >>> print(result)
    """
    if utool.VERBOSE:
        print('[*guitools] user_option:\n %r: %s' % (title, msg))
    # Recall decision
    cache_id = title + msg
    if use_cache:
        reply = _guitool_cache_read(cache_id, default=None)
        if reply is not None:
            return reply
    # Create message box
    msgbox = _newMsgBox(msg, title, parent)
    _addOptions(msgbox, options)
    if use_cache:
        # Add a remember me option if caching is on
        dontPrompt = _cacheReply(msgbox)
    # Wait for output
    optx = msgbox.exec_()
    if optx == QtGui.QMessageBox.Cancel:
        # User Canceled
        return None
    try:
        # User Selected an option
        reply = options[optx]
    except KeyError as ex:
        # This should be unreachable code.
        print('[*guitools] USER OPTION EXCEPTION !')
        print('[*guitools] optx = %r' % optx)
        print('[*guitools] options = %r' % options)
        print('[*guitools] ex = %r' % ex)
        raise
    # Remember decision if caching is on
    if use_cache and dontPrompt.isChecked():
        _guitool_cache_write(cache_id, reply)
    # Close the message box
    del msgbox
    return reply


def user_input(parent=None, msg='msg', title='user_input'):
    r"""
    Args:
        parent (None):
        msg (str):
        title (str):

    Returns:
        str:

    CommandLine:
        python -m guitool.guitool_dialogs --test-user_input

    Example:
        >>> # ENABLE_DOCTEST
        >>> from guitool.guitool_dialogs import *  # NOQA
        >>> # build test data
        >>> parent = None
        >>> msg = 'msg'
        >>> title = 'user_input'
        >>> # execute function
        >>> dpath = user_input(parent, msg, title)
        >>> # verify results
        >>> result = str(dpath)
        >>> print(result)
    """
    reply, ok = QtGui.QInputDialog.getText(parent, title, msg)
    if not ok:
        return None
    return str(reply)


def user_info(parent=None, msg='msg', title='user_info'):
    print('[dlg.user_info] title=%r, msg=%r' % (title, msg))
    msgbox = _newMsgBox(msg, title, parent)
    msgbox.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    msgbox.setStandardButtons(QtGui.QMessageBox.Ok)
    msgbox.setModal(False)
    msgbox.open(msgbox.close)
    msgbox.show()


def user_question(msg):
    raise NotImplementedError('user_question')
    msgbox = QtGui.QMessageBox.question(None, '', 'lovely day?')
    return msgbox


def select_directory(caption='Select Directory', directory=None):
    print(caption)
    if directory is None:
        directory_ = _guitool_cache_read(SELDIR_CACHEID, default='.')
    else:
        directory = directory_
    qdlg = QtGui.QFileDialog()
    # hack to fix the dialog window on ubuntu
    if 'ubuntu' in platform.platform().lower():
        qopt = QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontUseNativeDialog
    else:
        qopt = QtGui.QFileDialog.ShowDirsOnly
    qtkw = {
        'caption': caption,
        'options': qopt,
        'directory': directory_
    }
    dpath = str(qdlg.getExistingDirectory(None, **qtkw))
    print('dpath = %r' % dpath)
    if dpath == '' or dpath is None:
        dpath = None
        return dpath
    else:
        _guitool_cache_write(SELDIR_CACHEID, split(dpath)[0])
    print('Selected Directory: %r' % dpath)
    return dpath


def select_images(caption='Select images:', directory=None):
    name_filter = _getQtImageNameFilter()
    return select_files(caption, directory, name_filter)


def select_files(caption='Select Files:', directory=None, name_filter=None):
    'Selects one or more files from disk using a qt dialog'
    print(caption)
    if directory is None:
        directory = _guitool_cache_read(SELDIR_CACHEID, default='.')
    qdlg = QtGui.QFileDialog()
    qfile_list = qdlg.getOpenFileNames(caption=caption, directory=directory, filter=name_filter)
    file_list = list(map(str, qfile_list))
    print('Selected %d files' % len(file_list))
    _guitool_cache_write(SELDIR_CACHEID, directory)
    return file_list

# Prevent messageboxes from being garbage collected
__MESSAGE_BOXES__ = []


def _register_msgbox(msgbox):
    """ Dont let the message box lose scope """
    global __MESSAGE_BOXES__
    __MESSAGE_BOXES__.append(msgbox)
    @QtCore.pyqtSlot(QtCore.QObject)
    def _close_msgbox(qobj):
        global __MESSAGE_BOXES__
        __MESSAGE_BOXES__.remove(msgbox)
    msgbox.destroyed.connect(_close_msgbox)


def msgbox(msg, title='msgbox'):
    """ Make a non modal critical QtGui.QMessageBox. """
    msgbox = QtGui.QMessageBox(None)
    msgbox.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    msgbox.setStandardButtons(QtGui.QMessageBox.Ok)
    msgbox.setWindowTitle(title)
    msgbox.setText(msg)
    msgbox.setModal(False)
    msgbox.open(msgbox.close)
    msgbox.show()
    _register_msgbox(msgbox)
    return msgbox


def popup_menu(widget, pos, opt2_callback):
    menu = QtGui.QMenu(widget)
    actions = [menu.addAction(opt, func) for (opt, func) in opt2_callback]
    selection = menu.exec_(widget.mapToGlobal(pos))
    return selection, actions
    #pos=QtGui.QCursor.pos()


def connect_context_menu(widget, opt2_callback):
    def popup_slot(pos):
        return popup_menu(widget, pos, opt2_callback)
    # Remove other context menus from this widget
    for _slot in _get_scope(widget, '_popup_scope'):
        widget.customContextMenuRequested.disconnect(_slot)
    _clear_scope(widget, '_popup_scope')
    # Enable custom context menus to be requested
    widget.setContextMenuPolicy(Qt.CustomContextMenu)
    # Connect our context slot
    widget.customContextMenuRequested.connect(popup_slot)
    # Make sure popup_slot does not lose scope.
    _enforce_scope(widget, popup_slot, '_popup_scope')
    return popup_slot


def _get_scope(qobj, scope_title='_scope_list'):
    """ Helper for ensuring qt objects are not garbage collected """
    if not hasattr(qobj, scope_title):
        setattr(qobj, scope_title, [])
    return getattr(qobj, scope_title)


def _clear_scope(qobj, scope_title='_scope_list'):
    """ Helper for ensuring qt objects are not garbage collected """
    setattr(qobj, scope_title, [])


def _enforce_scope(qobj, scoped_obj, scope_title='_scope_list'):
    """ Helper for ensuring qt objects are not garbage collected """
    _get_scope(qobj, scope_title).append(scoped_obj)


def _addOptions(msgbox, options):
    #msgbox.addButton(QtGui.QMessageBox.Close)
    for opt in options:
        role = QtGui.QMessageBox.ApplyRole
        msgbox.addButton(QtGui.QPushButton(opt), role)


def _cacheReply(msgbox):
    dontPrompt = QtGui.QCheckBox('dont ask me again', parent=msgbox)
    dontPrompt.blockSignals(True)
    msgbox.addButton(dontPrompt, QtGui.QMessageBox.ActionRole)
    return dontPrompt


def _newMsgBox(msg='', title='', parent=None, options=None, cache_reply=False):
    msgbox = QtGui.QMessageBox(parent)
    #msgbox.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    #std_buts = QtGui.QMessageBox.Close
    #std_buts = QtGui.QMessageBox.NoButton
    std_buts = QtGui.QMessageBox.Cancel
    msgbox.setStandardButtons(std_buts)
    msgbox.setWindowTitle(title)
    msgbox.setText(msg)
    msgbox.setModal(parent is not None)
    return msgbox


def _getQtImageNameFilter():
    imgNamePat = ' '.join(['*' + ext for ext in util_path.IMG_EXTENSIONS])
    imgNameFilter = 'Images (%s)' % (imgNamePat)
    return imgNameFilter
