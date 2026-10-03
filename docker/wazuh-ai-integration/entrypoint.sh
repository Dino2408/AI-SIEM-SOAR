#!/bin/sh
set -eu
CONF="/wazuh-config-mount/etc/ossec.conf"
if [ -f "$CONF" ] && ! grep -q '<name>custom-ai</name>' "$CONF"; then
  python3 - "$CONF" <<'PY'
import sys
p=sys.argv[1]
s=open(p,encoding="utf-8").read()
block="""
  <!-- AI-SIEM-SOAR integration -->
  <localfile>
    <location>/var/log/suricata/eve.json</location>
    <log_format>json</log_format>
    <label key="@source">suricata</label>
  </localfile>
  <integration>
    <name>custom-ai</name>
    <hook_url>http://ai-analysis:8080/v1/webhook/wazuh</hook_url>
    <level>3</level>
    <alert_format>json</alert_format>
    <timeout>10</timeout>
    <retries>2</retries>
  </integration>
"""
pos=s.rfind("</ossec_config>")
if pos>=0:
    s=s[:pos]+block+s[pos:]
    open(p,"w",encoding="utf-8").write(s)
PY
fi
exec /init "$@"
