import csv
import sys
from tqdm import tqdm

from minet.facebook import FacebookMobileScraper
from minet.facebook.constants import (
    FACEBOOK_POST_CSV_HEADERS,
    FACEBOOK_POST_CSV_HEADERS_WITH_REACTIONS_TYPES,
)

scraper = FacebookMobileScraper(cookie="chrome")

# writer = csv.writer(sys.stdout)
# writer.writerow(FACEBOOK_POST_CSV_HEADERS)

# loading_bar = tqdm(desc="Scraping posts", unit=" posts")

# Danish: https://www.facebook.com/groups/186982538026569
# French: https://www.facebook.com/groups/444178993127747
# Langs: https://www.facebook.com/settings/?tab=language

# for post in scraper.posts("https://www.facebook.com/groups/186982538026569"):
#     loading_bar.update()
#     writer.writerow(post.as_csv_row())

# POSTS_FOR_USERS = [
#     "https://www.facebook.com/groups/186982538026569/posts/4310012825723499",
#     "https://www.facebook.com/groups/186982538026569/permalink/4300200843371364",
#     "https://www.facebook.com/groups/186982538026569/permalink/4276206219104160",
# ]

# for url in POSTS_FOR_USERS:
#     print(scraper.post_author(url))

writer = csv.writer(sys.stdout)
writer.writerow(FACEBOOK_POST_CSV_HEADERS_WITH_REACTIONS_TYPES)

loading_bar = tqdm(desc="Scraping posts", unit=" posts")

