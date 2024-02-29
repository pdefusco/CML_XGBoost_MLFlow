#****************************************************************************
# (C) Cloudera, Inc. 2020-2023
#  All rights reserved.
#
#  Applicable Open Source License: GNU Affero General Public License v3.0
#
#  NOTE: Cloudera open source products are modular software products
#  made up of hundreds of individual components, each of which was
#  individually copyrighted.  Each Cloudera open source product is a
#  collective work under U.S. Copyright Law. Your license to use the
#  collective work is as provided in your written agreement with
#  Cloudera.  Used apart from the collective work, this file is
#  licensed for your use pursuant to the open source license
#  identified above.
#
#  This code is provided to you pursuant a written agreement with
#  (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
#  this code. If you do not have a written agreement with Cloudera nor
#  with an authorized and properly licensed third party, you do not
#  have any rights to access nor to use this code.
#
#  Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
#  contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
#  KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
#  WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
#  IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
#  AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
#  ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
#  OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
#  CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
#  RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
#  BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
#  DATA.
#
# #  Author(s): Paul de Fusco
#***************************************************************************/

from __future__ import print_function
import cmlapi
from cmlapi.rest import ApiException
from pprint import pprint
import json, secrets, os, time
import mlflow


class ModelDeployment():
    """
    Class to manage the model deployment of the xgboost model
    """

    def __init__(self, client, projectId, username, experimentName, experimentId):
        self.client = client
        self.projectId = projectId
        self.username = username
        self.experimentName = experimentName
        self.experimentId = experimentId

    def registerModelFromExperimentRun(modelName, experimentId, experimentRunId, modelPath, sessionId):
        """
        Method to register a model from an Experiment Run
        This is an alternative to the mlflow method to register a model via the register_model parameter in the log_model method
        Input: requires an experiment run
        Output:
        """

        model_name = 'wine_model_' + username + "-" + sessionId

        CreateRegisteredModelRequest = {
                                        "project_id": os.environ['CDSW_PROJECT_ID'],
                                        "experiment_id" : experimentId,
                                        "run_id": experimentRunId,
                                        "model_name": modelName,
                                        "model_path": modelPath
                                       }

        try:
            # Register a model.
            api_response = client.create_registered_model(CreateRegisteredModelRequest)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling CMLServiceApi->create_registered_model: %s\n" % e)

        return api_response

    def createPRDProject():
        """
        Method to create a PRD Project
        """

        createProjRequest = {"name": "mlops_prd_prj", "template":"git", "git_url":"https://github.com/pdefusco/MLOps_CML_PRD_Proj.git"}

        try:
            # Create a new project
            api_response = client.create_project(createProjRequest)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling CMLServiceApi->create_project: %s\n" % e)

        return api_response

    def validatePRDProject(username):
        """
        Method to test successful project creation
        """

        try:
            # Return all projects, optionally filtered, sorted, and paginated.
            search_filter = {"owner.username" : username}
            search = json.dumps(search_filter)
            api_response = client.list_projects(search_filter=search)
            #pprint(api_response)
        except ApiException as e:
            print("Exception when calling CMLServiceApi->list_projects: %s\n" % e)

        return api_response

    def createModel(projectId, modelName, modelId, description = "My Spark Clf"):
        """
        Method to create a model
        """

        CreateModelRequest = {
                                "project_id": projectId,
                                "name" : modelName,
                                "description": description,
                                "registered_model_id": modelId
                             }

        try:
            # Create a model.
            api_response = client.create_model(CreateModelRequest, projectId)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling CMLServiceApi->create_model: %s\n" % e)

        return api_response

    def createModelBuild(projectId, modelVersionId, modelCreationId):
        """
        Method to create a Model build
        """

        # Create Model Build
        CreateModelBuildRequest = {
                                    "registered_model_version_id": modelVersionId,
                                    "runtime_identifier": "docker.repository.cloudera.com/cloudera/cdsw/ml-runtime-workbench-python3.9-standard:2023.08.2-b8",
                                    "comment": "invoking model build",
                                    "model_id": modelCreationId
                                  }

        try:
            # Create a model build.
            api_response = client.create_model_build(CreateModelBuildRequest, projectId, modelCreationId)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling CMLServiceApi->create_model_build: %s\n" % e)

        return api_response

    def createModelDeployment(modelBuildId, projectId, modelCreationId):
        """
        Method to deploy a model build
        """

        CreateModelDeploymentRequest = {
          "cpu" : "2",
          "memory" : "4"
        }

        try:
            # Create a model deployment.
            api_response = client.create_model_deployment(CreateModelDeploymentRequest, projectId, modelCreationId, modelBuildId)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling CMLServiceApi->create_model_deployment: %s\n" % e)

        return api_response


client = cmlapi.default_client()

client.list_projects()

projectId = os.environ['CDSW_PROJECT_ID']
username = os.environ["PROJECT_OWNER"]

experimentName = "MySparkMlClf"
experimentId = mlflow.get_experiment_by_name(experimentName).experiment_id
runsDf = mlflow.search_runs(experimentId, run_view_type=1)

experimentId = runsDf.iloc[-1]['experiment_id']
experimentRunId = runsDf.iloc[-1]['run_id']

deployment = ModelDeployment(client, projectId, username, experimentName, experimentId)

sessionId = secrets.token_hex(nbytes=4)
modelPath = "best-model"
modelName = "SparkClf-" + username + "-" + sessionId

registeredModelResponse = deployment.registerModelFromExperimentRun(modelName, experimentId, experimentRunId, modelPath, sessionId)
projectCreationResponse = deployment.createPRDProject()
apiResp = deployment.validatePRDProject(os.environ["PROJECT_OWNER"])

prdProjId = projectCreationResponse.id
modelId = registeredModelResponse.model_id
modelVersionId = registeredModelResponse.model_versions[0].model_version_id
modelName = "SparkClf-" + username + "-" + sessionId

registeredModelResponse.model_versions[0].model_version_id

createModelResponse = deployment.createModel(prdProjId, modelName, modelId)

modelCreationId = createModelResponse.id

createModelBuildResponse = deployment.createModelBuild(prdProjId, modelVersionId, modelCreationId)

modelBuildId = createModelBuildResponse.id

deployment.createModelDeployment(modelBuildId, prdProjId, modelCreationId)

## NOW TRY A REQUEST WITH THIS PAYLOAD!

model_request = {"dataframe_split": {"columns": ["age", "credit_card_balance", "bank_account_balance", "mortgage_balance", "primary_loan_balance", "sec_bank_account_balance", "savings_account_balance", "sec_savings_account_balance", "secondary_loan_balance", "total_est_nworth", "college_loan_balance", "transaction_amount", "latitude", "longitude"],
                                     "data":[[11.5, 20000.5, 3900.5, 14000.5, 2944.5, 3400.5, 12000.5, 29000.5, 1300.5, 15000.5, 10000.5, 2000.5, 90.5, 120.5]]}}

#REMEMBER TO MAKE SURE ALL NUMBERS ARE FLOATS
#model_request = {"dataframe_split": {"columns":["fixed acidity", "volatile acidity", "citric acid",
#"residual sugar", "chlorides", "free sulfur dioxide", "total sulfur dioxide", "density", "pH",
#"sulphates", "alcohol"],"data":[[6.2, 0.66, 0.48, 1.2, 0.029, 29.1, 75.1, 0.98, 3.33, 0.39, 12.8]]}}