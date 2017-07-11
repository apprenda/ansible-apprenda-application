#!/usr/bin/python

from email.header import Header
from ansible.module_utils.basic import AnsibleModule
import requests

def authenticate(url, user, password, tenant):
    auth_url = "{0}/authentication/api/v1/sessions/developer".format(url)
    auth_data = {
        'username': user,
        'password': password,
        'tenant': tenant
    }
    resp = requests.post(auth_url, verify=False, json=auth_data)
    resp_json = resp.json()
    return resp_json['apprendaSessionToken']

def list_apps(authToken, url):
    apps_url = "{0}/developer/api/v1/apps".format(url)
    resp = requests.get(apps_url, verify=False, headers=authToken)
    return resp.json(), 0

def get_app_info(authToken, url, alias):
    apps_url = "{0}/developer/api/v1/apps/{1}".format(url, alias)
    resp = requests.get(apps_url, verify=False, headers=authToken)
    return resp.json(), 0

def get_version_info(authToken, url, alias, version_alias):
    version_url = "{0}/versions/{1}/{2}".format(url, alias, version_alias)
    resp = requests.get(version_url, verify=False, headers=authToken)
    return resp.json(), 0

def create_app(authToken, url, name, alias, desc):
    apps_url = "{0}/developer/api/v1/apps".format(url)
    apps_data = {
        'name': name,
        'alias': alias,
        'description': desc
    }
    resp = requests.post(apps_url, json=apps_data, verify=False, headers=authToken)
    if (resp.status_code != 201):
        return "App not created, response was {0}".format(resp.status_code), 1
    return "OK", 0

def create_version(authToken, url, app_alias, version_alias, version_name, version_desc):
    version_url = "{0}/developer/api/v1/versions/{1}".format(url, app_alias)
    version_data = {
        'name': version_name,
        'alias': version_alias,
        'description': version_desc
    }
    resp = requests.post(version_url, json=version_data, verify=False, headers=authToken)
    if (resp.status_code != 201):
        return "Version not created, response was {0}".format(resp.status_code), 1
    return "OK", 0

def delete_version(authToken, url, app_alias, version_alias):
    version_url = "{0}/versions/{1}/{2}".format(url, app_alias, version_alias)
    resp = requests.delete(version_url, verify=False, headers=authToken)
    if (resp.status_code != 204):
        return "Error - Response {0}".format(resp.status_code), 1
    return resp.status_code, 0

def delete_app(authToken, url, alias):
    apps_url = "{0}/developer/api/v1/apps/{1}".format(url, alias)
    resp = requests.delete(apps_url, verify=False, headers=authToken)
    if (resp.status_code != 204):
        return "Error - Response {0}".format(resp.status_code), 1
    return resp.status_code, 0

def set_archive(authToken, url, alias, version, archive_path, archive_uri):
    if archive_path == "":
        archive_url = "{0}/developer/api/v1/versions/{1}/{2}?action=setArchive&archiveUri={3}".format(url, alias, version, archive_uri)
        resp = requests.post(archive_url, headers=authToken, verify=False)
    else:
        archive_url = "{0}/developer/api/v1/versions/{1}/{2}?action=setArchive".format(url, alias, version)
        archive_file = {'archive': open(archive_path, "rb")}
        resp = requests.post(archive_url, files=archive_file, headers=authToken, verify=False)
    if (resp.status_code != 200):
        return resp.json(), 1
    return resp.json(), 0

def set_lifecycle_state(authToken, url, alias, version, state):
    version_url = "{0}/developer/api/v1/versions/{1}/{2}?action=promote&stage={3}".format(url, alias, version, state)
    resp = requests.post(version_url, headers=authToken, verify=False)
    if resp.status_code != 200:
        return resp.json(), 1
    return resp.json(), 0

def set_application_state(authToken, url, alias, version, state):
    version_url = "{0}/developer/api/v1/versions/{1}/{2}?action={3}".format(url, alias, version, state)
    resp = requests.post(version_url, headers=authToken, verify=False)
    if resp.status_code != 200:
        return "Error: {0}".format(resp.status_code), 1
    return resp.status_code, 0

def get_components(authToken, url, alias, version):
    component_url = "{0}/developer/api/v1/components/{1}/{2}".format(url, alias, version)
    resp = requests.get(component_url, headers=authToken, verify=False)
    if resp.status_code != 200:
        return resp.json(), 1
    return resp.json(), 0

def update_component(authToken, url, alias, version, component, new_settings):
    component_url = "{0}/developer/api/v1/components/{1}/{2}/{3}".format(url, alias, version, component)
    component_settings = requests.get(component_url, headers=authToken, verify=False).json()
    for key in component_settings:
        if key in new_settings:
            component_settings[key] = new_settings[key]
            if key == "resourcePolicy":
                policy_id = get_policy(authToken, url, new_settings[key])
                component_settings[key] = {'href': policy_id}
            
    resp = requests.put(component_url, json=component_settings, headers=authToken, verify=False)
    if resp.status_code != 204:
        return resp.status_code, 1
    return resp.status_code, 0

