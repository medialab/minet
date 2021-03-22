# Joining 2 CSV files by urls

* [Use case](#use-case)
* [Basic minet url-join usage](#basic-minet-url-join-usage)
* [Keeping only certain columns from first file in final output](#keeping-only-certain-columns-from-first-file-in-final-output)
* [What to do when entities are symbolized by multiple urls](#what-to-do-when-entities-are-symbolized-by-multiple-urls)
* [How to do the same thing in python](#how-to-do-the-same-thing-in-python)
* [The difficulty of joining files by urls](#the-difficulty-of-joining-files-by-urls)

## Use case

In this guide I will show you how to use `minet`'s command line interface to "join" or "reconcile" (i.e. match lines from both files) two CSV files containing urls.

The usecase is the following: let's say on the one hand you are interested by online media websites and you have a CSV file listing those medias along with some useful metadata:

| id    | homepage                        | media            | politics |
|-------|---------------------------------|------------------|----------|
| 1     | https://www.lemonde.fr          | lemonde          | center   |
| 2     | https://www.lefigaro.fr         | lefigaro         | right    |
| 3     | https://www.liberation.fr       | liberation       | left     |
| 4     | https://www.lemonde.fr/economie | lemonde-business | right    |
| ...   | ...                             | ...              | ...      |

On the other hand, you collected many tweets while researching some subject. And sometimes those tweets may mention urls. As such, to study how Twitter users are referencing your list of online medias, you created a second CSV file such as each line is representing one Twitter user mentioning a given url in one of their tweets. It could look like this:

| tweet_id | twitter_user | url                                                             |
|----------|--------------|-----------------------------------------------------------------|
| 1        | @johnjohn    | https://www.lemonde.fr/planete/article/2021/02/23/covid...      |
| 2        | @jackie      | https://www.lefigaro.fr/flash-actu/le-zoo-de-lille...           |
| 3        | @mary        | https://www.liberation.fr/societe/sante/apres-la-vaccination... |
| ...      | ...          | ...                                                             |

But now if you want to be able to answer whether your users share more right-wing or left-wing media articles, for instance, you will need to find a way to match lines from your second file to the correct ones from the first one so we can obtain this result in the end:

| tweet_id | twitter_user | url                                                             | politics |
|----------|--------------|-----------------------------------------------------------------|----------|
| 1        | @johnjohn    | https://www.lemonde.fr/planete/article/2021/02/23/covid...      | center   |
| 2        | @jackie      | https://www.lefigaro.fr/flash-actu/le-zoo-de-lille...           | right    |
| 3        | @mary        | https://www.liberation.fr/societe/sante/apres-la-vaccination... | left     |
| ...      | ...          | ...                                                             | ...      |

## Basic minet url-join usage

Fortunately `minet` can help you to do all this from the comfort of the command line (note that doing so correctly is not completely straightforward and you can read more about it [at the end of this document](#the-difficulty-of-joining-files-by-urls) if you wish).

```bash
minet url-join homepage medias.csv url tweets.csv > joined.csv
```

Do so and you will get a `joined.csv` file with as many lines as `tweet.csv` but with 4 new columns `id`, `media`, `homepage` and `politics`, filled with relevant info from the `medias.csv` file. As such this can be thought as a `RIGHT JOIN` where the "right" table is `tweet.csv`.

The order in which the arguments are to be given can be hard to remember, so be sure to try `minet`'s help before doing things in reverse:

```bash
minet url-join -h
```

and it will remind you that you need to provide:

1. the name of the column containing urls symbolizing your "entities" in the CSV file to index
2. the path to the CSV file to index
3. the name of the column containing urls you need to match in the second CSV file
4. the path to this second CSV file

## Keeping only certain columns from first file in final output

In some cases, you may want to avoid copying all the columns from the first file into the second one when matching. If so, you can use the `-s/--select` flag to indicate which columns to keep from first file in the final output:

```bash
minet url-join homepage medias.csv url tweets.csv -s id,media > joined.csv
```

will produce:

| tweet_id | twitter_user | url                                                             | id  | media      |
|----------|--------------|-----------------------------------------------------------------|-----|------------|
| 1        | @johnjohn    | https://www.lemonde.fr/planete/article/2021/02/23/covid...      | 1   | lemonde    |
| 2        | @jackie      | https://www.lefigaro.fr/flash-actu/le-zoo-de-lille...           | 2   | lefigaro   |
| 3        | @mary        | https://www.liberation.fr/societe/sante/apres-la-vaccination... | 3   | liberation |
| ...      | ...          | ...                                                             | ... | ...        |

or if you are only interested on those media's politics:

```bash
minet url-join homepage medias.csv url tweets.csv -s politics > joined.csv
```

and you will get:

| tweet_id | twitter_user | url                                                             | politics |
|----------|--------------|-----------------------------------------------------------------|----------|
| 1        | @johnjohn    | https://www.lemonde.fr/planete/article/2021/02/23/covid...      | center   |
| 2        | @jackie      | https://www.lefigaro.fr/flash-actu/le-zoo-de-lille...           | right    |
| 3        | @mary        | https://www.liberation.fr/societe/sante/apres-la-vaccination... | left     |
| ...      | ...          | ...                                                             | ...      |

Also, for clarity and if you want to avoid having two columns with the same name (for instance if your `tweet_id` column was also called `id`), you can use the `-p/--match-column-prefix` flag to add a prefix to the first file's columns like so:

```bash
minet url-join homepage medias.csv url tweets.csv -s id -p media_ > joined.csv
```

and you will get:

| tweet_id | twitter_user | url                                                             | media_id  |
|----------|--------------|-----------------------------------------------------------------|-----|
| 1        | @johnjohn    | https://www.lemonde.fr/planete/article/2021/02/23/covid...      | 1   |
| 2        | @jackie      | https://www.lefigaro.fr/flash-actu/le-zoo-de-lille...           | 2   |
| 3        | @mary        | https://www.liberation.fr/societe/sante/apres-la-vaccination... | 3   |
| ...      | ...          | ...                                                             | ... |

## What to do when entities are symbolized by multiple urls

Often you will find that a single url is not enough to delimit an interesting "entity" you would want to study as a whole. For instance, you may want to assert that any url of a tweet posted by Le Monde's Twitter account should be associated to the media, as well as any article. But to do so, Le Monde's homepage is not sufficient as you will now require at least two urls to symbolize the borders of your entity: https://www.lemonde.fr/ and https://twitter.com/lemondefr.

So that both those urls:

* https://www.lemonde.fr/pixels/article/2021/02/23/jeu-video-entre-suite-et-reedition-le-retour-sur-le-devant-de-la-scene-de-diablo_6070953_4408996.html
* https://twitter.com/lemondefr/status/1364248725661564928

can be matched to this same "Le Monde" entity.

This is not an uncommon approach and multiple tools, such as our web crawler [Hyphe](https://hyphe.medialab.sciences-po.fr/) will keep multiple url prefixes per entity.

The most natural way to handle this is of course to have multiple lines per media in our first file like so:

| id  | prefix                        | media   | politics |
|-----|-------------------------------|---------|----------|
| 1   | https://www.lemonde.fr        | lemonde | center   |
| 1   | https://twitter.com/lemondefr | lemonde | center   |
| ... | ...                           | ...     | ...      |

As such, the same metadata can be accessed through different urls.

But you may also prefer keeping both urls in the same CSV line and to do so, people often tend to keep them in a single cell, separated by a specific character such as `|`, `,` or just a simple space, for instance.

To handle this, `minet` can be told to consider a CSV column as separated by this special character so that you can represent your entities thusly:

| id  | prefixes                                             | media   | politics |
|-----|------------------------------------------------------|---------|----------|
| 1   | https://www.lemonde.fr https://twitter.com/lemondefr | lemonde | center   |
| ... | ...                                                  | ...     | ...      |

You can then use the `--separator` flag to do tell `minet` to consider the `prefixes` column as able to contain multiple values:

```bash
minet url-join prefixes medias.csv url tweets.csv --separator " " > joined.csv
```

## How to do the same thing in python

To join two files based on url, `minet` uses its sister library [`ural`](https://github.com/medialab/ural) under the hood.

The first thing you need to do is to index your first file's lines in a [`LRUTrie`](https://github.com/medialab/ural#LRUTrie) or [`NormalizedLRUTrie`](https://github.com/medialab/ural#NormalizedLRUTrie), before using it to match the second file's lines like so:

```python
import csv
from ural.lru import NormalizedLRUTrie

# 1. Indexing our medias by url in a trie
trie = NormalizedLRUTrie()

with open('medias.csv') as f:
  for line in csv.DictReader(f):
    trie.set(line['homepage'], line)

# 2. Matching our url shares
with open('shares.csv') as f:
  for line in csv.DictReader(f):
    matched_line = trie.match(line['url'])

    if matched_line is None:
      print('Could not match %s' % line['url'])
    else:
      print('%s matched %s' % (line['url'], matched_line['media']))
```

Of course `minet` does a lot more things to handle some tricky cases and wrap this in a convenient package but the above logic remains the core of this whole operation.

---

<p align="center">⁂</p>

## The difficulty of joining files by urls

Matching urls correctly is not as easy as it first seems.

A naive approach could be to match urls if they share a common prefix, or based on their domain name, for instance. But as you will quickly discover when working with web data and more specifically urls, nothing is ever straightforward and everything requires a pinch of craft and tricks.

Indeed, urls are an incredibly messy way of conveying a sense of content hierarchy and you might stumble upon various issues preventing you from considering urls as sound hierarchical sequences such as subdomains, or web actors (such as a media) living on multiple domains and/or sites at once.

So, in order to correctly match urls, what you really need is first to reorder urls as meaningful hierarchical sequences of parts such as their domain, path, query, fragment etc. We personally use a method to do so that produce sequences we like to call LRUs, as a pun (a reverse URL). You can read more about this [here](https://github.com/medialab/ural#lru-explanation).

Equipped with this method producing truly hierarchical sequences from urls and a specialized [prefix tree](https://en.wikipedia.org/wiki/Trie), we can now match urls as being the longest matching prefix of the ones we indexed in our tree.

To illustrate this, let's consider we consider 3 online "medias":

1. Le Monde: https://www.lemonde.fr
2. Le Monde business section: https://www.lemonde.fr/economie/ (because we want to keep it as a separate entity in our aggregations)
3. Le Figaro: https://www.lefigaro.fr
4. Libération: https://www.liberation.fr

Then this url: https://www.lefigaro.fr/flash-actu/le-zoo-de-lille-accueille-un-jeune-panda-roux-male-pour-tenter-la-reproduction-20210223 should of course match `Le Figaro`

This url: https://www.lemonde.fr/idees/article/2021/02/23/macron-se-retrouve-face-a-un-double-defi-s-inventer-un-bilan-et-au-dela-tracer-des-voies-pour-2022_6070906_3232.html should match `Le Monde`

But this next url: https://www.lemonde.fr/economie/article/2021/02/23/les-lits-inexploites-mal-persistant-du-tourisme-de-montagne_6070899_3234.html should match `Le Monde business` and not `Le Monde`!

Finally, note that in our current example, the https://www.mediapart.fr/journal/france/180321/les-gobelins-une-institution-royale-l-heure-neoliberale url should not match anything.

On top of this, you can sprinkle other issues related to url having parts which are not useful to determine whether they point to the same resource or not (such as `www`, `http` vs. `https` or those pesky `?xtor` query items you can easily find attached to urls found on the web so SEO people can track what you do and where you come from...) and you have yourself quite a challenge if you want to reliably join files by the urls they contain.

But fortunately, `minet` sister library [`ural`](https://github.com/medialab/ural) offers many way to alleviate those issues and we of course leverage those for you when joining files by url from the command line.
