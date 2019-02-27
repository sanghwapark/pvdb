#!/bin/csh

#set pvdb enviroment

#Check rcdb environment variables first
if ( ! $?RCDB_HOME ) then
   echo "Did you set rcdb environment variables?"
   echo "Go to rcdb and source environment.csh"
   exit(1)
endif

#set pvdb python path
set CURRENT_DIR = `pwd`

setenv PYTHONPATH "$CURRENT_DIR":$PYTHONPATH
