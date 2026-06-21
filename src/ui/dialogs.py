from CTkMessagebox import CTkMessagebox

def show_error(title, message):
    CTkMessagebox(title=title, message=message, icon="cancel")

def show_warning(title, message):
    CTkMessagebox(title=title, message=message, icon="warning")

def show_info(title, message):
    CTkMessagebox(title=title, message=message, icon="info")

def ask_yes_no(title, message):
    msg = CTkMessagebox(title=title, message=message, icon="question", option_1="No", option_2="Yes")
    return msg.get() == "Yes"
