
# Updates dataset counts in Open Council Data map, using CKAN and CartoDB APIs.
# Result: https://stevage1.cartodb.com/viz/ac41a874-7b34-11e4-ac15-0e4fddd5de28/map

# Dependencies:
# pip install cartodb ckanapi


from cartodb import  CartoDBAPIKey, CartoDBException
import ckanapi, re

# You must create settings.py, with your API key and CartoDB subdomain.
import settings

cl = CartoDBAPIKey(settings.cartodb_api_key, settings.cartodb_domain)

datagovau = ckanapi.RemoteCKAN('http://data.gov.au', user_agent='opencouncildata.org')

orgs = cl.sql("select cartodb_id, data_portal_url, datasets from lga_datasets where data_portal='data.gov.au'")['rows']

for row in orgs:
  org = re.search('organization/([^/]+)/?$', row['data_portal_url']).group(1)

  # Warning: data.gov.au only returns first 10 datasets if using include_datasets=True.
  num_datasets = datagovau.action.organization_show(id=org, include_datasets=False)['package_count']

  print "%s: %d (was %d)" % (org, num_datasets, row['datasets'])
  
  cl.sql("UPDATE lga_datasets SET datasets='%d' WHERE cartodb_id='%d'" % (num_datasets, row['cartodb_id']))
  