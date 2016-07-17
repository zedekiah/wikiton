from flask import url_for, redirect, render_template, request, abort
from wikiton.db import db, Page, PageHistory, Option, DoesNotExist
from argparse import ArgumentParser
from os.path import basename
from wikiton.app import app


@app.route('/')
def home():
    path = Option.get_value('main_page', 'main')
    lang = Option.get_value('default_lang', 'ru')
    return redirect(url_for('show_page', lang=lang, path=path))


@app.route('/wiki/options/')
def options():
    return render_template('options.html', options=Option.select())


@app.route('/<lang>/<path:path>/')
def show_page(lang, path=''):
    if len(lang) != 2 and lang not in ('ru', 'en'):
        path = lang + '/' + path
        lang = Option.get('default_lang', 'en')
        return redirect(url_for('show_path', lang=lang, path=path))

    try:
        page = Page.get(Page.path == path, Page.lang == lang)

        return render_template('page.html', page=page, title=page.title,
                               content=page.content_html)
    except DoesNotExist as e:
        app.logger.debug('Page "%s" does not exist. %s', path, e.message)
        return redirect(url_for('edit_page', lang=lang, path=path))


@app.route('/<lang>/<path:path>:edit/', methods=['GET', 'POST'])
def edit_page(lang, path):
    try:
        page = Page.get(path=path, lang=lang)
    except DoesNotExist:
        page = None

    if request.method == 'GET':
        if not page:
            page = Page(title=basename(path), path=path, lang=lang, content='')
        return render_template('edit.html',
                               title='Edit page "%s"' % page.title,
                               page=page)
    elif request.method == 'POST':
        page, _ = Page.get_or_create(lang=lang, path=path)
        page.content = request.form['content']
        page.title = request.form['title']
        page.save()
        PageHistory.create_from_page(page)
        return redirect(url_for('show_page', lang=lang, path=path))


@app.route('/<lang>/<path:path>:delete/', methods=["GET", "POST"])
def delete_page(lang, path):
    Page.delete().where(lang=lang, path=path).execute()
    return redirect(url_for('home'))


@app.route('/<lang>/<path:path>:move/', methods=["GET", "POST"])
def move_page(lang, path):
    try:
        page = Page.get(lang=lang, path=path)

        if request.method == 'GET':
            return render_template('move.html', page=page)
        else:  # POST
            page.path = request.form['path']
            page.save()
            return redirect(url_for('show_page', lang=lang, path=page.path))
    except DoesNotExist:
        abort(404)


@app.route('/<lang>/<path:path>:default/')
def make_main(lang, path):
    Option.set_value('main_page', path)
    return redirect(url_for('show_page', path=path, lang=lang))


def main(init_db=False, insert_defaults=False, debug=False):
    if init_db:
        db.connect()
        db.create_tables([Page, PageHistory, Option])
    if insert_defaults:
        Option.set_value('default_lang', 'ru')
        Option.set_value('main_page', 'main')
        Page.create(lang='ru', title='default_main', path='main',
                    content='Welcome to Wikitone')

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
