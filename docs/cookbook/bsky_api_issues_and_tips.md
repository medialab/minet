# Bluesky API Issues/Tips
*This file purpose is to document issues and notable details related to the Bluesky API found during the development of the bsky formatting and normalizing tools within [Twitwi](https://github.com/medialab/twitwi/) and the `minet bsky` command within [minet](https://github.com/medialab/minet/). We assume it isn't exhaustive, and every new notable issue or even clarification on some already existing ones is very welcomed.*

## Issues/Tips related to Bluesky API in general

### **Tip** : App passwords
When using the `minet bsky` command, you need to be registered using [App passwords](https://bsky.app/settings/app-passwords). There is a rate limit for an app password of 3000 requests per 5 minutes (i.e. 600 requests per minute, or 10 requests per second). This limit is shared across all the commands using the same app password, and is almost never reached. However, if you plan to do a large number of requests, and due to the slowness of response, it is recommended to create multiple app passwords and use them in parallel (e.g. using `tmux` sessions), as the rate limit is only shared on the app password, not on the user identifier.

### **Issue/Tip** : Retrying on errors from the API
Sometimes, when doing too much requests in a short time, or when using some specific route with big quantities of data to retrieve, the Bluesky API raises errors. Minet bypass the most commons of the unpredictable ones by waiting and retrying after a short time:
- *ExpiredToken* (HTTP Status 400): Somehow happens after 2 hours on a request (which worked fine before). For now, it seems that it is raised when using [`app-bsky-feed-search-posts` route](https://docs.bsky.app/docs/api/app-bsky-feed-search-posts) on queries matching a very dense amount of posts in a short time range of publication. Associated Minet exception : `BlueskyExpiredToken`.
- *HTTP Statuses 502*: the most common error raised by the API when doing many requests in a short time. `minet bsky` retries automatically on this error.

[//]: # (TODO: find HTTP Status)
- *UpstreamFailure*: happens sometimes when doing many requests in a short time. Associated Minet exception : `BlueskyUpstreamFailureError`.

## Issues/Tips related to post payloads

### **Issue** : Wrong `lang` field value
The `lang` field of a post payload is supposed to correspond to the language of the post content. However, it appears that this field is not always correctly set. For example, some posts written in French have their `lang` field set to `en` (English) instead of `fr` (French) and vice versa.
Indeed, the language detection algorithm is active only when the text reach a certain length (115 characters according to our experiments), and even then, the user can choose not to have it applied. When not applied or when the text is too short, the `lang` field is set to the user preferred language, but the user can override it and set it to any value.

To illustrate this issue, we made a collection of all posts having the `lang` attribute set to `fr` (French) using the `minet bsky search-posts "lang:fr"` command. In this collection, we found that only about 72% of the 32,969,538 posts are actually written in French when detecting their language using [Lingua Rust language detection library](https://docs.rs/lingua/latest/lingua/) on the post content.

[//]: # (TODO: determine stats on:)
[//]: # (- which proportion of the posts in french are we missing using `lang:fr` query using the dataset of the bsky-fr collection)

As a workaround, it is recommended to use a language detection library on the post content to determine its language more accurately.

### **Tip** : Different types of publications on Bluesky
There are several types of publications on Bluesky, which might break your normalization process if you don't know them:
- Regular posts:
    - their url follows the pattern `https://bsky.app/profile/{user_handle or user_did}/post/{post_did}`
    - their uri follows the pattern `at://{user_did}/app.bsky.feed.post/{post_did}`
- Feeds: specialized news feeds that allow the user to choose the topics that interest them the most, rather than relying on a central algorithm that decides for them based on their activity
    - their url follows the pattern `https://bsky.app/profile/{user_handle or user_did}/feed/{feed_did}`
    - their uri follows the pattern `at://{user_did}/app.bsky.feed.generator/{feed_did}`
- Lists: user-created lists that can be add to their feed
    - their url follows the pattern `https://bsky.app/profile/{user_handle or user_did}/lists/{list_did}`
    - their uri follows the pattern `at://{user_did}/app.bsky.graph.list/{list_did}`
- Starter packs: predefined lists of users to follow (when creating a new account for example)
    - their url follows the pattern `https://bsky.app/starter-pack/{user_handle or user_did}/{starter_pack_did}`
    - their uri follows the pattern `at://{user_did}/app.bsky.graph.starterpack/{starter_pack_did}`

When normalizing Bluesky posts, it is recommended to check the `type` field of the post payload to determine the type of publication and handle it accordingly.

### **Tip** : Unique identifier of a post
The unique identifier of a regular post on Bluesky is its `uri` field, which follows the pattern `at://{user_did}/app.bsky.feed.post/{post_did}`.

### **Issue** : Personnalized links in post content
The users have the possibility to publish content on Bluesky from a personnal server, allowing them to personnalize the data of their posts, including link encoding and placement. Consequently, the links/mentions found in the `text` field of a post payload might be shifted when the alignement on the link/mention characters is not done properly, especially if the text contains emojis or special characters. For examples:
- [shifted mention](https://bsky.app/profile/snjcgt.bsky.social/post/3lpmqkkkgp52u)
- [shifted link](https://bsky.app/profile/ecrime.ch/post/3lqotmopayr23)
- [personnalized and shifted link](https://bsky.app/profile/radiogaspesie.bsky.social/post/3lmkzhvhtta22)
- [personnalized and shifted link](https://bsky.app/profile/sudetsoleil.bsky.social/post/3ljf3h74wee2m) where we can't possibly know what the user wanted to do

> Usually, [Twitwi](https://github.com/medialab/twitwi/) replaces in the original text the links by their real link (replacing some text by the link when having a personnalized link for example), but when having undecidable cases like the previous one, it doesn't replace anything at all.

## Issues/Tips related to user profile payloads

### **Tip** : Different user profile payload structures
There are two different structures for user profile payloads on Bluesky:
- The one retrieved using the [`app.bsky.actor.getProfiles` route](https://docs.bsky.app/docs/api/app-bsky-actor-get-profiles) (used by `minet bsky profiles` command) is the most complete one, containing all the fields of the user profile.
- The one retrieved using the [`app.bsky.graph.getFollowers`](https://docs.bsky.app/docs/api/app-bsky-graph-get-followers#responses)/[`app.bsky.app.getFollows`](https://docs.bsky.app/docs/api/app-bsky-graph-get-follows#responses) routes for example, which is a subset of the previous one, missing fields `banner`, `followersCount`, `followsCount` and `postsCount`.

## Issues/Tips related to specific Bluesky API routes

### [`app-bsky-feed-search-posts` route](https://docs.bsky.app/docs/api/app-bsky-feed-search-posts)
*[`minet bsky search-posts`](https://github.com/medialab/minet/blob/master/docs/cli.md#search-posts) is the Minet command using this route.*

#### **Tip** : Precision of the datetime timestamps
The datetime timestamps retrieved by the Bluesky API are precised to the microsecond. However, when using `since` and `until` args, the effective *precision is only up to the millisecond*. Indeed, when testing with timestamps differing only by microseconds, the results are the same as if the timestamps were rounded to the nearest millisecond.
> Consequently, in this document, when referring to "datetime" timestamps, we will consider that their precision is up to the millisecond.

#### **Issue** : Sorting of retrieved posts
The command retrieves posts sorted by `latest` ranking order. The [documentation of the `app-bsky-feed-search-posts` route](https://docs.bsky.app/docs/api/app-bsky-feed-search-posts) precises that when using `since` and `until` args, the user is "expected to use 'sortAt' timestamp, which may not match 'createdAt'", meaning that the datetime which they are basing their ranking order is this 'sortAt' timestamp. Still according to [their documentation](https://docs.bsky.app/docs/advanced-guides/timestamps#sortat), the `sortAt` timestamp is 'defined as the "earlier" of the `createdAt` and `indexedAt` timestamps', (where `createdAt` timestamp is "assumed to represent the original time of posting, but clients are allowed to insert any value", and `indexedAt` timestamp "generally represents the time the record was "first seen" by an API server").

Using `sortAt` timestamp prevent posts which have an artificial `createdAt` timestamp (e.g. set in the future) from appearing everytime at the start of the results of a search query. Even though it is smart, after some tests, it seems that the posts retrieved by the route are not always perfectly sorted by the `sortAt` timestamp, either using `since` and/or `until` or not. Indeed, this timestamp depends on the `createdAt` one, and we observed that in some cases, this value is artificial, which might be the source of the issue (cf their [indexation code](https://github.com/bluesky-social/indigo/blob/c5eaa30f683f959af20ea17fdf390d8a22d471cd/search/transform.go#L225)).

#### **Issue** : Paging
The [`app-bsky-feed-search-posts` route](https://docs.bsky.app/docs/api/app-bsky-feed-search-posts) appears to limit the number of results to 10,000 posts per query.
To work around this limitation, Minet uses **datetime range paging** when this limit is reached: it makes a new query with the `until` parameter adjusted to the `createdAt` timestamp of the oldest post retrieved so far, allowing it to collect posts that were published before those already collected.
However, due to this method, if there are more than 10,000 unique posts with the same datetime, we won't be able to get them all. Moreover, when reaching that limit and time paging, we noticed that Bluesky API doesn't return exactly the same 10,000 posts again: some new posts are found, but most are already seen, and most importantly it seems that there is no logic behind the order of these posts, meaning **we are for now unable to ensure we retrieve the exact same posts when executing the same command multiple times**... This issue is being investigated.

#### **Tip** : `since` and `until` args overwrite the ones in the query
When using `since` and/or `until` args of the `minet bsky search-posts` command, they overwrite the corresponding `since:` and/or `until:` parts of the query string when provided. For example, the following two commands are equivalent:
```bash
minet bsky search-posts "lang:fr since:2024-12-01T00:00:00.000Z" --since 2024-11-01T00:00:00.000Z > bsky-fr.csv
```
```bash
minet bsky search-posts "lang:fr" --since 2024-11-01T00:00:00.000Z > bsky-fr.csv
```
