from traits.etsconfig.api import ETSConfig


def is_current_backend(backend_name):
    return ETSConfig.toolkit == backend_name


def press_button_by_label(ui, label):
    ''' Imitate pressing a button in the UI

    Parameters
    ----------
    ui : traits.ui.UI
    label : str
       Text on the button
    '''
    if is_current_backend("wx"):
        import wx

        button = ui.control.FindWindowByLabel(label)
        click_event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,
                                      button.GetId())
        button.ProcessEvent(click_event)
    elif is_current_backend("qt4"):
        from pyface import qt

        buttons = ui.control.findChildren(qt.QtGui.QPushButton)
        for button in buttons:
            if button.text() == label:
                button.click()
                break