def create_subscription(authToken, url, alias, version, name, count, tenant):
    plan_url = "{0}/developer/api/v1/apps/{1}/versions/{2}/plans".format(url, alias, version)
    plans = requests.get(plan_url, headers=authToken, verify=False).json()
    for plan in plans['items']:
        if plan['name'] == name:
            plan_id = plan
    subscription_url = "{0}/developer/api/v1/apps/{1}/versions/{2}/tenants/{3}/subscriptions".format(url, alias, version, tenant)
    subscription_data = {
        'planName': name,
        'numberOfSubscriptions': count,
        'entitlementName': plan_id['entitlementName'],
        'entitlementDefinitionType': plan_id['entitlementDefinitionType']
    }
    resp = requests.post(subscription_url, headers=authToken, json=subscription_data, verify=False)
    locator_id = resp.json()[0]['locator']
    if resp.status_code != 201:
        return "Error - {0} {1}".format(resp.text, resp.status_code), 1
    return resp.json(), 0, locator_id

def get_policy(authToken, url, name):
    policy_url = "{0}/developer/api/v1/policies".format(url)
    resp = requests.get(policy_url, headers=authToken, verify=False)
    for policy in resp.json():
        if policy['name'] == name:
            return policy['href']

def main():
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True, choices=['list', 
                'create_application', 
                'delete_application', 
                'create_version', 
                'delete_version', 
                'set_archive',
                'set_lifecycle_state',
                'set_application_state',
                'update_component',
                'create_subscription']),
            apprenda_url=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            tenant=dict(type='str', required=True),
            app_name=dict(required=False, type='str'),
            app_alias=dict(required=False, type='str'),
            app_description=dict(required=False, type='str'),
            app_version_name=dict(required=False, type='str'),
            app_version_alias=dict(required=False, type='str'),
            app_version_desc=dict(required=False, type='str'),
            app_archive_path=dict(required=False, type='str'),
            app_archive_uri=dict(required=False, type='str'),
            app_patch_mode=dict(required=False, type='str'),
            app_lifecycle_state=dict(required=False, choices=['sandbox', 'published']),
            app_state=dict(required=False, choices=['started', 'stopped']),
            app_component_alias=dict(required=False, type='str'),
            app_component_settings=dict(required=False, type='dict'),
            app_subscription_count=dict(required=False, type='int'),
            app_subscription_plan_name=dict(required=False, type='str')
        )
    )
    action = module.params['action']
    apprenda_url = module.params['apprenda_url']
    username = module.params['username']
    password = module.params['password']
    tenant = module.params['tenant']

    authTokenString = authenticate(apprenda_url, username, password, tenant)
    authToken = { "ApprendaSessionToken": str(Header(authTokenString, 'utf-8')) }
    extra_facts = {}
    if action == "list" and (module.params['app_alias'] == "" or module.params['app_version_alias'] == ""):
        (out, rc) = list_apps(authToken, apprenda_url)
    if action == "list" and module.params['app_alias'] is not None and module.params['app_version_alias'] == "":
        alias = module.params['app_alias']
        (out, rc) = get_app_info(authToken, apprenda_url, alias)
    if action == "list" and module.params['app_alias'] != "" and module.params['app_version_alias'] != "":
        alias = module.params['app_alias']
        version_alias = module.params['app_version_alias']
        (out, rc) = get_version_info(authToken, apprenda_url, alias, version_alias)
    if action == "create_application":
        name = module.params['app_name']
        alias = module.params['app_alias']
        desc = module.params['app_description']
        (out, rc) = create_app(authToken, apprenda_url, name, alias, desc)
    if action == "delete_application":
        alias = module.params['app_alias']
        (out, rc) = delete_app(authToken, apprenda_url, alias)
    if action == "create_version":
        alias = module.params['app_alias']
        version_alias = module.params['app_version_alias']
        version_name = module.params['app_version_name']
        version_desc = module.params['app_version_desc']
        (out, rc) = create_version(authToken, apprenda_url, alias, version_alias, version_name, version_desc)
    if action == "delete_version":
        alias = module.params['app_alias']
        version_alias = module.params['app_version_alias']
        (out, rc) = delete_version(authToken, apprenda_url, alias, version_alias)
    if action == "set_archive":
        alias = module.params['app_alias']
        version_alias = module.params['app_version_alias']
        app_archive_path = module.params['app_archive_path']
        app_archive_uri = module.params['app_archive_uri']
        (out, rc) = set_archive(authToken, apprenda_url, alias, version_alias, app_archive_path, app_archive_uri)
    if action == "set_lifecycle_state":
        alias = module.params['app_alias']
        version_alias = module.params['app_version_alias']
        lifecycle_state = module.params['app_lifecycle_state']
        (out, rc) = set_lifecycle_state(authToken, apprenda_url, alias, version_alias, lifecycle_state)
    if action == "set_application_state":
        alias = module.params['app_alias']
        version_alias = module.params['app_version_alias']
        application_state = module.params['app_state']
        (out, rc) = set_application_state(authToken, apprenda_url, alias, version_alias, application_state)
    if action == "update_component":
        alias = module.params['app_alias']
        version_alias = module.params['app_version_alias']
        component_alias = module.params['app_component_alias']
        component_settings = module.params['app_component_settings']
        (out, rc) = update_component(authToken, apprenda_url, alias, version_alias, component_alias, component_settings)
    if action == "create_subscription":
        alias = module.params['app_alias']
        version_alias = module.params['app_version_alias']
        count = module.params['app_subscription_count']
        plan_name = module.params['app_subscription_plan_name']
        locator_id = ""
        (out, rc, locator_id) = create_subscription(authToken, apprenda_url, alias, version_alias, plan_name, count, tenant)
        extra_facts['locator_id'] = locator_id
    if (rc != 0):
        module.fail_json(msg="failure", result=out)
    if len(extra_facts) > 0:
        module.exit_json(msg="success", result=out, ansible_facts=extra_facts)
    else:
        module.exit_json(msg="success", result=out)

if __name__ == '__main__':
    main()