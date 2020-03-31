Misty Package Manager (mpm)
===========================

Getting Started
---------------

Install ``mpm`` as a `Python package <https://pypi.org/project/mpm/>`_::

  pip install mpm

Create an empty skill named "demo"::

  mpm init demo

The resulting JavaScript (JS) file and meta file are in the directory src/. When
ready, create a bundle and upload it to a Misty robot::

  mpm build
  mpm upload

If not configured already, ``upload`` will fail because the robot address is not
known.  Enter the address of the robot with ``mpm config``. For example, ::

  mpm config --addr 192.168.1.30

(Change ``192.168.1.30`` as needed.) Start to execute the skill::

  mpm skillstart


Participating
-------------

All participation must follow our code of conduct, elaborated in the file
CODE_OF_CONDUCT.md in the same directory as this README.

The source code repository is available at https://github.com/rerobots/MistyPackageManager


License
-------

This is free software, released under the Apache License, Version 2.0.
You may obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
