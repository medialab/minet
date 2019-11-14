# Fetching a bunch of urls from the web

Let's say you are interested in what urls are shared by some Twitter accounts and you suceeded in collecting them using a dedicated tool ([gazouilloire](https://github.com/medialab/gazouilloire) or [TCAT](https://github.com/digitalmethodsinitiative/dmi-tcat), for instance).

You now have a large bunch of urls shared by people and want to move on to the next step: what if we analyzed the text content linked by those urls to see what people are speaking about.

You will obviously need to download the pages before being able to do anything.

Let's use the `minet fetch` command to do so!

Being a diligent researcher, you decided to store the found url in a very simple [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) file:

| id | url                       |
|----|---------------------------|
| 1  | https://www.lemonde.fr    |
| 2  | https://www.lefigaro.fr   |
| 3  | https://www.liberation.fr |
