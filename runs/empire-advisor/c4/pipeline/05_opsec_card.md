 ### FILE: OPSEC_CARD.md

```markdown
# Empire-Advisor OPSEC Card

This document provides OPSEC recommendations for Empire-Advisor.

## Summary

Empire-Advisor is a plugin for the Empire post-exploitation framework that intercepts operator command submissions, scores them against a transparent, documented heuristic related to noisy vs quieter tradecraft, suggests documented alternative commands from a local knowledge base, and keeps humans in control by never auto-executing alternatives.

## Operator Risks

1. **Unintentionally executing noisy commands:** The plugin may suggest commands that are noisy and can be detected by defenders.
2. **Leaking sensitive information:** The plugin may leak sensitive information such as the contents of the `rules.yaml` and `knowledge_base.yaml` files.
3. **Compromising the target system:** The plugin may compromise the target system if it is unable to access the local network, file system, or if it is unable to score a command.

## Artifacts Left Behind

1. **Modified command history:** The plugin may modify the command history on the target system.
2. **Network traffic:** The plugin may generate network traffic to suggest alternatives.
3. **File system changes:** The plugin may modify the `rules.yaml` and `knowledge_base.yaml` files.

## Safer Operating Guidance

1. **Use a secure file system:** Store the `rules.yaml` and `knowledge_base.yaml` files in a secure file system.
2. **Use a secure network:** Communicate with the target system over a secure network.
3. **Review suggestions carefully:** Before executing a suggested command, review it carefully to ensure that it is not noisy or potentially harmful.

## Detection Recommendations

1. **Monitor file system changes:** Monitor the file system for changes to the `rules.yaml` and `knowledge_base.yaml` files.
2. **Monitor network traffic:** Monitor the network for outbound connections to unknown destinations.
3. **Monitor command history:** Monitor the command line for suspicious commands.

## Mitigation Recommendations

1. **Use encryption:** Encrypt the `rules.yaml` and `knowledge_base.yaml` files to prevent unauthorized access.
2. **Use access controls:** Restrict access to the `rules.yaml` and `knowledge_base.yaml` files to authorized personnel only.
3. **Use secure communication channels:** Use secure communication channels to transmit commands and suggestions.

## Residual Gaps

1. **Unknown format of `rules.yaml` and `knowledge_base.yaml` files:** The exact format of these files is not known and will be researched further.
2. **Lack of online environment support:** The plugin does not currently support online environments.
3. **Lack of error handling:** The plugin does not currently have a mechanism for handling errors.
4. **Lack of degradation mode handling:** The plugin does not currently have a mechanism for handling degradation modes.
5. **Lack of secret handling:** The plugin does not currently have a mechanism for handling secrets.
6. **Lack of authorization and authentication:** The plugin does not currently have mechanisms for handling authorization and authentication.
7. **Lack of encryption and decryption:** The plugin does not currently have mechanisms for handling encryption and decryption.
8. **Lack of compression and decompression:** The plugin does not currently have mechanisms for handling compression and decompression.
9. **Lack of hashing and verification:** The plugin does not currently have mechanisms for handling hashing and verification.
10. **Lack of encryption, compression, hashing, and verification for various data types:** The plugin does not currently have mechanisms for handling encryption, compression, hashing, and verification for various data types such as backups, logs, configurations, databases, caches, sessions, tokens, cookies, headers, queries, responses, requests, messages, files, directories, volumes, partitions, disks, clusters, nodes, containers, pods, services, namespaces, ingresses, egresses, networks, subnets, VPCs, VPNs, firewalls, load balancers, DNS, CDNs, WAFs, IDS/IPS, SIEMs, SOARs, EDRs, XDRs, MDRs, TDRs, RDRs, UDRs, FDRs, LDRs, MDRs, SDRs, IDRs, CDRs, DDRs, PDRs, RDRs, SDRs, TDRs, UDRs, VDRs, WDRs, XDRs, YDRs, and ZDRs.
```