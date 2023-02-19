"""
FireAlpaca GUI Automation

FireAlpaca doesn't currently have a way to do impex
without manually clicking through the dialog options.

To make this slightly easier on myself, I made a script which
can automate the app with decent reliability.

The app sometimes eats button inputs, which is why I'm looking into
using frida to directly poke functions in the code.
"""

from pywinauto.application import Application


def close_ad_popup(app: Application) -> None:
    # Popup is named "FireAlpaca", while main window is named
    # "FireAlpaca (32bit)" or "FireAlpaca (64bit)"
    dlg_spec = app.window(title="FireAlpaca", control_type="Window")
    dlg_spec.wait(wait_for='exists')

    # Take the easy route:
    dlg_spec.close()


def open_file(app: Application, filename: str) -> None:
    dlg_spec0 = app.window(title_re="FireAlpaca \(\d+bit\)", control_type="Window")

    dlg_spec0.type_keys("^o")

    dlg_spec1 = dlg_spec0.child_window(title="Open Image", control_type="Window")
    dlg_spec1.wait(wait_for='exists')

    dlg_spec2 = dlg_spec1.child_window(title="File name:", auto_id="1148", control_type="Edit")
    dlg_wrap2 = dlg_spec2.wrapper_object()

    dlg_wrap2.set_text(filename)

    dlg_spec3 = dlg_spec1.child_window(title="Open", auto_id="1", control_type="Button")
    dlg_wrap3 = dlg_spec3.wrapper_object()

    dlg_wrap3.click()


def save_as_file(app: Application, filename: str) -> None:
    dlg_spec0 = app.window(title_re="FireAlpaca \(\d+bit\)", control_type="Window")

    dlg_spec0.type_keys("^+s")

    dlg_spec1 = dlg_spec0.child_window(title="Save Image", control_type="Window")
    dlg_spec1.wait(wait_for='exists')

    # Unlike other applications, doesn't have an "All supported formats" option
    # So we need to select the right type manually

    dlg_spec4 = dlg_spec1.child_window(title="Save as type:", auto_id="FileTypeControlHost", control_type="ComboBox") \
                         .child_window(title="Open", auto_id="DropDown", control_type="Button")
    dlg_wrap4 = dlg_spec4.wrapper_object()

    dlg_wrap4.click()

    dlg_spec4 = dlg_spec1.child_window(title="Save as type:", auto_id="FileTypeControlHost", control_type="ComboBox") \
                         .child_window(title="Save as type:", control_type="List")
    dlg_wrap4 = dlg_spec4.wrapper_object()

    dlg_wrap5 = None

    # if filename.endswith(".psd"):
    #     dlg_wrap5 = dlg_wrap4.item('PSD (*.psd)')

    for save_as_type_dlg in dlg_wrap4.items():
        labels = save_as_type_dlg.texts()
        for label in labels:
            _label = label.rpartition("(")[2]
            _label = _label.rpartition(")")[0]
            _label = _label.strip()

            fexts = list(map(lambda x: x.lstrip("*"), _label.split()))

            for fext in fexts:
                if filename.endswith(fext):
                    dlg_wrap5 = save_as_type_dlg
                    break

            if dlg_wrap5 is not None:
                break
        if dlg_wrap5 is not None:
            break

    if dlg_wrap5 is None:
        dlg_wrap5 = dlg_wrap4.item(0)

    print(dlg_wrap5)

    dlg_wrap5.select()

    dlg_spec2 = dlg_spec1.child_window(title="File name:", auto_id="1001", control_type="Edit")
    dlg_wrap2 = dlg_spec2.wrapper_object()

    dlg_wrap2.set_text(filename)

    dlg_spec3 = dlg_spec1.child_window(title="Save", auto_id="1", control_type="Button")
    dlg_wrap3 = dlg_spec3.wrapper_object()

    dlg_wrap3.click()

    # TODO: Handle overwrite prompts and such


def close_file(app: Application) -> None:
    dlg_spec0 = app.window(title_re="FireAlpaca \(\d+bit\)", control_type="Window")

    # TODO


def main() -> None:
    app = Application(backend="uia")

    #app.start("./FireAlpacaWin64_2_8_11/FireAlpaca.exe")
    app.connect(title_re="FireAlpaca \(\d+bit\)", control_type="Window")

    # Ad Popup might already be closed
    try:
        close_ad_popup(app)
    except:
        pass

    open_file(app, "%USERPROFILE%\Downloads\yohaku_370x320.mdp")

    # TODO: Wait for Load

    save_as_file(app, "%USERPROFILE%\Downloads\yohaku_370x320_tmp.psd")

    close_file(app)

if __name__ == "__main__":
    main()
