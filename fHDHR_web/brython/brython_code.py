from browser import document, bind  # alert, window, html
from browser.local_storage import storage
from browser.widgets.menu import Menu
import json

storage['session'] = json.loads(document['session'].value)
storage['servicename'] = document['servicename'].value
storage['access_level'] = document['access_level'].value


def main_menu_setup():
    zone = document["main_menu"]
    menu = Menu(zone)

    menu.add_item("fHDHR")
    menu.add_item(storage['servicename'])

    for page_dict in storage['route_list']["pages"]:
        if storage['route_list']["pages"][page_dict]["name"] != "page_index_html" and storage['access_level'] >= storage['route_list']["pages"][page_dict]["endpoint_access_level"]:
            menu.add_item(storage['route_list']["pages"][page_dict]["pretty_name"])

    """
    <button onclick="location.href='/index'" type="button">fHDHR</button>
    <button onclick="location.href='/origin'" type="button">{{ fhdhr.config.dict["main"]["servicename"] }}</button>

    {% for page_dict in session["route_list"]["pages"] %}
        {% if session["route_list"]["pages"][page_dict]["name"] != "page_index_html" and fhdhr.config.dict["web_ui"]["access_level"] >= session["route_list"]["pages"][page_dict]["endpoint_access_level"] %}
          <button onclick="location.href='{{ session["route_list"]["pages"][page_dict]["endpoints"][0] }}'" type="button">{{ session["route_list"]["pages"][page_dict]["pretty_name"] }}</button>
        {% endif %}
    {% endfor %}
    """

    """
    file_menu = menu.add_menu("File")

    save_menu = file_menu.add_menu("Save")
    choice1 = save_menu.add_menu("choice 1")
    choice1.add_item("sub-choice 1")
    choice1.add_item("sub-choice 2")
    save_menu.add_item("choice 2")

    file_menu.add_item("Open")
    save_menu = file_menu.add_menu("Properties")
    save_menu.add_item("size")
    save_menu.add_item("security")

    file_menu.add_item("Print")

    edit_menu = menu.add_menu("Edition")
    edit_menu.add_item("Search")
    """


def chan_edit_data(items, channel_id):

    chanlist = []
    chandict = {}

    for element in items:
        if element.name == "id":
            if len(chandict.keys()) >= 2 and "id" in list(chandict.keys()):
                chanlist.append(chandict)
            chandict = {"id": element.value}
        if element.type == "checkbox":
            if element.name in ["enabled"]:
                save_val = element.checked
            else:
                save_val = int(element.checked)
        else:
            save_val = element.value
        if element.name != "id":
            cur_value = element.placeholder
            if element.type == "checkbox":
                if element.name in ["enabled"]:
                    cur_value = element.placeholder
                else:
                    cur_value = int(element.placeholder)
            if str(save_val) != str(cur_value):
                chandict[element.name] = save_val

    if channel_id != "all":
        chanlist == [x for x in chanlist if x["id"] == channel_id]

    return chanlist


def chan_edit_postform(chanlist):
    postForm = document.createElement('form')
    postForm.method = "POST"
    postForm.action = "/api/channels?method=modify&redirect=/channels_editor"
    postForm.setRequestHeader = "('Content-Type', 'application/json')"

    postData = document.createElement('input')
    postData.type = 'hidden'
    postData.name = "channels"
    postData.value = json.dumps(chanlist)

    postForm.appendChild(postData)
    document.body.appendChild(postForm)
    return postForm


@bind("#Chan_Edit_Reset", "submit")
def chan_edit_reset(evt):
    chanlist = chan_edit_data(
                              document.select(".reset"),
                              str(evt.currentTarget.children[0].id).replace("reset_", ""))
    postForm = chan_edit_postform(chanlist)
    postForm.submit()
    evt.preventDefault()


@bind("#Chan_Edit_Modify", "submit")
def chan_edit_modify(evt):
    chanlist = chan_edit_data(
                              document.select(".channels"),
                              str(evt.currentTarget.children[0].id).replace("update_", ""))
    postForm = chan_edit_postform(chanlist)
    postForm.submit()
    evt.preventDefault()


@bind("#Chan_Edit_Enable_Toggle", "click")
def chan_edit_enable(event):
    enable_bool = bool(int(document["enable_button"].value))
    for element in document.get(selector='input[type="checkbox"]'):
        if element.name == "enabled":
            element.checked = enable_bool
            element.value = enable_bool

    if not enable_bool:
        document["enable_button"].value = "1"
        document["enable_button"].text = "Enable All"
    else:
        document["enable_button"].value = "0"
        document["enable_button"].text = "Disable All"


@bind("#Chan_Edit_Favorite_Toggle", "click")
def chan_edit_favorite(event):
    enable_bool = bool(int(document["favorite_button"].value))
    for element in document.get(selector='input[type="checkbox"]'):
        if element.name == "favorite":
            element.checked = enable_bool
            element.value = int(enable_bool)

    if not enable_bool:
        document["favorite_button"].value = "1"
        document["favorite_button"].text = "Favorite All"
    else:
        document["favorite_button"].value = "0"
        document["favorite_button"].text = "Unfavorite All"


main_menu_setup()
