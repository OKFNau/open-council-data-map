# Updates dataset counts in Open Council Data map, using CKAN and CartoDB APIs.

from cartodb import  CartoDBAPIKey, CartoDBException
import ckanapi, re,requests,sqlite3, csv

# You must create settings.py, with your API key and CartoDB subdomain.
import settings

def updateDatasetCount(lga, datasets):
    cur.execute('INSERT INTO lga_datasets (lga, datasets) VALUES(?,?)', (lga, datasets))

def writeCSV(cur):
    cur.execute('SELECT * from lga_datasets;')
    csv_path = "out.csv"
    with open(csv_path, "wb") as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write headers.
        csv_writer.writerow([i[0] for i in cur.description])
        # Write data.
        csv_writer.writerows(cur)

def updateCkanCount(portal, endpoint, orgName=None):
    orgs = cl.sql("select cartodb_id, data_portal_url, datasets from lga_datasets where data_portal='%s'" % portal)['rows']
    #print orgs
    for row in orgs:
        ckan = ckanapi.RemoteCKAN(endpoint, user_agent='opencouncildata.org')
        ckan.get_only = True
        if orgName == None:
            org = re.search('organization/([^/]+)/?$', row['data_portal_url']).group(1)
            # Warning: data.gov.au only returns first 10 datasets if using include_datasets=True.
            try:
                num_datasets = ckan.action.organization_show(id=org, include_datasets=False)['package_count']
            except:
                print "ERROR with organisation %s. Did its endpoint change?" % org
                num_datasets = 0

        else:
            
            num_datasets = len(ckan.action.package_list())
            org = orgName # Bleh. Just trying to find a way to handle single-organisation CKANs.
        try:
            print "%s: %d (was %d)" % (org, num_datasets, row['datasets'])
        except TypeError:
            pass      
        cl.sql("UPDATE lga_datasets SET datasets='%d' WHERE cartodb_id='%d'" % (num_datasets, row['cartodb_id']))
        updateDatasetCount(org, num_datasets)

def updateSocrataCount(portal_url, city):
    try:
        num_datasets = len(requests.get(portal_url + '/data.json').json()['dataset'])
    except:
        print "ERROR with %s. Maybe an SSL problem?" % city
        num_datasets = 0
    print "%s (%s): %d datasets" % (city, portal_url, num_datasets)
    cl.sql("UPDATE lga_datasets SET datasets='%d' WHERE data_portal_url='%s'" % (num_datasets, portal_url))
    updateDatasetCount(city,num_datasets)



cl = CartoDBAPIKey(settings.cartodb_api_key, settings.cartodb_domain)

conn = sqlite3.connect('lgas.db')
cur = conn.cursor()
try:
    cur.execute('DROP TABLE lga_datasets');
except:
    ''
    # Not a problem.
cur.execute('CREATE TABLE lga_datasets (lga varchar(100), datasets number);')

print '*** data.brisbane.qld.gov.au ***'
updateCkanCount('data.brisbane.qld.gov.au', 'http://data.brisbane.qld.gov.au/data', 'Brisbane')
print '*** data.gov.au ***'
updateCkanCount('data.gov.au', 'http://data.gov.au')
print '*** data.sa.gov.au ***'
updateCkanCount('data.sa.gov.au', 'http://data.sa.gov.au/data')
print '*** Socrata ***'  
updateSocrataCount('http://data.melbourne.vic.gov.au', 'Melbourne')
updateSocrataCount('http://data.sunshinecoast.qld.gov.au', 'Sunshine Coast')
updateSocrataCount('http://data.act.gov.au', 'ACT')
# updateSocrataCount('http://mooneevalley.demo.socrata.com', 'Moonee Valley')

conn.commit()

writeCSV(cur)
conn.close()

