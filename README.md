## Open council data map updater
Updates dataset counts in Open Council Data map, using CKAN and CartoDB APIs.

Result: https://stevage1.cartodb.com/viz/ac41a874-7b34-11e4-ac15-0e4fddd5de28/map

See also: opencouncildata.org

Written by Steve Bennett, melbdataguru.tumblr.com, stevebennett.me, @stevage1
License: CC-BY AU 3.0

## Install

```
git clone https://github.com/OKFNau/open-council-data-map

cd open-council-data-map

# Add your CartoDB API key: 
echo "cartodb_api_key = '123456...'" > settings.py
echo "cartodb_domain = 'stevage1'" >> settings.py

# Of course, that's all assuming you have a table called lga_datasets formatted just like mine.

pip install cartodb ckanapi

python update-cartodb.py
```