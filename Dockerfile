#!BuildTag: suseinfra/zabbix-cstate:latest

FROM suse/sle15:15.4

MAINTAINER georg.pfuetzenreuter@suse.com

# labelprefix=de.suse.libertacasa.pipeline
LABEL org.opencontainers.image.title="Zabbix Cstate"
LABEL org.opencontainers.image.description="Zabbix Cstate Synchronization Server"
LABEL org.openbuildservice.disturl="%DISTURL%"
LABEL org.opencontainers.image.created="%BUILDTIME%"
LABEL com.suse.eula="sle-bci"
LABEL com.suse.image-type="application"
# endlabelprefix

RUN set -eu ; \
	zypper ar https://download.opensuse.org/repositories/isv:/SUSEInfra:/Tools/15.4 InfraTools ; \
	zypper -n --gpg-auto-import-keys ref ; \
	zypper -n in zabbix-cstate ; \
	zypper -n clean -a

ENTRYPOINT ["/usr/bin/python3"]
CMD ["/usr/bin/zabbix-cstate"]
HEALTHCHECK --interval=30s --timeout=5s --retries=1 CMD ["curl", "-fI", "localhost:8090"]
