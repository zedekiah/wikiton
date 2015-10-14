INSERT OR IGNORE INTO pages (lang, path, title, content) VALUES
  ('ru', 'default_main', 'Welcome to Wikitone', ''),
  ('ru', 'help', 'Wikitone help', '');

INSERT OR IGNORE INTO options (name, value) VALUES
  ('main_page', 'default_main'),
  ('default_lang', 'ru');