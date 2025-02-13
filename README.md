# Here To There
## An easy way to transfer files
You know how dispite the fact that every device has internet acsess, it is imposable to share files.

Here to there is a open source, self hosted verson I made of send anywhere. 
It allows you to upload files and retreve them via a code to easily. solving the problem of how to transfer your files from one device to another.
I made it because all of the options eather have ads, only work on the lan, or cost on a subscription basis. A nas also seems overkill for a problem like this.

## To Run

(This is desined to be run on linux)

### linux
to run this program, make a venv virtual enviroment and run `pip install cherrypy qrcode pillow`,
edit `htt.conf` and then run `start.py`. 
### docker

just clone this repo, remote into the container, use nano to edit `htt.conf`, and restart the container


## ToDo
- [ ] make file ids use avalible random numbers
- [ ] Encrypt on drive

# for devs
## start.py
`start.py` contains all of the backend stuff. 

## uploads
The `uploads` folder contains all of the files being transfered

The uploads folders structure is as follows

- uploads
   - 1
     - file with id 1
   - 2
     - file with id 2

## webpage
this folder contains all of the html templates that htt uses. 
