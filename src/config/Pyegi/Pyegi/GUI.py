import io
import os
import PySimpleGUI as sg
from PIL import Image
import appdirs

def change_preview_container_visiblity(visible: bool):
    if visible:
        preview_container_element.update(visible=True)
        preview_container_element.expand(expand_x=True, expand_y=True)
        preview_img_element.expand(expand_x=True, expand_y=True)
        preview_selector_element.expand(expand_x=True, expand_row=False)
    else:
        preview_container_element.update(visible=False)

aegisub_automation_dir = os.path.join(appdirs.user_data_dir("Aegisub", "", roaming=True), "automation")
scripts_dir = os.path.join(aegisub_automation_dir, "config", "Pyegi", "PythonScripts")
scripts = [f for f in os.listdir(scripts_dir) if os.path.isdir(os.path.join(scripts_dir, f))]
previews = []

preview_layout = [ [sg.Image(key="preview_img", pad=(0,0))],
                   [sg.Text("Select Preview:"), sg.Combo(previews, key="preview_selector", change_submits=True, readonly=True)] ]
main_layout = [ [sg.Text("Select Script:"), sg.Combo(scripts, key="script_selector", change_submits=True, readonly=True)],
                [sg.pin(sg.Frame("Script Preview", preview_layout, key="preview_container", element_justification="c", visible=False), expand_x=True, expand_y=True)] ]
footer_layout = [ [sg.Button('Cancel', key="cancel", size=(10,1)),
                   sg.Text("", key="spacer1"),
                   sg.Button('Settings', key="setting", size=(10,1)),
                   sg.Text("", key="spacer2"),
                   sg.Button('Next', key="ok", size=(10,1))] ]
layout = [ [sg.Column(main_layout, key="main", justification="c", element_justification="c", expand_x=True, expand_y=True)],
           [sg.Column(footer_layout, key="footer", justification="c", expand_x=True)] ]

screen_size = sg.Window.get_screen_size()
content_size = (int(screen_size[0]/2), int(screen_size[1]*3/4))
window = sg.Window('Pyegi', layout, size=content_size, resizable=True, finalize=True)
preview_img_element: sg.Image = window["preview_img"]
preview_selector_element: sg.Combo = window["preview_selector"]
preview_container_element: sg.Frame = window["preview_container"]

window["script_selector"].expand(expand_x=True, expand_row=False)
spacers: list[sg.Text] = [entry for entry in footer_layout[0] if entry.Key.startswith("spacer")]
for spacer in spacers:
    spacer.expand(expand_x=True, expand_y=True)

script = ""
preview = ""
preview_img: Image.Image = None
frame_number = 0
frame_duration = 0
timeout = 50
while True:
    event, values = window.read(timeout=timeout)
    frame_duration += timeout
    print(event, values)
    
    if event in (sg.WIN_CLOSED, 'cancel'):
        break
    elif event in ("script_selector") and values["script_selector"] != script:
        script = values["script_selector"]
        if script != "":
            previews = [f.removesuffix(".webp") for f in os.listdir(os.path.join(scripts_dir, script)) if f.endswith(".webp")]
        else:
            previews = []
            preview = ""
        change_preview_container_visiblity(previews != [])
        preview_selector_element.update(values=previews)
    elif event in ("preview_selector") and values["preview_selector"] != preview:
        preview = values["preview_selector"]
        frame_number = 0
        frame_duration = 0
        if preview != "":
            if preview_img != None: preview_img.close()
            preview_img = Image.open(os.path.join(scripts_dir, script, preview+".webp"))
        else:
            preview_img.close()
            preview_img = None
            preview_img.update(data=None)

    if preview_img != None:
        try:
            preview_img.seek(frame_number)
        except EOFError:
            frame_number = 0
            preview_img.seek(frame_number)
        img_buffer = io.BytesIO()
        image_container_size = preview_img_element.get_size()
        if image_container_size[0] > preview_img.width or preview_img.height > preview_img.width:
            img_width = preview_img.width*image_container_size[1]/preview_img.height - 2
            img_height = image_container_size[1] - 2
        else:
            img_width = image_container_size[0] - 2
            img_height = preview_img.height*image_container_size[0]/preview_img.width - 2
        preview_img.resize((int(img_width), int(img_height)), resample=Image.LANCZOS).save(img_buffer, "png")
        preview_img_element.update(data=img_buffer.getvalue())
        if preview_img.info["duration"] - frame_duration < timeout/2:
            frame_number += 1
            frame_duration = 0

window.close()
if preview_img != None: preview_img.close()
