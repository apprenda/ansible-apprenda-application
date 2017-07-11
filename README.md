Apprenda Application
=========

This role enables management of Apprenda Applications.

Requirements
------------

* Apprenda Cloud Platform v7.1 or higher
* Python requests library

Role Variables
--------------

`apprenda_url` - FQDN of your ACP instance (i.e, `https://apps.apprenda.com`) **Required**

`username` - Platform user to execute role actions under. **Required**

`password` - Password of the platform user. **Required**

`tenant` - Tenant Alias of the platform user. **Required**

`action` - The action to perform. This can be one of the following. Required parameters for each action are below the action. **Required**
- `create_application`: Creates a new Apprenda application.
  - `app_name`: The application name.
  - `app_alias`: The application alias.
  - `app_description`: The application description.
- `delete_application`: Deletes an existing Apprenda application.
  - `app_alias`: The application alias.
- `create_version`: Creates a new version of an existing Apprenda application.
  - `app_alias`: The application alias.
  - `app_version_alias`: The version alias.
  - `app_version_name`: The version name.
  - `app_version_desc`: The version description.
- `delete_version`: Deletes an existing version of an existing Apprenda application.
  - `app_alias`: The application alias.
  - `app_version_alias`: The version alias.
- `set_archive`: Sets the archive for an existing version of an existing Apprenda application.
  - `app_alias`: The application alias.
  - `app_version_alias`: The version alias.
  - `app_archive_path` or `app_archive_uri`: Exclusive; Either the local path to the application archive, or a URI where it can be downloaded from.
- `set_lifecycle_state`: Sets the lifecycle state (`sandbox` or `published`) for a version of an existing Apprenda application.
  - `app_alias`: The application alias.
  - `app_version_alias`: The version alias.
  - `app_lifecycle_state`: One of `sandbox` or `published`.
- `set_application_state`: Sets the application state (`started` or `stopped`) for a version of an existing Apprenda application.
  - `app_alias`: The application alias.
  - `app_version_alias`: The version alias.
  - `app_state`: One of `started` or `stopped`.
- `update_component`: Sets various options on a component of an existing version of an existing Apprenda application.
  - `app_alias`: The application alias.
  - `app_version_alias`: The version alias.
  - `app_component_alias`: The component alias to update.
  - `app_component_settings`: The settings to update as a dictionary. Please see ACP Developer REST API documentation for more information.
- `create_subscription`: Creates a subscription to an existing version of an existing Multi-Tenant Apprenda application. Sets the `locator_id` fact.
  - `app_alias`: The application alias.
  - `app_version_alias`: The version alias.
  - `app_subscription_count`: The amount of subscriptions to create.
  - `app_subscription_plan_name`: The name of the plan to create a subscription to.

Dependencies
------------


Example Playbook
----------------

This demonstrates how to create an application, set a version, change component information, and create an application subscription.


    - hosts: localhost
      roles:
      - role: "apprenda_application"
        name: "Create new test app"
        action: "create_application"
        app_name: "Ansible Test Application"
        app_alias: "ansibledemo"
        app_description: "A Test Application for Demonstrating Ansible"
      
      - role: "apprenda_application"
        name: "Set application archive to test archive"
        action: "set_archive"
        app_alias: "ansibledemo"
        app_version_alias: "v1"
        app_archive_path: "/users/apprenda/web.zip"

      - role: "apprenda_application"
        name: "Promote test app to published"
        action: "set_lifecycle_state"
        app_alias: "ansibledemo"
        app_version_alias: "v1"
        app_lifecycle_state: "published"

      - role: "apprenda_application"
        name: "Set maximum instance count to 2, enable auto scaling, and apply resource policy"
        action: "update_component"
        app_alias: "ansibledemo"
        app_version_alias: "v1"
        app_component_alias: "ui-root"
        app_component_settings: {
          "scalingType": "Automatic",
          "maximumInstanceCount": 2,
          "resourcePolicy": "small"
        }
      
      - role: "apprenda_application"
        name: "Create subscription to BasicPlan"
        action: "create_subscription"
        app_alias: "ansibledemo"
        app_version_alias: "v1"
        app_subscription_plan_name: "BasicPlan"

License
-------

MIT

Author Information
------------------

Please see http://www.apprenda.com for more information about the Apprenda Cloud Platform.
