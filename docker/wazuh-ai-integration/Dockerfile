ARG WAZUH_VERSION=4.14.8
FROM wazuh/wazuh-manager:\${WAZUH_VERSION}
COPY docker/wazuh-ai-integration/custom-ai /var/ossec/integrations/custom-ai
COPY docker/wazuh-ai-integration/entrypoint.sh /entrypoint-custom-ai.sh
RUN chmod 750 /var/ossec/integrations/custom-ai /entrypoint-custom-ai.sh && chown root:wazuh /var/ossec/integrations/custom-ai
ENTRYPOINT ["/entrypoint-custom-ai.sh"]
