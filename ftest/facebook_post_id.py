import sys
from minet.facebook import post_id_from_url

CT_URL = "https://api.crowdtangle.com/post/%s?token=%s"

URLS = [
    "https://www.facebook.com/groups/277506326438568/permalink/319815378874329",
    "https://www.facebook.com/permalink.php?story_fbid=1354978971282622&id=598338556946671",
    "https://www.facebook.com/permalink.php?story_fbid=1611111632462822&id=100006920017953",
    "https://www.facebook.com/Sante.Nutrition.org/posts/1454663224647529",
    "https://www.facebook.com/bvoltaire.fr/posts/1381087101956645",
    "https://www.facebook.com/meilleurdesmondesoff/posts/1954103778253459",
    "https://www.facebook.com/meilleurdesmondesoff/posts/1806885356308636",
    "https://www.facebook.com/meilleurdesmondesoff/posts/1810737099256795",
    "https://www.facebook.com/bvoltaire.fr/posts/1381087101956645",
    "https://www.facebook.com/cequevouscachentlesmedias/posts/1188187031274557",
    "https://www.facebook.com/cequevouscachentlesmedias/posts/1146401278786466",
    "https://www.facebook.com/cequevouscachentlesmedias/posts/1399569903469601",
    "https://www.facebook.com/cequevouscachentlesmedias/posts/1344654302294495",
    "https://www.facebook.com/cequevouscachentlesmedias/posts/1642141075879148",
    "https://www.facebook.com/cequevouscachentlesmedias/posts/1391995717560353",
    "https://www.facebook.com/cequevouscachentlesmedias/posts/1636414523118470",
    "https://www.facebook.com/cequevouscachentlesmedias/posts/1245022468924346",
    "https://www.facebook.com/cequevouscachentlesmedias/posts/1461857323907525",
    "https://www.facebook.com/FLASHINFO11343066/posts/1250239335079022",
    "https://www.facebook.com/SYNERGIEFRANCAISE/posts/1524581257625272",
    "https://www.facebook.com/croaplus/posts/1813907755590757",
    "https://www.facebook.com/dordognefn24/posts/1830473427026569",
    "https://www.facebook.com/Debout.La.France.16/posts/459708937722519",
    "https://www.facebook.com/groups/US4MF/permalink/787216138752904/",
    "https://www.facebook.com/groups/695576960543188/permalink/2072659646168239",
    "https://www.facebook.com/DonaldDuck/posts/10158544709064277",
]


def work(url):
    print(url)
    full_id = post_id_from_url(url)

    print(full_id)

    if full_id is not None:
        print(CT_URL % (full_id, sys.argv[1]))

    print()


for url in URLS:
    work(url)
