
# Free Python Scripts for Sitewide Link Quality



## About Me

Hi my name is Alton and I am a data scientist who now builds tools for SEO. You can find me on twitter @alton_lex where I share practical ways to accerlate the adoption of technology.


## About FatJoe.com

FatJoe.com is an SEO agency that is internatinally recognized for helping grow websites & brands with SEO & digital marketing services. 


For years FatJoe and team have used a variety of scripts, tech and manuall processes to bring the best value to every client. Scripts like these reperesnt their forward thinking and use of technology.



## About these free scripts

Joe (@joecowmanwd and Head of SEO @fatjoewho) reached out to me in January 2023 and we agreed to publish these as helpful tools for the SEO community.

See the full backstory here 


#### There are four use cases in total:

1) Ratio of URLs to Outbound Links

2) Pages published per year

3) Traffic/Pages Ratio

4) Sitemap Links compared to Indexed Links






# 1) Ratio of URLs to Outbound Links

### Objective:

To assess the quality of a domain as a backlink source by measuring how frequently they link to external sources in comparison with the amount of pages. 

### Example: 

A blog that has 100 articles but links to 2000 external sources would be sending 20 backlinks per article. This would no doubt dilute the efficacy of a backlink and could potentially indicate that a domain is operating solely to sell links, with minimal content quality.

### Manual alternative:

Find amount of URLs in sitemap via /sitemap.xml or Screaming Frog

Find amount of outbound links in SEMRush, ahrefs, or Screaming Frog 
Calculate ratio of Urls to outbound links

### Example - fatjoe.com:

130 URLs in sitemap (found from /sitemap.xml)

1419 outbound links (exported outbound domains report from SEMRush to a spreadsheet, then created a SUM of the column detailing number of links to provide total)








# 2) Pages published per year


### Objective:

To assess the quality of a domain as a backlink source by measuring how frequently pages are published on an annual basis.

### Example:

A blog was set up in 2020, and published 50 articles in one month, then published just 5 articles in 2021, and in 2022 published 145 articles within another single-month period. This is poor practice of content velocity and a low-quality method of content management which could potentially indicate spam activity to search engines. 

### Manual process:

Find domain age using any online tool
Find publish date of all URLs??
*May be better to assess on monthly basis than yearly?





# 3) Traffic/Pages Ratio

### Objective: 

To assess the quality of a domain as a backlink source by measuring how many pages are receiving traffic.

### Example: 

A blog that receives 1000 visitors per month, but has 10,000 articles. It is unlikely that a new article will rank and receive any traffic on this domain.

### Manual process:

Top Pages Report in ahrefs shows number of pages and total traffic
Calculate ratio of traffic to pages

### Example - fatjoe.com:

117 pages

8400 traffic p/m

8440 / 117 = 72 visitors per page p/m







# 4) Sitemap Links compared to Indexed Links

### Objective: 

To assess the quality of a domain as a backlink source by measuring how many pages in the sitemap are indexed

### Example: 

A blog with 1000 pages, but only 200 pages indexed, indicates low quality content, or at least technical SEO issues which could prevent indexation of a new article. 

### Manual process:

Append /sitemap.xml to the homepage URL to find number of pages in sitemap
If not visible in sitemap, use Screaming Frog
Google search the domain with ‘site:’ appended to the beginning and find number of results

### Example - fatjoe.com:

131 URLs in sitemap

138 Google results 

+7 results in index 
