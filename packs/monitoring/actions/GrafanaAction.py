from st2client.client import Client
from st2client.models import KeyValuePair
from st2common.runners.base_action import Action
from jinja2 import Environment, FileSystemLoader
import requests
from requests.auth import HTTPBasicAuth
import json
import subprocess
import logging
from datetime import datetime
import sys
import ecs_logging
from error import operationfailed
from packs.utility.actions.get_secret_vm import get_secret

error_code_value = "error.code"
error_message_value = "error.message"
application_value = 'application/json'
bearer_value = 'Bearer '
http_value = "https://"
error_api_value = "Error in API call to URL: "
refer_response_value = ". Refer response details"
api_path_value = "/api/datasources/"
file_path_value = " file: "
app_name = "Centralized Monitoring Framework"
project_path = "/opt/stackstorm/"
certfile = 'rootcacert.pem'
api_db_post = "/api/dashboards/db"

class GrafanaAction(Action):
    
    def __init__(self, **kwargs):
                self.logger = logging.getLogger("app")
                self.logger.setLevel(logging.DEBUG)
                handler = logging.StreamHandler(sys.stdout)
                handler.setFormatter(ecs_logging.StdlibFormatter())
                self.logger.addHandler(handler)
                self.logger_json = {
                        "tags": ["grafana","api","stackstorm"],
                        "labels": {"action": "grafana provision api"},
                        "business_unit": "R&D Tech",
                        "solution_group": "Emerging Tech, Architecture, & AI",
                        "product_family": "Quality Engineering and Design",
                        "PRODUCT": "DevSecOps",
                        "ENVIRONMENT": "Dev",
                        "APPLICATION_NAME": app_name, 
                        "APPLICATION_OWNER_POC": "Andrew.x.Dalmeny@gsk.com"
                }
    
    def logger_exception(self, stmt, error_message):
        self.logger_json[error_code_value] = ""
        self.logger_json[error_message_value] = error_message

        self.logger.exception(stmt, extra = self.logger_json)
    
    def logger_error(self, stmt, error_code, error_message):
        self.logger_json[error_code_value] = error_code
        self.logger_json[error_message_value] = error_message

        self.logger.error(stmt, extra = self.logger_json)

    def logger_info(self, stmt):
        self.logger_json[error_code_value] = ""
        self.logger_json[error_message_value] = ""

        self.logger.info(stmt, extra = self.logger_json)
    
    def get_secrets(self):
            #Block to read credentials of az service principal from stackstorm server
            try:
                sp_username = get_secret(app_name, "monitoring_sp_username")
                sp_password = get_secret(app_name, "monitoring_sp_password")
                sp_tenant = get_secret(app_name, "monitoring_sp_tenant")
                fa_pat = get_secret(app_name, "monitoring_fa_pat")
                mimir_ip = get_secret(app_name, "monitoring_mimir_server")
                api_token = get_secret(app_name, "monitoring_grafana_apikey")
                grafana_url = get_secret(app_name, "monitoring_grafana_endpoint")
                sdb_url = get_secret(app_name, "monitoring_search_db_url")
                repo_name = get_secret(app_name, "monitoring_grafana_repo")
                sdb_uid = sdb_url.split("/d/")[1].split("/search-dashboard")[0]
            except Exception as e:
                    self.logger_exception("ERROR when reading metadata secrets: ", str(e))
                    raise operationfailed("ERROR when reading metadata secrets: "+str(e))

            if (fa_pat is None or mimir_ip is None or api_token is None or grafana_url is None or sdb_url is None):
                    self.logger_exception("", "Secret variable(s) is not set. Please check metadat connection")
                    raise operationfailed('Secret variable(s) is not set. Please check metadata connection')

            cmd_list = ['az login --service-principal --username '+sp_username+' --password '+sp_password+' --tenant '+sp_tenant+' --allow-no-subscriptions',
            'az keyvault secret show --name "MonitoringGrafanaCert" --vault-name "RDMonitoringDevTestKV" --query value',
            'az logout']

            for command in cmd_list:
                code, out, err = self.run_command(command)
                if err != '' and 'warning' not in err.lower() and err!="b''":
                    raise operationfailed ("ERROR: "+ err)
                if 'az keyvault secret show' in command:
                    cacert = out.split("\\n")
                    with open(project_path+certfile, 'w') as cafile:
                        cafile.writelines( "%s\n" % line for line in cacert )
            
            return 0, fa_pat, mimir_ip, api_token, grafana_url, sdb_url, repo_name, sdb_uid

    def CreateTeam(self, team_name, ad_group_name, grafana_url, headers):
        #1. Create Team
        #Ref: https://grafana.com/docs/grafana/v9.0/developers/http_api/team/

        team_found = False

        url = http_value+grafana_url+"/api/teams"

        #POST /api/teams
        apidata = {
          "name": team_name
        }

        #Read "team_id" field from response into variable
        req = requests.post(url, json=apidata, headers=headers, verify=project_path+certfile)
        print(req.status_code)
        print(req.text)
        if req.status_code != 200 and req.status_code != 202:
            if req.status_code == 409:
                team_found = True
                url = "https://grafana-devtest.gsk.com/api/teams/search?query="+team_name
                req = requests.get(url, headers=headers, verify=project_path+certfile)
                result = req.json()
                team_id = result["teams"][0]["id"]
            else:
                print(apidata)
                print(req.text)
                self.logger_error(error_api_value+url, req.status_code, req.text)
                raise operationfailed(error_api_value+url+refer_response_value)
        if not team_found:
            result = req.json()
            team_id = result["teamId"]   
        
        #2. Add Bind DN
        #Ref: https://grafana.com/docs/grafana/v9.0/developers/http_api/external_group_sync/
        #POST /api/teams/teamID/members
        url= http_value+grafana_url+"/api/teams/"+str(team_id)+"/groups"
        groupdn = "CN="+ad_group_name+",OU=SG,OU=MIMPortal,OU=DirectoryServices,OU=Groups,DC=wmservice,DC=corpnet1,DC=com"
   
        apidata = {
          "groupId": groupdn
        }

        req = requests.post(url, json=apidata, headers=headers, verify=project_path+certfile)
        print(req.status_code)
        print(req.text)
        if req.status_code != 200 and req.status_code != 202:
            if req.status_code == 400 and req.json()["message"]=="Group is already added to this team":
                self.logger_info("Group already added to team")
            else:
                print(apidata)
                print(req.text)
                self.logger_error(error_api_value+url, req.status_code, req.text)
                raise operationfailed(error_api_value+url+refer_response_value)   
        return 0, team_id

    
    def CreateDatasource(self, data_source_name, headers, mimir_ip, clustername, grafana_url, sdb_uid):
        # Ref: https://grafana.com/docs/grafana/latest/developers/http_api/data_source/
        # Create new mimir datasource with clustername (tenant ID) in HTTP header
        url = http_value+grafana_url+"/api/datasources"
        apidata = {
            "name": data_source_name,
            "type": "prometheus",
            "url": "http://"+mimir_ip+"/prometheus",
            "access": "proxy",
            "jsonData": {
                 "httpHeaderName1": "X-Scope-OrgID"	  
	             },
            "secureJsonData": {
                 "httpHeaderValue1": clustername
                 }
        }

        req = requests.post(url, json=apidata, headers=headers, verify=project_path+certfile)
        print(req.status_code)
        print(req.text)
        if req.status_code not in (200, 202):
            print(apidata)
            print(req.text)
            self.logger_error(error_api_value+url, req.status_code, req.text)
            raise operationfailed(error_api_value+url+refer_response_value)
        result = req.json()
        ds_uid = result["datasource"]["uid"]
        ds_id = result["datasource"]["id"]

        url = 'https://'+grafana_url+'/api/dashboards/uid/'+sdb_uid

        req = requests.get(url, headers=headers, verify=project_path+certfile)
        print(req.status_code)
        result = req.json()
        if req.status_code not in (200, 202):
            print(req.text)
            self.logger_error(error_api_value+url, req.status_code, req.text)
            raise operationfailed(error_api_value+url+refer_response_value)
        
        for vars in result["dashboard"]["templating"]["list"]:
            if vars["name"]=="cluster":
                querystr=vars["query"]

        # Append ClusterName (tenant ID) to HTTP header of mimir joint-datasource, and update new value in vault (if not already present in header text)
        tenant_found = False
        if querystr == "select 'x' from dual":
            new_querystr = "select '"+clustername+"' from dual"
        else:
            if clustername not in querystr:
                new_querystr = querystr+" union all select '"+clustername+"' from dual"
            else:
                tenant_found = True
        
        if not tenant_found:
            sdb_template = json.dumps(result)
            sdb_new_template = sdb_template.replace(querystr, new_querystr)

            url = "https://"+grafana_url+api_db_post
            apidata = json.loads(sdb_new_template)
            req = requests.post(url, json=apidata, headers=headers, verify=project_path+certfile)
            print(req.status_code)
            if req.status_code not in (200, 202):
                print(apidata)
                print(req.text)
                self.logger_error("Error in API call to URL: "+url, req.status_code, req.text)
                raise operationfailed("Error in API call. URL: "+url+". Refer response details")

        print(ds_uid)
        return 0, ds_uid, ds_id

    def CreateFolder(self, folder_title, headers, grafana_url):
        #Ref: https://grafana.com/docs/grafana/latest/developers/http_api/folder/
        #Create new folder with AppName+Envname in title
        url = http_value+grafana_url+"/api/folders"

        apidata = {
            "title": folder_title
        }

        req = requests.post(url, json=apidata, headers=headers, verify=project_path+certfile)
        print(req.status_code)
        print(req.text)
        if req.status_code != 200 and req.status_code != 202:
            print(apidata)
            print(req.text)
            self.logger_error(error_api_value+url, req.status_code, req.text)
            raise operationfailed(error_api_value+url+refer_response_value)
        result = req.json()
        folder_id = result["id"]
        folder_uid = result["uid"]
        print(folder_id)
        return 0, folder_id, folder_uid
    
    def run_command(self, cmd):
                """_summary_

                Args:
                cmd (str): Shell script to run

                Returns:
                returncode (int)
                stdout (str)
                stderr (str)
                """
                proc = subprocess.Popen(cmd,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                shell = True
                )
                stdout, stderr = proc.communicate()

                return proc.returncode, stdout.rstrip().decode('ascii'), stderr.rstrip().decode('ascii')
    
    def generate_template(self, tmplt_vars, src, target, tmplt_path):
                
                #Read file data into string
                with open(tmplt_path+'/'+src, 'r') as file :
                    filedata = file.read()

                # Iterate through template json, replace "key" with "value"
                for key in tmplt_vars:
                    filedata = filedata.replace("{{ "+key+" }}", str(tmplt_vars[key]))

                # Write the resulting string to target file
                with open(tmplt_path+'/'+target, 'w') as file:
                    file.write(filedata)
                
                return 0
    
    def CreateDashboardJSON(self, grafana_url, sdb_url, datasource_uid, business_unit, solution_group, product_family, product_name, folder_id, fa_pat, clustername, repo_name):
                
                fa_usr = get_secret(app_name, "monitoring_fa_usr")
                grafana_branch = get_secret(app_name, "monitoring_grafana_branch")
                
                #Git clone grafana dashboard templates
                cmd_list = ['rm -rf qed-op-monitoring-framework-grafana',
                    'git clone -b '+grafana_branch+' https://'+fa_usr+':'+fa_pat+'@mygithub.gsk.com/gsk-tech/'+repo_name+'.git']
                tmplt_path = project_path+repo_name+'/dbtemplates'

                for command in cmd_list:
                        code, out, err = self.run_command(command)
                        if err != '' and 'warning' not in err.lower() and 'Cloning into' not in err:
                                self.logger_exception("COMMAND: ", err)
                                raise operationfailed ("ERROR: "+err+"\n COMMAND: "+command)

                #data json with format {"placeholder string to search for": "value to replace with"}
                # id will be null for first pass
                tmplt_vars = {
                        "grafana_url": grafana_url,
                        "ds_prometheus": datasource_uid,
                        "db_id": "null",
                        "business_unit": business_unit,
                        "solution_group": solution_group,
                        "product_family": product_family,
                        "product_name": product_name,
                        "clustername": clustername,
                        "folder_id": folder_id
                }

                #List of templates with common set of placeholders to replace
                tmplt_list = ['cluster_summary', 
                'nodes', 
                'pods']

                #Loop through template list, replace placeholders (source: *.json file) with target values (target: *_tmp.json file)
                try:
                    for tmplt in tmplt_list:
                        code = self.generate_template(tmplt_vars, tmplt+'.json' , tmplt+'_tmp.json', tmplt_path)
                except Exception as e: 
                    print ("ERROR WHEN CREATING FROM TEMPLATE: "+str(e)+file_path_value+tmplt+".json")
                    self.cleanup()
                    return 1

                #data json with format {"string to search for": "value to replace with"} for main dashboard
                tmplt_vars = {
                        "grafana_url": grafana_url,
                        "search_url": sdb_url,
                        "ds_prometheus": datasource_uid,
                        "db_id": "null",
                        "business_unit": business_unit,
                        "solution_group": solution_group,
                        "product_family": product_family,
                        "product_name": product_name,
                        "clustername": clustername,
                        "folder_id": folder_id
                }

                #Main dashboard template: replace placeholders (source: main.json file) with target values (target: main_tmp.json file)
                try:
                    code = self.generate_template(tmplt_vars, 'main.json' , 'main_tmp.json', tmplt_path)
                except Exception as e: 
                    print ("ERROR WHEN CREATING FROM TEMPLATE: "+e+file_path_value+tmplt+".json")
                    self.cleanup()
                    return 1
                
                return 0, tmplt_path, tmplt_list

    def CreateDashboard(self, headers, tmplt_path, tmplt_list, grafana_url):
        #Ref: https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/
        #Overall Steps: 1. Create the dashboard 2. Get ID of dashboard for subsequent updates
        #3. Get link of dashboard to update inter-dashboard links in the final step
        
        #Call to create Main dashboard, and get the resulting Link and ID into variables
        url = http_value+grafana_url+api_db_post

        apidata = open(tmplt_path+'/main_tmp.json', 'rb').read()
        req = requests.post(url, json=json.loads(apidata), headers=headers, verify=project_path+certfile)
        print(req.status_code)
        if req.status_code != 200 and req.status_code != 202:
            print(apidata)
            print(req.text)
            self.logger_error(error_api_value+url, req.status_code, req.text)
            raise operationfailed(error_api_value+url+refer_response_value)
        result = req.json()        
        main_db_url = result["url"]
        main_db_id = result["id"]

        dbdict = {}

        #Loop through template list, and create each dashboard, and copy resulting Link and ID variables into dictionary
        for tmplt in tmplt_list:
            apidata = open(tmplt_path+'/'+tmplt+'_tmp.json', 'rb').read()

            req = requests.post(url, json=json.loads(apidata), headers=headers, verify=project_path+certfile)
            print(req.status_code)
            if req.status_code != 200 and req.status_code != 202:
                print(apidata)
                print(req.text)
                self.logger_error(error_api_value+url, req.status_code, req.text)
                raise operationfailed(error_api_value+url+" Template: "+tmplt+refer_response_value)
            result = req.json()
            dbdict[tmplt] = [result["id"], result["url"]]

        #Return main dashboard link+ID, and sub-dashboard link+IDs
        return 0, main_db_url, main_db_id, dbdict
        
    def postDashboardUpdate (self, headers, main_db_url, main_db_id, dbdict, tmplt_path, grafana_url):
        #Ref: https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/
        #Note: all updates to a dashboard must contain the dashboard ID in request

        url = http_value+grafana_url+api_db_post

        #Build template vars JSON to replace sub-dashboard link placeholders in main dashboard template, 
        # and do the replacement
        tmplt_vars_str = "{\n"+'"db_id": '+str(main_db_id)+",\n"

        #Example: {"apiserver_url": "/d/abcdef/api-server"}
        for key in dbdict:
            tmplt_vars_str = tmplt_vars_str +'"'+ key+'_url": "' + dbdict[key][1]+'"'
            if key != list(dbdict.keys())[-1]:
                tmplt_vars_str = tmplt_vars_str + ",\n"
        
        tmplt_vars_str = tmplt_vars_str + "\n}"
        
        tmplt_vars = json.loads(tmplt_vars_str)

        try:
            code = self.generate_template(tmplt_vars, "main_tmp.json", "main_final.json", tmplt_path)
        except Exception as e: 
            print ("ERROR WHEN CREATING FROM TEMPLATE: "+e+" file: main_tmp.json")
            self.cleanup()
            return 1

        #Update main dashboard
        apidata = open(tmplt_path+'/main_final.json', 'rb').read()

        req = requests.post(url, json=json.loads(apidata), headers=headers, verify=project_path+certfile)
        print(req.status_code)
        if req.status_code != 200 and req.status_code != 202:
            print(apidata)
            print(req.text)
            self.logger_error(error_api_value+url, req.status_code, req.text)
            raise operationfailed(error_api_value+url+refer_response_value)

        #Iterate through template dict, declare tmplt vars JSON to replace main dashboard url in all 
        # sub-dashboards (cluster-overview link), do the replacement
        for key in dbdict:

            tmplt_vars = {
                "main_db_url": main_db_url,
                "db_id": dbdict[key][0]
            }

            try:
                code = self.generate_template (tmplt_vars, key+"_tmp.json", key+"_final.json", tmplt_path)
            except Exception as e: 
                print ("ERROR WHEN CREATING FROM TEMPLATE: "+e+file_path_value+key+"_tmp.json")
                self.cleanup()
                return 1
            
            apidata = open(tmplt_path+'/'+key+'_final.json', 'rb').read()
            
            req = requests.post(url, json=json.loads(apidata), headers=headers, verify=project_path+certfile)
            print(req.status_code)
            if req.status_code != 200 and req.status_code != 202:
                print(apidata)
                print(req.text)
                self.logger_error(error_api_value+url, req.status_code, req.text)
                raise operationfailed(error_api_value+url+". Template: "+key+refer_response_value)

        return 0

    def AddPermissions(self, team_id, folder_uid, grafana_url, headers, datasource_id):
        #Folder Permissions
        #Ref: https://grafana.com/docs/grafana/latest/developers/http_api/folder_permissions/
        url = http_value+grafana_url+"/api/folders/"+folder_uid+"/permissions"
         
        apidata={
        "items": [
          {
            "role": "Viewer",
            "permission": 1
          },
          {
            "role": "Editor",
            "permission": 2
          },
          {
            "teamId": team_id,
            "permission": 2
          }
        ]
        }

        req = requests.post(url, json=apidata, headers=headers, verify=project_path+certfile)
        print(req.status_code)
        print(req.text)
        if req.status_code != 200 and req.status_code != 202:
            print(apidata)
            print(req.text)
            self.logger_error(error_api_value+url, req.status_code, req.text)
            raise operationfailed(error_api_value+url+refer_response_value)
        
        #Datasource Permissions
        #Ref https://grafana.com/docs/grafana/latest/developers/http_api/datasource_permissions/
        
        url = http_value+grafana_url+api_path_value+str(datasource_id)+"/enable-permissions"

        req = requests.post(url, headers=headers, verify=project_path+certfile)
        print(req.status_code)
        print(req.text)
        if req.status_code != 200 and req.status_code != 202:
            print(req.text)
            self.logger_error(error_api_value+url, req.status_code, req.text)
            raise operationfailed(error_api_value+url+refer_response_value)

        url = http_value+grafana_url+api_path_value+str(datasource_id)+"/permissions"

        apidata = {
            "teamId": team_id,
            "permission": 2
        }
        
        req = requests.post(url, json=apidata, headers=headers, verify=project_path+certfile)
        print(req.status_code)
        print(req.text)
        if req.status_code != 200 and req.status_code != 202:
            print(apidata)
            print(req.text)
            self.logger_error(error_api_value+url, req.status_code, req.text)
            raise operationfailed(error_api_value+url+refer_response_value)

        return 0

    def SetHomeDashboard(self, team_id, main_db_id, grafana_url, headers):
        #Ref: https://grafana.com/docs/grafana/v9.0/developers/http_api/team/
        #PUT /api/teams/team_id/preferences
        
        url = http_value+grafana_url+"/api/teams/"+str(team_id)+"/preferences"
        
        apidata = {
          "theme": "",
          "homeDashboardId": main_db_id,
          "timezone": ""
        }

        req = requests.put(url, json=apidata, headers=headers, verify=project_path+certfile)
        print(req.status_code)
        print(req.text)
        if req.status_code != 200 and req.status_code != 202:
            print(apidata)
            print(req.text)
            self.logger_error(error_api_value+url, req.status_code, req.text)
            raise operationfailed(error_api_value+url+refer_response_value)
        return 0

    def cleanup(self):
        #Cleanup
        cmd_list = ['rm -rf qed-op-monitoring-framework-grafana',
        'rm '+project_path+certfile]
        for command in cmd_list:
            code, out, err = self.run_command(command)
            if err != '' and 'warning' not in err.lower():
                    self.logger_exception("COMMAND: ", err)
                    raise operationfailed ("ERROR: "+err+"\n COMMAND: "+command)


    # Main Function

    def run(self, business_unit, solution_group, product_family, product_name, team_name, env_name, clustername, ad_group_name):

        requests.packages.urllib3.disable_warnings()

        strteam_name = team_name.replace(' ','_')

        self.logger_info("Reading secrets")
        code, fa_pat, mimir_ip, api_token, grafana_url, sdb_url, repo_name, sdb_uid = self.get_secrets()

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+api_token
        }

        if code==0:
            self.logger_info("Creating Team")
            code = 1
            code, team_id = self.CreateTeam(strteam_name+'_'+env_name+'_TEAM', ad_group_name, grafana_url, headers)
        
        if code==0:
            self.logger_info("Creating Datasource")
            code = 1
            code, datasource_uid, datasource_id = self.CreateDatasource(clustername+'_DS', headers, mimir_ip, clustername, grafana_url, sdb_uid)

        if code==0:
            self.logger_info("Creating Folder")
            code = 1
            code, folder_id, folder_uid = self.CreateFolder(clustername+'_DASHBOARDS', headers, grafana_url)

        if code==0:
            self.logger_info("Creating Dashboard JSONs")
            code = 1
            code, tmplt_path, tmplt_list = self.CreateDashboardJSON(grafana_url, sdb_url, datasource_uid, business_unit, solution_group, 
                                product_family, product_name, folder_id, fa_pat, clustername, repo_name)

        if code==0:
            self.logger_info("Creating Dashboard")
            code = 1
            code, main_db_url, main_db_id, dbdict = self.CreateDashboard(headers, tmplt_path, tmplt_list, grafana_url)

        if code==0:
            self.logger_info("Post Dashboard Update")
            code = 1
            code = self.postDashboardUpdate(headers, main_db_url, main_db_id, dbdict, tmplt_path, grafana_url)

        if code==0:
            self.logger_info("Adding Permissions")
            code = 1
            code = self.AddPermissions(team_id, folder_uid, grafana_url, headers, datasource_id)
        
        if code==0:
            self.logger_info("Set Home Dashboard")
            code = 1
            self.SetHomeDashboard(team_id, main_db_id, grafana_url, headers)
        
        self.cleanup()
