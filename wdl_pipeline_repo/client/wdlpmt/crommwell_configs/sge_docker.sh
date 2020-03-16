#!/bin/bash

# pipeline parameter
input_json=input.json

# You may change the pipline path

pathdir=/export/personal/menggl/dev/Hi-C_Assembly_pipeline
workflow_source=${pathdir}/src/wdl/LibraryQC/Workflow/LibraryQC.wdl
depends=${pathdir}/src.zip
template_cromwell_config=${pathdir}/docker/template.sge.normal-user.docker.config

cromwell_jar=/export/personal/menggl/soft/cromwell-47/cromwell-47.jar

# Create a new cromwell config file
cromwell_config="cromwell.config"

if [ -f "${cromwell_config}" ];
then
    echo Using existing Cromwell configure file: ${cromwell_config}
  
else
    sed  "s#__DOCKER_ROOT__#$PWD/cromwell\-executions#" ${template_cromwell_config} > ${cromwell_config}

fi

# Run the WDL pipeline
java -Xmx2G -Dsystem.job-shell=/bin/sh \
-Dconfig.file=${cromwell_config} \
-jar ${cromwell_jar} run \
${workflow_source} \
-p ${depends} \
-i ${input_json} \
1>crm.log 2>crm.err
