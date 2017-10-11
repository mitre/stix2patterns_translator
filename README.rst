stix-pattern-translator
===================


This repository contains a prototype analytic translator that converts `STIX2 Patterning`_
queries into other query languages, currently ElasticSearch and Splunk. In addition to translating
query syntax, the translator will also translate from STIX 2's Data Model to other target data models,
currently MITRE's `Cyber Analytic Repository (CAR)`_ and Splunk's `Common Information Model (CIM)`_.
Both the query language translation and the data model translation are implemented as loosely-coupled
modules and other targets can be added simply by implementing new modules to generate them.

This functionality was originally developed for MITRE's CASCADE_ project.
This repository offers CASCADE's translation capability as a standalone feature,
and replaces CASCADE's own domain-specific language (DSL) with STIX 2.0 Patterning.

.. _`STIX2 Patterning`: http://docs.oasis-open.org/cti/stix/v2.0/stix-v2.0-part5-stix-patterning.html
.. _`Cyber Analytic Repository (CAR)`: https://car.mitre.org/wiki/Data_Model
.. _`Common Information Model (CIM)`: http://docs.splunk.com/Documentation/CIM/4.9.0/User/Overview
.. _CASCADE: https://github.com/mitre/cascade-server

Requirements
------------

-  `Python <https://www.python.org>`__ 3.3, 3.4, 3.5, or 3.6
-  ANTLR grammar runtime (4.7 or newer):

   -  `antlr4-python3-runtime <https://pypi.python.org/pypi/antlr4-python3-runtime>`__
      (Python 3)

   -  `python-dateutil <https://pypi.python.org/pypi/python-dateutil>`__ (Python 3.3)

Optionally, the Web API requires:

   -  `Flask <https://pypi.python.org/pypi/Flask>`__ (Python 3.3)


Installation
---------------

Install with `pip <https://pip.pypa.io/en/stable/>`__:

.. code:: bash

    $ pip install stix-pattern-translator
    
Optionally, to use the Web API, install with `pip <https://pip.pypa.io/en/stable/>`__:

.. code:: bash

    $ pip install stix-pattern-translator[web]

Note: if you are doing development, make sure to install the development dependencies with:

.. code:: bash

    $ pip install stix-pattern-translator[dev]

Usage
-----

The STIX Analytic Translator provides an executable script (`translate-pattern`), a simple web API provided as a Flask application, and Python translation
method (`stix2patterns_translator.translate`).

From Python Code
~~~~~~~~~~~~~~~~

.. code:: python

    from stix2patterns_translator.translator import *

    translate("[file:hashes.MD5 = '79054025255fb1a26e4bc422aef54eb4']", SearchPlatforms.ELASTIC, DataModels.CAR)

Command Line
~~~~~~~~~~~~

Use the command `translate-stix-pattern`, passing in the desired output language, data taxonomy, and STIX2 pattern:

.. code:: bash

    $ translate-stix-pattern --output-language=elastic --output-data-model=car "[file:hashes.MD5 = '79054025255fb1a26e4bc422aef54eb4']"

Web API
~~~~~~~

The web API is provided as a Flask server that accepts the STIX pattern as input and returns the translated pattern. The path determines the output
search platform and data taxonomy. To run the web server, install the 'web' extras (flask).

.. code:: bash

    $ pip install stix-pattern-translator[web]

The server can be run directly from the source code, via a command line script, or by importing the code into an existing application. The easiest way to
test it is via the command line script:

.. code:: bash

    $ pattern-translator-server

With the server running, use a command-line to send and receive from Flask instance, either locally or across a network.
As the below example shows, using cURL to send a POST with JSON generates results back to the calling shell:

.. code:: bash

    $ curl -X POST -H "Content-Type: text/plain" -d "[process:pid <= 5]" http://localhost:5000/car-elastic

That yields:

.. code:: bash

    data_model.object:"process" AND data_model.action:"*" AND (
        data_model.fields.pid:<=5
    )

Testing
-------

Pytest integration tests are auto generated from input patterns pulled from files in test/input_files. Input files are named by test type,
e.g. "md5_hash.json" and contain json with input pattern (key = stix-input) and expected results, where the key is <datamodel>-<platform>
and the value is the expected result:

.. code:: json

    {
      "stix-input":"[file:hashes.MD5 ='79054025255fb1a26e4bc422aef54eb4']",
      "car-elastic":"data_model.object:\"file\" AND data_model.action:\"*\" AND (data_model.fields.md5_hash:\"79054025255fb1a26e4bc422aef54eb4\")",
      "car-splunk":"match(tag, \"dm-file-.*\") md5_hash=\"79054025255fb1a26e4bc422aef54eb4\"",
      "cim-elastic": null,
      "cim-splunk":null
    }

Expected result can either be a string, which tests for success and a match of that string, or null, which tests for error.
As usual, the tests can be run by running pytest:

.. code:: bash

    pytest

Tests can also be run that push events to Splunk/Elastic and then making sure the correct events match. They use the same input files, but require a few
additional keys. The "matches" key should contain a dictionary with a set of keys for each data model (currently just "CAR"). That dictionary then contains
a list of events that should match the pattern. The "nonmatches" key is identical, but obviously will be tested to make sure they don't match.
Running the live integration tests requires starting docker:

.. code:: bash

    docker-compose -f test.docker-compose.yml up

They can then be run via pytest, by calling the test directly:

.. code:: bash

    pytest test/integration_tests.py
