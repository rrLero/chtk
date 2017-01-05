drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null,
  'date_of_article' text not null,
  'images' BLOB null
);
