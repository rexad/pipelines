# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import warnings
from kubernetes import client as k8s_client

from ..dsl._container_op import BaseOp, ContainerOp


def add_pod_env(op: BaseOp) -> BaseOp:
  """Adds environment info if the Pod has the label `add-pod-env = true`.
    """
  if isinstance(
      op, ContainerOp
  ) and op.pod_labels and 'add-pod-env' in op.pod_labels and op.pod_labels[
      'add-pod-env'] == 'true':
    return add_kfp_pod_env(op)


def add_kfp_pod_env(op: BaseOp) -> BaseOp:
  """Adds KFP pod environment info to the specified ContainerOp.
    """
  if not isinstance(op, ContainerOp):
    warnings.warn(
        'Trying to add default KFP environment variables to an Op that is '
        'not a ContainerOp. Ignoring request.')
    return op

  op.container.add_env_variable(
      k8s_client.V1EnvVar(name='KFP_POD_NAME',
                          value_from=k8s_client.V1EnvVarSource(
                              field_ref=k8s_client.V1ObjectFieldSelector(
                                  field_path='metadata.name')))
  ).add_env_variable(
      k8s_client.V1EnvVar(name='KFP_NAMESPACE',
                          value_from=k8s_client.V1EnvVarSource(
                              field_ref=k8s_client.V1ObjectFieldSelector(
                                  field_path='metadata.namespace')))
  ).add_env_variable(
      k8s_client.V1EnvVar(
          name='WORKFLOW_ID',
          value_from=k8s_client.
          V1EnvVarSource(field_ref=k8s_client.V1ObjectFieldSelector(
              field_path="metadata.labels['workflows.argoproj.io/workflow']")))
  )
  return op
