DROP TABLE IF EXISTS pages;
CREATE TABLE pages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lang TEXT,
  path TEXT,
  title TEXT,
  content TEXT
);

DROP TABLE IF EXISTS options;
CREATE TABLE options (
  name TEXT PRIMARY KEY,
  value TEXT
);
