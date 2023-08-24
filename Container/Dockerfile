#!BuildTag: suseinfra/zabbix-cstate:latest

# Copyright 2023, Georg Pfuetzenreuter for SUSE LLC
#
# Licensed under the EUPL, Version 1.2 or - as soon they will be approved by the European Commission - subsequent versions of the EUPL (the "Licence").
# You may not use this work except in compliance with the Licence.
# An English copy of the Licence is shipped in a file called LICENSE along with this applications source code.
# You may obtain copies of the Licence in any of the official languages at https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12.

FROM suse/sle15:15.5

MAINTAINER georg.pfuetzenreuter@suse.com

# labelprefix=de.suse.infra.zabbix-cstate
LABEL org.opencontainers.image.title="Zabbix Cstate"
LABEL org.opencontainers.image.description="Zabbix Cstate Synchronization Server"
LABEL org.openbuildservice.disturl="%DISTURL%"
LABEL org.opencontainers.image.created="%BUILDTIME%"
LABEL com.suse.eula="sle-bci"
LABEL com.suse.image-type="application"
# endlabelprefix

COPY entrypoint.sh /usr/local/sbin/

RUN set -eu ; \
	zypper ar https://download.opensuse.org/repositories/isv:/SUSEInfra:/Tools/15.4 InfraTools ; \
	zypper -n --gpg-auto-import-keys ref ; \
	zypper -n in zabbix-cstate ; \
	zypper -n clean -a ; \
	mkdir -p /usr/local/etc/zc ; chown _zabbixcstate /usr/local/etc/zc

EXPOSE 8090

USER _zabbixcstate

ENTRYPOINT ["/usr/local/sbin/entrypoint.sh"]

CMD ["/usr/bin/zabbix-cstate"]

# to-do, add healthz endpoint?
#HEALTHCHECK --interval=30s --timeout=5s --retries=1 CMD ["curl", "-fI", "localhost:8090"]
