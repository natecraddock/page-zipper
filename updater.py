import requests
from tkinter import messagebox
import webbrowser


# Returns tag from latest release on a given repository
def get_tag_name(repository_name):
    try:
        request = requests.get(f"https://api.github.com/repos/{repository_name}/releases/latest")
        if request.status_code == 200:
            return request.json()["tag_name"]
        else:
                raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
    except:
        raise Exception("Failed to make request")


def check_for_updates(v):
    repository = "natecraddock/page-zipper"
    tag = get_tag_name(repository)

    # Strip text
    tag = tag[1:]
    version = float(tag)

    # If latest version is greater than current version
    if version > v:
        print("Update found!")
        result = messagebox.askyesno("Updates Found", f"An updated version of Page Zipper has been found (v{v}), would you like to download the update?")

        if result:
            print("Updating")
            webbrowser.open(f"https://www.github.com/{repository}/releases/latest")
        else:
            print("Not updating")


if __name__ == "__main__":
    check_for_updates(1.2)
