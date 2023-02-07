

# Analize Twitter Audiences

With the changes in organic search it has never been more important to understand who the influencers are in you target market.


We use this code to analize the accounts on Twitter that are in the Niche Site space (aka organic content sites monetized with ads and affilaite)


## Code

[extract-and-analyze-twitter-audience.ipynb](https://github.com/FrontAnalyticsInc/data-winners/blob/main/analysis-audience-twitter/extract-and-analyze-twitter-audience.ipynb)


## Methodology

See this Tweet for the announcement and for reference: 
https://twitter.com/alton_lex/status/1623082624465133568

Steps:

1) Create a 'seed' list of users that have a clean list of people they follow

2) Aggregate all the people this 'seed' lists follows => Call the top one's influencers

3) for each influencer we pull who they follow

4) Aggregate these lists into what we are calling who influences the influencers.



## Reference

Getting started: https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api

Sample Code: https://github.com/twitterdev/Twitter-API-v2-sample-code