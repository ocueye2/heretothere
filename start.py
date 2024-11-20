import os
import sys
import cherrypy
import time
import shutil

def popup(mesage):
    out = load("popup.html")
    return  out.replace("<popuphere>",mesage)

def load(file):
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    with open(f"{path}/webpage/{file}") as f:
        return f.read()
# Maximum time in minutes before a file is removed
MAINTENANCE_INTERVAL_MINUTES = 1


def clear_cache():
    """
    Deletes files in the 'uploads' directory that have not been modified
    within the last MAINTENANCE_INTERVAL_MINUTES.
    """
    upload_dir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "uploads")
    print(upload_dir)
    if not os.path.exists(upload_dir):
        print("notfound")
        return  # If the directory doesn't exist, nothing to clean.

    for file in os.listdir(upload_dir):
        print(file)
        item_path = os.path.join(upload_dir, file)
        last_mod_time = os.path.getmtime(item_path)
        time_diff_minutes = (time.time() - last_mod_time) / 60

        if time_diff_minutes >= MAINTENANCE_INTERVAL_MINUTES:
            try:
                shutil.rmtree(item_path)
                print(f"Deleted {item_path}")
            except Exception as e:
                print(f"Error deleting {item_path}: {e}")
        else:
            print(f"File {file} is {time_diff_minutes:.2f} minutes old, not deleting.")


class FileUploadApp:
    upload_dir = "uploads/"  # Directory to save uploaded files

    def __init__(self):
        # Ensure the upload directory exists
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    @cherrypy.expose
    def index(self):
        # HTML form for file upload and file retrieval
        return load("index.html")

    @cherrypy.expose
    def upload(self, file):
        clear_cache()
        try:
            # Find the lowest unused number as the identifier
            existing_ids = set(int(folder) for folder in os.listdir(self.upload_dir) if folder.isdigit())
            ident = 1  # Start checking from 1
            while ident in existing_ids:
                ident += 1
            
            # Create the directory for the new upload
            upload_path = os.path.join(self.upload_dir, str(ident))
            os.makedirs(upload_path)
            file_path = os.path.join(upload_path, file.filename)

            # Save the file to the upload directory
            with open(file_path, "wb") as f:
                while chunk := file.file.read(8192):
                    f.write(chunk)

            return popup(f"File '{file.filename}' uploaded successfully! Your code is {ident}.")
        except Exception as e:
            return popup(f"An error occurred during upload: {str(e)}")

    @cherrypy.expose
    def download(self, code):
        try:
            # Check if the directory for the code exists
            download_path = os.path.join(self.upload_dir, code)
            if not os.path.exists(download_path) or not os.path.isdir(download_path):
                raise FileNotFoundError("Invalid code or file not found.")

            # Get the first file in the directory
            files = os.listdir(download_path)
            if not files:
                raise FileNotFoundError("No files found for this code.")

            file_path = os.path.join(download_path, files[0])
            absolute_file_path = os.path.abspath(file_path)  # Convert to absolute path

            # Serve the file as a downloadable attachment
            return cherrypy.lib.static.serve_file(absolute_file_path, "application/octet-stream", "attachment")
        except Exception as e:
            return popup(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    config = {
        "/": {
            "tools.staticdir.root": os.path.abspath(os.getcwd())
        },
        "/uploads": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": os.path.abspath("uploads"),
        }
    }

    cherrypy.quickstart(FileUploadApp(), "/", config)
