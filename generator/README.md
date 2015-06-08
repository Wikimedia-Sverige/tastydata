#generator

Used to generate the menus and the json sources. The menus must live in the same directory
as `index.css`, `main.css`, `menu.js`, `code2langQ.json` and the `lib`
directory.

Create the jsons using something like `run(u'demodata.tsv', u'demomatches.tsv')`,
then create the pages using `run(u'demodata.json', u'demomatches.json', u'../test')`
