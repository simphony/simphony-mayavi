from traitsui.tests._tools import is_current_backend_wx, is_current_backend_qt4


def press_button_by_label(ui, label):
    ''' Imitate pressing a button in the UI

    Parameters
    ----------
    ui : traits.ui.UI
    label : str
       Text on the button
    '''
    if is_current_backend_wx():
        import wx
        
        button = ui.control.FindWindowByLabel(label)
        click_event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,
                                      button.GetId())
        button.ProcessEvent(click_event)
    elif is_current_backend_qt4():
        from pyface import qt

        buttons = ui.control.findChildren(qt.QtGui.QPushButton)
        button_texts = (button.text() for button in buttons)
        for button in buttons:
            if button.text() == label:
                button.click()
                break

