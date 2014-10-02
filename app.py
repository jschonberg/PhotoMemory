import re
import requests
from collections import namedtuple
from flask import Flask, render_template, request

Image = namedtuple("Image", ["dl", "preview"])
app = Flask(__name__)

#Globals (TODO: replace with DB storage)
urls = []


class DropboxGallery(object):
    def __init__(self, URL):
        self.position = 0
        r = requests.get(URL)
        self.images = ([Image(x, y) for x, y in
                       zip(self._dlURLs(r.text), self._previewURLs(r.text))])
        self.title = self._title(r.text)
        print self.title

    def _title(self, text):
        title_re = re.compile('SharingModel\.init\("(.+?)",')
        return title_re.search(text).group(1)

    def _dlURLs(self, text):
        link_re = re.compile(r'"dl_url": "(.+?)",')
        return [x.group(1) for x in link_re.finditer(text)]

    def _previewURLs(self, text):
        link_re = re.compile(r'"gallery_thumb": "(.+?)",')
        return [x.group(1) for x in link_re.finditer(text)]

    def __iter__(self):
        return self

    def next(self):
        if self.position == len(self.images):
            self.position = 0
            raise StopIteration
        else:
            self.position += 1
            return self.images[self.position - 1]

    def __str__(self):
        return str(self.images)


#Routes
@app.route('/', methods=['GET', 'POST'])
def gallery():
    if request.method == 'POST':
        dbg = DropboxGallery(request.form['dbx_url'])
        urls.append(dbg)

    return render_template('gallery.html', galleries=reversed(urls))


if __name__ == '__main__':
    app.run(port=8000, debug=True, use_reloader=True)
