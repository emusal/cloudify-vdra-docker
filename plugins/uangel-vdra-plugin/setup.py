# coding=utf-8
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import setuptools

setuptools.setup(

    name='cloudify-uangel-vdra-plugin',
    version='1.0',
    author='UANGEL',
    author_email='emusal@uangel.com',
    description='A UANGEL vDRA plugin',
    license='LICENCE',
    install_requires=[
        'cloudify-plugins-common>=3.3rc1',
        'docker-py==1.8.1'
    ],
    packages=['docker_plugin'],
    zip_safe=False
)