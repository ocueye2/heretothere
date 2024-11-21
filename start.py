import os
import sys
import cherrypy
import time
import shutil
import configparser
import qrcode
from io import BytesIO

config = configparser.ConfigParser()
config.read('htt.conf')
domain = str(config['DEFAULT']['domain'])
MAINTENANCE_INTERVAL_MINUTES = float(config['DEFAULT']['cleartime'])
port = int(config['DEFAULT']['port'])
maxfilesize = int(config['DEFAULT']['filesizemb'])
maxsizemb = str(maxfilesize)
maxfilesize = maxfilesize * 10 * 1024 * 1024

def popup(mesage,link="",file="popup.html"):
    out = load(file)
    out = out.replace("<popuphere>",str(mesage))
    out = out.replace("<linkhere>",str(link))
    return  out

def load(file):
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    
    
    with open(f"{path}/webpage/{file}") as f:
        out = f.read()
        if file == "index.html":
            out = out.replace("!MAXFILESIZEHERE!",str(maxsizemb))
        return out


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
            # test file size
            file_size = 0
            file.file.seek(0, os.SEEK_END)  # Seek to the end of the file
            file_size = file.file.tell()    # Get the current position (file size)
            file.file.seek(0)   #
            if file_size > maxfilesize:
                return  popup(f"This file is to large, max size is is {maxfilesize / 10,485,760}mb")

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

            return popup(ident,f"{domain}/download?code={ident}","upload.html")
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
            absolute_file_path = os.path.abspath(file_path)

            # Serve the file as a downloadable attachment
            return cherrypy.lib.static.serve_file(absolute_file_path, "application/octet-stream", "attachment")
        except Exception as e:
            return popup(f"An error occurred: {str(e)}")

    @cherrypy.expose
    def qrcode(self, link=None):
        if not link:
            raise cherrypy.HTTPError(400, "Bad Request: No link provided.")
        elif not domain in link:
            raise cherrypy.HTTPError(400, "Bad Request: No link provided.")

        # Generate the QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)

        # Create an image for the QR Code
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        buffered.seek(0)

        # Serve the image as PNG
        cherrypy.response.headers['Content-Type'] = 'image/png'
        return buffered.read()
        




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
    cherrypy.config.update({
                'server.socket_host': '0.0.0.0',  # Bind to all available network interfaces
                'server.socket_port': port,
                'log.screen': True,
                                    })

    cherrypy.quickstart(FileUploadApp(), "/", config)
