---
title: doctag
subtitle: Parsing boolean tag queries in Python.
author: Dan Turkel
date: June 10th, 2019
numbering: counter
aspectratio: 169
header-includes:
  - \usetheme[sectionpage = simple]{metropolis}
  - \usepackage{xcolor}

---

# Background

## Tags

A **tag** is a common form of metadata for organizing files (or **documents**).

Tags are a convenient supplement to a file system because they are not hierarchical like folders are.

Tags and documents have a **many-to-many** relationship: one document may have many tags, and one tag may be applied to many documents.

## Functionality

\begin{center}Tagging systems naturally motivate several additional actions beyond tagging and untagging:\end{center}

. . .

\vspace{0.4cm}

::::{.columns}
:::{.column}
show tags:

: display all tags for a given document

show docs:

: display all documents with a given tag
:::

. . .

:::{.column}

merge tags:

: replace all instances of `old` tag with `new`

delete tag:

: remove all usages of a given tag

clean doc:

: remove all tags from a given doc

. . .

\begin{description}
\color{blue}
\item[\color{blue} query docs:]
display all documents matching a tag query
\end{description}


:::
::::

## Data Structures: Database

One way to represent a set of tagged documents is through relational tables.[^1]

. . .

\vspace{0.2cm}

::::{.columns}
:::{.column width="33.3%"}
| docs      |
|-----------|
| doc\_id   |
| doc\_name |
:::
:::{.column width="33.3%"}
| tag\_map     |
|--------------|
| tag\_map\_id |
| tag\_id      |
| doc\_id      |
:::
:::{.column width="33.3%"}
| tags      |
|-----------|
| tag\_id   |
| tag\_name |
:::
::::

[^1]: http://howto.philippkeller.com/2005/04/24/Tags-Database-schemas/

## Data Structures: Database (Example)

::::{.columns}
:::{.column width="33.3%"}

\begin{center}docs\end{center}

| doc\_id | doc\_name           |
|---------|---------------------|
| 1       | movies.txt          |
| 2       | books.txt           |
| 3       | school.txt          |
:::
:::{.column width="33.3%"}
\begin{center}tag\_map\end{center}

| tag\_map\_id | tag\_id | doc\_id |
|--------------|---------|---------|
| 1            | 1       | 1       |
| 2            | 1       | 2       |
| 3            | 2       | 2       |
| 4            | 2       | 3       |
:::
:::{.column width="33.3%"}
\begin{center}tags\end{center}

| tag\_id | tag\_name |
|---------|-----------|
| 1       | list      |
| 2       | learning  |
:::
::::

\vspace{0.4cm}

We can tag/untag with `INSERT`/`DELETE`, delete tags or docs with `DELETE`, and show tags or docs `SELECT`. Merging tags can be done with a targeted `INSERT` followed by a `DELETE`, and building tag queries is simply a matter of building `WHERE` clauses for `SELECT` statements.

## Data Structures: Inverted Index

Another option for representing tagged documents is with an **index** and an **inverted index**.[^2] 

The index maps documents to tags, while the inverted index maps tags to documents.

Inverted indexes are used in NLP[^3] and search[^4] for quickly finding documents which contain specific user-defined content.

[^2]: <https://stackoverflow.com/a/24993487>

[^3]: <https://nlp.stanford.edu/IR-book/html/htmledition/a-first-take-at-building-an-inverted-index-1.html>

[^4]: <https://www.elastic.co/guide/en/elasticsearch/guide/current/inverted-index.html>

## Data Structures: Inverted Index (Example)

::::{.columns}
:::{.column}
\begin{center}index\end{center}

| doc        | tags           |
|------------|----------------|
| movies.txt | list           |
| books.txt  | list, learning |
| school.txt | learning       |
:::
:::{.column}
\begin{center}inverse index\end{center}

| tag      | docs                   |
|----------|------------------------|
| list     | movies.txt, books.txt  |
| learning | books.txt, school.txt  |
:::
::::

\vspace{0.4cm}

Tag and untag operations require writing to both indexes, but _show tags and show docs operations become trivial_. Deleting a tag is roughly the same process as in the tabular solution, and merging tags can be done by re-tagging in the index and unioning in the inverted index.

Querying has to be implemented through a series of intersections, unions, and negations.

# doctag

## doctag

::::{.columns}
:::{.column}
**doctag** is a Python library for building index/inverted index tagging systems and performing actions on those systems.

\vspace{0.2cm}

The library includes a `TagIndex` class which stores the index and inverted index and implements methods for tagging and retrieval.
:::
:::{.column}
**ultrajson**^5^ is used to (optionally) serialize and deserialize the `TagIndex` to disk _really fast_.

\vspace{0.2cm}

**boolean.py**^6^ is used to parse arbitrarily complex tag queries, like:

\begin{center}``(list and learning) or (not work)''\end{center}
:::
::::


\footnotetext[5]{https://github.com/bastikr/boolean.py}

\footnotetext[6]{https://github.com/esnme/ultrajson}

## 
