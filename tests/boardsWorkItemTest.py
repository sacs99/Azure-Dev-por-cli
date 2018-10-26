# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.testsdk import ScenarioTest
from azure_devtools.scenario_tests import AllowLargeResponse

class AzureDevTests(ScenarioTest):
    @AllowLargeResponse(size_kb=3072)
    def test_workItemCreateShowUpdateDelete(self):
        wi_name = 'samplebug'
        wi_test_project_name = 'WorkItemCreateShowUpdateDeleteTests'
        wi_account_instance='https://AzureDevOpsCliTest.visualstudio.com'
        wi_account_pat = 'lwghjbj67fghokrgxsytghg75nk2ssguljk7a78qpcg2ttygviyt'

        self.cmd('az dev configure --defaults instance=' + wi_account_instance)
        self.cmd('az dev login --token ' + wi_account_pat)

        try:
            create_wi_command = 'az boards work-item create --project '+ wi_test_project_name +' --title ' + wi_name +' --type Bug  --detect off --output json'
            wi_create = self.cmd(create_wi_command, checks=[
                self.check('fields."System.AreaPath"', wi_test_project_name),
                self.check('fields."System.WorkItemType"', 'Bug'),
                self.check('fields."System.Title"', wi_name)
            ]).get_output_in_json()

            wi_id = wi_create['id']

            show_wi_command ='az boards work-item show -i ' + wi_account_instance + ' --id '+ str(wi_id) + ' --detect off --output json'
            self.cmd(show_wi_command, checks=[
                self.check("id", wi_id)
            ]).get_output_in_json()

            update_wi_command = 'az boards work-item update -i ' + wi_account_instance + ' --id '+ str(wi_id)+' --state Resolved --detect off --output json'
            self.cmd(update_wi_command, checks=[
                self.check("id", wi_id),
                self.check('fields."System.AreaPath"', wi_test_project_name),
                self.check('fields."System.State"','Resolved')
            ]).get_output_in_json()

        finally:
            #delete the work item created for test
            delete_wi_command = 'az boards work-item delete -i ' + wi_account_instance + ' --id ' + str(wi_id) + ' --yes --project ' + wi_test_project_name + ' --detect off --output json'
            delete_wi_response = self.cmd(delete_wi_command , checks=[
                self.check('id', wi_id)
            ]).get_output_in_json()

            # verify if the work item is deleted or not
            with self.assertRaises(CLIError) as wi_except:
                wi_show = self.cmd(show_wi_command).get_output_in_json()
            self.assertEqual(str(wi_except.exception), 'TF401232: Work item ' + str(wi_id) + ' does not exist, or you do not have permissions to read it.')


