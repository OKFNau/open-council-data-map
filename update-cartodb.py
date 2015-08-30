# Updates dataset counts in Open Council Data map, using CKAN and CartoDB APIs.

from cartodb import  CartoDBAPIKey, CartoDBException
import ckanapi, re,requests,sqlite3, csv

# You must create settings.py, with your API key and CartoDB subdomain.
import settings



cl = CartoDBAPIKey(settings.cartodb_api_key, settings.cartodb_domain)

datagovau = ckanapi.RemoteCKAN('http://data.gov.au', user_agent='opencouncildata.org')

orgs = cl.sql("select cartodb_id, data_portal_url, datasets from lga_datasets where data_portal='data.gov.au'")['rows']

conn = sqlite3.connect('lgas.db')
cur = conn.cursor()
try:
  cur.execute('DROP TABLE lga_datasets');
except:
  ''
  # Not a problem.
cur.execute('CREATE TABLE lga_datasets (lga varchar(100), datasets number);')



def updateDatasetCount(lga, datasets):
  cur.execute('INSERT INTO lga_datasets (lga, datasets) VALUES(?,?)', (org, num_datasets))

def writeCSV(cur):
  cur.execute('SELECT * from lga_datasets;')
  csv_path = "out.csv"
  with open(csv_path, "wb") as csv_file:
    csv_writer = csv.writer(csv_file)
    # Write headers.
    csv_writer.writerow([i[0] for i in cur.description])
    # Write data.
    csv_writer.writerows(cur)




for row in orgs:
  org = re.search('organization/([^/]+)/?$', row['data_portal_url']).group(1)

  # Warning: data.gov.au only returns first 10 datasets if using include_datasets=True.
  num_datasets = datagovau.action.organization_show(id=org, include_datasets=False)['package_count']

  print "%s: %d (was %d)" % (org, num_datasets, row['datasets'])
  
  #cl.sql("UPDATE lga_datasets SET datasets='%d' WHERE cartodb_id='%d'" % (num_datasets, row['cartodb_id']))
  updateDatasetCount(org, num_datasets)
  
melb_datasets = len(requests.get('http://data.melbourne.vic.gov.au/data.json').json()['dataset'])
#cl.sql("UPDATE lga_datasets SET datasets='%d' WHERE data_portal_url='http://data.melbourne.vic.gov.au'" % (melb_datasets))
updateDatasetCount('Melbourne',melb_datasets)

conn.commit()

writeCSV(cur)
conn.close()