POSTS = [
    "https://m.facebook.com/story.php?story_fbid=pfbid02Ci6aWuuxRxm2Ky3X57AEFGHcgp21NUK57SMgYxUkFyho5tWxpY8GrnVEHXYgeuA3l&id=100064917002992&eav=Afbp7pgVbCzqTBY510CDlSeZs1hqbgpkXZ05r_pfOv6XPJLaJ2HG6c84k5QKzvg0JPw&refid=17&_ft_=encrypted_tracking_data.0AY-17VfXV0A9NEvRCW0Ex1MLtGh79KvJJiRJ0pXckkf2N8q_mM2lOkMma4bB2AiPhc5gecKQBA_KrS-QRc0PbRbbtD-0P_f1BpImViivM0zDvqwXAmqQUI73poHDlGKathTUJ2kStVwtH32L_YJdlRFLpR_ZxAq2RVX4jB2YeXfMRD1z6zExfy2NnnQ1wIZdbSGXl2rckSNz8JA4uc6JKhAriUGkqbQ6FC6Cc86Ef0p0mEjxanneqkWPXTxU76et5D1b156PA1j2YDgp-flfQTZO4bdwMVSi8Zh7Rk-s8wf2SxTeumW2gt9553wdWtK3-D1WfhK_H1KgHgNCAS14sv2FF7VrrMBEqT6xAIhJ0yu5v7-ec4WKlDQAsBMg-BU3sXiQD_VCbCzibxXVsV7dVir_fRsBFYxlLDDCJM9UuaV2cx5uJ_BVOdNkHfh-DvGRxldJNpni9iWiCdc_vILN3KmsYWUUW-vq9_xOftd-CJi8OR-sVhxafOhS9iMWWqfwzFsPOqFJPLyZ_CPf6b9ZX06syCYQ9n_xCjYGCmxMYlLxHZjl12Nf1SDIYJTVLYY3HSOn2ckNE30kmXA6UCeX8fbwhNuyqst8jH7q2qbirleu33coPG0cc-bj_u2sg-PLSoBU5FCbUJ1KDhqq9ehyhAOgrlZxkUF6FuKLPjt1oIz5pNtpqTNH0MZniKNZhzzdBu59GfZPtchR_Cks7GC8JCKmSLxrG7sjatMDghzAq0StsEZ-Sbpx0xDSMzJ4_N7Ig508IXGCbSEZBnRvVWDL2_NPw-bz1fKeMJhrroCzWmf2yTJXYyw6JAdZNI3A2dZcYr07WXpqFt8u_qJIn0LWbPN2Z2mzuvNLV0zvVgsjY7wuxU2-nQM_5BMBAWezVFmdqN8r-eCh9G9UWqjt7hY5ESKoBZhI4Vtw7CsFgXluoywXrLRSqD6R6G_yWgNQ2E7VLNDsJOZdK8CqXjt3mfznoqJtZtREf_ruC88Ekdys6v8TgxNkqLWDg6IzwbZWlUVB206lVzQYdAjKJMvcoeFyTWLY8EEVD0ZxeG1J3LYaZz5nOPV_Q_dIIgZbKx7YMmjHgYV713cnhfPZnNw401d64Q2oJsHH4hrw5S4uZCbEUufPLiYcwOm-jBXU5g_dsr0rm87cBF60p5ja49C2CpVhTeK_qLcvpPS2OYqivoOTH9xP5J4H6HM34oAvq_7HTxUktXMypqbEbWnKQiSRNg0zLxYosr1lOsoVciE-UesfChveYwnprQIWYdSub4_pCIGZjf0Odz4pBiBs-RONEVANVWHn3Cs_zyqwL9X0BPenb2JlI8Q0OR5bzjhEkyhwwXb12nSEVEjy7twT972zt9pNotG00h_LaSrrzadi0rPiv1Y1gNyl-Nv9FAcCveWDDNJdDMPIdtPynimCfK7AWudO9IlVsdE5PRAnIMFN9GYZxQ181vvEKhtMZrKpK7DBVEXTowFHrYXs7840bY9i7hCdIgMGYz4qccCpbj3_ppVDT78C5iuxx3-iiMiKt4QnHGhDbNQwoRJyx6InKYuuRD08wyiQNvywtGaZ5JcVvObIrG5W_W06e9174qLpNJMApLjygmCqLziu_AEmmjDm73DJ2NK5l6DcBHMHI8wpGQCH7Jo0t5RRtXDLzbbsE-_qPbN5FuR_N8JMQ6bqWN9dWrmf0Hd03pooaJWGpb1vyoe4bAoDoLpcJLVj1xbocFOQ-2voxHOPAYtk4kVMDf5u2dFNLzIJbJ4qSmKaF4kPiuElw0OmWBv30bAdUpRWY_lu0HWjgrKJf9rG0bNlEISguMXFaKmTtX_YhtOlTsIibmXdCONyxTDC241ZileZ74ULwbg4n9U_Ja4yQu5ErzOnLZVz_Hex3BcQyNxjgQZfim-np7F8sfFdVwbvoEH8bXHUcbE8jQ73yWYUEPGPjB7F5VBDhmuDY9jHZ7U-5DmaVS0SQzf3Tjg8lhIsUXT2GthgyZpiakekff9ErCOnqLFC3s2Ha-GaE-V3Tfa8fNhE8MtzqVgx5VG2iXYK-pv58Gcb_v3aPulPedBZFY9C_rOvJ3sCvpT0JaRjJ21e7rTqXS-KnIWtDN7J5dNI6BRgDWAdSH0BFqM4l589MP7DUkQHiMb9yPy4vP46o3xb38mCNc8puYYWVZ_3cqT7WlcEcNU8steOTuHC-lbBSJgwGMXlfcCK5q5SSateC-yBA28zHBkR502wUwRtztn_kx86AlB4DCnDGx_zB1INVoMJKet3T1pwMenjFbAWycIccEaBggeIN7eQy8-gJ9XnPrJ2mjwPnDIg8nR0Goxey5Ss87KDWfeRp2kE_rKZyDjBinNgqoivdAZl5Fv5jGTwztNWDyeJVl9SILy6Pir674-8_D5NaFdRo3aCamn7esKVoEpn_hQ7Ip16Aw4okwrcty8idkRAnuhRxOStBsTG3y_SMQ2v5pDloPoc1n9dB20YMNrMkFuduaUHKWnAn-UeaotFv_ebJD-_YmJI2WpuxNE_Tew&__tn__=%2AW-R&paipv=0#footer_action_list",
    "https://m.facebook.com/watch/?v=432814598951914&paipv=0&eav=AfbSEClMar9DCkcj9wVKQs5lBaoHq6S6Ix4ln9ZwLHYpWgmcF0JkIJ-77qs1sJp_vA8&_rdr",
    "https://m.facebook.com/watch/?v=448540820705115",
    "https://m.facebook.com/permalink.php?story_fbid=pfbid02mrrGB5n3JaLAB9turZdjjobpjLQNFUp3Q12T8cSxTa6x5wGgAaGjHzagAohkpybQl&id=136164895246",
    "https://m.facebook.com/permalink.php?story_fbid=pfbid02R7FCHUqsjyh1PBGGiLpjBWNTNopMbZB4LYTsfQAwcrUrsXYswbA6Z3f5bXkT6S6il&id=100057466090848",
    "https://www.facebook.com/groups/186982538026569/posts/4310012825723499",
    "https://www.facebook.com/SciencesPo/posts/pfbid0Kx1asPmZSa24AHpiBP1SrYfkSZPnEC9KmrEesgRVQ5LqVpVvrgnzpHAmrV3m2boul?__cft__[0]=AZW65NoV0gJjHouoc3_uQOf3kpMCJE7ohdFlOWMbWD_vqlSkTZNNiXDfF5M-UtQMhxfIK8yHsDIWXDUS_vs303wnTQ8aiJBnY2_3AKDCP_WgqdOA14LXQPjivNcZXNObdbzjr9Nd-j-qPavvXrNa4SK4qn4tU0gCRMNsctpQeRsZTLvLwhucC7-3DqS9VufbPOs&__tn__=%2CO%2CP-R",
]

for url in POSTS:
    loading_bar.update()
    post = scraper.post(url)
    writer.writerow(post.as_csv_row())
