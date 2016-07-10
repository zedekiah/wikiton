DROP TABLE IF EXISTS pages;
CREATE TABLE pages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lang TEXT,
  path TEXT,
  title TEXT,
  content TEXT
);

DROP TABLE IF EXISTS page_history;
CREATE TABLE page_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  page_id INTEGER,
  timestamp INTEGER,
  title TEXT,
  content TEXT
);

DROP TABLE IF EXISTS options;
CREATE TABLE options (
  name TEXT PRIMARY KEY,
  value TEXT
);


