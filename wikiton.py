from flask import Flask, url_for, redirect, render_template, request, abort
from argparse import ArgumentParser
from contextlib import closing
from creole import creole2html
from os.path import basename
from wikidb import WikiDB


app = Flask(__name__)


@app.route('/')
def home():
    with closing(WikiDB()) as db:
        page = db.get_main_page()
        return redirect(url_for('show_page',
                                lang=page['lang'],
                                path=page['path']))


@app.route('/wiki/options/')
def options():
    with closing(WikiDB()) as db:
        return render_template('options.html', options=db.get_options())


@app.route('/<path:path>/')
def show_page(path):
    db = WikiDB()
    lang = request.args.get('lang') or db.get_option('default_lang')
    page = db.get_page(path, lang)

    if not page:
        return redirect(url_for('edit_page', path=path))
    return render_template("page.html",
                           page=page,
                           title=page["title"],
                           content=creole2html(page["content"]))


@app.route('/<path:path>:edit/', methods=["GET", "POST"])
def edit_page(path):
    db = WikiDB()
    lang = request.args.get('lang') or db.get_option('default_lang')
    page = db.get_page(path, lang)
    if request.method == 'GET':
        if not page:
            page = dict(title=basename(path), path=path, content="")
        return render_template('edit.html',
                               title='Edit page "%s"' % page['title'],
                               page=page)
    elif request.method == 'POST':
        if page:
            db.update_page(page['id'], request.form['title'],
                           request.form['content'])
        else:
            db.add_page(lang, path, request.form['title'],
                        request.form['content'])
        return redirect(url_for('show_page', lang=lang, path=path))


@app.route('/<path:path>:delete/', methods=["GET", "POST"])
def delete_page(path):
    with closing(WikiDB()) as db:
        lang = request.args.get('lang') or db.get_option('default_lang')
        page = db.get_page(path, lang)
        if not page:
            abort(404)
        if request.method == 'GET':
            return render_template('delete.html', page=page)
        else:  # POST
            db.delete_page(path)
            return redirect(url_for('home'))


@app.route('/<path:path>:move/', methods=["GET", "POST"])
def move_page(path):
    with closing(WikiDB()) as db:
        lang = request.args.get('lang') or db.get_option('default_lang')
        page = db.get_page(path, lang)
        if not page:
            abort(404)

        if request.method == 'GET':
            return render_template('move.html', page=page)
        else:  # POST
            db.move_page(page['id'], request.form['path'])
            return redirect(url_for('show_page', path=request.form['path']))


def main(init_db=False, insert_defaults=False, debug=False):
    if init_db or insert_defaults:
        with closing(WikiDB()) as db:
            if init_db:
                with open('data/init.sql') as fd:
                    db.execute_script(fd.read())
            if insert_defaults:
                with open('data/defaults.sql') as fd:
                    db.execute_script(fd.read())
    else:
        app.run(debug=debug)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--init-db', default=False, action='store_true')
    parser.add_argument('--insert-defaults', default=False,
                        action='store_true')
    parser.add_argument('--debug', default=False, action='store_true')
    args = parser.parse_args()

    main(init_db=args.init_db, insert_defaults=args.insert_defaults,
         debug=args.debug)
