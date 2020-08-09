# India_Startup_Funding
India Startup Funding data exploration 

Exercise_Startup_Funding.py - source code of data extraction using webscarpping of site trak.in. Source code enough comments to get you started. 
Startup_funding.csv - extracted data file, still some cleanup is required which you can do manually by sorting column in excel reading software. 
Startup_funding_v3.csv - cleanedup final version of file which i used for data exploration. 

Some notes: 
0.Data read from source https://trak.in/india-startup-funding-investment-2015/
1.Some data manually copied from the site when beautifulsoup cannot read them right July 2015 36-45 rows  were missing
2. Cleaned up some rows from csv which had html tag. 
3. Manual cleanup of some extra rows which had only data for few columns 1 or 2
4. There was two names for same city like bangalore vs Bengaluru,  gurugram vs gurgoan, new delhi vs delhi, made them uniform.
5. Inconsistency in date format, some rows you see as 03/02/2012(dd/mm/yyyy) and some you see 1/12/2013 or 21/4/2016 or some random numbers, changed all of them to dd/mm/yyyy format.
6. Some tables had only 7 or 8 columns, I have filled them with respective column names, though i have ignored them during plotting. 



