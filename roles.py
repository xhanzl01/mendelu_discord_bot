

def is_valid_email(login):
    if (login[0] == 'x' or login[0] == 'qq') and login.split("@")[1] == "mendelu.cz":
        return True
    else:
        return False