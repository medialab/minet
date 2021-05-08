# Downloading images associated with a given hashtag on Twitter

Let's say we are interested in images being shared on tweets containing the [#saccageparis](https://twitter.com/hashtag/saccageparis) hashtag and that we need to download them to understand how this hashtag might be leveraged by different categories of actors.

This specific French example is interesting because it's a good example of how a hashtag initially fomented by right-wing activists can be repurposed through sarcasm and hijacking, as it is now used to mock those activists or redirect the discourse toward issues like urban planning and public transportation.

It is similar, in a sense, to what happened with "proud boys" tweets in Canada and the K-Pop fans flooding racist hashtags during the BLM movements.

So let's see how `minet` could help us achieve our goal efficiently.

## Summary

* [Scraping the relevant tweets](#scraping-the-relevant-tweets)
* [Downloading the images](#downloading-the-images)
* [Scaling up](#scaling-up)

## Scraping the relevant tweets

In order to retrieve the relevant tweets, we need to be able to formulate a query on Twitter's search engine that will only return tweets:

1. containing the `#saccageparis` hashtag and
2. containing at least an image.

Fortunately, writing such a query is fairly simple and it would look like this:

```
#saccageparis filter:images
```

Let's check on Twitter's public search that our query actually returns what we are looking for: [https://twitter.com/search?q=%23saccageparis%20filter%3Aimages&src=typed_query&f=live](https://twitter.com/search?q=%23saccageparis%20filter%3Aimages&src=typed_query&f=live)

Now we can give this query to minet in order to scrape those tweets like so:

```bash
minet twitter scrape tweets "#saccageparis filter:images" --limit 500 > tweets.csv
```

Notice how I am using a `--limit` for the time being because Twitter might return millions of tweets for some queries and for now we just want to make sure our methodology is actually working.

## Downloading the images

Now that we have scraped some tweets, we should have a CSV file containing all their relevant metadata.

In this metadata, we will find, in the `media_urls` column, a list of image urls separated by a `|` like so:

```
https://pbs.twimg.com/media/E03RN41XMAIeA4w.jpg|https://pbs.twimg.com/media/E03RN4uWEAYaSS8.jpg
```

We can now use minet `fetch` command to download them all as fast as possible:

```bash
minet fetch media_urls tweets.csv \
  --separator "|" \
  -d images \
  --throttle 0 \
  --domain-parallelism 5 > report.csv
```

Let's decompose the above command to understand what it does:

* `minet fetch media_urls tweets.csv` means we want minet to read the `tweets.csv` file and then fetch, i.e. download, the urls found within the `media_urls` column.
* The `--separator "|"` part is us telling minet that the url column may contain multiple urls, instead of a single one, and that those will be separated by the `|` character.
* The `-d images` part means that we want to store the downloaded images in the `images` folder (relative to our current working directory).
* The `--throttle 0` part indicates minet that we don't want to wait between two requests on the same domain. By default, minet tries to wait a little bit between two requests on the same domain not to be too hard on servers and to avoid getting kicked. But here, `twitter.com` doesn't really care and can take the load.
* The `--domain-parallelism 5` part tells minet we can accept making multiple requests on the same domain at once. For the same reasons as with `--throttle`, minet tries by default to avoid making multiple concurrent requests on the same domain but `twitter.com` can take it. So here, we will always be downloading at least 5 images at once. Feel free to increase or decrease this number based on your bandwith and Twitter's tolerance.

So now, when the command finishes, we will have downloaded all the images and we will be able to peruse them in the `images` folder. In the meantime, and this is what the `> report.csv` file of the command means, minet will write a CSV report containing the original tweet metadata along with some information about the HTTP requests made while downloading the images. What's more, a `filename` column can be found in this report so we can trace the downloaded images back to the tweets on which they were shared.

## Scaling up

Finally, here are some advice if you need to scale up and, for instance, download the images of *all* the tweets containing your hashtag:

1. Remove or increase the `--limit` flag of minet `twitter scrape` command.
2. You should of course ensure that you have sufficient disk space to spare to store the images before doing so.
3. If you want to save some space, you can use minet `fetch` `--compress` flag to gzip the images. But note that you will lose the possibility to browse them easily (without scripting or using a proper application able to display compressed images).
4. You might want to set minet `fetch` `--timeout` flag to some high value like `180` (3 minutes) to be sure minet `fetch` won't timeout on some very large images or if your internet connection can be subject to hiccups.
5. Storing many (> tens of thousands) images in a single folder can be a bad idea on some filesystems. You can use the `--folder-strategy`, or `--filename-template` flag to partition images within subfolders if required. I recommend `--folder-strategy prefix-2` or `--folder-strategy prefix-4` in this case.
6. Twitter search lets you filter chronologically using the `since` and `until` operator. This can be useful to search a specific period in the past or partition your work into batches.
