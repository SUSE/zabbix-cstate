#!/bin/sh
# Container entrypoint for the Zabbix Cstate synchronization server
# The following container variables are mandatory: ZC_ISSUES
# The following container variables are optional: ZC_LOGLEVEL ZC_HOST ZC_PORT
#
# Copyright 2023, Georg Pfuetzenreuter for SUSE LLC
#
# Licensed under the EUPL, Version 1.2 or - as soon they will be approved by the European Commission - subsequent versions of the EUPL (the "Licence").
# You may not use this work except in compliance with the Licence.
# An English copy of the Licence is shipped in a file called LICENSE along with this applications source code.
# You may obtain copies of the Licence in any of the official languages at https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12.
#
set -Ce

config="/usr/local/etc/zc/zabbix-cstate"
sedbin="/usr/bin/sed"

prepare () {
        set -- \
                'ZC_ISSUES'
        mandatory_settings="$@"

        for setting
        do
                eval var='$'"$1"
                if [ -z "$var" ]
                then
                        echo "Did you forget to define $setting? Aborting startup."
                        exit 1
                fi
        done

        set -- \
                'ZC_LOGLEVEL' 'ZC_HOST' 'ZC_PORT'
        optional_settings="$@"

        if [ -z "$ZC_HOST" ]
        then
            ZC_HOST='*'
        fi

}

setup () {
        set -- $mandatory_settings $optional_settings

        for setting
        do
                eval var='$'"$setting"
                if [ -n "$var" ]
                then
                    echo "$setting=$var" >> "$config"
                fi
        done

}

init () {
        prepare
        setup
        set -a
        . "$config"
        exec "$1"
}

init "$@"
