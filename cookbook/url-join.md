# Joining 2 CSV files by urls

## Use case

In this guide I will show you how to use `minet`'s command line interface to "join" (i.e. match lines from both files based on some condition) two CSV files containing urls.

The usecase is the following: let's say on the one hand you are interested by online media websites and that you have a CSV file listing those medias along with some useful metadata:

| id    | homepage                     | media      | politics |
|-------|------------------------------|------------|----------|
| 1     | https://www.lemonde.fr       | lemonde    | center   |
| 2     | https://www.lefigaro.fr      | lefigaro   | right    |
| 3     | https://www.liberation.fr    | liberation | left     |
| ...   | ...                          | ...        | ...      |

And on the other hand, you collected many tweets and sometimes those tweets may mention urls. As such, to see how users will reference online medias, you created a second CSV file such as each line is describing one Twitter user mentioning a given url in one of their tweets. It would look like this:

| tweet_id | twitter_user | url                                                             |
|----------|--------------|-----------------------------------------------------------------|
| 1        | @johnjohn    | https://www.lemonde.fr/planete/article/2021/02/23/covid...      |
| 2        | @jackie      | https://www.lefigaro.fr/flash-actu/le-zoo-de-lille...           |
| 3        | @mary        | https://www.liberation.fr/societe/sante/apres-la-vaccination... |
| ...      | ...          | ...                                                             |

Now, to be able to answer how users are sharing links from specific medias, you will need to match those two files so that your urls can be associated to the relevant media and its metadata as described by the first file.

## The difficulty of joining files using urls

An sensible approach would be to join both files based on the urls' domain name, but as you will quickly discover when working with web data and more specifically urls, it's not as easy as this. Indeed, urls are a messy way of conveying a sense of content hierarchy and you might quickly stumble upon issues (what about subdomains, what about a media living on more than one domain etc.).

So, in order to correctly match your urls and your media, what you really need is first to reorder urls as meaningful hierarchical sequences of tokens such as the url's domain, path, query etc. (which we personally chose to call LRUs as a pun, more about this [here](https://github.com/medialab/ural#lru-explanation)). Then you need to pair the urls of the second file with the ones "symbolizing" your medias in the first one so that this second url is the longest matching prefix of the first one.

For instance, let's say we have 3 "medias":

1. Le Monde: https://www.lemonde.fr
2. Le Monde business section (because we want to keep it as a separate entity in our aggregations): https://www.lemonde.fr/economie/
3. Le Figaro: https://www.lefigaro.fr

Then this url: https://www.lefigaro.fr/flash-actu/le-zoo-de-lille-accueille-un-jeune-panda-roux-male-pour-tenter-la-reproduction-20210223 should of course match `Le Figaro`

This url: https://www.lemonde.fr/idees/article/2021/02/23/macron-se-retrouve-face-a-un-double-defi-s-inventer-un-bilan-et-au-dela-tracer-des-voies-pour-2022_6070906_3232.html should match `Le Monde`

But this last url: https://www.lemonde.fr/economie/article/2021/02/23/les-lits-inexploites-mal-persistant-du-tourisme-de-montagne_6070899_3234.html should match `Le Monde business` and not `Le Monde`!

Finally, note that in our current example, the https://www.liberation.fr/societe/sante/pour-les-soignants-deja-piques-le-vaccin-est-une-precaution-en-plus-de-la-ceinture-et-des-bretelles-20210223_WO3XQZJLB5AYDDYVPCI5RS6QUA/ url should not match anything.

On top of this, you can sprinkle other issues related to url having parts which are not useful to determine whether they point to the same resource or not (such as `www` as a subdomain, the `http` vs. `https` or those pesky `xtor` like queries you can easily find attached to urls found on the web so SEO people can track what you do and where you come from...) and you have yourself quite a challenge if you want to reliably join two files such as ours, by the urls they contain.

## Basic minet url-join usage

That's when `minet` enters the stage to help you do so from the comfort of the command line (note that if you are not a CLI kind of person you can still script a similar behavior in python using our sister library [ural](https://github.com/medialab/ural)):

```bash
minet url-join homepage medias.csv url tweets.csv > joined.csv
```

Do so and you will get a `joined.csv` file having one line per line in `tweet.csv` with 4 new columns `id`, `media`, `homepage` and `politics`, that will be filled with relevant info from the `medias.csv` file.

The order in which the arguments are to be given can be hard to remember so be sure to try `minet`'s help before inverting things:

```bash
minet url-join -h
```

and it will remind you that you need to provide:

1. the name of the column containing urls symbolizing your "entities" in the CSV file to index
2. the path to the CSV file to index
3. the name of the column containing urls you need to match in the second CSV file
4. the path to this second CSV file

## Keeping only certain columns from first file in final output

In some case, you may want to avoid copying all the columns from the first file into the second one when matching. If so, you can use the `-s/--select` flag to indicate which column to keep from first file in the final output:

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

or if you are only interested to aggregate based on those media's politics only:

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

## What to do when entities are symbolized by multiple urls

Often you will find that a single url is not enough to delimit an interesting "entity" you would want to study as a whole. For instance, you may want to assert that any url of a tweet posted by Le Monde's Twitter account should be associated to the media, as well as any article. But doing so, Le Monde's homepage is not sufficient enough as you will now require at least two url prefix to symbolize the borders of your entity:

* https://www.lemonde.fr/
* https://twitter.com/lemondefr

So that both those urls:

* https://www.lemonde.fr/pixels/article/2021/02/23/jeu-video-entre-suite-et-reedition-le-retour-sur-le-devant-de-la-scene-de-diablo_6070953_4408996.html
* https://twitter.com/lemondefr/status/1364248725661564928

can be matched to this same "Le Monde" entity.

This is not an uncommon approach and multiple tools, such as our web crawler [Hyphe](https://hyphe.medialab.sciences-po.fr/) will keep multiple url prefixes per entity.

To handle this, `minet` can be told to consider a CSV column as separated by a special character (people typically use a space or `|` for urls) so that you can represent your entities thusly:

| id  | homepage                                             | media   | politics |
|-----|------------------------------------------------------|---------|----------|
| 1   | https://www.lemonde.fr https://twitter.com/lemondefr | lemonde | center   |
| ... | ...                                                  | ...     | ...      |

Just use the `--separator` flag to do so:

```bash
minet url-join homepage medias.csv url tweets.csv --separator " " > joined.csv
```
