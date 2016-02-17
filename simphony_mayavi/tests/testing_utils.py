def run_and_check_dialog_was_opened(test_case, tester, accept=False):
    ''' Open and run the tester, fail the test case if
    no dialog was open '''

    tester.dialog_was_opened = False

    def when_opened(tester):
        tester.dialog_was_opened = True
        tester.close(accept=accept)

    tester.open_and_run(when_opened=when_opened)

    if not tester.dialog_was_opened:
        test_case.fail("Dialog was not opened")
